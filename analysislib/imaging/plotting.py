"""The df_view_image figure.

One shot, shown the way ``df_view_image`` showed it: the raw frames on the
left, the density image with its integrated profiles and fits on the right, and
the atom box drawn on top so it is obvious what the fit integrated over.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def _hide_ticks(ax):
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)


def _draw_mask(ax, mask, params):
    """Outline the atom box, in the micron coordinates of the image axes."""
    if mask is None:
        return
    r0, r1, c0, c1 = mask
    scale = params.pixel_um
    row_origin, col_origin = params.view_origin
    ax.add_patch(Rectangle(((c0 + col_origin) * scale, (r0 + row_origin) * scale),
                           (c1 - c0) * scale, (r1 - r0) * scale,
                           fill=False, edgecolor='white', linewidth=0.8,
                           linestyle='--', alpha=0.7))


def _label(fit):
    """Short description of a trace fit for the profile legend."""
    if not fit.success:
        return 'fit failed'
    if fit.fit_type == 'tf':
        return rf'$R_{{TF}}$={fit.width:.0f} $\mu$m'
    label = rf'$\sigma$={fit.width:.0f} $\mu$m'
    if fit.separation is not None:
        label += rf', sep={fit.separation:.0f} $\mu$m'
    return label


def plot_shot(result, fit, params, title='', show=True, figsize=(14, 6)):
    """Draw the full single-shot view.

    Parameters
    ----------
    result : :class:`~.process.ShotResult`
    fit : :class:`~.fitting.ImageFit`
    params : :class:`~.params.ImagingParams`
    """
    ny, nx = result.nd.shape
    scale = params.pixel_um
    # Axes are full-frame position in microns, matching the fitted centres.
    row_origin, col_origin = params.view_origin
    extent = [col_origin * scale, (col_origin + nx) * scale,
              row_origin * scale, (row_origin + ny) * scale]
    density = result.nd / scale**2          # atoms per micron^2

    fig = plt.figure(constrained_layout=True, figsize=figsize)
    gs_outer = fig.add_gridspec(1, 2, wspace=0.3, width_ratios=[1, 2])

    # left: the raw frames plus the synthetic light frame the defringing built
    gs_left = gs_outer[0].subgridspec(2, 2)
    panels = [
        (gs_left[0, 0], result.images.atoms, 'Atoms'),
        (gs_left[0, 1], result.images.light, 'Light'),
        (gs_left[1, 0], result.images.dark, 'Dark'),
        (gs_left[1, 1], result.Aprime, "A' (defringed light)"),
    ]
    for cell, image, label in panels:
        ax = fig.add_subplot(cell)
        handle = ax.imshow(image, extent=extent, origin='lower')
        ax.set_title(label, fontsize=9)
        fig.colorbar(handle, ax=ax, location='bottom')
        _hide_ticks(ax)

    # right: density image with the x profile below and the y profile beside it
    gs_right = gs_outer[1].subgridspec(2, 3,
                                       height_ratios=[5, 1],
                                       width_ratios=[1, 8, 0.2],
                                       hspace=0.04, wspace=0.04)
    ax_density = fig.add_subplot(gs_right[0, 1])
    ax_y_prof = fig.add_subplot(gs_right[0, 0], sharey=ax_density)
    ax_cb = fig.add_subplot(gs_right[0, 2])
    ax_x_prof = fig.add_subplot(gs_right[1, 1], sharex=ax_density)

    positive = density[density > 0]
    vmax = float(np.percentile(positive, 99.5)) if positive.size else None
    handle = ax_density.imshow(density, vmin=0, vmax=vmax, extent=extent,
                               origin='lower')
    _draw_mask(ax_density, fit.mask, params)
    ax_density.set_title(
        rf'2D density (atoms/$\mu m^2$), N={fit.n_count:.2e}, '
        rf'OD$_{{peak}}$={fit.od_peak:.2f}', fontsize=10)
    fig.colorbar(handle, cax=ax_cb)
    ax_cb.set_ylabel(r'atoms/$\mu m^2$')
    _hide_ticks(ax_density)

    # profiles are atoms per micron along the axis
    ax_x_prof.scatter(fit.x.position, fit.x.trace / scale, s=4, alpha=0.5,
                      label='data')
    ax_x_prof.plot(fit.x.position, fit.x.fit_trace / scale, color='red',
                   label=_label(fit.x))
    ax_x_prof.set_xlabel(r'x ($\mu$m)')
    ax_x_prof.legend(fontsize=7, loc='upper right')

    ax_y_prof.scatter(fit.y.trace / scale, fit.y.position, s=4, alpha=0.5,
                      label='data')
    ax_y_prof.plot(fit.y.fit_trace / scale, fit.y.position, color='red',
                   label=_label(fit.y))
    ax_y_prof.set_ylabel(r'y ($\mu$m)')
    ax_y_prof.xaxis.set_label_position('top')
    ax_y_prof.xaxis.tick_top()
    ax_y_prof.legend(fontsize=7, loc='upper left')

    subtitle = (f'defringe: {result.defringe_mode} '
                f'({result.n_components} components '
                f'from {len(result.reference_paths) or 1} frames)')
    fig.suptitle(f'{title}\n{subtitle}' if title else subtitle, fontsize=10)

    if show:
        plt.show()
    return fig
