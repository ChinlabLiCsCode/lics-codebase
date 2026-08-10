from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

def load_cs_mot(t):
    """Function for loading the cesium MOT, starts at t-0.1 and ends at t+3.6 seconds"""

    #set Cs laser frequencies
    ct.Cs_MOT_Freq__b3c24.constant(t-0.1, -7.200012)

    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.499939)

    #close lithium shutters
    ct.Li_Rep_Shutter__b2c01.go_low(t)
    ct.Li_MOT_Shutter__b1c31.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_low(t)

    #bias field control
    ct.Bias_X_plus__b3c03.constant(t, -2.5)
    ct.Bias_X_minus__b3c04.constant(t, 1.00061)
    ct.Bias_Y_plus__b3c05.constant(t, -3.599854)
    ct.Bias_Y_minus__b3c06.constant(t, 2.600098)
    ct.Bias_Z_plus__b3c07.constant(t, -0.599976)
    ct.Bias_Z_minus__b3c08.constant(t, -0.499878)

    #bitter coil control
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)

    ct.Bitter_Lower_CC__b3c12.constant(t, 5)
    ct.Bitter_Lower_CV__b3c13.constant(t, 2.300110)
    ct.Bitter_Upper_CC__b3c16.constant(t, 5)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.399902)

    #Dipole trap control
    ct.oTOP_Mod_AM__b4c09.constant(t, 5)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    
    #open the Cs 2D MOT and zeeman shutters
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)

    #set bitter coil helmholtz/antihelmholtz configuration
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t+0.002, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t+0.002, 5)
    ct.Bitter_V_Lower__b3c19.constant(t+0.005, 0.188293)
    ct.Bitter_V_Upper__b3c20.constant(t+0.005, -0.020142)


    #open thre Cs 3D MOT shutter and switch on the 3D MOT AOM
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.1)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t+3.6)

    return t+3.6



if __name__ == '__main__':
    ct = ConnectionTable()