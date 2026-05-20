from labscript import start, stop,add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()


    start()
    # set background multiple times to avoid giving too few samples
    # to any NI box (minimum 4 needed)
    t = 10e-6
    ct.set_background(t)
    t += 10e-6
    ct.set_background(t)
    t += 10e-6
    ct.set_background(t)
    t += 10e-6
    ct.set_background(t)

    # pause for line trigger at 1ms
    t = 0.001
    add_time_marker(t, "Waiting for line trigger")
    wait('line_trigger', t, timeout=0.1)

    # start sequence for real at 2ms
    t = 0.002
    add_time_marker(t, "Sequence starts for real after trigger (t=2ms)")
    
    ct.Bias_X_HH.constant(t=t, value=0)
    ct.Bias_X_AH.constant(t=t, value=0)
    ct.Bias_X_HH.ramp(t=t+0.010, duration=0.020, initial=5, final=0, samplerate=1e5)
    ct.Bias_X_AH.constant(t=t+0.020, value=2)
    ct.Bias_X_AH.ramp(t=t+0.025, duration=0.005, initial=2, final=0, samplerate=1e5)

    # stop sequence at the end
    t = 0.05
    stop(t)