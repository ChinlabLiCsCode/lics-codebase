from labscript import start, stop,add_time_marker, DigitalOut, AnalogOut, StaticAnalogOut
from labscript.remote import RemoteBLACS
from labscript_devices.NI_DAQmx.models.NI_PXIe_6536 import NI_PXIe_6536
from labscript_devices.NI_DAQmx.models.NI_PXIe_6738 import NI_PXIe_6738
from LiCs_devices.DP832.labscript_devices import DP832
from labscript_devices.PrawnBlaster.labscript_devices import PrawnBlaster
from labscript_devices.DummyIntermediateDevice import DummyIntermediateDevice
from labscript_devices.DummyPseudoclock.labscript_devices import DummyPseudoclock

class ConnectionTable:
    """
    Connection table for LiCs Experiment

    Devices:
        2x NI PXIe-6536 Digital Cards
        2x NI PXIe-6738 Analog Cards
        1x Rigol DP832 Power supply
        
    """

    def __init__(self):
        
        #Define remote connections to other computers
        remotes = {
            'NiControlComputer': RemoteBLACS(name='NiControlComputer', host='192.168.1.39')

        }
        
        #dummy master pseudoclock
        DummyPseudoclock(name="linetriggerdummyclk") 

        #dummy trigger
        DummyIntermediateDevice(name='linetrigger', parent_device=linetriggerdummyclk.clockline)
        self.linetriggerout = DigitalOut(name='linetriggerout', parent_device=linetrigger, connection="dummy_dout")
        

        #Pseudoclock
        PrawnBlaster(name='prawnblaster', com_port='COM5', num_pseudoclocks=1, in_pins=[0],
                     trigger_device=linetrigger, trigger_connection=linetriggerout)

        # #Pseudoclock
        # PrawnBlaster(name='prawnblaster', com_port='COM5', num_pseudoclocks=1, in_pins=[0], line_triggered=True)


        #NI cards
        NiCards = {
            'DC1':NI_PXIe_6536(name='DC1', 
                                    parent_device=prawnblaster.clocklines[0], # type: ignore
                                    clock_terminal='PFI4',
                                    MAX_name='PXI1Slot2',
                                    worker=remotes['NiControlComputer'])
        }

        #     'DC2':NI_PXIe_6536(name='DC2',
        #                             parent_device=pc.clocklines[0], # type: ignore
        #                             clock_terminal='PFI4',
        #                             MAX_name='PXI1Slot3',
        #                             worker=remotes['NiControlComputer']),

        #     'AC2':NI_PXIe_6738(name='AC2',
        #                                 parent_device=pc.clocklines[0],
        #                                 clock_terminal='PFI4',
        #                                 MAX_name='PXI1Slot5',
        #                                 worker=remotes['NiControlComputer'])
        # }
        """
            'AC1':NI_PXIe_6738(name='AC1',
                                        parent_device=pc.clocklines[0],
                                        clock_terminal='PFI4',
                                        MAX_name='PXI1Slot4',
                                        worker=remotes['NiControlComputer']),
        """


        #power supplies
        """
        powerSupplies = {
            "ps1":DP832(name='ps1', VISA_name="USB0::0x1AB1::0x0E11::DP8C272M00087::INSTR", limited='current')
        }

        self.psOut = {
            'ch1':StaticAnalogOut("ch1", powerSupplies['ps1'], 'channel 1'),
            'ch2':StaticAnalogOut('ch2', powerSupplies['ps1'], 'channel 2'),
            'ch3':StaticAnalogOut('ch3', powerSupplies['ps1'], 'channel 3')
        }
        """

        
        #--------------------------------------------------------------------digital output for NI-PXIe 6536 cards--------------------------------------------------------------------------
        self.DC1Outs = {
            'DC1O0':DigitalOut(name='DC1O0', parent_device=NiCards['DC1'], connection='port0/line0'),
            'DC1O1':DigitalOut(name='DC1O1', parent_device=NiCards['DC1'], connection='port0/line1'),
            'DC1O2':DigitalOut(name='DC1O2', parent_device=NiCards['DC1'], connection='port0/line2'),
            'DC1O3':DigitalOut(name='DC1O3', parent_device=NiCards['DC1'], connection='port0/line3'),
            'DC1O4':DigitalOut(name='DC1O4', parent_device=NiCards['DC1'], connection='port0/line4'),
            'DC1O5':DigitalOut(name='DC1O5', parent_device=NiCards['DC1'], connection='port0/line5'),
            'DC1O6':DigitalOut(name='DC1O6', parent_device=NiCards['DC1'], connection='port0/line6'),
            'DC1O7':DigitalOut(name='DC1O7', parent_device=NiCards['DC1'], connection='port0/line7'),
            'DC1O8':DigitalOut(name='DC1O8', parent_device=NiCards['DC1'], connection='port1/line0'),
            'DC1O9':DigitalOut(name='DC1O9', parent_device=NiCards['DC1'], connection='port1/line1'),
            'DC1O10':DigitalOut(name='DC1O10', parent_device=NiCards['DC1'], connection='port1/line2'),
            'DC1O11':DigitalOut(name='DC1O11', parent_device=NiCards['DC1'], connection='port1/line3'),
            'DC1O12':DigitalOut(name='DC1O12', parent_device=NiCards['DC1'], connection='port1/line4'),
            'DC1O13':DigitalOut(name='DC1O13', parent_device=NiCards['DC1'], connection='port1/line5'),
            'DC1O14':DigitalOut(name='DC1O14', parent_device=NiCards['DC1'], connection='port1/line6'),
            'DC1O15':DigitalOut(name='DC1O15', parent_device=NiCards['DC1'], connection='port1/line7'),
            'DC1O16':DigitalOut(name='DC1O16', parent_device=NiCards['DC1'], connection='port2/line0'),
            'DC1O17':DigitalOut(name='DC1O17', parent_device=NiCards['DC1'], connection='port2/line1'),
            'DC1O18':DigitalOut(name='DC1O18', parent_device=NiCards['DC1'], connection='port2/line2'),
            'DC1O19':DigitalOut(name='DC1O19', parent_device=NiCards['DC1'], connection='port2/line3'),
            'DC1O20':DigitalOut(name='DC1O20', parent_device=NiCards['DC1'], connection='port2/line4'),
            'DC1O21':DigitalOut(name='DC1O21', parent_device=NiCards['DC1'], connection='port2/line5'),
            'DC1O22':DigitalOut(name='DC1O22', parent_device=NiCards['DC1'], connection='port2/line6'),
            'DC1O23':DigitalOut(name='DC1O23', parent_device=NiCards['DC1'], connection='port2/line7'),
            'DC1O24':DigitalOut(name='DC1O24', parent_device=NiCards['DC1'], connection='port3/line0'),
            'DC1O25':DigitalOut(name='DC1O25', parent_device=NiCards['DC1'], connection='port3/line1'),
            'DC1O26':DigitalOut(name='DC1O26', parent_device=NiCards['DC1'], connection='port3/line2'),
            'DC1O27':DigitalOut(name='DC1O27', parent_device=NiCards['DC1'], connection='port3/line3'),
            'DC1O28':DigitalOut(name='DC1O28', parent_device=NiCards['DC1'], connection='port3/line4'),
            'DC1O29':DigitalOut(name='DC1O29', parent_device=NiCards['DC1'], connection='port3/line5'),
            'DC1O30':DigitalOut(name='DC1O30', parent_device=NiCards['DC1'], connection='port3/line6'),
            'DC1O31':DigitalOut(name='DC1O31', parent_device=NiCards['DC1'], connection='port3/line7')
        }

        # self.DC2Outs = {
        #     'DC2O0':DigitalOut(name='DC2O0', parent_device=NiCards['DC2'], connection='port0/line0'),
        #     'DC2O1':DigitalOut(name='DC2O1', parent_device=NiCards['DC2'], connection='port0/line1'),
        #     'DC2O2':DigitalOut(name='DC2O2', parent_device=NiCards['DC2'], connection='port0/line2'),
        #     'DC2O3':DigitalOut(name='DC2O3', parent_device=NiCards['DC2'], connection='port0/line3'),
        #     'DC2O4':DigitalOut(name='DC2O4', parent_device=NiCards['DC2'], connection='port0/line4'),
        #     'DC2O5':DigitalOut(name='DC2O5', parent_device=NiCards['DC2'], connection='port0/line5'),
        #     'DC2O6':DigitalOut(name='DC2O6', parent_device=NiCards['DC2'], connection='port0/line6'),
        #     'DC2O7':DigitalOut(name='DC2O7', parent_device=NiCards['DC2'], connection='port0/line7'),
        #     'DC2O8':DigitalOut(name='DC2O8', parent_device=NiCards['DC2'], connection='port1/line0'),
        #     'DC2O9':DigitalOut(name='DC2O9', parent_device=NiCards['DC2'], connection='port1/line1'),
        #     'DC2O10':DigitalOut(name='DC2O10', parent_device=NiCards['DC2'], connection='port1/line2'),
        #     'DC2O11':DigitalOut(name='DC2O11', parent_device=NiCards['DC2'], connection='port1/line3'),
        #     'DC2O12':DigitalOut(name='DC2O12', parent_device=NiCards['DC2'], connection='port1/line4'),
        #     'DC2O13':DigitalOut(name='DC2O13', parent_device=NiCards['DC2'], connection='port1/line5'),
        #     'DC2O14':DigitalOut(name='DC2O14', parent_device=NiCards['DC2'], connection='port1/line6'),
        #     'DC2O15':DigitalOut(name='DC2O15', parent_device=NiCards['DC2'], connection='port1/line7'),
        #     'DC2O16':DigitalOut(name='DC2O16', parent_device=NiCards['DC2'], connection='port2/line0'),
        #     'DC2O17':DigitalOut(name='DC2O17', parent_device=NiCards['DC2'], connection='port2/line1'),
        #     'DC2O18':DigitalOut(name='DC2O18', parent_device=NiCards['DC2'], connection='port2/line2'),
        #     'DC2O19':DigitalOut(name='DC2O19', parent_device=NiCards['DC2'], connection='port2/line3'),
        #     'DC2O20':DigitalOut(name='DC2O20', parent_device=NiCards['DC2'], connection='port2/line4'),
        #     'DC2O21':DigitalOut(name='DC2O21', parent_device=NiCards['DC2'], connection='port2/line5'),
        #     'DC2O22':DigitalOut(name='DC2O22', parent_device=NiCards['DC2'], connection='port2/line6'),
        #     'DC2O23':DigitalOut(name='DC2O23', parent_device=NiCards['DC2'], connection='port2/line7'),
        #     'DC2O24':DigitalOut(name='DC2O24', parent_device=NiCards['DC2'], connection='port3/line0'),
        #     'DC2O25':DigitalOut(name='DC2O25', parent_device=NiCards['DC2'], connection='port3/line1'),
        #     'DC2O26':DigitalOut(name='DC2O26', parent_device=NiCards['DC2'], connection='port3/line2'),
        #     'DC2O27':DigitalOut(name='DC2O27', parent_device=NiCards['DC2'], connection='port3/line3'),
        #     'DC2O28':DigitalOut(name='DC2O28', parent_device=NiCards['DC2'], connection='port3/line4'),
        #     'DC2O29':DigitalOut(name='DC2O29', parent_device=NiCards['DC2'], connection='port3/line5'),
        #     'DC2O30':DigitalOut(name='DC2O30', parent_device=NiCards['DC2'], connection='port3/line6'),
        #     'DC2O31':DigitalOut(name='DC2O31', parent_device=NiCards['DC2'], connection='port3/line7')
        # }
        
        #-------------------------------------------------------------------analog outputs for NI PXIe-6738 cards---------------------------------------------------------------------------
        """self.AC1Outs = {
            'AC1O0':AnalogOut(name='AC1O0', parent_device=NiCards['AC1'], connection='ao0'),
            'AC1O1':AnalogOut(name='AC1O1', parent_device=NiCards['AC1'], connection='ao1'),
            'AC1O2':AnalogOut(name='AC1O2', parent_device=NiCards['AC1'], connection='ao2'),
            'AC1O3':AnalogOut(name='AC1O3', parent_device=NiCards['AC1'], connection='ao3'),
            'AC1O4':AnalogOut(name='AC1O4', parent_device=NiCards['AC1'], connection='ao4'),
            'AC1O5':AnalogOut(name='AC1O5', parent_device=NiCards['AC1'], connection='ao5'),
            'AC1O6':AnalogOut(name='AC1O6', parent_device=NiCards['AC1'], connection='ao6'),
            'AC1O7':AnalogOut(name='AC1O7', parent_device=NiCards['AC1'], connection='ao7'),
            'AC1O8':AnalogOut(name='AC1O8', parent_device=NiCards['AC1'], connection='ao0'),
            'AC1O9':AnalogOut(name='AC1O9', parent_device=NiCards['AC1'], connection='ao1'),
            'AC1O10':AnalogOut(name='AC1O10', parent_device=NiCards['AC1'], connection='ao2'),
            'AC1O11':AnalogOut(name='AC1O11', parent_device=NiCards['AC1'], connection='ao3'),
            'AC1O12':AnalogOut(name='AC1O12', parent_device=NiCards['AC1'], connection='ao4'),
            'AC1O13':AnalogOut(name='AC1O13', parent_device=NiCards['AC1'], connection='ao5'),
            'AC1O14':AnalogOut(name='AC1O14', parent_device=NiCards['AC1'], connection='ao6'),
            'AC1O15':AnalogOut(name='AC1O15', parent_device=NiCards['AC1'], connection='ao7'),
            'AC1O16':AnalogOut(name='AC1O16', parent_device=NiCards['AC1'], connection='ao0'),
            'AC1O17':AnalogOut(name='AC1O17', parent_device=NiCards['AC1'], connection='ao1'),
            'AC1O18':AnalogOut(name='AC1O18', parent_device=NiCards['AC1'], connection='ao2'),
            'AC1O19':AnalogOut(name='AC1O19', parent_device=NiCards['AC1'], connection='ao3'),
            'AC1O20':AnalogOut(name='AC1O20', parent_device=NiCards['AC1'], connection='ao4'),
            'AC1O21':AnalogOut(name='AC1O21', parent_device=NiCards['AC1'], connection='ao5'),
            'AC1O22':AnalogOut(name='AC1O22', parent_device=NiCards['AC1'], connection='ao6'),
            'AC1O23':AnalogOut(name='AC1O23', parent_device=NiCards['AC1'], connection='ao7'),
            'AC1O24':AnalogOut(name='AC1O24', parent_device=NiCards['AC1'], connection='ao0'),
            'AC1O25':AnalogOut(name='AC1O25', parent_device=NiCards['AC1'], connection='ao1'),
            'AC1O26':AnalogOut(name='AC1O26', parent_device=NiCards['AC1'], connection='ao2'),
            'AC1O27':AnalogOut(name='AC1O27', parent_device=NiCards['AC1'], connection='ao3'),
            'AC1O28':AnalogOut(name='AC1O28', parent_device=NiCards['AC1'], connection='ao4'),
            'AC1O29':AnalogOut(name='AC1O29', parent_device=NiCards['AC1'], connection='ao5'),
            'AC1O30':AnalogOut(name='AC1O30', parent_device=NiCards['AC1'], connection='ao6'),
            'AC1O31':AnalogOut(name='AC1O31', parent_device=NiCards['AC1'], connection='ao7')
        }
"""
        # self.AC2Outs = {
        #     'AC2O0':AnalogOut(name='AC2O0', parent_device=NiCards['AC2'], connection='ao0'),
        #     'AC2O1':AnalogOut(name='AC2O1', parent_device=NiCards['AC2'], connection='ao1'),
        #     'AC2O2':AnalogOut(name='AC2O2', parent_device=NiCards['AC2'], connection='ao2'),
        #     'AC2O3':AnalogOut(name='AC2O3', parent_device=NiCards['AC2'], connection='ao3'),
        #     'AC2O4':AnalogOut(name='AC2O4', parent_device=NiCards['AC2'], connection='ao4'),
        #     'AC2O5':AnalogOut(name='AC2O5', parent_device=NiCards['AC2'], connection='ao5'),
        #     'AC2O6':AnalogOut(name='AC2O6', parent_device=NiCards['AC2'], connection='ao6'),
        #     'AC2O7':AnalogOut(name='AC2O7', parent_device=NiCards['AC2'], connection='ao7'),
        #     'AC2O8':AnalogOut(name='AC2O8', parent_device=NiCards['AC2'], connection='ao0'),
        #     'AC2O9':AnalogOut(name='AC2O9', parent_device=NiCards['AC2'], connection='ao1'),
        #     'AC2O10':AnalogOut(name='AC2O10', parent_device=NiCards['AC2'], connection='ao2'),
        #     'AC2O11':AnalogOut(name='AC2O11', parent_device=NiCards['AC2'], connection='ao3'),
        #     'AC2O12':AnalogOut(name='AC2O12', parent_device=NiCards['AC2'], connection='ao4'),
        #     'AC2O13':AnalogOut(name='AC2O13', parent_device=NiCards['AC2'], connection='ao5'),
        #     'AC2O14':AnalogOut(name='AC2O14', parent_device=NiCards['AC2'], connection='ao6'),
        #     'AC2O15':AnalogOut(name='AC2O15', parent_device=NiCards['AC2'], connection='ao7'),
        #     'AC2O16':AnalogOut(name='AC2O16', parent_device=NiCards['AC2'], connection='ao0'),
        #     'AC2O17':AnalogOut(name='AC2O17', parent_device=NiCards['AC2'], connection='ao1'),
        #     'AC2O18':AnalogOut(name='AC2O18', parent_device=NiCards['AC2'], connection='ao2'),
        #     'AC2O19':AnalogOut(name='AC2O19', parent_device=NiCards['AC2'], connection='ao3'),
        #     'AC2O20':AnalogOut(name='AC2O20', parent_device=NiCards['AC2'], connection='ao4'),
        #     'AC2O21':AnalogOut(name='AC2O21', parent_device=NiCards['AC2'], connection='ao5'),
        #     'AC2O22':AnalogOut(name='AC2O22', parent_device=NiCards['AC2'], connection='ao6'),
        #     'AC2O23':AnalogOut(name='AC2O23', parent_device=NiCards['AC2'], connection='ao7'),
        #     'AC2O24':AnalogOut(name='AC2O24', parent_device=NiCards['AC2'], connection='ao0'),
        #     'AC2O25':AnalogOut(name='AC2O25', parent_device=NiCards['AC2'], connection='ao1'),
        #     'AC2O26':AnalogOut(name='AC2O26', parent_device=NiCards['AC2'], connection='ao2'),
        #     'AC2O27':AnalogOut(name='AC2O27', parent_device=NiCards['AC2'], connection='ao3'),
        #     'AC2O28':AnalogOut(name='AC2O28', parent_device=NiCards['AC2'], connection='ao4'),
        #     'AC2O29':AnalogOut(name='AC2O29', parent_device=NiCards['AC2'], connection='ao5'),
        #     'AC2O30':AnalogOut(name='AC2O30', parent_device=NiCards['AC2'], connection='ao6'),
        #     'AC2O31':AnalogOut(name='AC2O31', parent_device=NiCards['AC2'], connection='ao7')
        # }
        
        
if __name__ == '__main__':
    ConnectionTable()

    start()

    stop(1.0)
