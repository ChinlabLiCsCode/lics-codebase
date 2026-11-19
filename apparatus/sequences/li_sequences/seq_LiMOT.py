from labscript import start, stop, add_time_marker, wait
from apparatus.connection_table import ConnectionTable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _globals_stubs import *

def Li_MOT_Loading(t, ct: ConnectionTable, set_statics=True):
    """Function for setting all values to load Li MOT. 
    Starts: t=0
    Ends: t=0.005
    Returns: t=0.005
    Bitter coil must be in AH configuration BEFORE this function is called. 
    """
    # set Li laser frequencies
    ct.Li_MOT_Freq__b4c03.constant(t, Li_MOT_Freq_LiMOT)
    ct.Li_Rep_AO_FM__b4c04.constant(t, Li_Rep_AO_FM_LiMOT)
    
    # close Cs shutters
    ct.Cs_2DMOT_Shutter__b1c01.disable(t)
    ct.Cs_3DMOT_Shutter__b1c03.disable(t)
    ct.Cs_Zeeman_Shutter__b1c17.disable(t)
    ct.Cs_RSC_Shutter__b1c14.disable(t)
    

    # open the Li shutters
    ct.Li_Zeeman_Shutter__b2c03.enable(t)
    ct.Li_MOT_Shutter__b1c31.enable(t)
    ct.Li_Rep_Shutter__b2c01.enable(t)

    # close the Li img shutters
    ct.Li_HImg_Shutter__b1c28.disable(t)
    ct.Li_EOM_H_Shutter__b1c27.disable(t)
    # ct.Li_VImg_Shutter__b2c02.disable(t)

    # bias field control
    ct.Bias_X_HH.constant(t, Bias_X_HH_LiMOT)
    ct.Bias_X_AH.constant(t, Bias_X_AH_LiMOT)
    ct.Bias_Y_HH.constant(t, Bias_Y_HH_LiMOT)
    ct.Bias_Y_AH.constant(t, Bias_Y_AH_LiMOT)
    ct.Bias_Z_HH.constant(t, Bias_Z_HH_LiMOT)
    ct.Bias_Z_AH.constant(t, Bias_Z_AH_LiMOT)

    # zeeman coil control
    ct.Zeeman_C1__b4c10.constant(t, Zeeman_C1_LiMOT)
    ct.Zeeman_C2__b4c11.constant(t, Zeeman_C2_LiMOT)
    ct.Zeeman_C3__b4c12.constant(t, Zeeman_C3_LiMOT)
    ct.Zeeman_C4__b4c13.constant(t, Zeeman_C4_LiMOT)
    ct.Zeeman_C5__b4c14.constant(t, Zeeman_C5_LiMOT)

    # bitter coil control
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.Bitter_Lower_CC__b3c12.constant(t, Bitter_Lower_CC_LiMOT)
    ct.Bitter_Lower_CV__b3c13.constant(t, Bitter_Lower_CV_LiMOT)
    ct.Bitter_Upper_CC__b3c16.constant(t, Bitter_Upper_CC_LiMOT)
    ct.Bitter_Upper_CV__b3c17.constant(t, Bitter_Upper_CV_LiMOT)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t+0.002, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t+0.002, 5)
    ct.Bitter_V_HH.constant(t+0.005, Bitter_V_HH_LiMOT)
    ct.Bitter_V_AH.constant(t+0.005, Bitter_V_AH_LiMOT)

    #Dipole trap control
    #ct.oTOP_Mod_AM__b4c09.constant(t, 5)
    #ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    

    return t+0.005


if __name__ == '__main__':
    ct = ConnectionTable()
    start()

    # set all channels to init values
    t = 10e-6
    ct.set_background(t)
    t +=10e-6
    ct.set_background(t)
    t +=10e-6
    ct.set_background(t)


    # pause for line trigger at 1 us, with a timeout of 100 ms
    add_time_marker(t, 'Waiting for line trigger')
    wait('line_trigger', t, timeout=0.1)

    t = 10e-3
    add_time_marker(t, 'Li_MOT_Loading')
    t = Li_MOT_Loading(t, ct)
    t += 3
    stop(t)