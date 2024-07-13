# Experiment imaging 

This directory contains the matlab scripts for reading images and basic processing of images from the experiment. It is essentially intended to replace process_scan and df_view_image. 


The replacement functions will be:

- process_scan -> live_scan
- df_view_image -> df_images

As before, params for live_scan should apply equally well to df_images, since df_images's functionality is just a subset of live_scan. 

Here are the arguments for these functions:
- 'shots' can be any of the following options:
    - 1D or 2D array of shots (uses params.date)
    - shots struct (shots + date)
- 'bginfo' can be any of the following options:
    - 'none' (for V images)
    - 'self' (for H images)
    - 1D array of shots (uses params.date)
    - shots struct (shots + date)
    - 2D array (for H images)
    - 3D array (for V images)
- 'dfinfo' can be any of the following options:
    - 'none' 
    - 'self'
    - 1D array of shots (uses params.date)
    - shots struct (shots + date)
- 'params' should have the following fields:
    - 'date': [yyyy mm dd]
    - 'cam': 'H' or 'V'
    - 'atom': 'C' or 'L'
    - 'view': [xmin xmax ymin ymax]
    - 'mask': [xmin xmax ymin ymax], relative to view
    - 'wavelength': wavelength in m
    - 'pix': pixel size in m
    - 'I_sat': saturation intensity in counts per pixel 
    - 'alpha': correction factor for OD calculation, should take 
    the form [a b c] for the 0th, 1st, and 2nd order terms
    - 'df_method': 
        - 'od' (previous method, defringes the OD image)
        - 'raw' (defringes both the light and shadow images)
        - 'avg' (defringes the shadow image and uses an average bg image from the df set)
    - 'fit_type': 'gaussian', 'thomas-fermi', 'dbl'
    - plot_params: cell array of plot parameters, options are:
        - 'img'
        - 'tracex'
        - 'tracey'
        - 'nx'
        - 'ny'
        - 'n'
        - 'wx'
        - 'wy'
        - 'sep' (for dbl fit only)
- 'macro_fit' (optional): determines if we do some extra overall fitting. Should be a struct with fields:
    - 'type': 'mean', 'gaussian'
    - 'var': can be any fit variable (nx, ny, sep, etc)


