from labscript import start, stop,add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()


    start()
    
    ###testing the accuracy of the 60Hz line trigger.
    ###configuration
    n_cycles = 1 ###can also put 10 or 100 60 Hz periods to delay after trigger
    pulse_width = 1e-3 #This is the 1 ms pulse
    T_60HZ = 1 / 60
    #I should give pseudoclock something to do before the wait
    #From Claude: buffer to satisfy NI minimum of 4 samples before StartTask
    t = 100e-6
    ct.set_background(t)
    t += 100e-6
    ct.set_background(t)
    t += 100e-6
    ct.set_background(t)
    t += 100e-6


    add_time_marker(t, "Waiting for line trigger")
    wait('line_trigger', t, timeout=2.0)

    #After trigger fires the pseudoclock resumes from t,
    #such that t + n_cycles*T_60HZ is n cycles after the trigger edge.
    t_pulse = t + n_cycles * T_60HZ

    add_time_marker(t_pulse, f"Pulse ({n_cycles} cycle(s) after trigger)")
    ct.Scope_Trig__b2c08.go_high(t=t_pulse)
    ct.Scope_Trig__b2c08.go_low(t=t_pulse + pulse_width)


    stop(t_pulse + pulse_width + 1e-3)


    # t = 10e-6
    # t += wait('line_trigger', t, timeout=1/50)  # timeout = 1 full 60 Hz cycle
    # t = 20e-6
    # # add_time_marker(t, "Set Background Values")
    # # ct.set_background(t)
    # ct.DMD_Movie_Trig__b1c20.go_high(t=t)
    # ct.DMD_Movie_Trig__b1c20.go_low(t=t+1e-5)
    # ct.DMD_Movie_Trig__b1c20.go_high(t=t+2e-5)
    # ct.DMD_Movie_Trig__b1c20.go_low(t=t+3e-5)
    # ct.b3c23.constant(t=t, value=5)
    # ct.b3c23.constant(t=t+0.001, value=0)

    # add_time_marker(t, "Test Time!")
    # ct.b4c31.exp_ramp(t=t, duration=0.001, initial=5, final=0.5, zero=0, samplerate=1e5)
    # ct.b2c31.repeat_pulse_sequence(t=t, duration=0.001, pulse_sequence=((0, 1), (1e-5, 0)), period=2e-5, samplerate=2e5)



    
    # t = 0.004
    # add_time_marker(t, "Reset Background Values")
    # ct.set_background(t)
    # t += 0.001
    # ct.set_background(t)
    # t += 0.001
    # t = 1
    # stop(t)