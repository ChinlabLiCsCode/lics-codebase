import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#analysis code for fitting MOT loading data

def exponential_model(t, a, b, c):
    return a * (1 - np.exp(-t / b)) + c

def collect_data(shot_path, t0_mot, tf_mot, t0_bg, tf_bg):
    """Function to extract time, raw counts, and background-subtracted images from the h5 file for a given shot."""
    with h5py.File(shot_path, 'r') as f:
        images = f['images/ids_fluoro/fluorescence/images'][:]
        time = f['images/ids_fluoro/fluorescence/timestamps'][:]

    counts = images.sum(axis=(1, 2))

    mask = (time >= t0_mot) & (time <= tf_mot)
    mask_bg = (time >= t0_bg) & (time <= tf_bg)

    mot_loading_time = time[mask] - time[mask][0]  # Normalize time to start from zero for the MOT loading region
    mot_counts = counts[mask] - counts[mask].min()  # Subtract the minimum count to set the baseline to zero
    mot_image = images[mask][-1].astype(float) - images[mask_bg].mean(axis=0).astype(float)

    return mot_loading_time, mot_counts, mot_image 


def fit_to_exp(time, counts):

    popt, pcov = curve_fit(exponential_model, time, counts)

    # 4. Extract parameters
    a_opt, b_opt, c_opt = popt
    print(f"Fitted parameters: a={a_opt:.2f}, b={b_opt:.2f}, c={c_opt:.2f}")
    return a_opt, b_opt, c_opt

## load data
run = lyse.Run(lyse.path)
shot_path = lyse.path
time, counts, mot_image = collect_data(shot_path, t0_mot=4, tf_mot=12, t0_bg=13, tf_bg=14)  # Adjust t0 and tf based on your data


#fit and exctract parameters
a, b, c = fit_to_exp(time, counts)
t0 = -b * np.log(1 + c/a)
loss_rate = 1/b
loading_rate = loss_rate * (a - c)


# Plot the scatter data points and overlay the fitted curve
param_text = f"Exponential Fit: $a(1 - e^{{-t/b}})+c$\n$a$ = {a:.0f} counts\n$b$ = {b:.2f} s\n$c$ = {c:.0f} counts"

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

x_line = np.linspace(t0, time.max(), 200)
axes[0].scatter(time, counts, color='blue', alpha=0.6, label='ROI Counts Data')
axes[0].plot(x_line, exponential_model(x_line, a, b, c), color='red', linewidth=2.5, label=param_text)

axes[0].set_title('Cs MOT Loading Curve')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('Pixel Counts')
axes[0].legend()

im1 = axes[1].imshow(mot_image, cmap='gray')
axes[1].set_title('MOT Image (Raw - Background)')
plt.colorbar(im1, ax=axes[1], label='Counts')

run.save_result('a (counts)', a)
run.save_result('b (s)', b)
run.save_result('c (counts)', c)

run.save_result('loss_rate (1/s)', loss_rate)
run.save_result('loading_rate (counts/s)', loading_rate)

plt.tight_layout()
plt.show()