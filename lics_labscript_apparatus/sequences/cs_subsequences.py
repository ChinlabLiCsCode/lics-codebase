from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lics_labscript_apparatus._globals_stubs import *

def Cs_MOT_Loading(t, ct):
    """Function for loading the cesium MOT, starts at t-0.1 and ends at t+3.6 seconds"""

    #set Cs laser frequencies
    ct.Cs_MOT_Freq__b3c24.constant(t-0.1, -7.25)

    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.3)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.499939)

    #close lithium shutters
    ct.Li_Rep_Shutter__b2c01.go_low(t)
    ct.Li_MOT_Shutter__b1c31.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_low(t)

    #bias field control
    ct.Bias_X_plus__b3c03.constant(t, 0)
    ct.Bias_X_minus__b3c04.constant(t, 0)
    ct.Bias_Y_plus__b3c05.constant(t, 0)
    ct.Bias_Y_minus__b3c06.constant(t, 0)
    ct.Bias_Z_plus__b3c07.constant(t, 0)
    ct.Bias_Z_minus__b3c08.constant(t, 0)

    #bitter coil control
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)

    # ct.Bitter_Lower_CC__b3c12.constant(t, 1)
    # ct.Bitter_Lower_CV__b3c13.constant(t, 1.5)
    # ct.Bitter_Upper_CC__b3c16.constant(t, 1)
    # ct.Bitter_Upper_CV__b3c17.constant(t, 2)

    #zeeman coil control
    ct.Zeeman_C1__b4c10.constant(t, Zeeman_C1_CsMOT)
    ct.Zeeman_C2__b4c11.constant(t, Zeeman_C2_CsMOT)
    ct.Zeeman_C3__b4c12.constant(t, Zeeman_C3_CsMOT)
    ct.Zeeman_C4__b4c13.constant(t, Zeeman_C4_CsMOT)
    ct.Zeeman_C5__b4c14.constant(t, Zeeman_C5_CsMOT)

    #Dipole trap control
    #ct.oTOP_Mod_AM__b4c09.constant(t, 5)
    #ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    
    #open the Cs 2D MOT and zeeman shutters
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)

    #open thre Cs 3D MOT shutter and switch on the 3D MOT AOM
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.1)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t+0.1)

    #set bitter coil helmholtz/antihelmholtz configuration
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t+0.002, 0)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t+0.002, 5)
    # ct.Bitter_V_Lower__b3c19.constant(t+0.005, 0.17)
    # ct.Bitter_V_Upper__b3c20.constant(t+0.005, -0.2)

    return t+0.1

def Cs_CMOT(t, ct):
    """function for preparing the cs compressed mot, starts at t-0.03 and ends at t+0.04898 """

    #aom control
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t-0.03, 2.300110)

    #shutter control
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t-0.01)
    ct.Cs_2DMOT_Shutter__b1c01.go_low(t-0.01)

    #bias field control
    ct.Bias_X_plus__b3c03.constant(t-0.01, -2.5)
    ct.Bias_X_minus__b3c04.constant(t-0.01, 1.00061)
    ct.Bias_Y_plus__b3c05.constant(t-0.01, -3.599854)
    ct.Bias_Y_minus__b3c06.constant(t-0.01, 2.600098)
    ct.Bias_Z_plus__b3c07.constant(t-0.01, -0.59976)
    ct.Bias_Z_minus__b3c08.constant(t-0.01, -0.499878)

    #turn on dipole trap intensity lock
    #ct.Dual_780_Int_Lock__b3c30.constant(t-0.01, 5)

    #set mot and repump aom amplitudes
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.499878)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)

    #imaging shutter control
    ct.Cs_VRep_Shutter__b1c16.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_low(t)

    #bitter coil control
    ct.Bitter_V_Upper__b3c20.constant(t, -0.020142)
    ct.Bitter_V_Lower__b3c19.constant(t, 0.188293)

    #mot laser frequency control
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.200012)

    #turn off dipole trap intensity lock
    #ct.Dual_780_Int_Lock__b3c30.constant(t+0.04, 0)

    #set mot aom amplitude
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t+0.04, 0.499878)

    #set repump laser frequency
    ct.Cs_Rep_Freq__b3c26.constant(t+0.04, 6.499939)

    #set bitter coils
    ct.Bitter_V_Upper__b3c20.constant(t+0.04, -0.00916)
    ct.Bitter_V_Lower__b3c19.constant(t+0.04, 0.112610)

    #set mot laser frequency and amplitude
    ct.Cs_MOT_Freq__b3c24.constant(t+0.04, -6.799927)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t+0.048, 0.299988)

    #set bias fields again
    ct.Bias_X_plus__b3c03.constant(t+0.048, 2.000122)
    ct.Bias_X_minus__b3c04.constant(t+0.048, 0)
    ct.Bias_Y_plus__b3c05.constant(t+0.048, 0)
    ct.Bias_Y_minus__b3c06.constant(t+0.048, -0.700073)
    ct.Bias_Z_plus__b3c07.constant(t+0.048, 0.599976)
    ct.Bias_Z_minus__b3c08.constant(t+0.048, -1.199951)

    #set repump frequency again
    ct.Cs_Rep_Freq__b3c26.constant(t+0.04898, 5.466919)

    #set bitter coils again
    ct.Bitter_V_Upper__b3c20.constant(t+0.04898, 0.010071)
    ct.Bitter_V_Lower__b3c19.constant(t+0.04898, 0.075684)

    return t+0.04898

def Cs_Molasses_Cooling(t, ct):
    """Function for doing Cs optical molasses cooling, starts at t-0.002 and ends at t+0.005"""
    #adjust the MOT and repump frequencies
    ct.Cs_MOT_Freq__b3c24.constant(t-0.002, -6.799927)
    ct.Cs_Rep_Freq__b3c26.constant(t-0.001, 5.4666919)

    #adjust the MOT and repump aom amplitudes
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.700073)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)

    #bitter coil control
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)

    #bias coil control
    ct.Bias_X_plus__b3c03.constant(t, 0.499878)
    ct.Bias_X_minus__b3c04.constant(t, -1.00061)
    ct.Bias_Y_plus__b3c05.constant(t, 2.864075)
    ct.Bias_Y_minus__b3c06.constant(t, -1.499939)
    ct.Bias_Z_plus__b3c07.constant(t, -1.00061)
    ct.Bias_Z_minus__b3c08.constant(t, -0.400085)

    #trigger the oscilloscope and the spectrum analyzer
    ct.Spec_Analyzer_Trig__b2c09.go_high(t)
    ct.Scope_Trig__b2c08.go_high(t)
    ct.Spec_Analyzer_Trig__b2c09.go_low(t+0.001)
    ct.Scope_Trig__b2c08.go_lowe(t+0.001)

    #adjust the MOT and repump frequencies again
    ct.Cs_Rep_Freq__b3c26.constant(t+0.001, 6.400146)
    ct.Cs_MOT_Freq__b3c24.constant(t+0.004, -5.799866)

    #adjust the MOT aom amplitude again
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t+0.005, 0.100098)

    return t+0.005

def Cs_H_Imaging(t, ct):
    """Function for doing cesium horizontal imaging, starts at t-0.413 and ends at t+0.655"""
    ct.pco_panda.expose(t-0.413, name="absorption", frametype="im1", trigger_duration=0.1e-3)
    ct.Pixelfly_Shutter__b2c06.go_high(t-15e-3)

    ct.Cs_HOP_AO_Sw__b1c08.go_low(t-13e-3)
    ct.Cs_VRep_Shutter__b1c16.go_high(t-12e-3)
    ct.Cs_HImg_Shutter__b1c07.go_high(t-10e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t-10e-3)

    ct.Bias_Z_minus__b3c08.constant(t-10e-3, 0.499878)
    ct.Bias_Y_minus__b3c06.constant(t-5e-3, -1.9950073)

    ct.Cs_VRep_Shutter__b1c16.go_low(t-1e-3)

    ct.Cs_Rep_AO_AM__b3c25.constant(t-1e-3, 2.999878)

    ct.Cs_HOP_AO_Sw__b1c08.go_high(t-0.1e-3)

    ct.pco_panda.expose(t-0.02e-3, name='absorption', frametype='im2', trigger_duration=0.08e-3)

    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    ct.Cs_HImg_Shutter__b1c07.go_low(t)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t+0.6e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t+0.1e-3)

    ct.oTOP_Mod_AM__b4c09.constant(t+5e-3, 0)
    ct.oTOP_AO_AM__b4c06.constant(t+5e-3, 0)

    ct.Pixelfly_Shutter__b2c06.go_low(t+7e-3)

    ct.Cs_HOP_AO_Sw__b1c08.go_high(t+10e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t+15e-3)

    ct.Pixelfly_Shutter__b2c06.go_high(t+0.625)

    ct.Cs_HImg_Shutter__b1c07.go_high(t+0.625)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t+0.630)

    ct.pco_panda.expose(t+0.63998, name='absorption', frametype='im3', trigger_duration=0.08e-3)

    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t+0.640)
    ct.Cs_HImg_Shutter__b1c07.go_low(t+0.640)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t+0.64006)

    ct.Pixelfly_Shutter__b2c06.go_low(t+0.647)

    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t+0.655)

    return t+0.655

if __name__ == '__main__':
    ct = ConnectionTable()
