from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

def load_li_mot(t):
    # set Zeeman coil currents for Cs MOT loading
    ct.Zeeman_C1__b4c10.constant(t, 2.5)
    ct.Zeeman_C2__b4c11.constant(t, 3.5)
    ct.Zeeman_C3__b4c12.constant(t, 3.5)
    ct.Zeeman_C4__b4c13.constant(t, 4.250)
    ct.Zeeman_C5__b4c14.constant(t, 0.800)

    #open the Li Mot, repump, and zeeman shutters
    ct.Li_MOT_AO_Sw__b1c30.go_high(t)
    ct.Li_MOT_Shutter__b1c31.go_high(t)

    ct.Li_Rep_AO_Sw__b2c00.go_high(t)
    ct.Li_Rep_Shutter__b2c01.go_high(t)

    ct.Li_Zeeman_Shutter__b2c03.go_high(t)

    #set the bitter coils
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.00012)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.49994)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1.00006)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1.00006)

    ct.Bitter_V_HH.constant(t, -0.00946045)
    ct.Bitter_V_AH.constant(t, 0.347595)

    return t + 1


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
    add_time_marker(t, 'Cs_MOT_Loading')
    t = load_li_mot(t)

    stop(t)