from labscript import start, stop,add_time_marker

from lics_labscript_apparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()
    print("started")
    start()
    t = 0
    ct.set_background(t=0)
    add_time_marker(t, "Start", verbose=True)
    t = 3e-4
    stop(t)