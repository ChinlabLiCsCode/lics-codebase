from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable
from lics_labscript_apparatus.sequences.cs_subsequences import Cs_MOT_Loading, Cs_CMOT, Cs_Molasses_Cooling, Cs_H_Imaging

if __name__ == '__main__':
    ct = ConnectionTable()

    start()

    t = 10e-6

    ct.set_background(t)

    t = 20e-6

    ct.set_background(t)

    t = 30e-6

    ct.set_background(t)

    t = 0.1

    add_time_marker(t, 'Cs_MOT_Loading')
    t = Cs_MOT_Loading(t+0.1, ct)

    #close the repump shutter to get the background image
    ct.Cs_Rep_Shutter__b1c12.go_low(t+5)

    #reopen the repump shutter
    ct.Cs_Rep_Shutter__b1c12.go_high(t+5.1)

    ct.set_background(t+5.2)

    stop(t+5.3)