from labscript import start, stop,add_time_marker

from labscriptlib.LiCs_ExperimentApparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()

    # Begin issuing labscript primitives
    # A timing variable t is used for convenience
    # start() elicits the commencement of the shot
    t = 0
    add_time_marker(t, "Start", verbose=True)
    start()

    for i in range (1, int(31e3)):
        t=2*i *1e-5
        for out in ct.DC2Outs:
            ct.DC2Outs[out].go_high(t=t)
        t += 1 *1e-5

        for out in ct.DC2Outs:
            ct.DC2Outs[out].go_low(t=t)

    stop(t)
