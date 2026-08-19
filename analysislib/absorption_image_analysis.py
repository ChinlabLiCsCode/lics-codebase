import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

#constants
pixel_size = 6.5 #microns
magnification = 1.2823  # calibrated 2026-08-11 from TOF gravity measurement (g=9.8027 m/s² in Chicago)
conv = pixel_size/magnification # pixel to image size conversion (um/pix)
lambda_852 = 852.34727582e-9 # cs d2 transition wavelength in nm
span = np.linspace(0, 2048*conv, 2048) #array of pixels

#get run data
run = lyse.Run(lyse.path)
shot_path = lyse.path

run_name = os.path.basename(shot_path)

with h5py.File(shot_path, 'r') as f:
    acq = 'absorption1' if 'images/pco_panda/absorption1' in f else 'absorption'
    dark_image  = f[f'images/pco_panda/{acq}/dark'][:].astype(float)
    light_image = f[f'images/pco_panda/{acq}/light'][:].astype(float)
    atoms_image = f[f'images/pco_panda/{acq}/atoms'][:].astype(float)

##############################################################absorption image analysis#################################################
#calculate log image

def abs_calc(dark_image, light_image, atoms_image):
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
    sigma0 = 3 * (lambda_852*1e6)**2 / (2 * np.pi)

    #calculate the 2D density and atom number
    rho = log_image * (conv)**2 / sigma0 # rho has units of atoms/pixel^2
    N = rho.sum() # N is the total atom number from first principles

    return log_image, rho, N



###########################################################cloud size calculation################################################

# fitting functions
def gaussian_dist(x, A, x0:float, sigma:float, B:float):
    return A * np.exp(-(x - x0)**2/ (2 * sigma**2)) + B

def fit_fun(x, line_density):
    A_guess = line_density.max()
    B_guess = np.median(line_density)

    x0_guess = x[np.argmax(line_density)]

    p0 = np.array([A_guess - B_guess, x0_guess, 2000, B_guess])

    try:
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
    except Exception as e:
        print("Failed to fit")
        print(e)

        perr = np.full(p0.shape, 0.1)
        popt = np.full(p0.shape, 0.1)

    return popt, perr

#extract fit
def fit_extract(x_int, y_int):

    popt_x, perr_x = fit_fun(span, x_int/conv)
    popt_y, perr_y = fit_fun(span, y_int/conv)

    A_x, x0_x, sigma_x, B_x = popt_x
    Ax_err, x0x_err, sigmax_err, Bx_err = perr_x

    A_y, x0_y, sigma_y, B_y = popt_y
    Ay_err, x0y_err, sigmay_err, By_err = perr_y

    #get the atom number along x and y
    x_dist = gaussian_dist(span, A_x, x0_x, sigma_x, B_x)
    y_dist = gaussian_dist(span, A_y, x0_y, sigma_y, B_y)

    N_x = x_dist.sum()*conv
    N_y = y_dist.sum()*conv

    return x_dist, N_x, x0_x, sigma_x, y_dist, N_y, x0_y, sigma_y


####################################################################plotting code#############################
def plot_results(title):
    extent = [0, 2048*conv, 0, 2048*conv]  # rescale extent into microns

    # size = (6, 12)
    fig = plt.figure(constrained_layout=True) #, figsize=size)
    # fig.set_size_inches(size[0], size[1], forward=True)
    gs_outer = fig.add_gridspec(1, 2, wspace=0.3, width_ratios=[1, 2])

    # top row: raw images
    gs_top = gs_outer[0].subgridspec(2, 2)
    ax_dark  = fig.add_subplot(gs_top[0, 0])
    ax_light = fig.add_subplot(gs_top[1, 0])
    ax_atoms = fig.add_subplot(gs_top[0, 1])
    ax_od    = fig.add_subplot(gs_top[1, 1])

    im1 = ax_dark.imshow(dark_image, extent=extent, origin='lower')
    ax_dark.set_title("Dark")
    fig.colorbar(im1, ax=ax_dark, location='bottom')
    plt.setp(ax_dark.get_xticklabels(), visible=False)
    plt.setp(ax_dark.get_yticklabels(), visible=False)

    im2 = ax_light.imshow(light_image, extent=extent, origin='lower')
    ax_light.set_title("Light")
    fig.colorbar(im2, ax=ax_light, location='bottom')
    plt.setp(ax_light.get_yticklabels(), visible=False)
    plt.setp(ax_light.get_xticklabels(), visible=False)

    im3 = ax_atoms.imshow(atoms_image, extent=extent, origin='lower')
    ax_atoms.set_title("Atoms")
    fig.colorbar(im3, ax=ax_atoms, location='bottom')
    plt.setp(ax_atoms.get_xticklabels(), visible=False)
    plt.setp(ax_atoms.get_yticklabels(), visible=False)

    im_od = ax_od.imshow(log_image, extent=extent, origin='lower', vmin=0)
    ax_od.set_title("OD")
    fig.colorbar(im_od, ax=ax_od, location='bottom')
    plt.setp(ax_od.get_xticklabels(), visible=False)
    plt.setp(ax_od.get_yticklabels(), visible=False)

    # bottom: 2D density (main), x-profile below it, y-profile to the right
    # width_ratios: [main image, y-profile, colorbar]
    # height_ratios: [main image, x-profile]
    gs_bot = gs_outer[1].subgridspec(2, 3,
                                    height_ratios=[5, 1],
                                    width_ratios=[1, 8, 0.2],
                                    hspace=0.04, wspace=0.04)
    ax_density = fig.add_subplot(gs_bot[0, 1])
    ax_y_prof  = fig.add_subplot(gs_bot[0, 0], sharey=ax_density)
    ax_cb      = fig.add_subplot(gs_bot[0, 2])
    ax_x_prof  = fig.add_subplot(gs_bot[1, 1], sharex=ax_density)

    im4 = ax_density.imshow(rho/conv**2, vmin=0, vmax=rho.max()/conv**2, extent=extent, origin='lower')
    ax_density.set_title(rf"2D Density (atoms/$\mu m^2$), N={N:.1e}")
    fig.colorbar(im4, cax=ax_cb)
    ax_cb.set_ylabel(r'Density (atoms/$\mu m^2$)')
    plt.setp(ax_density.get_xticklabels(), visible=False)
    plt.setp(ax_density.get_yticklabels(), visible=False)

    # x-profile: below the image, x-axis shared with density plot
    ax_x_prof.scatter(span[::1], x_int[::1]/conv, s=4, alpha=0.5, label='data')
    ax_x_prof.plot(span, x_dist, color='red', label=rf'fit $\sigma$={sigma_x:.0f} μm')
    ax_x_prof.set_xlabel(r'x ($\mu$m)')
    # ax_x_prof.set_ylabel(r'Density (atoms/$\mu$m)')
    # ax_x_prof.legend(fontsize=8)

    # y-profile: right of the image, y-axis shared with density plot; axes transposed
    ax_y_prof.scatter(y_int[::1]/conv, span[::1], s=4, alpha=0.5, label='data')
    ax_y_prof.plot(y_dist, span, color='red', label=rf'fit $\sigma$={sigma_y:.0f} μm')
    ax_y_prof.set_ylabel(r'y ($\mu$m)')
    ax_y_prof.xaxis.set_label_position('top')
    ax_y_prof.xaxis.tick_top()
    # ax_y_prof.invert_yaxis()
    # ax_y_prof.set_xlabel(r'Density (atoms/$\mu$m)')
    # ax_y_prof.legend(fontsize=8)

    fig.suptitle(run_name+title)
    plt.show()

###############################################get all parameters and plot results############################
#log_image, 2d density and atom number
log_image, rho, N = abs_calc(dark_image, light_image, atoms_image)

#integrated density along x and y
x_int = rho.sum(axis=0)
y_int = rho.sum(axis=1)

#fit results
x_dist, N_x, x0_x, sigma_x, y_dist, N_y, x0_y, sigma_y = fit_extract(x_int, y_int)

plot_results("")


########################################################save results#########################################
run.save_result("N_int", N)
run.save_result("sigma_x (um)", sigma_x)
run.save_result("sigma_y (um)", sigma_y)
run.save_result("x0_x (um)", x0_x)
run.save_result("x0_y (um)", x0_y)
run.save_result("N_x", N_x)
run.save_result("N_y", N_y)