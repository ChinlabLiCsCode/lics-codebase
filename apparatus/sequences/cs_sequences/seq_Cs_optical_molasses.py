from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

def cs_optical_molasses_cooling(t):
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

if __name__ == '__main__':
    ct = ConnectionTable()