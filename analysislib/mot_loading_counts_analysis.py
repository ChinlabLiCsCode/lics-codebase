import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

try:
    from analysislib import helperfuncs
except ImportError:      # lyse runs routines with their own folder as sys.path[0]
    import helperfuncs

#analysis code for fitting MOT loading data

def exponential_model(t, a, b, c):
    return a * (1 - np.exp(-t / b)) + c

def loading_window(shot_path, start='Cs_MOT_Loading', stop='Cs_CMOT'):
    """Return (t0, tf) of the MOT loading stage on the camera's time base.

    The markers are in labscript time while the camera measures real elapsed
    seconds, so a wait — the line_trigger, which stops the clock for up to
    0.1 s — shifts everything after it. Shot.real_time does that bookkeeping.

    Returns None for shots whose timestamps predate the sequence time base
    (no 'time_base' attribute), since a marker time means nothing against a
    recording that starts at BLACS programming time.
    """
    shot = helperfuncs.Shot(shot_path)
    with h5py.File(shot_path, 'r') as f:
        grp = f['images/ids_fluoro/fluorescence']
        if grp.attrs.get('time_base') != 'sequence':
            return None

    markers = dict(shot.marker_times())
    if start not in markers or stop not in markers:
        return None
    return markers[start], markers[stop]


def collect_data(shot_path, t0_mot, tf_mot):
    """Function to extract time, raw counts, and background-subtracted images from the h5 file for a given shot."""
    with h5py.File(shot_path, 'r') as f:
        counts = f['images/ids_fluoro/fluorescence/counts'][:]
        time = f['images/ids_fluoro/fluorescence/timestamps'][:]


    mask = (time >= t0_mot) & (time <= tf_mot)

    mot_loading_time = time[mask] - time[mask][0]  # Normalize time to start from zero for the MOT loading region
    mot_counts = counts[mask] - counts[mask].min()  # Subtract the minimum count to set the baseline to zero
    return mot_loading_time, mot_counts 


def fit_to_exp(time, counts):

    popt, pcov = curve_fit(exponential_model, time, counts)

    # 4. Extract parameters
    a_opt, b_opt, c_opt = popt
    print(f"Fitted parameters: a={a_opt:.2f}, b={b_opt:.2f}, c={c_opt:.2f}")
    return a_opt, b_opt, c_opt

## load data
run = lyse.Run(lyse.path)
shot_path = lyse.path

# Prefer the sequence's own markers; fall back to the hand-tuned window for
# shots recorded before the camera timestamps were aligned to sequence time.
window = loading_window(shot_path)
if window is None:
    window = (0.5, 5.5)
    print(f'No sequence time base in this shot; using the fixed window {window}.')
else:
    print(f'MOT loading window from time markers: {window[0]:.3f} to {window[1]:.3f} s')
time, counts = collect_data(shot_path, t0_mot=window[0], tf_mot=window[1])
run_name = os.path.basename(shot_path).split('_')
run_name = run_name[0] + "_" + run_name[1] #get the name of the run from the shot file name

#fit and exctract parameters
a, b, c = fit_to_exp(time, counts)
t0 = -b * np.log(1 + c/a)
loss_rate = 1/b
loading_rate = loss_rate * (a - c)


# Plot the scatter data points and overlay the fitted curve
param_text = f"Exponential Fit: $a(1 - e^{{-t/b}})+c$\n$a$ = {a:.0f} counts\n$b$ = {b:.2f} s\n$c$ = {c:.0f} counts"

fig, axe = plt.subplots()

x_line = np.linspace(t0, time.max(), 200)
axe.scatter(time, counts, color='blue', alpha=0.6, label='ROI Counts Data')
axe.plot(x_line, exponential_model(x_line, a, b, c), color='red', linewidth=2.5, label=param_text)

axe.set_title('Cs MOT Loading Curve: ' + run_name)
axe.set_xlabel('Time (s)')
axe.set_ylabel('Pixel Counts')
axe.legend()

run.save_result('a (counts)', a)
run.save_result('b (s)', b)
run.save_result('c (counts)', c)

run.save_result('loss_rate (1/s)', loss_rate)
run.save_result('loading_rate (counts/s)', loading_rate)

plt.tight_layout()
plt.show()