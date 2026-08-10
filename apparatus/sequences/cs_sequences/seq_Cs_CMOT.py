from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

def cs_cmot(t):
    """function for preparing the cs compressed mot, starts at t-0.03 and ends at t+0.04898 """
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t-0.03, 2.300110)

    ct.Cs_Zeeman_Shutter__b1c17.go_low(t-0.01)
    ct.Cs_2DMOT_Shutter__b1c01.go_low(t-0.01)

    ct.Bias_X_plus__b3c03.constant(t-0.01, -2.5)
    ct.Bias_X_minus__b3c04.constant(t-0.01, 1.00061)
    ct.Bias_Y_plus__b3c05.constant(t-0.01, -3.599854)
    ct.Bias_Y_minus__b3c06.constant(t-0.01, 2.600098)
    ct.Bias_Z_plus__b3c07.constant(t-0.01, -0.59976)
    ct.Bias_Z_minus__b3c08.constant(t-0.01, -0.499878)

    ct.Dual_780_Int_Lock__b3c30.constant(t-0.01, 5)

    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.499878)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)

    ct.Cs_VRep_Shutter__b1c16.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_low(t)

    ct.Bitter_V_Upper__b3c20.constant(t, -0.020142)
    ct.Bitter_V_Lower__b3c19.constant(t, 0.188293)

    ct.Cs_MOT_Freq__b3c24.constant(t, -7.200012)

    ct.Dual_780_Int_Lock__b3c30.constant(t+0.04, 0)

    ct.Cs_3DMOT_AO_AM__b3c21.constant(t+0.04, 0.499878)

    ct.Cs_Rep_Freq__b3c26.constant(t+0.04, 6.499939)

    ct.Bitter_V_Upper__b3c20.constant(t+0.04, -0.00916)
    ct.Bitter_V_Lower__b3c19.constant(t+0.04, 0.112610)

    ct.Cs_MOT_Freq__b3c24.constant(t+0.04, -6.799927)

    ct.Cs_3DMOT_AO_AM__b3c21.constant(t+0.048, 0.299988)

    ct.Bias_X_plus__b3c03.constant(t-0.048, 2.000122)
    ct.Bias_X_minus__b3c04.constant(t-0.048, 0)
    ct.Bias_Y_plus__b3c05.constant(t-0.048, 0)
    ct.Bias_Y_minus__b3c06.constant(t-0.048, -0.700073)
    ct.Bias_Z_plus__b3c07.constant(t-0.048, 0.599976)
    ct.Bias_Z_minus__b3c08.constant(t-0.048, -1.199951)

    ct.Cs_Rep_Freq__b3c26.constant(t+0.04898, 5.466919)

    ct.Bitter_V_Upper__b3c20.constant(t+0.04898, 0.010071)
    ct.Bitter_V_Lower__b3c19.constant(t+0.04898, 0.075684)

    return t+0.04898


if __name__ == '__main__':
    ct = ConnectionTable()