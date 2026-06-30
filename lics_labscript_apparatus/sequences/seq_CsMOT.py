from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lics_labscript_apparatus._globals_stubs import *

from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    t = 0
    ct = ConnectionTable()

    start()

    # set all channels to init values
    t = 10e-6
    ct.set_background(t)

    # pause for line trigger at 1 us, with a timeout of 100 ms
    add_time_marker(t, 'Waiting for line trigger')
    wait('line_trigger', t, timeout=0.1)

    t = 11700e-3
    add_time_marker(t, 'Cs_MOT_Loading')

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


    # open shutters for Cs MOT loading, close other shutters
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, Cs_3DMOT_AO_AM_CsMOT)
    ct.Li_Rep_Shutter__b2c01.go_low(t)
    ct.Li_MOT_Shutter__b1c31.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_low(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 100e-3)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, Cs_VImg_AO_AM_CsMOT)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 1e-3)


    # set up bitter coil for Cs MOT loading
    ct.Bitter_Lower_FF__b3c14.constant(t, Bitter_Lower_FF_CsMOT)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, Bitter_HH_Upper_FF_CsMOT)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, Bitter_Upper_HH_Sw_CsMOT)
    ct.Bitter_Lower_CV__b3c13.constant(t, Bitter_Lower_CV_CsMOT)
    ct.Bitter_Upper_CV__b3c17.constant(t, Bitter_Upper_CV_CsMOT)
    ct.Bitter_Upper_CC__b3c16.constant(t, Bitter_Upper_CC_CsMOT)
    ct.Bitter_Lower_CC__b3c12.constant(t, Bitter_Lower_CC_CsMOT)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 2e-3, Bitter_IServo_FB_Sw_CsMOT)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 2e-3, Bitter_Upper_AH_Sw_CsMOT)
    ct.Bitter_V_AH.constant(t, Bitter_V_AH_CsMOT)


    # transition from Li Feshbach to Cs MOT
    # ct.Bitter_V_AH.ramp(t=t + 5e-3, duration=45e-3, initial=-0.0619507, final=0.188293, samplerate=FAST_FREQ)
    # ct.Bitter_V_HH.ramp(t=t + 5e-3, duration=45e-3, initial=0.0469971, final=-0.0201416, samplerate=FAST_FREQ)
    # for isolated Cs MOT loading, just set the Bitter V channels to the final values


    # set otop and 780 laser powers in the background
    # ct.oTOP_Int_Lock__b4c08.constant(t, 0.599976)
    # ct.oTOP_FCarrier__b4c07.constant(t, 1.79993)
    # ct.oTOP_Mod_AM__b4c09.constant(t, 5.49988)
    # ct.Dual_780_Int_Lock__b3c30.constant(t, 2.5)
    # ct.Dual_1064_Int_Lock__b4c16.constant(t, 3.75)



