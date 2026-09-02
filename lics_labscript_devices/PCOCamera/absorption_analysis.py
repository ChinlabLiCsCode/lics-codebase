"""Shared absorption-imaging physics for the pco_panda camera.

This is the single source of truth for the calibration constants and the
OD / density / cloud-size calculation used by both:

    - analysislib/absorption_image_analysis.py  (post-shot lyse analysis,
      full plots + fit)
    - lics_labscript_devices/PCOCamera/blacs_workers.py  (live BLACS-tab
      display in 'absorption' display_mode, + 'live_image_analysis' logging)

Changing a calibration constant, a fit option, or the calculation itself here
changes both consumers together. Only plotting (matplotlib) is lyse-specific
and stays in analysislib.
"""

import numpy as np
from scipy.optimize import curve_fit

# Device name under which images are saved in the shot HDF5 file
# (images/<DEVICE_NAME>/<exposure name>/<frametype>), i.e. the labscript
# device name of the PCOCamera in apparatus/connection_table.py.
DEVICE_NAME = 'pco_panda'

# --- calibration constants ---
PIXEL_SIZE_UM = 6.5  # microns, physical pixel pitch of the PCO Panda 4.2
MAGNIFICATION = 1.2823  # calibrated 2026-08-11 from TOF gravity measurement (g=9.8027 m/s^2 in Chicago)
CONV_UM_PER_PIX = PIXEL_SIZE_UM / MAGNIFICATION  # pixel-to-image-size conversion (um/pix)

# Resonant D2 transition wavelengths, meters. Species affects only the resonant cross
# section (and therefore density/atom-number results) -- the OD image itself doesn't
# depend on species.
LAMBDA_852_M = 852.34727582e-9   # Cs-133 D2
LAMBDA_671_M = 670.977338e-9     # Li-7 D2
SPECIES_WAVELENGTH_M = {
    'Cs': LAMBDA_852_M,
    'Li': LAMBDA_671_M,
}
DEFAULT_SPECIES = 'Cs'


def resonant_cross_section_um2(species=DEFAULT_SPECIES):
    """Resonant scattering cross section sigma0 = 3*lambda^2/(2*pi), in um^2."""
    if species not in SPECIES_WAVELENGTH_M:
        raise ValueError(f"species must be one of {list(SPECIES_WAVELENGTH_M)}, not {species!r}")
    wavelength_um = SPECIES_WAVELENGTH_M[species] * 1e6
    return 3 * wavelength_um ** 2 / (2 * np.pi)


SENSOR_PIXELS = 2048
SPAN_UM = np.linspace(0, SENSOR_PIXELS * CONV_UM_PER_PIX, SENSOR_PIXELS)  # array of pixel positions, in microns

# --- fit options ---
FIT_OFFSET = True           # fit a constant background term B in the Gaussian
INCLUDE_OFFSET_IN_N = False  # include the B*span contribution in N_x and N_y


def abs_calc(dark_image, light_image, atoms_image, species=DEFAULT_SPECIES):
    """Compute the OD (log) image, 2D atomic density rho (atoms/pixel^2), and
    total atom number N_int (from first principles / summed OD) from
    dark/light/atoms frames. `species` ('Cs' or 'Li') selects the resonant cross
    section used to convert OD to density -- it does not affect log_image."""
    dark_image = np.asarray(dark_image, dtype=float)
    light_image = np.asarray(light_image, dtype=float)
    atoms_image = np.asarray(atoms_image, dtype=float)

    atoms_minus_dark = atoms_image - dark_image
    light_minus_dark = light_image - dark_image
    ratio = np.divide(
        atoms_minus_dark,
        light_minus_dark,
        out=np.full(atoms_image.shape, 1.0, dtype=float),
        where=light_minus_dark != 0,
    )

    ratio[ratio <= 0] = 1
    log_image = -np.log(ratio)

    # 2D density and atom number from first principles
    sigma0 = resonant_cross_section_um2(species)
    rho = log_image * (CONV_UM_PER_PIX) ** 2 / sigma0  # atoms/pixel^2
    N_int = rho.sum()  # total atom number, summed OD

    return log_image, rho, N_int


# --- cloud size fitting ---

def gaussian_dist(x, A, x0: float, sigma: float, B: float = 0.0):
    return A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2)) + B


def gaussian_dist_nooffset(x, A, x0: float, sigma: float):
    return gaussian_dist(x, A, x0, sigma, 0.0)


def fit_fun(x, line_density, fit_offset=FIT_OFFSET):
    """Fit a 1D Gaussian to line_density.

    Always returns popt/perr of length 4, ordered (A, x0, sigma, B). When
    fit_offset is False the constant term is not a free parameter and is
    reported as B = 0 with zero uncertainty.
    """
    A_guess = line_density.max()
    B_guess = np.median(line_density)

    x0_guess = x[np.argmax(line_density)]

    if fit_offset:
        model = gaussian_dist
        p0 = np.array([A_guess - B_guess, x0_guess, 2000, B_guess])
        bounds = ([0, x.min(), 1, -np.inf],
                  [np.inf, x.max(), np.ptp(x), np.inf])
    else:
        model = gaussian_dist_nooffset
        p0 = np.array([A_guess, x0_guess, 2000])
        bounds = ([0, x.min(), 1],
                  [np.inf, x.max(), np.ptp(x)])

    try:
        popt, pcov = curve_fit(
            model,
            x,
            line_density,
            p0=p0,
            bounds=bounds
        )

        perr = np.sqrt(np.diag(pcov))
        popt[2] = abs(popt[2])
    except Exception as e:
        print("Failed to fit")
        print(e)

        perr = np.full(p0.shape, 0.1)
        popt = np.full(p0.shape, 0.1)

    if not fit_offset:
        # pad with B = 0 so callers always see the same parameter ordering
        popt = np.append(popt, 0.0)
        perr = np.append(perr, 0.0)

    return popt, perr


def fit_extract(x_int, y_int, span=SPAN_UM, conv=CONV_UM_PER_PIX,
                 fit_offset=FIT_OFFSET, include_offset_in_N=INCLUDE_OFFSET_IN_N):
    """Fit Gaussians to the x/y integrated density profiles and return the
    fitted distributions, atom numbers, centres, widths and offsets."""
    popt_x, perr_x = fit_fun(span, x_int / conv, fit_offset=fit_offset)
    popt_y, perr_y = fit_fun(span, y_int / conv, fit_offset=fit_offset)

    A_x, x0_x, sigma_x, B_x = popt_x
    A_y, x0_y, sigma_y, B_y = popt_y

    # the curves to plot: the full fit, offset included if it was fitted
    x_dist = gaussian_dist(span, A_x, x0_x, sigma_x, B_x)
    y_dist = gaussian_dist(span, A_y, x0_y, sigma_y, B_y)

    # get the atom number along x and y, with or without the constant term
    B_x_N = B_x if include_offset_in_N else 0.0
    B_y_N = B_y if include_offset_in_N else 0.0

    N_x = gaussian_dist(span, A_x, x0_x, sigma_x, B_x_N).sum() * conv
    N_y = gaussian_dist(span, A_y, x0_y, sigma_y, B_y_N).sum() * conv

    return x_dist, N_x, x0_x, sigma_x, B_x, y_dist, N_y, x0_y, sigma_y, B_y


def full_analysis(dark_image, light_image, atoms_image, species=DEFAULT_SPECIES,
                   fit_offset=FIT_OFFSET, include_offset_in_N=INCLUDE_OFFSET_IN_N):
    """Run the full OD/density/fit pipeline and return everything a consumer
    might want. `results` holds exactly the set of named results that
    absorption_image_analysis.py saves via run.save_result()/save_results(),
    also used verbatim for BLACS's 'live_image_analysis' logging."""
    log_image, rho, N_int = abs_calc(dark_image, light_image, atoms_image, species=species)
    density = rho / CONV_UM_PER_PIX ** 2  # atoms/um^2

    x_int = rho.sum(axis=0)
    y_int = rho.sum(axis=1)

    x_dist, N_x, x0_x, sigma_x, B_x, y_dist, N_y, x0_y, sigma_y, B_y = fit_extract(
        x_int, y_int, fit_offset=fit_offset, include_offset_in_N=include_offset_in_N
    )

    # "True" atom number: geometric mean of the two independent 1D-fit atom numbers.
    N = np.sqrt(N_x * N_y)
    area = np.pi * sigma_x * sigma_y
    rho_2d = N / area

    results = {
        "N_int": N_int,
        "sigma_x (um)": sigma_x,
        "sigma_y (um)": sigma_y,
        "x0_x (um)": x0_x,
        "x0_y (um)": x0_y,
        "B_x": B_x,
        "B_y": B_y,
        "N_x": N_x,
        "N_y": N_y,
        "N": N,
        "rho_2d (atoms/um^2)": rho_2d,
    }

    return {
        'log_image': log_image,
        'rho': rho,
        'density': density,
        'x_int': x_int,
        'y_int': y_int,
        'x_dist': x_dist,
        'y_dist': y_dist,
        'N': N,
        'results': results,
    }
