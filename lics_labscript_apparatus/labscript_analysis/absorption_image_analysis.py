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


od_image = - np.log10((atoms_image-dark_image)/(light_image-dark_image))

fig, axes = plt.subplots(2,2, figsize=(10,10))

im1 = axes[0,0].imshow(dark_image)
axes[0,0].set_title("dark_image")
plt.colorbar(im1, ax=axes[0,0])

im2 = axes[0,1].imshow(light_image)
axes[0,1].set_title("light_image")
plt.colorbar(im2, ax=axes[0,1])

im3 = axes[1,0].imshow(atoms_image)
axes[1,0].set_title("atoms_image")
plt.colorbar(im3, ax=axes[1,0])

im4 = axes[1,1].imshow(od_image)
axes[1,1].set_title("od_image")
plt.colorbar(im4, ax=axes[1,1])

fig.suptitle("Cs MOT Healthcheck:" + run_name)

run.save_result("Max Light Image Pixel Count", light_image.max())
run.save_result("Max Atoms Image Pixel Count", atoms_image.max())

plt.show()