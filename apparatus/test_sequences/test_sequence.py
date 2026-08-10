from labscript import start, stop,add_time_marker

from labscriptlib.LiCs_ExperimentApparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()
    print("started")
    start()
    t = 0
    add_time_marker(t, "Start", verbose=True)

    # check if I can set the analog out too fast
    t = 5e-6
    ct.AC1Outs["AC1O0"].constant(t=t, value=5)
    ct.AC1Outs["AC1O0"].constant(t=t+1e-6, value=0)
    
    t = 10e-6
    # ni card testing sequence
    ct.DC1Outs["DC1O0"].go_high(t=t+10e-6)
    ct.DC1Outs["DC1O0"].go_low(t=t+20e-6)

    ct.AC1Outs["AC1O0"].constant(t=t+10e-6, value=5)
    ct.AC1Outs["AC1O0"].constant(t=t+20e-6, value=0)

    ct.AC1Outs["AC1O0"].ramp(t=t+30e-6, duration=1e-4, initial=0, final=5, samplerate=1e5)
    ct.DC1Outs["DC1O0"].go_high(t=t+30e-6)
    ct.DC1Outs["DC1O0"].go_low(t=t+40e-6)

    t = 2e-4
    ct.AC1Outs["AC1O0"].constant(t=t, value=ct.AC1Outs["AC1O0"].default_value)
    t = 3e-4
    stop(t)