from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lics_labscript_apparatus._globals_stubs import *

from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable
from lics_labscript_apparatus.sequences.seq_CsMOT import load_cs_mot

def fluorescence_image_test(t):
    # take background image (no MOT beams)
    ct.pco_panda.expose(t+ 1e-4, name='fluorescence', frametype='background', trigger_duration=1e-3)

    # wait for background exposure to finish (~50ms), then open MOT beams
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t+0.06)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t+0.1)

    # take picture of the atoms
    ct.pco_panda.expose(t+0.15, name='fluorescence', frametype='atoms', trigger_duration=1e-3)

    # close MOT beams after image
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t + 0.2)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 0.25)

    return t + 0.25

def cs_fluorescence_image(t):
    """Function for taking a fluorescence image of the Cs MOT. Should take 6.1s, returns time after imaging is complete"""
    #open the shutter and take an initial fluorescence image of the MOT
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
    ct.pco_panda.expose(t+0.5, name='fluorescence', frametype='atoms', trigger_duration=100e-3)

    #turn off the MOT coils and take a background image
    ct.Bitter_V_AH.constant(t + 0.900, 0)
    ct.Bitter_V_HH.constant(t + 0.900, 0)
    ct.pco_panda.expose(t + 3, name='fluorescence', frametype='background', trigger_duration=100e-3)

    #turn off the MOT beams and take a final image
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t + 3.5)
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t + 3.5)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 3.5)
    ct.pco_panda.expose(t+4, name='fluorescence', frametype='dark', trigger_duration=100e-3)

    # turn the MOT beams and coils back on to background states
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t + 4.500)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t + 4.500)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 4.500)
    ct.Bitter_V_AH.constant(t + 4.500, Bitter_V_AH_CsMOT)
    ct.Bitter_V_HH.constant(t + 4.500, Bitter_V_HH_CsMOT)

    return t + 4.5



   
if __name__ == '__main__':
    ct = ConnectionTable()
    start()

    t = 10e-6
    ct.set_background(t)

    #t = load_cs_mot(t+1e-4)

    stop(t + 1e-3)

