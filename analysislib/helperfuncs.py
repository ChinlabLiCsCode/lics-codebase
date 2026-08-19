import os
import glob
import time
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import clear_output, display, HTML
from scipy.optimize import curve_fit
from labscript_utils.labconfig import LabConfig
from lyse.dataframe_utilities import get_dataframe_from_shots, get_series_from_shot


# ── DataFrame helpers (shared with multishot_scan_plotter) ────────────────────

def get_column(df, key):
    """Return a Series from df by string name or (routine, result) tuple.

    Globals are stored as (name, '') in the lyse DataFrame.
    """
    if key in df.columns:
        return df[key]
    if isinstance(key, str):
        if (key, '') in df.columns:
            return df[(key, '')]
        matches = [c for c in df.columns if (isinstance(c, tuple) and c[-1] == key) or c == key]
        if len(matches) == 1:
            return df[matches[0]]
        if len(matches) > 1:
            raise KeyError(f"Ambiguous key {key!r} — matches {matches}. Use a tuple.")
    raise KeyError(f"Column {key!r} not found in DataFrame.")


def col_label(key):
    if isinstance(key, tuple):
        return key[0] if key[-1] == '' else key[-1]
    return key


def find_scanned_globals(df):
    """Return column keys for numeric globals that vary across shots."""
    meta = {'filepath', 'sequence_index', 'run number', 'run repeat', 'sequence', 'run'}
    scanned = []
    for col in df.columns:
        if not (isinstance(col, tuple) and col[-1] == ''):
            continue
        if col[0] in meta:
            continue
        try:
            vals = df[col].dropna()
            if np.issubdtype(vals.dtype, np.number) and vals.nunique() >= 2:
                scanned.append(col)
        except Exception:
            pass
    return scanned


_FIT_TYPES = ('mean', 'linear', 'quadratic', 'gaussian', 'exponential', 'ballistic')


def _resolve_fits(fits, pairs):
    """Return a list of fit-type strings (or None) aligned to pairs."""
    if fits is None:
        return [None] * len(pairs)
    if isinstance(fits, str):
        return [fits] * len(pairs)
    if isinstance(fits, (list, tuple)):
        return list(fits)
    if isinstance(fits, dict):
        result = []
        for i, (rkey, skey) in enumerate(pairs):
            val = fits.get((rkey, skey))           # exact: (full_rkey, skey)
            if val is None:
                val = fits.get((col_label(rkey), skey))  # short: ('N_int', skey)
            if val is None:
                val = fits.get(i)                  # by subplot index
            result.append(val)
        return result
    raise TypeError(f'fits must be a string, list, or dict; got {type(fits)}')


def _do_fit(fit_type, x, y, yerr=None):
    """Fit y(x) and return (x_fine, y_fit, label, marker, coeffs).

    marker is (x, y) for the fit centre (gaussian/quadratic), else None.
    coeffs is a dict of named fit parameters for downstream calculation.
    Raises on failure.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    sigma = np.asarray(yerr, dtype=float) if yerr is not None else None
    if sigma is not None and not np.all(np.isfinite(sigma) & (sigma > 0)):
        sigma = None
    x_fine = np.linspace(x.min(), x.max(), 300)

    if fit_type == 'mean':
        weights = 1 / sigma**2 if sigma is not None else None
        val = np.average(y, weights=weights)
        return (x_fine, np.full_like(x_fine, val), f'mean = {val:.4g}',
                None, {'type': 'mean', 'mean': val})

    if fit_type == 'linear':
        if len(x) < 2:
            raise ValueError('need ≥2 points for linear fit')
        w = np.sqrt(1 / sigma**2) if sigma is not None else None
        a, b = np.polyfit(x, y, 1, w=w)
        sign = '+' if b >= 0 else '-'
        return (x_fine, a * x_fine + b, f'{a:.3g}x {sign} {abs(b):.3g}',
                None, {'type': 'linear', 'slope': a, 'intercept': b})

    if fit_type == 'quadratic':
        if len(x) < 3:
            raise ValueError('need ≥3 points for quadratic fit')
        w = np.sqrt(1 / sigma**2) if sigma is not None else None
        a, b, c = np.polyfit(x, y, 2, w=w)
        x_vertex = -b / (2 * a)
        y_vertex = c - b**2 / (4 * a)
        sign = '+' if b >= 0 else '-'
        label = f'{a:.3g}x² {sign} {abs(b):.3g}x, vertex={x_vertex:.4g}'
        return (x_fine, np.polyval([a, b, c], x_fine), label,
                (x_vertex, y_vertex),
                {'type': 'quadratic', 'a': a, 'b': b, 'c': c,
                 'vertex_x': x_vertex, 'vertex_y': y_vertex})

    if fit_type == 'gaussian':
        if len(x) < 4:
            raise ValueError('need ≥4 points for gaussian fit')
        def gauss(x, A, x0, sig, B):
            return A * np.exp(-(x - x0)**2 / (2 * sig**2)) + B
        A0 = y.max() - y.min()
        x0_0 = x[np.argmax(y)]
        sig0 = max((x.max() - x.min()) / 4, 1e-10)
        popt, _ = curve_fit(gauss, x, y, p0=[A0, x0_0, sig0, y.min()],
                            sigma=sigma, maxfev=10000,
                            bounds=([-np.inf, x.min(), 0, -np.inf],
                                    [np.inf, x.max(), np.inf, np.inf]))
        A, x0, sig, B = popt
        return (x_fine, gauss(x_fine, *popt), f'μ={x0:.4g}, σ={sig:.4g}',
                (x0, A + B),
                {'type': 'gaussian', 'A': A, 'x0': x0, 'sigma': sig, 'B': B})

    if fit_type == 'exponential':
        if len(x) < 3:
            raise ValueError('need ≥3 points for exponential fit')
        # fit A·exp(−rate·(x−x[0])) + B; rate>0 → decay, rate<0 → growth
        xs = x - x[0]
        def exp_func(xs, A, rate, B):
            return A * np.exp(-rate * xs) + B
        A0 = float(y[0] - y[-1])
        span = float(xs[-1]) if xs[-1] != 0 else 1.0
        p0 = [A0 if A0 != 0 else 1.0, 1.0 / span, float(y[-1])]
        popt, _ = curve_fit(exp_func, xs, y, p0=p0, sigma=sigma, maxfev=10000)
        A, rate, B = popt
        tau = 1.0 / rate if rate != 0 else np.inf
        return (x_fine, exp_func(x_fine - x[0], *popt), f'τ={tau:.4g}',
                None, {'type': 'exponential', 'A': A, 'rate': rate, 'tau': tau, 'B': B})

    if fit_type == 'ballistic':
        # σ²(t) = σ₀² + v_rms²·t²  — linear fit in (t², σ²) space
        if len(x) < 2:
            raise ValueError('need ≥2 points for ballistic fit')
        t2 = x**2
        s2 = y**2
        w = None
        if sigma is not None:
            s2_err = 2 * y * sigma   # error propagation: d(y²) = 2y·dy
            if np.all(s2_err > 0):
                w = 1 / s2_err
        slope, intercept = np.polyfit(t2, s2, 1, w=w)
        intercept = max(intercept, 0.0)   # σ₀² must be non-negative
        v_rms  = np.sqrt(max(slope, 0.0))
        sigma0 = np.sqrt(intercept)
        y_fit  = np.sqrt(np.maximum(slope * x_fine**2 + intercept, 0.0))
        label  = f'σ₀={sigma0:.3g} μm, v={v_rms:.3g} μm/s'
        return (x_fine, y_fit, label, None,
                {'type': 'ballistic', 'slope': slope, 'intercept': intercept,
                 'v_rms': v_rms, 'sigma0': sigma0})

    raise ValueError(f'Unknown fit type {fit_type!r}. Choose from: {_FIT_TYPES}')


def plot_scan(df, result_keys, scan_keys=None, fits=None, title=None, show=True):
    """Plot result columns vs scanned globals from a load_scan DataFrame.

    Parameters
    ----------
    df : DataFrame
        As returned by load_scan.
    result_keys : list
        Column keys for the y-axis.
    scan_keys : list or None
        Column keys to use as the x-axis. None auto-detects varying globals.
    fits : str, list, or dict, optional
        Fit to overlay on each subplot. Choices per subplot: 'mean', 'linear',
        'gaussian', 'exponential'. Pass a single string to apply to all subplots,
        a list (one per subplot pair in order), or a dict keyed by (rkey, skey)
        tuple or by integer subplot index.
    title : str or None
        Figure suptitle. Defaults to the filename of the first shot.
    """
    if title is None:
        try:
            first_path = get_column(df, 'filepath').iloc[0]
            title = os.path.basename(first_path)
        except Exception:
            title = 'Scan results'

    scan_keys = scan_keys if scan_keys else find_scanned_globals(df)
    if not scan_keys:
        raise ValueError('No varying globals found. Pass scan_keys explicitly.')

    pairs = [(rkey, skey) for rkey in result_keys for skey in scan_keys]
    fit_types = _resolve_fits(fits, pairs)
    fit_results = {}
    n = int(np.ceil(np.sqrt(len(pairs))))

    fig, axes = plt.subplots(n, n, figsize=(5 * n, 4 * n), squeeze=False)
    flat_axes = axes.flat
    fig.suptitle(title, fontsize=13)

    for i, (rkey, skey) in enumerate(pairs):
        ax = flat_axes[i]
        try:
            y = get_column(df, rkey).astype(float)
        except (KeyError, TypeError) as e:
            print(f'Skipping result {rkey!r}: {e}')
            ax.set_visible(False)
            continue
        ylabel = col_label(rkey)

        u_key = (rkey[0], 'u_' + rkey[-1]) if isinstance(rkey, tuple) else 'u_' + rkey
        try:
            yerr = get_column(df, u_key).astype(float)
        except (KeyError, TypeError):
            yerr = None

        try:
            x = get_column(df, skey).astype(float)
        except (KeyError, TypeError) as e:
            print(f'Skipping scan key {skey!r}: {e}')
            ax.set_visible(False)
            continue
        xlabel = col_label(skey)

        valid = x.notna() & y.notna()
        xv, yv = x[valid].values, y[valid].values
        yev = yerr[valid].values if yerr is not None else None

        unique_x, inv = np.unique(xv, return_inverse=True)
        counts = np.bincount(inv)
        yv_mean = np.array([yv[inv == i].mean() for i in range(len(unique_x))])

        if (counts > 1).any():
            yv_err = np.array([
                yv[inv == i].std(ddof=1) / np.sqrt(counts[i]) if counts[i] > 1 else np.nan
                for i in range(len(unique_x))
            ])
        elif yev is not None:
            yv_err = np.array([yev[inv == i].mean() for i in range(len(unique_x))])
        else:
            yv_err = None

        i_max = int(np.argmax(yv_mean))
        x_max, y_max = float(unique_x[i_max]), float(yv_mean[i_max])
        data_max = {'x': x_max, 'y': y_max}

        ax.errorbar(unique_x, yv_mean, yerr=yv_err,
                    fmt='o', capsize=4, linewidth=1.5, label='data')
        ax.plot(x_max, y_max, '*', color='gold', markersize=12, zorder=6,
                markeredgecolor='k', markeredgewidth=0.5, label=f'max: ({x_max:.4g}, {y_max:.4g})')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        fit_type = fit_types[i]
        result_key = (col_label(rkey), col_label(skey))
        if fit_type is not None and len(unique_x) >= 2:
            try:
                xf, yf, flabel, marker, coeffs = _do_fit(fit_type, unique_x, yv_mean, yv_err)
                ax.plot(xf, yf, 'r-', linewidth=1.5, label=flabel)
                if marker is not None and unique_x.min() <= marker[0] <= unique_x.max():
                    ax.axvline(marker[0], color='r', linestyle='--', linewidth=0.8, alpha=0.5)
                    ax.plot(marker[0], marker[1], 'rv', markersize=9, zorder=5)
                coeffs['data_max'] = data_max
                fit_results[result_key] = coeffs
            except Exception as e:
                ax.text(0.05, 0.95, f'fit failed: {e}', transform=ax.transAxes,
                        fontsize=7, va='top', color='red')
                fit_results[result_key] = {'data_max': data_max}
        else:
            fit_results[result_key] = {'data_max': data_max}
        ax.legend(fontsize=8)

    for ax in list(flat_axes)[len(pairs):]:
        ax.set_visible(False)

    plt.tight_layout()
    if show:
        plt.show()
    return fig, fit_results


def live_plot_scan(year, month, day, sequence, number, result_keys,
                   n_shots=None, scan_keys=None, fits=None, poll_interval=2.0):
    """Poll a sequence folder and replot as shots arrive, until n_shots are done.

    n_shots is read automatically from the n_runs attribute of the first h5 file
    if not provided. Retries silently when result columns are missing (lyse not
    yet finished). Interrupt with Ctrl-C to stop early.
    """
    folder = _sequence_folder(year, month, day, sequence, number)
    print(f'Watching {folder}')

    tick = 0
    while True:
        tick += 1
        h5_files = sorted(glob.glob(os.path.join(folder, '*.h5')))
        n_found = len(h5_files)

        if not h5_files:
            clear_output(wait=True)
            print(f'[{tick}] Waiting for first shot in {folder}')
            time.sleep(poll_interval)
            continue

        try:
            df = get_dataframe_from_shots(h5_files)

            if n_shots is None:
                try:
                    n_shots = int(get_column(df, 'n_runs').dropna().iloc[0])
                except (KeyError, IndexError):
                    clear_output(wait=True)
                    print(f'[{tick}] {n_found} file(s) — waiting for n_runs attribute')
                    time.sleep(poll_interval)
                    continue

            # Count rows where every result key is non-NaN
            complete = np.ones(len(df), dtype=bool)
            for rkey in result_keys:
                try:
                    complete &= get_column(df, rkey).notna().values
                except KeyError:
                    complete[:] = False
            n_complete = int(complete.sum())

            if n_complete == 0:
                clear_output(wait=True)
                print(f'[{tick}] {n_found} file(s) — waiting for lyse results '
                      f'(0/{n_shots} complete)')
                time.sleep(poll_interval)
                continue

            plt.close('all')
            fig, fit_results = plot_scan(df[complete], result_keys, scan_keys=scan_keys, fits=fits, show=False)
            fig.canvas.draw()
            pct = n_complete / n_shots * 100
            bar = (f'<div style="margin:4px 0 8px">'
                   f'<div style="background:#ddd;border-radius:4px;height:22px">'
                   f'<div style="background:#4caf50;width:{pct:.0f}%;height:22px;'
                   f'border-radius:4px;line-height:22px;color:#fff;text-align:center;'
                   f'font-size:13px">{n_complete}/{n_shots}</div></div></div>')
            clear_output(wait=True)
            display(HTML(bar))
            display(fig)
            plt.close(fig)
            print(f'[{tick}] {n_complete}/{n_shots} complete  ({n_found} files found)')

            if n_complete >= n_shots:
                print(f'Done — all {n_shots} shots processed.')
                return fit_results

        except Exception as e:
            clear_output(wait=True)
            print(f'[{tick}] {n_found} file(s) — {type(e).__name__}: {e}')

        time.sleep(poll_interval)


_M_CS = 132.905 * 1.66054e-27   # kg
_K_B  = 1.38065e-23              # J/K


def tof_temperature(fit_results, sigma_key, tof_key='TOF_Time'):
    """Compute temperature from a TOF sigma fit.

    Supports two fit types:
      'linear'   : T = m/k_B * slope²  (assumes point source; underestimates T
                   when initial cloud size is significant)
      'ballistic': T = m/k_B * v_rms²  where σ²(t) = σ₀² + v_rms²·t²
                   (physically correct; accounts for finite initial size)

    Parameters
    ----------
    fit_results : dict
        As returned by plot_scan (second element of the tuple).
    sigma_key : str
        Short result name used as the fit_results key, e.g. 'sigma_x (um)'.
    tof_key : str
        Short scan key name, default 'TOF_Time'.

    Returns
    -------
    T : float
        Temperature in Kelvin.
    """
    coeffs = fit_results[(sigma_key, tof_key)]
    if coeffs['type'] == 'linear':
        v_rms_m = coeffs['slope'] * 1e-6           # slope in um/s → m/s
    elif coeffs['type'] == 'ballistic':
        v_rms_m = coeffs['v_rms'] * 1e-6           # v_rms in um/s → m/s
    else:
        raise ValueError(
            f'Expected linear or ballistic fit for {sigma_key!r}, got {coeffs["type"]!r}')
    return _M_CS / _K_B * v_rms_m**2


def tof_gravity(fit_results, pos_key, tof_key='TOF_Time'):
    """Compute gravitational acceleration from a quadratic TOF position fit.

    y(t) = a·t² + b·t + c  →  g = −2a  (converted from um/s² to m/s²)

    Parameters
    ----------
    fit_results : dict
        As returned by plot_scan (second element of the tuple).
    pos_key : str
        Short result name used as the fit_results key, e.g. 'x0_y (um)'.
    tof_key : str
        Short scan key name, default 'TOF_Time'.

    Returns
    -------
    g : float
        Gravitational acceleration in m/s².  Positive value = downward fall.
    """
    coeffs = fit_results[(pos_key, tof_key)]
    if coeffs['type'] != 'quadratic':
        raise ValueError(f'Expected a quadratic fit for {pos_key!r}, got {coeffs["type"]!r}')
    a_um_per_s2 = coeffs['a']          # um/s²
    return -2 * a_um_per_s2 * 1e-6    # m/s²


_G_TRUE = 9.8027  # m/s², local gravitational acceleration in Chicago


def calibrate_from_gravity(fit_results, pos_key, magnification, pixel_size=6.5,
                            g_true=_G_TRUE, tof_key='TOF_Time'):
    """Calibrate imaging magnification using the known value of g.

    A wrong magnification scales all measured lengths by a constant factor k,
    so measured g = true g * k.  Inverting this gives the true magnification
    and a correction factor for all length and temperature measurements.

    Parameters
    ----------
    fit_results : dict
        As returned by plot_scan / live_plot_scan.
    pos_key : str
        Fit key for the falling-atom position (must be a quadratic fit),
        e.g. 'x0_y (um)'.
    magnification : float
        Nominal magnification used in absorption_image_analysis.py.
    pixel_size : float
        Camera pixel size in μm (default 6.5 for PCO Panda).
    g_true : float
        True gravitational acceleration in m/s² (default: standard gravity).
    tof_key : str
        Scan key name for TOF time (default 'TOF_Time').

    Returns
    -------
    dict with keys:
        'magnification'  : calibrated magnification
        'conv'           : calibrated μm/pixel conversion factor
        'g_measured'     : raw measured g before calibration (m/s²)
        'length_scale'   : multiply any measured length by this to get true length
        'temp_scale'     : multiply any measured temperature by this to get true T
    """
    g_meas = abs(tof_gravity(fit_results, pos_key, tof_key))
    # measured length = true length * (M_true / M_nom)
    # g_meas = g_true * (M_true / M_nom)  →  M_true = M_nom * g_meas / g_true
    mag_calibrated = magnification * g_meas / g_true
    conv_calibrated = pixel_size / mag_calibrated       # μm/pixel
    length_scale = g_true / g_meas                     # true = measured * length_scale
    return {
        'magnification': mag_calibrated,
        'conv': conv_calibrated,
        'g_measured': g_meas,
        'length_scale': length_scale,
        'temp_scale': length_scale**2,
    }


def _sequence_folder(year, month, day, sequence, number):
    """Return the path to a sequence folder using experiment_shot_storage from labconfig."""
    labconfig = LabConfig()
    storage = labconfig.get('DEFAULT', 'experiment_shot_storage')
    return os.path.join(storage, sequence, f'{year:04d}', f'{month:02d}', f'{day:02d}', f'{number:04d}')


def _find_h5_files(folder):
    h5_files = sorted(glob.glob(os.path.join(folder, '*.h5')))
    if not h5_files:
        raise FileNotFoundError(f'No h5 files found in {folder}')
    return h5_files


def load_shot(year, month, day, sequence, number):
    """Load the first shot from the specified sequence folder.

    Returns a pandas Series containing globals and any saved results.
    """
    folder = _sequence_folder(year, month, day, sequence, number)
    h5_files = _find_h5_files(folder)
    return get_series_from_shot(h5_files[0])


def load_scan(year, month, day, sequence, number):
    """Load all shots from the specified sequence folder as a DataFrame.

    Autodetects all h5 files in the folder, sorted by filename.
    """
    folder = _sequence_folder(year, month, day, sequence, number)
    h5_files = _find_h5_files(folder)
    return get_dataframe_from_shots(h5_files)


# testing:
if __name__ == '__main__':
    shot = load_shot(2026, 8, 10, 'cs_mot_healthcheck', 39)
    print('load_shot keys:', shot.index.tolist())

    scan = load_scan(2026, 8, 10, 'cs_mot_healthcheck', 40)
    print('load_scan shape:', scan.shape)
    print('load_scan columns:', scan.columns.tolist())
