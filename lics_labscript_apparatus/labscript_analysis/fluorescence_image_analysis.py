import lyse
import numpy as np
import matplotlib.pyplot as plt

run = lyse.Run(lyse.path)

########################Experimant Data########################
atoms = run.get_image('pco_panda', 'fluorescence', 'atoms')
background = run.get_image('pco_panda', 'fluorescence', 'background')

diff = atoms.astype(float) - background.astype(float)


######################Experimental Parameters######################
r_beam = 1.27e-2 #beam radius in m
p_tot = 24.3e-3 + 21.4e-3 + 22.8e-3 # total laser power in W

r_lens = 8e-3 # radius of the imaging lens in m
d = 11 * 2.54e-2 # distance from atoms to lens in m (number of holes * 2.54 cm/hole)

xi = 0.45 #quantum efficiency of the camera at 852 nm in electrons/photon
t_exp = 100e-3 #exposure time in seconds
gain = 0.65 # camera gain in counts/electron


#####################Relevant Cesium Constants####################
gamma = 2*np.pi * 5.234e6 #D2 transition linewidth in Hz
I_sat = 11.049 #|F=4,m_F=pm 4> to |F=5, m_F=pm 5> saturation intensity in W/m^2
delta = 2 * gamma #laser detuning in Hz

######################Atom Number Calculation####################
cx, cy, r = 1000, 1000, 150
diff_crop = diff[cy-r:cy+r, cx-r:cx+r] # crop out the ring

A_beam = np.pi * r_beam**2 # laser beam area in m^2
I = p_tot/A_beam # laser intensity in W/m^2

sa = np.pi * r_lens**2 / d**2 #solid angle of the imaging lens
eta = sa/ (4 * np.pi) #collection efficiency of the imaging lens

N_c = np.sum(diff_crop) #number of counts in the image
rho_ee = 0.5 * (I/I_sat) / (1 + I/I_sat + 4 * ((delta)/gamma)**2) #excited state population fraction
N_a = (N_c * gain) / (rho_ee * gamma * eta * t_exp * xi) #number of atoms in the image


######################Results#####################
print(f"N_a = {N_a:.3e},  N_c = {N_c:.0f},  rho_ee = {rho_ee:.4f}")
run.save_result('N_a', N_a)

######################Plotting the Images#####################
fig = plt.figure('fluorescence image analysis')
fig.clf()
fig.set_size_inches(12, 5)
axes = fig.subplots(1, 2)
im0 = axes[0].imshow(atoms, cmap='viridis', origin='upper', vmin=0, vmax=np.percentile(diff, 99.9))
axes[0].set_title('Atoms (raw)')
plt.colorbar(im0, ax=axes[0])

im1 = axes[1].imshow(diff, cmap='viridis', origin='upper', vmin=0, vmax=np.percentile(diff, 99.9))
axes[1].set_title('Atoms - Background')
plt.colorbar(im1, ax=axes[1])
plt.tight_layout()
plt.show()