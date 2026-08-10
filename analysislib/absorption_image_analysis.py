import os
import lyse
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

run = lyse.Run(lyse.path)
shot_path = lyse.path

run_name = os.path.basename(shot_path).split("_")
run_name = run_name[0] + "_" + run_name[1]

with h5py.File(shot_path, 'r') as f:
        dark_image = f['images/pco_panda/absorption/dark'][:].astype(float)
        light_image = f['images/pco_panda/absorption/light'][:].astype(float)
        atoms_image = f['images/pco_panda/absorption/atoms'][:].astype(float)

atoms_minus_dark = atoms_image - dark_image
light_minus_dark = light_image - dark_image
ratio = np.divide(
        atoms_minus_dark,
        light_minus_dark,
        out = np.full(atoms_image.shape, 0.1, dtype=float),
        where = light_minus_dark != 0)
ratio[ratio<=0]=0.1

log_image = - np.log10(ratio)
log_image[log_image==np.inf]=0

sigma0 = 3 * (852.34727582e-9) **2 / (2 * np.pi)

od_image = log_image / sigma0

fig, axes = plt.subplots(2,2, figsize=(10,10))

extent=[0, 2048*6.5/1.2, 0, 2048*6.5/1.2]
im1 = axes[0,0].imshow(dark_image, extent=extent)
axes[0,0].set_title("dark_image")
plt.colorbar(im1, ax=axes[0,0])
axes[0,0].set_xlabel('x (um)')
axes[0,0].set_ylabel('x (um)')

im2 = axes[0,1].imshow(light_image, extent=extent)
axes[0,1].set_title("light_image")
plt.colorbar(im2, ax=axes[0,1])
axes[0,1].set_xlabel('x (um)')
axes[0,1].set_ylabel('x (um)')

im3 = axes[1,0].imshow(atoms_image, extent=extent)
axes[1,0].set_title("atoms_image")
plt.colorbar(im3, ax=axes[1,0])
axes[1,0].set_xlabel('x (um)')
axes[1,0].set_ylabel('x (um)')

im4 = axes[1,1].imshow(od_image, vmin=0, vmax=od_image.max(), extent=extent)
axes[1,1].set_title("2D Density")
plt.colorbar(im4, ax=axes[1,1])
axes[1,1].set_xlabel('x (um)')
axes[1,1].set_ylabel('x (um)')

fig.suptitle("Cs MOT Healthcheck:" + run_name)

run.save_result("Max Light Image Pixel Count", light_image.max())
run.save_result("Max Atoms Image Pixel Count", atoms_image.max())
run.save_result("Max OD Image Pixel Count", od_image.max())

plt.tight_layout()
plt.show()