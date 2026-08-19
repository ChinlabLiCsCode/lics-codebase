from labscript import start, stop, add_time_marker, wait
from apparatus.connection_table import ConnectionTable
from apparatus.sequences.cs_sequences.cs_subsequences import *

if __name__ == '__main__':
    ct = ConnectionTable()

    start()

    t = 10e-6

    t = ct.digital_jiggle(t)
    ct.set_background(t)

    # pause for line trigger at 1ms
    t = 0.001
    add_time_marker(t, "Waiting for line trigger")
    wait('line_trigger', t, timeout=0.1)

    #turn off the MOT first
    ct.Cs_Rep_Shutter__b1c12.disable(t+0.01)

    # Cs_MOT_Loading
    t = 0.1
    add_time_marker(t, 'Cs_MOT_Loading')
    t = Cs_MOT_Loading(t, ct)

    # wait for MOT to load
    t += Cs_MOT_Load_Time
    add_time_marker(t, 'Cs_MOT_Loading_End')

    # Cs_CMOT
    add_time_marker(t, 'Cs_CMOT')
    t = Cs_CMOT(t, ct)

    # Cs_CMOT
    add_time_marker(t, 'Cs_Molasses')
    t = Cs_Molasses(t, ct)

    # TOF - kill all trapping beams
    add_time_marker(t, 'TOF')
    t = TOF(t, ct)
    # set bitter coil V to zero
    ct.Bitter_V_AH.constant(t, 0)
    ct.Bitter_V_HH.constant(t, 0)

    # wait TOF time
    t += TOF_Time

    # Cs_LF_H_Img
    add_time_marker(t, 'Cs_LF_H_Imaging')
    t = Cs_LF_H_Imaging(t, ct, image_num=1)

    # set background values back
    t += 0.001
    ct.set_background(t)

    # end sequence
    t += 0.001
    stop(t)