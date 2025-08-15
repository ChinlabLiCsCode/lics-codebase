from labscript import start, stop, add_time_marker, Trigger, DigitalOut
from labscript.remote import RemoteBLACS
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock
from labscript_devices.NI_DAQmx.models.NI_PXIe_6536 import NI_PXIe_6536

class ConnectionTable:
    def __init__(self):
        #Pseudoclock
        DummyPseudoclock("dummyClock", BLACS_connection='dummy')

        #Define remote connections to other computers
        remotes = {
            'NiControlComputer': RemoteBLACS(name='NiControlComputer', host='192.168.1.39')

        }

        #NI cards
        NiCards = {
            'digCard1':NI_PXIe_6536(name='digCard1', 
                                    parent_device=dummyClock.clockline,
                                    clock_terminal='PFI4',
                                    MAX_name='PXI1Slot3',
                                    worker=remotes['NiControlComputer'])
        }

        #digital output for NI-PXIe 6536
        self.digOuts = {
            'do0': DigitalOut(name='do0', parent_device=NiCards['digCard1'], connection='port0/line0'),
            'do1': DigitalOut(name='do1', parent_device=NiCards['digCard1'], connection='port0/line1'),
            'do2':DigitalOut(name='do2', parent_device=NiCards['digCard1'], connection='port0/line2'),
            'do3':DigitalOut(name='do3', parent_device=NiCards['digCard1'], connection='port0/line3'),
            'do4':DigitalOut(name='do4', parent_device=NiCards['digCard1'], connection='port0/line4'),
            'do5':DigitalOut(name='do5', parent_device=NiCards['digCard1'], connection='port0/line5'),
            'do6':DigitalOut(name='do6', parent_device=NiCards['digCard1'], connection='port0/line6'),
            'do7':DigitalOut(name='do7', parent_device=NiCards['digCard1'], connection='port0/line7'),
            'do8':DigitalOut(name='do8', parent_device=NiCards['digCard1'], connection='port1/line0'),
            'do9':DigitalOut(name='do9', parent_device=NiCards['digCard1'], connection='port1/line1'),
            'do10':DigitalOut(name='do10', parent_device=NiCards['digCard1'], connection='port1/line2'),
            'do11':DigitalOut(name='do11', parent_device=NiCards['digCard1'], connection='port1/line3'),
            'do12':DigitalOut(name='do12', parent_device=NiCards['digCard1'], connection='port1/line4'),
            'do13':DigitalOut(name='do13', parent_device=NiCards['digCard1'], connection='port1/line5'),
            'do14':DigitalOut(name='do14', parent_device=NiCards['digCard1'], connection='port1/line6'),
            'do15':DigitalOut(name='do15', parent_device=NiCards['digCard1'], connection='port1/line7'),
            'do16':DigitalOut(name='do16', parent_device=NiCards['digCard1'], connection='port2/line0'),
            'do17':DigitalOut(name='do17', parent_device=NiCards['digCard1'], connection='port2/line1'),
            'do18':DigitalOut(name='do18', parent_device=NiCards['digCard1'], connection='port2/line2'),
            'do19':DigitalOut(name='do19', parent_device=NiCards['digCard1'], connection='port2/line3'),
            'do20':DigitalOut(name='do20', parent_device=NiCards['digCard1'], connection='port2/line4'),
            'do21':DigitalOut(name='do21', parent_device=NiCards['digCard1'], connection='port2/line5'),
            'do22':DigitalOut(name='do22', parent_device=NiCards['digCard1'], connection='port2/line6'),
            'do23':DigitalOut(name='do23', parent_device=NiCards['digCard1'], connection='port2/line7'),
            'do24':DigitalOut(name='do24', parent_device=NiCards['digCard1'], connection='port3/line0'),
            'do25':DigitalOut(name='do25', parent_device=NiCards['digCard1'], connection='port3/line1'),
            'do26':DigitalOut(name='do26', parent_device=NiCards['digCard1'], connection='port3/line2'),
            'do27':DigitalOut(name='do27', parent_device=NiCards['digCard1'], connection='port3/line3'),
            'do28':DigitalOut(name='do28', parent_device=NiCards['digCard1'], connection='port3/line4'),
            'do29':DigitalOut(name='do29', parent_device=NiCards['digCard1'], connection='port3/line5'),
            'do30':DigitalOut(name='do30', parent_device=NiCards['digCard1'], connection='port3/line6'),
            'do31':DigitalOut(name='do31', parent_device=NiCards['digCard1'], connection='port3/line7')
        }

if __name__ == '__main__':
    ConnectionTable()

    # start() elicits the commencement of the shot
    start()

    # Stop the experiment shot with stop()
    stop(1.0)
