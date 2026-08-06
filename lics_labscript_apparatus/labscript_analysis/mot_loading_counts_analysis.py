import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#analysis code for fitting MOT loading data

def exponential_model(t, a, b, c):
    return a * (1 - np.exp(-t / b)) + c

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
time, counts = collect_data(shot_path, t0_mot=0.5, tf_mot=5.5)  # Adjust t0 and tf based on your data
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