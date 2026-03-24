from labscript import start, stop,add_time_marker

from labscriptlib.LiCs_ExperimentApparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()

    print()
    start()
    
    t = 1
    stop(t)