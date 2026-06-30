from labscript import start, stop,add_time_marker

from lics_labscript_apparatus.connection_table import ConnectionTable

if __name__ == '__main__':
    ct = ConnectionTable()
    print("started")
    start()
    t = 0
    add_time_marker(t, "Start", verbose=True)
    ct.set_background(t=1e-3)
    ct.set_background(t=2e-3)
    ct.set_background(t=3e-3)
    ct.set_background(t=4e-3)
    stop(5e-3)