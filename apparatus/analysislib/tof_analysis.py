import lyse
import matplotlib.pyplot as plt

df = lyse.data()

atom_number = df['absorption_image_analysis']['Atom Number'][-10:]
img_freq  = df['Cs_MOT_Freq_CsLFHImg'][-10:]

plt.plot(img_freq, atom_number)

plt.show()