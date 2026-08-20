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

#fit options
FIT_OFFSET = True           # fit a constant background term B in the Gaussian
INCLUDE_OFFSET_IN_N = False # include the B*span contribution in N_x and N_y

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
def gaussian_dist(x, A, x0:float, sigma:float, B:float=0.0):
    return A * np.exp(-(x - x0)**2/ (2 * sigma**2)) + B

def gaussian_dist_nooffset(x, A, x0:float, sigma:float):
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

#extract fit
def fit_extract(x_int, y_int, fit_offset=FIT_OFFSET,
                include_offset_in_N=INCLUDE_OFFSET_IN_N):

    popt_x, perr_x = fit_fun(span, x_int/conv, fit_offset=fit_offset)
    popt_y, perr_y = fit_fun(span, y_int/conv, fit_offset=fit_offset)

    A_x, x0_x, sigma_x, B_x = popt_x
    Ax_err, x0x_err, sigmax_err, Bx_err = perr_x

    A_y, x0_y, sigma_y, B_y = popt_y
    Ay_err, x0y_err, sigmay_err, By_err = perr_y

    #the curves to plot: the full fit, offset included if it was fitted
    x_dist = gaussian_dist(span, A_x, x0_x, sigma_x, B_x)
    y_dist = gaussian_dist(span, A_y, x0_y, sigma_y, B_y)

    #get the atom number along x and y, with or without the constant term
    B_x_N = B_x if include_offset_in_N else 0.0
    B_y_N = B_y if include_offset_in_N else 0.0

    N_x = gaussian_dist(span, A_x, x0_x, sigma_x, B_x_N).sum()*conv
    N_y = gaussian_dist(span, A_y, x0_y, sigma_y, B_y_N).sum()*conv

    return x_dist, N_x, x0_x, sigma_x, B_x, y_dist, N_y, x0_y, sigma_y, B_y


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

    vmax_density = float(np.percentile(rho[rho > 0], 99.5)) / conv**2
    im4 = ax_density.imshow(rho/conv**2, vmin=0, vmax=vmax_density, extent=extent, origin='lower')
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
x_dist, N_x, x0_x, sigma_x, B_x, y_dist, N_y, x0_y, sigma_y, B_y = fit_extract(x_int, y_int)

plot_results("")


########################################################save results#########################################
run.save_result("N_int", N)
run.save_result("sigma_x (um)", sigma_x)
run.save_result("sigma_y (um)", sigma_y)
run.save_result("x0_x (um)", x0_x)
run.save_result("x0_y (um)", x0_y)
run.save_result("B_x", B_x)
run.save_result("B_y", B_y)
run.save_result("N_x", N_x)
run.save_result("N_y", N_y)