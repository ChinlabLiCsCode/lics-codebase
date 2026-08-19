from labscript import start, stop, add_time_marker, wait
from apparatus.connection_table import ConnectionTable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from _globals_stubs import *

def Cs_MOT_Loading(t, ct: ConnectionTable, set_statics=True):
    """Function for setting all values to load Cs MOT. 
    Starts: t=0
    Ends: t=0.005
    Returns: t=0.005
    Bitter coil must be in AH configuration BEFORE this function is called. 
    Currently this subsequence doesn't touch the bitter coils at all. 
    """


    # set Cs laser frequencies
    ct.Cs_MOT_Freq__b3c24.constant(t, Cs_MOT_Freq_CsMOT)
    ct.Cs_Rep_Freq__b3c26.constant(t, Cs_Rep_Freq_CsMOT)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, Cs_3DMOT_AO_AM_CsMOT)
    
    # close Li shutters
    ct.Li_Rep_Shutter__b2c01.disable(t)
    ct.Li_MOT_Shutter__b1c31.disable(t)
    ct.Li_Zeeman_Shutter__b2c03.disable(t)

    # open the Cs shutters
    ct.Cs_Zeeman_Shutter__b1c17.enable(t)
    if Enable_2DMOT:
        ct.Cs_2DMOT_Shutter__b1c01.enable(t)
    else:
        ct.Cs_2DMOT_Shutter__b1c01.disable(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.enable(t)
    ct.Cs_3DMOT_Shutter__b1c03.enable(t)
    ct.Cs_Rep_Shutter__b1c12.enable(t)

    # bias field control
    ct.Bias_X_HH.constant(t, Bias_X_HH_CsMOT)
    ct.Bias_X_AH.constant(t, Bias_X_AH_CsMOT)
    ct.Bias_Y_HH.constant(t, Bias_Y_HH_CsMOT)
    ct.Bias_Y_AH.constant(t, Bias_Y_AH_CsMOT)
    ct.Bias_Z_HH.constant(t, Bias_Z_HH_CsMOT)
    ct.Bias_Z_AH.constant(t, Bias_Z_AH_CsMOT)

    # zeeman coil control
    ct.Zeeman_C1__b4c10.constant(t, Zeeman_C1_CsMOT)
    ct.Zeeman_C2__b4c11.constant(t, Zeeman_C2_CsMOT)
    ct.Zeeman_C3__b4c12.constant(t, Zeeman_C3_CsMOT)
    ct.Zeeman_C4__b4c13.constant(t, Zeeman_C4_CsMOT)
    ct.Zeeman_C5__b4c14.constant(t, Zeeman_C5_CsMOT)

    # 2D MOT coil control (static outputs — can only be set once per shot)
    if set_statics:
        ct.Cs_2DMOT_X_minus.constant(Cs_2DMOT_X_minus_CsMOT)
        ct.Cs_2DMOT_X_plus.constant(Cs_2DMOT_X_plus_CsMOT)
        ct.Cs_2DMOT_Y_minus.constant(Cs_2DMOT_Y_minus_CsMOT)
        ct.Cs_2DMOT_Y_plus.constant(Cs_2DMOT_Y_plus_CsMOT)

    # bitter coil control
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.Bitter_Lower_CC__b3c12.constant(t, 5)
    ct.Bitter_Lower_CV__b3c13.constant(t, 2.3)
    ct.Bitter_Upper_CC__b3c16.constant(t, 5)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.4)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t+0.002, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t+0.002, 5)
    ct.Bitter_V_HH.constant(t+0.005, Bitter_V_HH_CsMOT)
    ct.Bitter_V_AH.constant(t+0.005, Bitter_V_AH_CsMOT)

    #Dipole trap control
    #ct.oTOP_Mod_AM__b4c09.constant(t, 5)
    #ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    

    return t+0.005

def Cs_CMOT(t, ct: ConnectionTable):
    """Function for compressing the Cs MOT. 
    Starts: t=-0.030
    Ends: t=0.049
    Returns: t=0.050
    This function assumes that the Cs MOT is already loaded and that 
    the Bitter coils are in the AH configuration from the Cs_MOT_Loading 
    function. The function will adjust the bias fields, MOT and repump 
    frequencies and amplitudes, and the bitter coils to compress the MOT.
    """

    # MOT AOM amplitude trajectory
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t-0.030, 0.030, Cs_3DMOT_AO_AM_CsMOT, Cs_3DMOT_AO_AM_CsCMOT1, ct.FINE)
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t+0.04, 0.008, Cs_3DMOT_AO_AM_CsCMOT1, Cs_3DMOT_AO_AM_CsCMOT2, ct.FINE)

    # MOT frequency
    ct.Cs_MOT_Freq__b3c24.ramp(t, 0.040, Cs_MOT_Freq_CsMOT, Cs_MOT_Freq_CsCMOT, ct.FINE)

    # set repump laser frequency
    ct.Cs_Rep_Freq__b3c26.ramp(t+0.040, 0.009, Cs_Rep_Freq_CsMOT, Cs_Rep_Freq_CsCMOT, ct.FINE)

    # turn off Zeeman slower and 2D MOT
    ct.Cs_Zeeman_Shutter__b1c17.disable(t-0.010)
    ct.Cs_2DMOT_Shutter__b1c01.disable(t-0.010)
    ct.Zeeman_C1__b4c10.constant(t-0.010, 0)
    ct.Zeeman_C2__b4c11.constant(t-0.010, 0)
    ct.Zeeman_C3__b4c12.constant(t-0.010, 0)
    ct.Zeeman_C4__b4c13.constant(t-0.010, 0)
    ct.Zeeman_C5__b4c14.constant(t-0.010, 0)

    # ramp bias fields 
    ct.Bias_X_HH.ramp(t-0.010, 0.058, Bias_X_HH_CsMOT, Bias_X_HH_CsCMOT, ct.FINE)
    ct.Bias_X_AH.ramp(t-0.010, 0.058, Bias_X_AH_CsMOT, Bias_X_AH_CsCMOT, ct.FINE)
    ct.Bias_Y_HH.ramp(t-0.010, 0.058, Bias_Y_HH_CsMOT, Bias_Y_HH_CsCMOT, ct.FINE)
    ct.Bias_Y_AH.ramp(t-0.010, 0.058, Bias_Y_AH_CsMOT, Bias_Y_AH_CsCMOT, ct.FINE)
    ct.Bias_Z_HH.ramp(t-0.010, 0.058, Bias_Z_HH_CsMOT, Bias_Z_HH_CsCMOT, ct.FINE)
    ct.Bias_Z_AH.ramp(t-0.010, 0.058, Bias_Z_AH_CsMOT, Bias_Z_AH_CsCMOT, ct.FINE)

    #imaging shutter control
    ct.Cs_VOP_Shutter__b1c16.disable(t)
    ct.Cs_HOP_Shutter__b1c09.disable(t)

    #bitter coil control
    ct.Bitter_V_HH.ramp(t, 0.040, Bitter_V_HH_CsMOT, Bitter_V_HH_CsCMOT1, ct.FINE)
    ct.Bitter_V_HH.ramp(t+0.040, 0.009, Bitter_V_HH_CsCMOT1, Bitter_V_HH_CsCMOT2, ct.FINE)
    ct.Bitter_V_AH.ramp(t, 0.040, Bitter_V_AH_CsMOT, Bitter_V_AH_CsCMOT1, ct.FINE)
    ct.Bitter_V_AH.ramp(t+0.040, 0.009, Bitter_V_AH_CsCMOT1, Bitter_V_AH_CsCMOT2, ct.FINE)

    #turn off dipole trap intensity lock
    #ct.Dual_780_Int_Lock__b3c30.constant(t+0.04, 0)

    return t+0.050

def Cs_Molasses(t, ct: ConnectionTable):
    """Function for doing Cs optical molasses cooling. Includes Cs_Molasses_Cooling 
    and Cs_Molasses_Dark from the old sequence. 
    Starts: t-0.002
    Ends: t+0.005
    Returns: t+0.005
    """
    #adjust the MOT and repump frequencies
    ct.Cs_MOT_Freq__b3c24.ramp(t-0.002, 0.006, Cs_MOT_Freq_CsCMOT, Cs_MOT_Freq_Molasses, ct.FINE)
    ct.Cs_Rep_Freq__b3c26.ramp(t-0.001, 0.002, Cs_Rep_Freq_CsCMOT, Cs_Rep_Freq_Molasses, ct.FINE)

    #adjust the MOT and optical pump aom amplitudes
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t, 0.005, Cs_3DMOT_AO_AM_CsCMOT2, Cs_3DMOT_AO_AM_Molasses, ct.FINE)
    ct.Cs_OP_AO_AM__b3c25.constant(t, 5)

    #bitter coil control
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)

    #bias coil control
    # ct.Bias_X_plus__b3c03.constant(t, 0.499878)
    # ct.Bias_X_minus__b3c04.constant(t, -1.00061)
    # ct.Bias_Y_plus__b3c05.constant(t, 2.864075)
    # ct.Bias_Y_minus__b3c06.constant(t, -1.499939)
    # ct.Bias_Z_plus__b3c07.constant(t, -1.00061)
    # ct.Bias_Z_minus__b3c08.constant(t, -0.400085)

    # turn MOT light off after molasses
    ct.Cs_3DMOT_AO_Sw__b1c02.disable(t+0.005)
    ct.Cs_3DMOT_Shutter__b1c03.disable(t+0.005) # this was actually -7ms but I brought it up

    # reset MOT laser frequency after molasses
    ct.Cs_MOT_Freq__b3c24.ramp(t+0.008, 0.001, Cs_MOT_Freq_Molasses, Cs_MOT_Freq_CsLFHImg, ct.FINE)

    return t+0.005

def TOF(t, ct: ConnectionTable):
    """Function to turn off all shutters and AOMs related to the MOT, dipole traps, etc."""

    # these can happen even earlier because they aren't important
    ct.Cs_Zeeman_Shutter__b1c17.disable(t-0.020)
    ct.Cs_2DMOT_Shutter__b1c01.disable(t-0.020)

    # make sure Cs MOT light is off
    ct.Cs_3DMOT_AO_Sw__b1c02.disable(t)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0)
    ct.Cs_3DMOT_Shutter__b1c03.disable(t-0.014)

    # make sure RSC light is off
    ct.Cs_RSC_AO_Sw__b1c13.disable(t)
    ct.Cs_RSC_Shutter__b1c14.disable(t)

    return t


def Cs_LF_H_Imaging(t, ct: ConnectionTable, image_num):
    """Function for doing cesium horizontal imaging at low field, i.e. after MOT.
    Starts: t=-0.2 (background image with shutter closed) 
    Ends: t+0.300
    Returns: t+0.300
    This function assumes that the bitter coil is OFF (AH and HH switch set to 0).
    It also assumes that the Cs MOT light and such are turned off.
    It's really designed to follow up the Cs_Molasses_Cooling function, which will 
    have turned the coil off.
    """
    name = f'absorption{image_num}'
    # collect initial background image with the shutter closed 
    ct.Pixelfly_Shutter__b2c06.disable(t-0.225)
    ct.pco_panda.expose(t-0.225, name=name, frametype="dark", trigger_duration=0.030)


    # make sure MOT and REP freqs are right
    ct.Cs_MOT_Freq__b3c24.constant(t-0.001, Cs_MOT_Freq_CsLFHImg)
    ct.Cs_Rep_Freq__b3c26.constant(t-0.001, Cs_Rep_Freq_CsLFHImg)

    # make sure REP shutter is closed
    ct.Cs_Rep_Shutter__b1c12.disable(t-0.015)

    # set bias fields appropriately for imaging
    # 
    #


    # ATOM IMAGE at t=0.000

    # acquire image
    ct.pco_panda.expose(t-0.025, name=name, frametype='atoms', trigger_duration=0.030)

    # pixelfly shutter
    ct.Pixelfly_Shutter__b2c06.enable(t-0.006)
    ct.Pixelfly_Shutter__b2c06.disable(t-0.001)

    # imaging beam
    ct.Cs_LFImg_AO_Sw__b1c10.disable(t-0.013)
    ct.Cs_HImg_Shutter__b1c07.enable(t-0.012)
    ct.Cs_LFImg_Shutter__b1c11.enable(t-0.012)
    ct.Cs_LFImg_AO_Sw__b1c10.enable(t)
    ct.Cs_LFImg_AO_Sw__b1c10.disable(t+Img_Pulse_Length_CsLFHImg) # 100 us imaging pulse
    ct.Scope_Trig__b2c08.enable(t)
    ct.Scope_Trig__b2c08.disable(t+Img_Pulse_Length_CsLFHImg)
    ct.Cs_HImg_Shutter__b1c07.disable(t)
    ct.Cs_LFImg_AO_Sw__b1c10.enable(t+0.030)

    # V OP beam
    ct.Cs_OP_AO_Sw__b1c08.disable(t-0.013)
    ct.Cs_VOP_Shutter__b1c16.enable(t-0.012)
    ct.Cs_OP_AO_AM__b3c25.constant(t-0.001, 3)
    ct.Cs_OP_AO_Sw__b1c08.enable(t-0.001)
    ct.Cs_OP_AO_Sw__b1c08.disable(t+Img_Pulse_Length_CsLFHImg)
    ct.Cs_VOP_Shutter__b1c16.disable(t-0.001)
    ct.Cs_OP_AO_Sw__b1c08.enable(t+0.010)
    

    # turn off dipole traps after image
    # ct.oTOP_Mod_AM__b4c09.constant(t+5e-3, 0)
    # ct.oTOP_AO_AM__b4c06.constant(t+5e-3, 0)

    # LIGHT IMAGE at t=0.200

    # aquire image
    ct.pco_panda.expose(t+0.175, name=name, frametype='light', trigger_duration=0.030)

    # pixelfly shutter 
    ct.Pixelfly_Shutter__b2c06.enable(t+0.194)
    ct.Pixelfly_Shutter__b2c06.disable(t+0.199)

    # imaging beam
    ct.Cs_LFImg_AO_Sw__b1c10.disable(t+0.187)
    ct.Cs_HImg_Shutter__b1c07.enable(t+0.188)
    ct.Cs_LFImg_Shutter__b1c11.enable(t+0.188)
    ct.Cs_LFImg_AO_Sw__b1c10.enable(t+0.200)
    ct.Cs_LFImg_AO_Sw__b1c10.disable(t+0.200+Img_Pulse_Length_CsLFHImg) # 100 us imaging pulse
    # ct.Scope_Trig__b2c08.enable(t+0.200)
    # ct.Scope_Trig__b2c08.disable(t+0.200+Img_Pulse_Length_CsLFHImg)
    ct.Cs_HImg_Shutter__b1c07.disable(t+0.200)
    ct.Cs_LFImg_AO_Sw__b1c10.enable(t+0.230)

    # V OP beam
    ct.Cs_OP_AO_Sw__b1c08.disable(t+0.187)
    ct.Cs_VOP_Shutter__b1c16.enable(t+0.188)
    ct.Cs_OP_AO_AM__b3c25.constant(t+0.199, 3)
    ct.Cs_OP_AO_Sw__b1c08.enable(t+0.199)
    ct.Cs_OP_AO_Sw__b1c08.disable(t+0.200+Img_Pulse_Length_CsLFHImg)
    ct.Cs_VOP_Shutter__b1c16.disable(t+0.198)
    ct.Cs_OP_AO_Sw__b1c08.enable(t+0.210)


    return t+0.300

if __name__ == '__main__':
    ct = ConnectionTable()
