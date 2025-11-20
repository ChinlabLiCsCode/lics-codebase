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

    ct.psOut['ch2'].constant(0)
    ct.psOut['ch1'].constant(1)
    ct.psOut['ch3'].constant(2)


    t+=1

    stop(t)
