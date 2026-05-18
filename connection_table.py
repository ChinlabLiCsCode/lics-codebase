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
        1x PrawnBlaster Pseudo Clock
        2x NI PXIe-6536 Digital Cards
        2x NI PXIe-6738 Analog Cards
        
    """


    def __init__(self):
        
        
        #Pseudoclock
        prawnblaster = PrawnBlaster(name='prawnblaster', com_port='COM3', 
                                    num_pseudoclocks=4, pico_board="pico2",
                                    in_pins=[0,0,0,0])#,
                                    # external_clock_pin=20, clock_frequency=10e6)
        # final line configures external clocking. currently unstable.

        #NI cards
        NIBox1 = NI_PXIe_6536(
            name = 'NIBox1', 
            parent_device = prawnblaster.clocklines[0], 
            clock_terminal = 'PFI4',
            MAX_name = 'PXI1Slot2')

        NIBox2 = NI_PXIe_6536(
            name = 'NIBox2',
            parent_device = prawnblaster.clocklines[1], 
            clock_terminal = 'PFI4',
            MAX_name = 'PXI1Slot3')
            
        NIBox3 = NI_PXIe_6738(
            name = 'NIBox3',
            parent_device = prawnblaster.clocklines[2],
            clock_terminal = '/PXI1Slot4/PFI0',
            MAX_name = 'PXI1Slot4',
            max_AO_sample_rate = 4e5)
            
        NIBox4 = NI_PXIe_6738(
            name = 'NIBox4',
            parent_device = prawnblaster.clocklines[3],
            clock_terminal = '/PXI1Slot5/PFI0',
            MAX_name = 'PXI1Slot5',
            max_AO_sample_rate = 4e5)
   

        # power supplies
        
        # powerSupplies = {
        #     "ps1":DP832(name='ps1', VISA_name="USB0::0x1AB1::0x0E11::DP8C272M00087::INSTR", limited='current')
        # }

        # self.psOut = {
        #     'ch1':StaticAnalogOut("ch1", powerSupplies['ps1'], 'channel 1'),
        #     'ch2':StaticAnalogOut('ch2', powerSupplies['ps1'], 'channel 2'),
        #     'ch3':StaticAnalogOut('ch3', powerSupplies['ps1'], 'channel 3')
        # }
       

        
        #--------------------------------------------------------------------digital output for NI-PXIe 6536 cards--------------------------------------------------------------------------

        # Box1 digital outputs
        self.Bitter_Precision_Disable__b1c00  = DigitalOut(default_value=1,          name='Bitter_Precision_Disable__b1c00',  parent_device=NIBox1, connection='port0/line0')
        self.Cs_2DMOT_Shutter__b1c01          = DigitalOut(default_value=1,          name='Cs_2DMOT_Shutter__b1c01',          parent_device=NIBox1, connection='port0/line1')
        self.Cs_3DMOT_AO_Sw__b1c02            = DigitalOut(default_value=1,          name='Cs_3DMOT_AO_Sw__b1c02',            parent_device=NIBox1, connection='port0/line2')
        self.Cs_3DMOT_Shutter__b1c03          = DigitalOut(default_value=1,          name='Cs_3DMOT_Shutter__b1c03',          parent_device=NIBox1, connection='port0/line3')
        self.Cs_Andor_Trig__b1c04             = DigitalOut(default_value=0,          name='Cs_Andor_Trig__b1c04',             parent_device=NIBox1, connection='port0/line4')
        self.Cs_HFImg_AO_Sw__b1c05            = DigitalOut(default_value=1,          name='Cs_HFImg_AO_Sw__b1c05',            parent_device=NIBox1, connection='port0/line5')
        self.Cs_HFImg_Shutter__b1c06          = DigitalOut(default_value=0,          name='Cs_HFImg_Shutter__b1c06',          parent_device=NIBox1, connection='port0/line6')
        self.Cs_HImg_Shutter__b1c07           = DigitalOut(default_value=0,          name='Cs_HImg_Shutter__b1c07',           parent_device=NIBox1, connection='port0/line7')
        self.Cs_HOP_AO_Sw__b1c08              = DigitalOut(default_value=1,          name='Cs_HOP_AO_Sw__b1c08',              parent_device=NIBox1, connection='port1/line0')
        self.Cs_HOP_Shutter__b1c09            = DigitalOut(default_value=1,          name='Cs_HOP_Shutter__b1c09',            parent_device=NIBox1, connection='port1/line1')
        self.Cs_LFImg_AO_Sw__b1c10            = DigitalOut(default_value=1,          name='Cs_LFImg_AO_Sw__b1c10',            parent_device=NIBox1, connection='port1/line2', inverted=True)
        self.Cs_LFImg_Shutter__b1c11          = DigitalOut(default_value=1,          name='Cs_LFImg_Shutter__b1c11',          parent_device=NIBox1, connection='port1/line3')
        self.Cs_Rep_Shutter__b1c12            = DigitalOut(default_value=1,          name='Cs_Rep_Shutter__b1c12',            parent_device=NIBox1, connection='port1/line4')
        self.Cs_RSC_AO_Sw__b1c13              = DigitalOut(default_value=1,          name='Cs_RSC_AO_Sw__b1c13',              parent_device=NIBox1, connection='port1/line5')
        self.Cs_RSC_Shutter__b1c14            = DigitalOut(default_value=0,          name='Cs_RSC_Shutter__b1c14',            parent_device=NIBox1, connection='port1/line6')
        self.Cs_VImg_Shutter__b1c15           = DigitalOut(default_value=0,          name='Cs_VImg_Shutter__b1c15',           parent_device=NIBox1, connection='port1/line7')
        self.Cs_VRep_Shutter__b1c16           = DigitalOut(default_value=1,          name='Cs_VRep_Shutter__b1c16',           parent_device=NIBox1, connection='port2/line0')
        self.Cs_Zeeman_Shutter__b1c17         = DigitalOut(default_value=1,          name='Cs_Zeeman_Shutter__b1c17',         parent_device=NIBox1, connection='port2/line1')
        self.DMD_AO_FM__b1c18                 = DigitalOut(default_value=0,          name='DMD_AO_FM__b1c18',                 parent_device=NIBox1, connection='port2/line2')
        self.DMD_AO_Sw__b1c19                 = DigitalOut(default_value=1,          name='DMD_AO_Sw__b1c19',                 parent_device=NIBox1, connection='port2/line3')
        self.DMD_Movie_Trig__b1c20            = DigitalOut(default_value=0,          name='DMD_Movie_Trig__b1c20',            parent_device=NIBox1, connection='port2/line4')
        self.DMD_Shutter__b1c21               = DigitalOut(default_value=0,          name='DMD_Shutter__b1c21',               parent_device=NIBox1, connection='port2/line5')
        self.Dual_1064_AO_Sw__b1c22           = DigitalOut(default_value=1,          name='Dual_1064_AO_Sw__b1c22',           parent_device=NIBox1, connection='port2/line6')
        self.Dual_780_AO_Sw__b1c23            = DigitalOut(default_value=1,          name='Dual_780_AO_Sw__b1c23',            parent_device=NIBox1, connection='port2/line7')
        self.FF_Disable__b1c24                = DigitalOut(default_value=0,          name='FF_Disable__b1c24',                parent_device=NIBox1, connection='port3/line0')
        self.Li_Andor_Trig__b1c25             = DigitalOut(default_value=0,          name='Li_Andor_Trig__b1c25',             parent_device=NIBox1, connection='port3/line1')
        self.Li_EOM_AO_Sw__b1c26              = DigitalOut(default_value=1,          name='Li_EOM_AO_Sw__b1c26',              parent_device=NIBox1, connection='port3/line2', inverted=True)
        self.Li_EOM_H_Shutter__b1c27          = DigitalOut(default_value=0,          name='Li_EOM_H_Shutter__b1c27',          parent_device=NIBox1, connection='port3/line3')
        self.Li_HImg_Shutter__b1c28           = DigitalOut(default_value=1,          name='Li_HImg_Shutter__b1c28',           parent_device=NIBox1, connection='port3/line4')
        self.Li_Img_AO_Sw__b1c29              = DigitalOut(default_value=1,          name='Li_Img_AO_Sw__b1c29',              parent_device=NIBox1, connection='port3/line5')
        self.Li_MOT_AO_Sw__b1c30              = DigitalOut(default_value=1,          name='Li_MOT_AO_Sw__b1c30',              parent_device=NIBox1, connection='port3/line6')
        self.Li_MOT_Shutter__b1c31            = DigitalOut(default_value=1,          name='Li_MOT_Shutter__b1c31',            parent_device=NIBox1, connection='port3/line7')
        
        # Box2 digital outputs
        self.Li_Rep_AO_Sw__b2c00              = DigitalOut(default_value=1,          name='Li_Rep_AO_Sw__b2c00',              parent_device=NIBox2, connection='port0/line0')
        self.Li_Rep_Shutter__b2c01            = DigitalOut(default_value=1,          name='Li_Rep_Shutter__b2c01',            parent_device=NIBox2, connection='port0/line1')
        self.Li_VImg_Shutter__b2c02           = DigitalOut(default_value=0,          name='Li_VImg_Shutter__b2c02',           parent_device=NIBox2, connection='port0/line2')
        self.Li_Zeeman_Shutter__b2c03         = DigitalOut(default_value=1,          name='Li_Zeeman_Shutter__b2c03',         parent_device=NIBox2, connection='port0/line3')
        self.MW_Trig__b2c04                   = DigitalOut(default_value=0,          name='MW_Trig__b2c04',                   parent_device=NIBox2, connection='port0/line4')
        self.oTOP_Pos_Lock_Enable__b2c05      = DigitalOut(default_value=0,          name='oTOP_Pos_Lock_Enable__b2c05',      parent_device=NIBox2, connection='port0/line5')
        self.Pixelfly_Shutter__b2c06          = DigitalOut(default_value=1,          name='Pixelfly_Shutter__b2c06',          parent_device=NIBox2, connection='port0/line6')
        self.Pixelfly_Trig__b2c07             = DigitalOut(default_value=0,          name='Pixelfly_Trig__b2c07',             parent_device=NIBox2, connection='port0/line7')
        self.Scope_Trig__b2c08                = DigitalOut(default_value=0,          name='Scope_Trig__b2c08',                parent_device=NIBox2, connection='port1/line0')
        self.Spec_Analyzer_Trig__b2c09        = DigitalOut(default_value=0,          name='Spec_Analyzer_Trig__b2c09',        parent_device=NIBox2, connection='port1/line1')
        self.b2c10                            = DigitalOut(default_value=0,          name='b2c10',                            parent_device=NIBox2, connection='port1/line2')
        self.b2c11                            = DigitalOut(default_value=0,          name='b2c11',                            parent_device=NIBox2, connection='port1/line3')
        self.b2c12                            = DigitalOut(default_value=0,          name='b2c12',                            parent_device=NIBox2, connection='port1/line4')
        self.b2c13                            = DigitalOut(default_value=0,          name='b2c13',                            parent_device=NIBox2, connection='port1/line5')
        self.b2c14                            = DigitalOut(default_value=0,          name='b2c14',                            parent_device=NIBox2, connection='port1/line6')
        self.b2c15                            = DigitalOut(default_value=0,          name='b2c15',                            parent_device=NIBox2, connection='port1/line7')
        self.b2c16                            = DigitalOut(default_value=0,          name='b2c16',                            parent_device=NIBox2, connection='port2/line0')
        self.b2c17                            = DigitalOut(default_value=0,          name='b2c17',                            parent_device=NIBox2, connection='port2/line1')
        self.b2c18                            = DigitalOut(default_value=0,          name='b2c18',                            parent_device=NIBox2, connection='port2/line2')
        self.b2c19                            = DigitalOut(default_value=0,          name='b2c19',                            parent_device=NIBox2, connection='port2/line3')
        self.b2c20                            = DigitalOut(default_value=0,          name='b2c20',                            parent_device=NIBox2, connection='port2/line4')
        self.b2c21                            = DigitalOut(default_value=0,          name='b2c21',                            parent_device=NIBox2, connection='port2/line5')
        self.b2c22                            = DigitalOut(default_value=0,          name='b2c22',                            parent_device=NIBox2, connection='port2/line6')
        self.b2c23                            = DigitalOut(default_value=0,          name='b2c23',                            parent_device=NIBox2, connection='port2/line7')
        self.b2c24                            = DigitalOut(default_value=0,          name='b2c24',                            parent_device=NIBox2, connection='port3/line0')    
        self.b2c25                            = DigitalOut(default_value=0,          name='b2c25',                            parent_device=NIBox2, connection='port3/line1')
        self.b2c26                            = DigitalOut(default_value=0,          name='b2c26',                            parent_device=NIBox2, connection='port3/line2')
        self.b2c27                            = DigitalOut(default_value=0,          name='b2c27',                            parent_device=NIBox2, connection='port3/line3')
        self.b2c28                            = DigitalOut(default_value=0,          name='b2c28',                            parent_device=NIBox2, connection='port3/line4')
        self.b2c29                            = DigitalOut(default_value=0,          name='b2c29',                            parent_device=NIBox2, connection='port3/line5')
        self.b2c30                            = DigitalOut(default_value=0,          name='b2c30',                            parent_device=NIBox2, connection='port3/line6')
        self.b2c31                            = DigitalOut(default_value=0,          name='b2c31',                            parent_device=NIBox2, connection='port3/line7')
        
        #-------------------------------------------------------------------analog outputs for NI PXIe-6738 cards---------------------------------------------------------------------------

        # Box3 analog outputs
        self.Aerotech_Control__b3c00          = AnalogOut(default_value=0,           name='Aerotech_Control__b3c00',          parent_device=NIBox3, connection='ao0')
        self.BFL_AO_Sw__b3c01                 = AnalogOut(default_value=5,           name='BFL_AO_Sw__b3c01',                 parent_device=NIBox3, connection='ao1')
        self.BFL_Int_Lock__b3c02              = AnalogOut(default_value=0.1,         name='BFL_Int_Lock__b3c02',              parent_device=NIBox3, connection='ao2')
        self.Bias_X_AH__b3c03                 = AnalogOut(default_value=1,           name='Bias_X_AH__b3c03',                 parent_device=NIBox3, connection='ao3')
        self.Bias_X_HH__b3c04                 = AnalogOut(default_value=-1,          name='Bias_X_HH__b3c04',                 parent_device=NIBox3, connection='ao4')
        self.Bias_Y_AH__b3c05                 = AnalogOut(default_value=0,           name='Bias_Y_AH__b3c05',                 parent_device=NIBox3, connection='ao5')
        self.Bias_Y_HH__b3c06                 = AnalogOut(default_value=1,           name='Bias_Y_HH__b3c06',                 parent_device=NIBox3, connection='ao6')
        self.Bias_Z_AH__b3c07                 = AnalogOut(default_value=-1,          name='Bias_Z_AH__b3c07',                 parent_device=NIBox3, connection='ao7')
        self.Bias_Z_HH__b3c08                 = AnalogOut(default_value=-6,          name='Bias_Z_HH__b3c08',                 parent_device=NIBox3, connection='ao8')
        self.Bitter_AH_Upper_FF__b3c09        = AnalogOut(default_value=0,           name='Bitter_AH_Upper_FF__b3c09',        parent_device=NIBox3, connection='ao9')
        self.Bitter_HH_Upper_FF__b3c10        = AnalogOut(default_value=0,           name='Bitter_HH_Upper_FF__b3c10',        parent_device=NIBox3, connection='ao10')
        self.Bitter_IServo_FB_Sw__b3c11       = AnalogOut(default_value=0,           name='Bitter_IServo_FB_Sw__b3c11',       parent_device=NIBox3, connection='ao11')
        self.Bitter_Lower_CC__b3c12           = AnalogOut(default_value=1,           name='Bitter_Lower_CC__b3c12',           parent_device=NIBox3, connection='ao12')
        self.Bitter_Lower_CV__b3c13           = AnalogOut(default_value=1.5,         name='Bitter_Lower_CV__b3c13',           parent_device=NIBox3, connection='ao13')
        self.Bitter_Lower_FF__b3c14           = AnalogOut(default_value=0,           name='Bitter_Lower_FF__b3c14',           parent_device=NIBox3, connection='ao14')
        self.Bitter_Upper_AH_Sw__b3c15        = AnalogOut(default_value=5,           name='Bitter_Upper_AH_Sw__b3c15',        parent_device=NIBox3, connection='ao15')
        self.Bitter_Upper_CC__b3c16           = AnalogOut(default_value=1,           name='Bitter_Upper_CC__b3c16',           parent_device=NIBox3, connection='ao16')
        self.Bitter_Upper_CV__b3c17           = AnalogOut(default_value=2,           name='Bitter_Upper_CV__b3c17',           parent_device=NIBox3, connection='ao17')
        self.Bitter_Upper_HH_Sw__b3c18        = AnalogOut(default_value=0,           name='Bitter_Upper_HH_Sw__b3c18',        parent_device=NIBox3, connection='ao18')
        self.Bitter_V_AH__b3c19               = AnalogOut(default_value=0.1883,      name='Bitter_V_AH__b3c19',               parent_device=NIBox3, connection='ao19')
        self.Bitter_V_HH__b3c20               = AnalogOut(default_value=-0.0183,     name='Bitter_V_HH__b3c20',               parent_device=NIBox3, connection='ao20')
        self.Cs_3DMOT_AO_AM__b3c21            = AnalogOut(default_value=2.3,         name='Cs_3DMOT_AO_AM__b3c21',            parent_device=NIBox3, connection='ao21')
        self.CS_HFImg_Freq__b3c22             = AnalogOut(default_value=-10,         name='CS_HFImg_Freq__b3c22',             parent_device=NIBox3, connection='ao22')
        self.b3c23                            = AnalogOut(default_value=0,           name='b3c23',                            parent_device=NIBox3, connection='ao23')
        self.Cs_MOT_Freq__b3c24               = AnalogOut(default_value=-7.15,       name='Cs_MOT_Freq__b3c24',               parent_device=NIBox3, connection='ao24')
        self.Cs_Rep_AO_AM__b3c25              = AnalogOut(default_value=5,           name='Cs_Rep_AO_AM__b3c25',              parent_device=NIBox3, connection='ao25')
        self.Cs_Rep_Freq__b3c26               = AnalogOut(default_value=6.51,        name='Cs_Rep_Freq__b3c26',               parent_device=NIBox3, connection='ao26')
        self.Cs_RSC_AO_AM__b3c27              = AnalogOut(default_value=5,           name='Cs_RSC_AO_AM__b3c27',              parent_device=NIBox3, connection='ao27')
        self.Cs_VImg_AO_AM__b3c28             = AnalogOut(default_value=5,           name='Cs_VImg_AO_AM__b3c28',             parent_device=NIBox3, connection='ao28')
        self.DMD_AO_AM__b3c29                 = AnalogOut(default_value=3.8,         name='DMD_AO_AM__b3c29',                 parent_device=NIBox3, connection='ao29')
        self.Dual_780_Int_Lock__b3c30         = AnalogOut(default_value=2.5,         name='Dual_780_Int_Lock__b3c30',         parent_device=NIBox3, connection='ao30')
        self.Li_EOM_Freq__b3c31               = AnalogOut(default_value=-4.5,        name='Li_EOM_Freq__b3c31',               parent_device=NIBox3, connection='ao31')
        
        # Box4 analog outputs
        self.Li_Img_AO_AM__b4c00              = AnalogOut(default_value=10,          name='Li_Img_AO_AM__b4c00',              parent_device=NIBox4, connection='ao0')
        self.Li_Img_Freq__b4c01               = AnalogOut(default_value=-5.2499,     name='Li_Img_Freq__b4c01',               parent_device=NIBox4, connection='ao1')
        self.Li_MOT_AO_AM__b4c02              = AnalogOut(default_value=10,          name='Li_MOT_AO_AM__b4c02',              parent_device=NIBox4, connection='ao2')
        self.Li_MOT_Freq__b4c03               = AnalogOut(default_value=5.2844,      name='Li_MOT_Freq__b4c03',               parent_device=NIBox4, connection='ao3')
        self.Li_MRep_AO_FM__b4c04             = AnalogOut(default_value=0.4086,      name='Li_MRep_AO_FM__b4c04',             parent_device=NIBox4, connection='ao4')
        self.Li_Rep_AO_AM__b4c05              = AnalogOut(default_value=10,          name='Li_Rep_AO_AM__b4c05',              parent_device=NIBox4, connection='ao5')
        self.oTOP_AO_AM__b4c06                = AnalogOut(default_value=10,          name='oTOP_AO_AM__b4c06',                parent_device=NIBox4, connection='ao6')
        self.oTOP_FCarrier__b4c07             = AnalogOut(default_value=1.7999,      name='oTOP_FCarrier__b4c07',             parent_device=NIBox4, connection='ao7')
        self.oTOP_Int_Lock__b4c08             = AnalogOut(default_value=0.3,         name='oTOP_Int_Lock__b4c08',             parent_device=NIBox4, connection='ao8')
        self.oTOP_Mod_AM__b4c09               = AnalogOut(default_value=0,           name='oTOP_Mod_AM__b4c09',               parent_device=NIBox4, connection='ao9')
        self.Zeeman_C1__b4c10                 = AnalogOut(default_value=0,           name='Zeeman_C1__b4c10',                 parent_device=NIBox4, connection='ao10')
        self.Zeeman_C2__b4c11                 = AnalogOut(default_value=0,           name='Zeeman_C2__b4c11',                 parent_device=NIBox4, connection='ao11')
        self.Zeeman_C3__b4c12                 = AnalogOut(default_value=0,           name='Zeeman_C3__b4c12',                 parent_device=NIBox4, connection='ao12')
        self.Zeeman_C4__b4c13                 = AnalogOut(default_value=0,           name='Zeeman_C4__b4c13',                 parent_device=NIBox4, connection='ao13')
        self.Zeeman_C5__b4c14                 = AnalogOut(default_value=0,           name='Zeeman_C5__b4c14',                 parent_device=NIBox4, connection='ao14')
        self.Cs_EOM_Freq_b4c15                = AnalogOut(default_value=9,           name='Cs_EOM_Freq_b4c15',                parent_device=NIBox4, connection='ao15')
        self.b4c16                            = AnalogOut(default_value=0,           name='b4c16',                            parent_device=NIBox4, connection='ao16')
        self.b4c17                            = AnalogOut(default_value=0,           name='b4c17',                            parent_device=NIBox4, connection='ao17')
        self.b4c18                            = AnalogOut(default_value=0,           name='b4c18',                            parent_device=NIBox4, connection='ao18')
        self.b4c19                            = AnalogOut(default_value=0,           name='b4c19',                            parent_device=NIBox4, connection='ao19')
        self.b4c20                            = AnalogOut(default_value=0,           name='b4c20',                            parent_device=NIBox4, connection='ao20')
        self.b4c21                            = AnalogOut(default_value=0,           name='b4c21',                            parent_device=NIBox4, connection='ao21')
        self.b4c22                            = AnalogOut(default_value=0,           name='b4c22',                            parent_device=NIBox4, connection='ao22')
        self.b4c23                            = AnalogOut(default_value=0,           name='b4c23',                            parent_device=NIBox4, connection='ao23')
        self.b4c24                            = AnalogOut(default_value=0,           name='b4c24',                            parent_device=NIBox4, connection='ao24')
        self.b4c25                            = AnalogOut(default_value=0,           name='b4c25',                            parent_device=NIBox4, connection='ao25')
        self.b4c26                            = AnalogOut(default_value=0,           name='b4c26',                            parent_device=NIBox4, connection='ao26')
        self.b4c27                            = AnalogOut(default_value=0,           name='b4c27',                            parent_device=NIBox4, connection='ao27')
        self.b4c28                            = AnalogOut(default_value=0,           name='b4c28',                            parent_device=NIBox4, connection='ao28')
        self.b4c29                            = AnalogOut(default_value=0,           name='b4c29',                            parent_device=NIBox4, connection='ao29')
        self.b4c30                            = AnalogOut(default_value=0,           name='b4c30',                            parent_device=NIBox4, connection='ao30')
        self.b4c31                            = AnalogOut(default_value=0,           name='b4c31',                            parent_device=NIBox4, connection='ao31')   

    def set_background(self, t):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, DigitalOut):
                if attr.default_value == 0:
                    attr.go_low(t=t)
                else:
                    attr.go_high(t=t)
            if isinstance(attr, AnalogOut):
                attr.constant(t=t, value=attr.default_value)
        
if __name__ == '__main__':
    ct = ConnectionTable()

    start()
    t = 0
    # t += 0.001 
    # add_time_marker(t, "Reset Background Values", verbose=True)
    # ct.set_background(t)
    t += 0.001
    stop(t)
