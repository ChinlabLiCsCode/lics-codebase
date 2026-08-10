from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

def cs_h_imaging(t):
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