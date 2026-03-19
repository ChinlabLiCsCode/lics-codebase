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
        1x Rigol DP832 Power supply
        
    """


    def __init__(self):
        
              
        # #dummy master pseudoclock
        # DummyPseudoclock(name="linetriggerdummyclk") 

        # #dummy trigger
        # DummyIntermediateDevice(name='linetrigger', parent_device=linetriggerdummyclk.clockline)
        # self.linetriggerout = DigitalOut(name='linetriggerout', parent_device=linetrigger, connection="dummy_dout")
        

        # #Pseudoclock
        # PrawnBlaster(name='prawnblaster', com_port='COM3', num_pseudoclocks=4, in_pins=[0],
        #              trigger_device=linetrigger, trigger_connection=linetriggerout)
        

        #Pseudoclock
        prawnblaster = PrawnBlaster(name='prawnblaster', com_port='COM3', num_pseudoclocks=4, pico_board="pico2")


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
            clock_terminal = '/PXI1Slot4/PFI2',
            MAX_name = 'PXI1Slot4',
            max_AO_sample_rate = 4e5)
            
        NIBox4 = NI_PXIe_6738(
            name = 'NIBox4',
            parent_device = prawnblaster.clocklines[3],
            clock_terminal = '/PXI1Slot5/PFI2',
            MAX_name = 'PXI1Slot5',
            max_AO_sample_rate = 4e5)
   

        # power supplies
        
        powerSupplies = {
            "ps1":DP832(name='ps1', VISA_name="USB0::0x1AB1::0x0E11::DP8C272M00087::INSTR", limited='current')
        }

        self.psOut = {
            'ch1':StaticAnalogOut("ch1", powerSupplies['ps1'], 'channel 1'),
            'ch2':StaticAnalogOut('ch2', powerSupplies['ps1'], 'channel 2'),
            'ch3':StaticAnalogOut('ch3', powerSupplies['ps1'], 'channel 3')
        }
       

        
        #--------------------------------------------------------------------digital output for NI-PXIe 6536 cards--------------------------------------------------------------------------

        Bitter_Precision_Disable__b1c00  = DigitalOut(default_value=5,          name='Bitter_Precision_Disable__b1c00',  parent_device=NIBox1, connection='port0/line0')
        Cs_2DMOT_Shutter__b1c01          = DigitalOut(default_value=5,          name='Cs_2DMOT_Shutter__b1c01',          parent_device=NIBox1, connection='port0/line1')
        Cs_3DMOT_AO_Sw__b1c02            = DigitalOut(default_value=5,          name='Cs_3DMOT_AO_Sw__b1c02',            parent_device=NIBox1, connection='port0/line2')
        Cs_3DMOT_Shutter__b1c03          = DigitalOut(default_value=5,          name='Cs_3DMOT_Shutter__b1c03',          parent_device=NIBox1, connection='port0/line3')
        Cs_Andor_Trig__b1c04             = DigitalOut(default_value=0,          name='Cs_Andor_Trig__b1c04',             parent_device=NIBox1, connection='port0/line4')
        Cs_HFImg_AO_Sw__b1c05            = DigitalOut(default_value=5,          name='Cs_HFImg_AO_Sw__b1c05',            parent_device=NIBox1, connection='port0/line5')
        Cs_HFImg_Shutter__b1c06          = DigitalOut(default_value=0,          name='Cs_HFImg_Shutter__b1c06',          parent_device=NIBox1, connection='port0/line6')
        Cs_HImg_Shutter__b1c07           = DigitalOut(default_value=0,          name='Cs_HImg_Shutter__b1c07',           parent_device=NIBox1, connection='port0/line7')
        Cs_HOP_AO_Sw__b1c08              = DigitalOut(default_value=5,          name='Cs_HOP_AO_Sw__b1c08',              parent_device=NIBox1, connection='port1/line0')
        Cs_HOP_Shutter__b1c09            = DigitalOut(default_value=5,          name='Cs_HOP_Shutter__b1c09',            parent_device=NIBox1, connection='port1/line1')
        Cs_LFImg_AO_Sw__b1c10            = DigitalOut(default_value=5,          name='Cs_LFImg_AO_Sw__b1c10',            parent_device=NIBox1, connection='port1/line2')
        Cs_LFImg_Shutter__b1c11          = DigitalOut(default_value=5,          name='Cs_LFImg_Shutter__b1c11',          parent_device=NIBox1, connection='port1/line3')
        Cs_Rep_Shutter__b1c12            = DigitalOut(default_value=5,          name='Cs_Rep_Shutter__b1c12',            parent_device=NIBox1, connection='port1/line4')
        Cs_RSC_AO_Sw__b1c13              = DigitalOut(default_value=5,          name='Cs_RSC_AO_Sw__b1c13',              parent_device=NIBox1, connection='port1/line5')
        Cs_RSC_Shutter__b1c14            = DigitalOut(default_value=0,          name='Cs_RSC_Shutter__b1c14',            parent_device=NIBox1, connection='port1/line6')
        Cs_VImg_Shutter__b1c15           = DigitalOut(default_value=0,          name='Cs_VImg_Shutter__b1c15',           parent_device=NIBox1, connection='port1/line7')
        Cs_VRep_Shutter__b1c16           = DigitalOut(default_value=5,          name='Cs_VRep_Shutter__b1c16',           parent_device=NIBox1, connection='port2/line0')
        Cs_Zeeman_Shutter__b1c17         = DigitalOut(default_value=5,          name='Cs_Zeeman_Shutter__b1c17',         parent_device=NIBox1, connection='port2/line1')
        DMD_AO_FM__b1c18                 = DigitalOut(default_value=0,          name='DMD_AO_FM__b1c18',                 parent_device=NIBox1, connection='port2/line2')
        DMD_AO_Sw__b1c19                 = DigitalOut(default_value=5,          name='DMD_AO_Sw__b1c19',                 parent_device=NIBox1, connection='port2/line3')
        DMD_Movie_Trig__b1c20            = DigitalOut(default_value=0,          name='DMD_Movie_Trig__b1c20',            parent_device=NIBox1, connection='port2/line4')
        DMD_Shutter__b1c21               = DigitalOut(default_value=0,          name='DMD_Shutter__b1c21',               parent_device=NIBox1, connection='port2/line5')
        Dual_1064_AO_Sw__b1c22           = DigitalOut(default_value=5,          name='Dual_1064_AO_Sw__b1c22',           parent_device=NIBox1, connection='port2/line6')
        Dual_780_AO_Sw__b1c23            = DigitalOut(default_value=5,          name='Dual_780_AO_Sw__b1c23',            parent_device=NIBox1, connection='port2/line7')
        FF_Disable__b1c24                = DigitalOut(default_value=0,          name='FF_Disable__b1c24',                parent_device=NIBox1, connection='port3/line0')
        Li_Andor_Trig__b1c25             = DigitalOut(default_value=0,          name='Li_Andor_Trig__b1c25',             parent_device=NIBox1, connection='port3/line1')
        Li_EOM_AO_Sw__b1c26              = DigitalOut(default_value=5,          name='Li_EOM_AO_Sw__b1c26',              parent_device=NIBox1, connection='port3/line2')
        Li_EOM_H_Shutter__b1c27          = DigitalOut(default_value=0,          name='Li_EOM_H_Shutter__b1c27',          parent_device=NIBox1, connection='port3/line3')
        Li_HImg_Shutter__b1c28           = DigitalOut(default_value=0,          name='Li_HImg_Shutter__b1c28',           parent_device=NIBox1, connection='port3/line4')
        Li_Img_AO_Sw__b1c29              = DigitalOut(default_value=5,          name='Li_Img_AO_Sw__b1c29',              parent_device=NIBox1, connection='port3/line5')
        Li_MOT_AO_Sw__b1c30              = DigitalOut(default_value=5,          name='Li_MOT_AO_Sw__b1c30',              parent_device=NIBox1, connection='port3/line6')
        Li_MOT_Shutter__b1c31            = DigitalOut(default_value=5,          name='Li_MOT_Shutter__b1c31',            parent_device=NIBox1, connection='port3/line7')
        
        
        Li_Rep_AO_Sw__b2c00              = DigitalOut(default_value=5,          name='Li_Rep_AO_Sw__b2c00',              parent_device=NIBox2, connection='port0/line0')
        Li_Rep_Shutter__b2c01            = DigitalOut(default_value=5,          name='Li_Rep_Shutter__b2c01',            parent_device=NIBox2, connection='port0/line1')
        Li_VImg_Shutter__b2c02           = DigitalOut(default_value=0,          name='Li_VImg_Shutter__b2c02',           parent_device=NIBox2, connection='port0/line2')
        Li_Zeeman_Shutter__b2c03         = DigitalOut(default_value=5,          name='Li_Zeeman_Shutter__b2c03',         parent_device=NIBox2, connection='port0/line3')
        MW_Trig__b2c04                   = DigitalOut(default_value=0,          name='MW_Trig__b2c04',                   parent_device=NIBox2, connection='port0/line4')
        oTOP_Pos_Lock_Enable__b2c05      = DigitalOut(default_value=0,          name='oTOP_Pos_Lock_Enable__b2c05',      parent_device=NIBox2, connection='port0/line5')
        Pixelfly_Shutter__b2c06          = DigitalOut(default_value=5,          name='Pixelfly_Shutter__b2c06',          parent_device=NIBox2, connection='port0/line6')
        Pixelfly_Trig__b2c07             = DigitalOut(default_value=0,          name='Pixelfly_Trig__b2c07',             parent_device=NIBox2, connection='port0/line7')
        Scope_Trig__b2c08                = DigitalOut(default_value=0,          name='Scope_Trig__b2c08',                parent_device=NIBox2, connection='port1/line0')
        Spec_Analyzer_Trig__b2c09        = DigitalOut(default_value=0,          name='Spec_Analyzer_Trig__b2c09',        parent_device=NIBox2, connection='port1/line1')
        b2c10                            = DigitalOut(default_value=0,          name='b2c10',                            parent_device=NIBox2, connection='port1/line2')
        b2c11                            = DigitalOut(default_value=0,          name='b2c11',                            parent_device=NIBox2, connection='port1/line3')
        b2c12                            = DigitalOut(default_value=0,          name='b2c12',                            parent_device=NIBox2, connection='port1/line4')
        b2c13                            = DigitalOut(default_value=0,          name='b2c13',                            parent_device=NIBox2, connection='port1/line5')
        b2c14                            = DigitalOut(default_value=0,          name='b2c14',                            parent_device=NIBox2, connection='port1/line6')
        b2c15                            = DigitalOut(default_value=0,          name='b2c15',                            parent_device=NIBox2, connection='port1/line7')
        b2c16                            = DigitalOut(default_value=0,          name='b2c16',                            parent_device=NIBox2, connection='port2/line0')
        b2c17                            = DigitalOut(default_value=0,          name='b2c17',                            parent_device=NIBox2, connection='port2/line1')
        b2c18                            = DigitalOut(default_value=0,          name='b2c18',                            parent_device=NIBox2, connection='port2/line2')
        b2c19                            = DigitalOut(default_value=0,          name='b2c19',                            parent_device=NIBox2, connection='port2/line3')
        b2c20                            = DigitalOut(default_value=0,          name='b2c20',                            parent_device=NIBox2, connection='port2/line4')
        b2c21                            = DigitalOut(default_value=0,          name='b2c21',                            parent_device=NIBox2, connection='port2/line5')
        b2c22                            = DigitalOut(default_value=0,          name='b2c22',                            parent_device=NIBox2, connection='port2/line6')
        b2c23                            = DigitalOut(default_value=0,          name='b2c23',                            parent_device=NIBox2, connection='port2/line7')
        b2c24                            = DigitalOut(default_value=0,          name='b2c24',                            parent_device=NIBox2, connection='port3/line0')    
        b2c25                            = DigitalOut(default_value=0,          name='b2c25',                            parent_device=NIBox2, connection='port3/line1')
        b2c26                            = DigitalOut(default_value=0,          name='b2c26',                            parent_device=NIBox2, connection='port3/line2')
        b2c27                            = DigitalOut(default_value=0,          name='b2c27',                            parent_device=NIBox2, connection='port3/line3')
        b2c28                            = DigitalOut(default_value=0,          name='b2c28',                            parent_device=NIBox2, connection='port3/line4')
        b2c29                            = DigitalOut(default_value=0,          name='b2c29',                            parent_device=NIBox2, connection='port3/line5')
        b2c30                            = DigitalOut(default_value=0,          name='b2c30',                            parent_device=NIBox2, connection='port3/line6')
        b2c31                            = DigitalOut(default_value=0,          name='b2c31',                            parent_device=NIBox2, connection='port3/line7')
        
        #-------------------------------------------------------------------analog outputs for NI PXIe-6738 cards---------------------------------------------------------------------------

        Aerotech_Control__b3c00          = AnalogOut(default_value=0,           name='Aerotech_Control__b3c00',          parent_device=NIBox3, connection='ao0')
        BFL_AO_Sw__b3c01                 = AnalogOut(default_value=5,           name='BFL_AO_Sw__b3c01',                 parent_device=NIBox3, connection='ao1')
        BFL_Int_Lock__b3c02              = AnalogOut(default_value=0.1,         name='BFL_Int_Lock__b3c02',              parent_device=NIBox3, connection='ao2')
        Bias_X_AH__b3c03                 = AnalogOut(default_value=1,           name='Bias_X_AH__b3c03',                 parent_device=NIBox3, connection='ao3')
        Bias_X_HH__b3c04                 = AnalogOut(default_value=-1,          name='Bias_X_HH__b3c04',                 parent_device=NIBox3, connection='ao4')
        Bias_Y_AH__b3c05                 = AnalogOut(default_value=0,           name='Bias_Y_AH__b3c05',                 parent_device=NIBox3, connection='ao5')
        Bias_Y_HH__b3c06                 = AnalogOut(default_value=1,           name='Bias_Y_HH__b3c06',                 parent_device=NIBox3, connection='ao6')
        Bias_Z_AH__b3c07                 = AnalogOut(default_value=-1,          name='Bias_Z_AH__b3c07',                 parent_device=NIBox3, connection='ao7')
        Bias_Z_HH__b3c08                 = AnalogOut(default_value=-6,          name='Bias_Z_HH__b3c08',                 parent_device=NIBox3, connection='ao8')
        Bitter_AH_Upper_FF__b3c09        = AnalogOut(default_value=0,           name='Bitter_AH_Upper_FF__b3c09',        parent_device=NIBox3, connection='ao9')
        Bitter_HH_Upper_FF__b3c10        = AnalogOut(default_value=0,           name='Bitter_HH_Upper_FF__b3c10',        parent_device=NIBox3, connection='ao10')
        Bitter_IServo_FB_Sw__b3c11       = AnalogOut(default_value=0,           name='Bitter_IServo_FB_Sw__b3c11',       parent_device=NIBox3, connection='ao11')
        Bitter_Lower_CC__b3c12           = AnalogOut(default_value=1,           name='Bitter_Lower_CC__b3c12',           parent_device=NIBox3, connection='ao12')
        Bitter_Lower_CV__b3c13           = AnalogOut(default_value=1.5,         name='Bitter_Lower_CV__b3c13',           parent_device=NIBox3, connection='ao13')
        Bitter_Lower_FF__b3c14           = AnalogOut(default_value=0,           name='Bitter_Lower_FF__b3c14',           parent_device=NIBox3, connection='ao14')
        Bitter_Upper_AH_Sw__b3c15        = AnalogOut(default_value=5,           name='Bitter_Upper_AH_Sw__b3c15',        parent_device=NIBox3, connection='ao15')
        Bitter_Upper_CC__b3c16           = AnalogOut(default_value=1,           name='Bitter_Upper_CC__b3c16',           parent_device=NIBox3, connection='ao16')
        Bitter_Upper_CV__b3c17           = AnalogOut(default_value=2,           name='Bitter_Upper_CV__b3c17',           parent_device=NIBox3, connection='ao17')
        Bitter_Upper_HH_Sw__b3c18        = AnalogOut(default_value=0,           name='Bitter_Upper_HH_Sw__b3c18',        parent_device=NIBox3, connection='ao18')
        Bitter_V_AH__b3c19               = AnalogOut(default_value=0.1883,      name='Bitter_V_AH__b3c19',               parent_device=NIBox3, connection='ao19')
        Bitter_V_HH__b3c20               = AnalogOut(default_value=-0.0183,     name='Bitter_V_HH__b3c20',               parent_device=NIBox3, connection='ao20')
        Cs_3DMOT_AO_AM__b3c21            = AnalogOut(default_value=2.3,         name='Cs_3DMOT_AO_AM__b3c21',            parent_device=NIBox3, connection='ao21')
        CS_HFImg_Freq__b3c22             = AnalogOut(default_value=-10,         name='CS_HFImg_Freq__b3c22',             parent_device=NIBox3, connection='ao22')
        Cs_LFImg_AO_AM__b3c23            = AnalogOut(default_value=10,          name='Cs_LFImg_AO_AM__b3c23',            parent_device=NIBox3, connection='ao23')
        Cs_MOT_Freq__b3c24               = AnalogOut(default_value=-7.15,       name='Cs_MOT_Freq__b3c24',               parent_device=NIBox3, connection='ao24')
        Cs_Rep_AO_AM__b3c25              = AnalogOut(default_value=5,           name='Cs_Rep_AO_AM__b3c25',              parent_device=NIBox3, connection='ao25')
        Cs_Rep_Freq__b3c26               = AnalogOut(default_value=6.51,        name='Cs_Rep_Freq__b3c26',               parent_device=NIBox3, connection='ao26')
        Cs_RSC_AO_AM__b3c27              = AnalogOut(default_value=5,           name='Cs_RSC_AO_AM__b3c27',              parent_device=NIBox3, connection='ao27')
        Cs_VImg_AO_AM__b3c28             = AnalogOut(default_value=5,           name='Cs_VImg_AO_AM__b3c28',             parent_device=NIBox3, connection='ao28')
        DMD_AO_AM__b3c29                 = AnalogOut(default_value=3.8,         name='DMD_AO_AM__b3c29',                 parent_device=NIBox3, connection='ao29')
        Dual_780_Int_Lock__b3c30         = AnalogOut(default_value=2.5,         name='Dual_780_Int_Lock__b3c30',         parent_device=NIBox3, connection='ao30')
        Li_EOM_Freq__b3c31               = AnalogOut(default_value=-4.5,        name='Li_EOM_Freq__b3c31',               parent_device=NIBox3, connection='ao31')
        
        
        Li_Img_AO_AM__b4c00              = AnalogOut(default_value=10,          name='Li_Img_AO_AM__b4c00',              parent_device=NIBox4, connection='ao0')
        Li_Img_Freq__b4c01               = AnalogOut(default_value=-5.2499,     name='Li_Img_Freq__b4c01',               parent_device=NIBox4, connection='ao1')
        Li_MOT_AO_AM__b4c02              = AnalogOut(default_value=10,          name='Li_MOT_AO_AM__b4c02',              parent_device=NIBox4, connection='ao2')
        Li_MOT_Freq__b4c03               = AnalogOut(default_value=5.2844,      name='Li_MOT_Freq__b4c03',               parent_device=NIBox4, connection='ao3')
        Li_MRep_AO_FM__b4c04             = AnalogOut(default_value=0.4086,      name='Li_MRep_AO_FM__b4c04',             parent_device=NIBox4, connection='ao4')
        Li_Rep_AO_AM__b4c05              = AnalogOut(default_value=10,          name='Li_Rep_AO_AM__b4c05',              parent_device=NIBox4, connection='ao5')
        oTOP_AO_AM__b4c06                = AnalogOut(default_value=10,          name='oTOP_AO_AM__b4c06',                parent_device=NIBox4, connection='ao6')
        oTOP_FCarrier__b4c07             = AnalogOut(default_value=1.7999,      name='oTOP_FCarrier__b4c07',             parent_device=NIBox4, connection='ao7')
        oTOP_Int_Lock__b4c08             = AnalogOut(default_value=0.3,         name='oTOP_Int_Lock__b4c08',             parent_device=NIBox4, connection='ao8')
        oTOP_Mod_AM__b4c09               = AnalogOut(default_value=0,           name='oTOP_Mod_AM__b4c09',               parent_device=NIBox4, connection='ao9')
        Zeeman_C1__b4c10                 = AnalogOut(default_value=0,           name='Zeeman_C1__b4c10',                 parent_device=NIBox4, connection='ao10')
        Zeeman_C2__b4c11                 = AnalogOut(default_value=0,           name='Zeeman_C2__b4c11',                 parent_device=NIBox4, connection='ao11')
        Zeeman_C3__b4c12                 = AnalogOut(default_value=0,           name='Zeeman_C3__b4c12',                 parent_device=NIBox4, connection='ao12')
        Zeeman_C4__b4c13                 = AnalogOut(default_value=0,           name='Zeeman_C4__b4c13',                 parent_device=NIBox4, connection='ao13')
        Zeeman_C5__b4c14                 = AnalogOut(default_value=0,           name='Zeeman_C5__b4c14',                 parent_device=NIBox4, connection='ao14')
        b4c15                            = AnalogOut(default_value=0,           name='b4c15',                            parent_device=NIBox4, connection='ao15')
        b4c16                            = AnalogOut(default_value=0,           name='b4c16',                            parent_device=NIBox4, connection='ao16')
        b4c17                            = AnalogOut(default_value=0,           name='b4c17',                            parent_device=NIBox4, connection='ao17')
        b4c18                            = AnalogOut(default_value=0,           name='b4c18',                            parent_device=NIBox4, connection='ao18')
        b4c19                            = AnalogOut(default_value=0,           name='b4c19',                            parent_device=NIBox4, connection='ao19')
        b4c20                            = AnalogOut(default_value=0,           name='b4c20',                            parent_device=NIBox4, connection='ao20')
        b4c21                            = AnalogOut(default_value=0,           name='b4c21',                            parent_device=NIBox4, connection='ao21')
        b4c22                            = AnalogOut(default_value=0,           name='b4c22',                            parent_device=NIBox4, connection='ao22')
        b4c23                            = AnalogOut(default_value=0,           name='b4c23',                            parent_device=NIBox4, connection='ao23')
        b4c24                            = AnalogOut(default_value=0,           name='b4c24',                            parent_device=NIBox4, connection='ao24')
        b4c25                            = AnalogOut(default_value=0,           name='b4c25',                            parent_device=NIBox4, connection='ao25')
        b4c26                            = AnalogOut(default_value=0,           name='b4c26',                            parent_device=NIBox4, connection='ao26')
        b4c27                            = AnalogOut(default_value=0,           name='b4c27',                            parent_device=NIBox4, connection='ao27')
        b4c28                            = AnalogOut(default_value=0,           name='b4c28',                            parent_device=NIBox4, connection='ao28')
        b4c29                            = AnalogOut(default_value=0,           name='b4c29',                            parent_device=NIBox4, connection='ao29')
        b4c30                            = AnalogOut(default_value=0,           name='b4c30',                            parent_device=NIBox4, connection='ao30')
        b4c31                            = AnalogOut(default_value=0,           name='b4c31',                            parent_device=NIBox4, connection='ao31')   

        
        
if __name__ == '__main__':
    ConnectionTable()

    start()

    stop(1.0)
