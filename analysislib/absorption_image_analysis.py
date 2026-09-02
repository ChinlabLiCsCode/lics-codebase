import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt

# Shared physics (calibration constants, fit options, OD/density/fit calculation) lives
# in the device package so that BLACS's live 'absorption' display_mode and
# 'live_image_analysis' logging always agree with this post-shot analysis. See
# lics_labscript_devices/PCOCamera/absorption_analysis.py.
from lics_labscript_devices.PCOCamera.absorption_analysis import (
    DEVICE_NAME,
    CONV_UM_PER_PIX as conv,
    SPAN_UM as span,
    full_analysis,
)

#get run data
run = lyse.Run(lyse.path)
shot_path = lyse.path

run_name = os.path.basename(shot_path)

with h5py.File(shot_path, 'r') as f:
    acq = 'absorption1' if f'images/{DEVICE_NAME}/absorption1' in f else 'absorption'
    dark_image  = f[f'images/{DEVICE_NAME}/{acq}/dark'][:].astype(float)
    light_image = f[f'images/{DEVICE_NAME}/{acq}/light'][:].astype(float)
    atoms_image = f[f'images/{DEVICE_NAME}/{acq}/atoms'][:].astype(float)

##############################################################absorption image analysis#################################################
# OD, density, cloud-size fit, and derived atom numbers all come from the shared
# abs_calc/fit_extract in lics_labscript_devices.PCOCamera.absorption_analysis.
analysis = full_analysis(dark_image, light_image, atoms_image)

log_image = analysis['log_image']
rho       = analysis['rho']
x_int     = analysis['x_int']
y_int     = analysis['y_int']
x_dist    = analysis['x_dist']
y_dist    = analysis['y_dist']
N         = analysis['N']  # "true" atom number: geometric mean of N_x, N_y

N_int   = analysis['results']['N_int']
sigma_x = analysis['results']['sigma_x (um)']
sigma_y = analysis['results']['sigma_y (um)']
x0_x    = analysis['results']['x0_x (um)']
x0_y    = analysis['results']['x0_y (um)']
B_x     = analysis['results']['B_x']
B_y     = analysis['results']['B_y']
N_x     = analysis['results']['N_x']
N_y     = analysis['results']['N_y']
rho_2d  = analysis['results']['rho_2d (atoms/um^2)']


####################################################################plotting code#############################
def big_number(value):
    """Format an atom number as mantissa x 10^exponent, for the large readout."""
    if not np.isfinite(value) or value <= 0:
        return '--'
    exponent = int(np.floor(np.log10(value)))
    mantissa = value / 10**exponent
    return rf'${mantissa:.2f}\times10^{{{exponent}}}$'


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

    # # Displaying the N_y value larger
    # fig_2 = plt.figure(constrained_layout=True, figsize=(6, 2.5))
    # ax_big = fig_2.add_subplot(111)
    # ax_big.axis('off')
    # ax_big.text(0.5, 0.6, big_number(N_y), ha='center', va='center',
    #             fontsize=128, fontweight='bold', transform=ax_big.transAxes)
    # ax_big.text(0.5, 0.1, 'atoms ($N_y$)', ha='center', va='center',
    #             fontsize=26, color='gray', transform=ax_big.transAxes)

    plt.show()

###############################################plot results############################
plot_results("")


########################################################save results#########################################
run.save_result("N", N)
run.save_result("N_int", N_int)
run.save_result("sigma_x (um)", sigma_x)
run.save_result("sigma_y (um)", sigma_y)
run.save_result("x0_x (um)", x0_x)
run.save_result("x0_y (um)", x0_y)
run.save_result("B_x", B_x)
run.save_result("B_y", B_y)
run.save_result("N_x", N_x)
run.save_result("N_y", N_y)
run.save_results("rho_2d (atoms/um^2)", rho_2d)
