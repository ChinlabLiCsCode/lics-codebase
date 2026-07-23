from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lics_labscript_apparatus._globals_stubs import *

from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

FAST_RAMP = 1e5
SLOW_RAMP = 1e3

ct = ConnectionTable()
start()

t = 10e-6
# ct.set_background(t)

# set all values to Cs MOT values
t = 0.001

# set Cs laser frequencies for Cs MOT loading
ct.Cs_MOT_Freq__b3c24.constant(t, Cs_MOT_Freq_CsMOT)
ct.Cs_Rep_Freq__b3c26.constant(t, Cs_Rep_Freq_CsMOT)


# set Zeeman coil currents for Cs MOT loading
ct.Zeeman_C1__b4c10.constant(t, Zeeman_C1_CsMOT)
ct.Zeeman_C2__b4c11.constant(t, Zeeman_C2_CsMOT)
ct.Zeeman_C3__b4c12.constant(t, Zeeman_C3_CsMOT)
ct.Zeeman_C4__b4c13.constant(t, Zeeman_C4_CsMOT)
ct.Zeeman_C5__b4c14.constant(t, Zeeman_C5_CsMOT)


# set bias coil currents for Cs MOT loading
ct.Bias_X_HH.constant(t, Bias_X_HH_CsMOT)
ct.Bias_X_AH.constant(t, Bias_X_AH_CsMOT)
ct.Bias_Y_HH.constant(t, Bias_Y_HH_CsMOT)
ct.Bias_Y_AH.constant(t, Bias_Y_AH_CsMOT)
ct.Bias_Z_HH.constant(t, Bias_Z_HH_CsMOT)
ct.Bias_Z_AH.constant(t, Bias_Z_AH_CsMOT)

# set up bitter coil for Cs MOT loading
ct.Bitter_Lower_FF__b3c14.constant(t, 0)  
ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
ct.Bitter_Lower_CV__b3c13.constant(t, Bitter_Lower_CV_CsMOT)
ct.Bitter_Upper_CV__b3c17.constant(t, Bitter_Upper_CV_CsMOT)
ct.Bitter_Upper_CC__b3c16.constant(t, 5)
ct.Bitter_Lower_CC__b3c12.constant(t, 5)
ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 0.002, 0)
ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 0.002, 5)
ct.Bitter_V_AH.constant(t + 0.005, Bitter_V_AH_CsMOT)
ct.Bitter_V_HH.constant(t + 0.005, Bitter_V_HH_CsMOT)

# close Li shutters
# ct.Li_Rep_Shutter__b2c01.go_low(t)
# ct.Li_MOT_Shutter__b1c31.go_low(t)
# ct.Li_Zeeman_Shutter__b2c03.go_low(t)
# ct.Li_HImg_Shutter__b1c28.go_low(t)
# ct.Li_VImg_Shutter__b2c02.go_low(t)
# ct.Li_EOM_H_Shutter__b1c27.go_low(t)

# set Cs AOM values and open shutters 
ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
ct.Cs_VImg_AO_AM__b3c28.constant(t, Cs_VImg_AO_AM_CsMOT)
ct.Cs_3DMOT_AO_AM__b3c21.constant(t, Cs_3DMOT_AO_AM_CsMOT)
ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)

# load the Cs MOT for the next 2s
t = 2

# turn off bitter coil to kill MOT
ct.Bitter_V_AH.ramp(t, duration=0.005, initial=Bitter_V_AH_CsMOT, final=0, samplerate=FAST_RAMP)
ct.Bitter_V_HH.ramp(t, duration=0.005, initial=Bitter_V_HH_CsMOT, final=0, samplerate=FAST_RAMP)

# turn bitter coil back on 
t = 2.1
ct.Bitter_V_AH.ramp(t, duration=0.005, initial=0, final=Bitter_V_AH_CsMOT, samplerate=FAST_RAMP)
ct.Bitter_V_HH.ramp(t, duration=0.005, initial=0, final=Bitter_V_HH_CsMOT, samplerate=FAST_RAMP)

# sent test trigger 
ct.Scope_Trig__b2c08.go_high(t)
ct.Scope_Trig__b2c08.go_low(t + 0.010)

# set background multiple times to just ensure we have enough digital edges for digital boxes
ct.b2c31.go_low(t)
ct.b2c31.go_low(t + 0.001)
ct.b2c31.go_low(t + 0.002)
ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.001)
ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.002)

stop(t + 0.020)


def fluorescence_image_test(t):
    # take background image (no MOT beams)
    ct.pco_panda.expose(t+ 1e-4, name='fluorescence', frametype='background', trigger_duration=1e-3)

    # wait for background exposure to finish (~50ms), then open MOT beams
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t+0.06)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.1)

    # take picture of the atoms
    ct.pco_panda.expose(t+0.15, name='fluorescence', frametype='atoms', trigger_duration=1e-3)

    # close MOT beams after image
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t + 0.2)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 0.25)

    return t + 0.25

def cs_fluorescence_image(t):
    """Function for taking a fluorescence image of the Cs MOT. Should take 6.1s, returns time after imaging is complete"""
    #open the shutter and take an initial fluorescence image of the MOT
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
    ct.pco_panda.expose(t+0.5, name='fluorescence', frametype='atoms', trigger_duration=100e-3)

    #turn off the MOT coils and take a background image
    ct.Bitter_V_AH.constant(t + 0.900, 0)
    ct.Bitter_V_HH.constant(t + 0.900, 0)
    ct.pco_panda.expose(t + 3, name='fluorescence', frametype='background', trigger_duration=100e-3)

    #turn off the MOT beams and take a final image
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t + 3.5)
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t + 3.5)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 3.5)
    ct.pco_panda.expose(t+4, name='fluorescence', frametype='dark', trigger_duration=100e-3)

    # turn the MOT beams and coils back on to background states
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t + 4.500)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t + 4.500)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 4.500)
    ct.Bitter_V_AH.constant(t + 4.500, Bitter_V_AH_CsMOT)
    ct.Bitter_V_HH.constant(t + 4.500, Bitter_V_HH_CsMOT)

    return t + 4.5

   


