from labscript import start, stop,add_time_marker

from labscriptlib.LiCs_ExperimentApparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()
    print("started")
    start()
    t = 0
    add_time_marker(t, "Start", verbose=True)
    # ct.linetriggerout.go_high(t=t)
    
    #ni card testing sequence
    """t += 1e-4
    ct.DC1Outs['DC1O1'].go_high(t=t)
    t += 1e-4
    ct.DC1Outs['DC1O1'].go_low(t=t)
    t += 1e-4
    ct.DC1Outs['DC1O1'].go_high(t=t)
    t += 1e-4
    ct.DC1Outs['DC1O1'].go_low(t=t)
"""

    for i in range(60):
        ct.DC1Outs["DC1O0"].go_high(t=t)
        ct.DC2Outs["DC2O0"].go_high(t=t)
        ct.AC1Outs["AC1O0"].constant(t=t, value=5)
        
        t +=1e-5

        ct.DC1Outs['DC1O0'].go_low(t=t)
        ct.DC2Outs["DC2O0"].go_low(t=t)
        ct.AC1Outs["AC1O0"].constant(t=t, value=0)

        t +=1
    ct.AC1Outs["AC1O0"].ramp(t=t, duration=2, initial=0, final=5, samplerate=1e4)
    t+=2
    ct.AC1Outs["AC1O0"].ramp(t=t, duration=2, initial=5, final=0, samplerate=1e4)
    t +=2

        
    stop(t)