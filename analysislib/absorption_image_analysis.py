import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#constants
pixel_size = 6.5 #microns
magnification = 1.2
conv = pixel_size/magnification # pixel to image size conversion
lambda_852 = 852.34727582e-9 #cs d2 transition wavelength in nm

#get run data
run = lyse.Run(lyse.path)
shot_path = lyse.path

run_name = os.path.basename(shot_path).split("_")
run_name = run_name[0] + "_" + run_name[1]

with h5py.File(shot_path, 'r') as f:
        dark_image = f['images/pco_panda/absorption/dark'][:].astype(float)
        light_image = f['images/pco_panda/absorption/light'][:].astype(float)
        atoms_image = f['images/pco_panda/absorption/atoms'][:].astype(float)

##############################################################absorption image analysis#################################################
#calculate log image
atoms_minus_dark = atoms_image - dark_image
light_minus_dark = light_image - dark_image
ratio = np.divide(
        atoms_minus_dark,
        light_minus_dark,
        out = np.full(atoms_image.shape, 1, dtype=float),
        where = light_minus_dark != 0)

ratio[ratio<=0]=1
log_image = - np.log(ratio)

#calculate the resonant cross section in microns
sigma0 = 3 * (lambda_852*1e6) **2 / (2 * np.pi)

#calculate the 2D density and atom number
rho = log_image / sigma0 * (conv)**2
N = rho.sum()

#plot data
fig = 
extent=[0, 2048*conv, 0, 2048*conv] # handles image magnification from lens

im1 = axes[0,0].imshow(dark_image, extent=extent)
axes[0,0].set_title("Dark Image (counts)")
plt.colorbar(im1, ax=axes[0,0])
axes[0,0].set_xlabel(r'x ($\mu$m)')
axes[0,0].set_ylabel(r'y ($\mu$m)')

im2 = axes[0,1].imshow(light_image, extent=extent)
axes[0,1].set_title("Light Image (counts)")
plt.colorbar(im2, ax=axes[0,1])
axes[0,1].set_xlabel(r'x ($\mu$m)')
axes[0,1].set_ylabel(r'y ($\mu$m)')

im3 = axes[1,0].imshow(atoms_image, extent=extent)
axes[1,0].set_title("Atoms Image (counts)")
plt.colorbar(im3, ax=axes[1,0])
axes[1,0].set_xlabel(r'x ($\mu$m)')
axes[1,0].set_ylabel(r'y ($\mu$m)')

im4 = axes[1,1].imshow(rho, vmin=0, vmax=rho.max(), extent=extent)
axes[1,1].set_title(rf"2D Density (atoms/$\mu m^2$), N={N:.3e}")
plt.colorbar(im4, ax=axes[1,1])
axes[1,1].set_xlabel(r'x ($\mu$m)')
axes[1,1].set_ylabel(r'y ($\mu$m)')

fig.suptitle("Cs MOT Healthcheck:" + run_name)

run.save_result("Atom Number", N)

plt.tight_layout()
plt.show()

###########################################################cloud size calculation################################################
#get integrated densities along x and y
x_int = rho.sum(axis=0)
y_int = rho.sum(axis=1)[::-1]

span = np.linspace(0, 2048*conv, 2048)

# fitting functions
def gaussian_dist(x, A, x0:float, sigma:float, B:float):
    return A * np.exp(-(x - x0)**2/ (2 * sigma**2)) + B

def fit_fun(x, line_density):
    A_guess = line_density.max()
    B_guess = np.median(line_density)

    x0_guess = x[np.argmax(line_density)]

    p0 = [A_guess - B_guess, x0_guess, 2000, B_guess]

    popt, pcov = curve_fit(
        gaussian_dist,
        x,
        line_density,
        p0=p0,
        bounds=([0, x.min(), 1, -np.inf],
                               [np.inf, x.max(), np.ptp(x), np.inf])
        )

    perr = np.sqrt(np.diag(pcov))
    popt[2] = abs(popt[2])

    return popt, perr

#extract fit
popt_x, perr_x = fit_fun(span, x_int)
popt_y, perr_y = fit_fun(span, y_int)

A_x, x0_x, sigma_x, B_x = popt_x
Ax_err, x0x_err, sigmax_err, Bx_err = perr_x

A_y, x0_y, sigma_y, B_y = popt_y
Ay_err, x0y_err, sigmay_err, By_err = perr_y

#get the atom number along x and y
x_dist = gaussian_dist(span, A_x, x0_x, sigma_x, B_x)
y_dist = gaussian_dist(span, A_y, x0_y, sigma_y, B_y)

N_x = x_dist.sum()
N_y = y_dist.sum()

#plot fit against data
fig, axe = plt.subplots()

axe.scatter(span[::4], x_int[::4], s=4, alpha=0.5, label='x')
axe.plot(span, x_dist)

axe.scatter(span[::4], y_int[::4], s=4, alpha=0.5, label='y')
axe.plot(span, y_dist)

axe.set_xlabel(r"Position $\mu$m")
axe.set_ylabel(r"Density (atoms/$\mu m$)")
axe.set_title("Integrated X and Y densities")

run.save_result("Sigma x (microns)", sigma_x)
run.save_result("Sigma y (microns)", sigma_y)
run.save_result("N_x", N_x)
run.save_result("N_y", N_y)

axe.legend()
plt.tight_layout()
plt.show()

print(f"sigma_x = {sigma_x:.2f} ± {sigmax_err:.2f} microns")
print(f"sigma_y = {sigma_y:.2f} ± {sigmay_err:.2f} microns")
