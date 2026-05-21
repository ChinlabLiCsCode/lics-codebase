from labscript import start, stop, add_time_marker, DigitalOut, AnalogOut, VirtualAnalogOut, StaticAnalogOut
from labscript.remote import RemoteBLACS
from labscript_devices.NI_DAQmx.models.NI_PXIe_6536 import NI_PXIe_6536
from labscript_devices.NI_DAQmx.models.NI_PXIe_6738 import NI_PXIe_6738
from lics_labscript_devices.DP832.labscript_devices import DP832
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
        self.b1_c00__Bitter_Precision_Disable  = DigitalOut(default_value=1,          name='b1_c00__Bitter_Precision_Disable',  parent_device=NIBox1, connection='port0/line0')
        self.b1_c01__Cs_2DMOT_Shutter          = DigitalOut(default_value=0,          name='b1_c01__Cs_2DMOT_Shutter',          parent_device=NIBox1, connection='port0/line1')
        self.b1_c02__Cs_3DMOT_AO_Sw            = DigitalOut(default_value=1,          name='b1_c02__Cs_3DMOT_AO_Sw',            parent_device=NIBox1, connection='port0/line2')
        self.b1_c03__Cs_3DMOT_Shutter          = DigitalOut(default_value=0,          name='b1_c03__Cs_3DMOT_Shutter',          parent_device=NIBox1, connection='port0/line3')
        self.b1_c04__Cs_Andor_Trig             = DigitalOut(default_value=0,          name='b1_c04__Cs_Andor_Trig',             parent_device=NIBox1, connection='port0/line4')
        self.b1_c05__Cs_HFImg_AO_Sw            = DigitalOut(default_value=1,          name='b1_c05__Cs_HFImg_AO_Sw',            parent_device=NIBox1, connection='port0/line5')
        self.b1_c06__Cs_HFImg_Shutter          = DigitalOut(default_value=1,          name='b1_c06__Cs_HFImg_Shutter',          parent_device=NIBox1, connection='port0/line6')
        self.b1_c07__Cs_HImg_Shutter           = DigitalOut(default_value=0,          name='b1_c07__Cs_HImg_Shutter',           parent_device=NIBox1, connection='port0/line7')
        self.b1_c08__Cs_HOP_AO_Sw              = DigitalOut(default_value=1,          name='b1_c08__Cs_HOP_AO_Sw',              parent_device=NIBox1, connection='port1/line0')
        self.b1_c09__Cs_HOP_Shutter            = DigitalOut(default_value=0,          name='b1_c09__Cs_HOP_Shutter',            parent_device=NIBox1, connection='port1/line1')
        self.b1_c10__Cs_LFImg_AO_Sw            = DigitalOut(default_value=1,          name='b1_c10__Cs_LFImg_AO_Sw',            parent_device=NIBox1, connection='port1/line2', inverted=True)
        self.b1_c11__Cs_LFImg_Shutter          = DigitalOut(default_value=0,          name='b1_c11__Cs_LFImg_Shutter',          parent_device=NIBox1, connection='port1/line3')
        self.b1_c12__Cs_Rep_Shutter            = DigitalOut(default_value=1,          name='b1_c12__Cs_Rep_Shutter',            parent_device=NIBox1, connection='port1/line4')
        self.b1_c13__Cs_RSC_AO_Sw              = DigitalOut(default_value=1,          name='b1_c13__Cs_RSC_AO_Sw',              parent_device=NIBox1, connection='port1/line5')
        self.b1_c14__Cs_RSC_Shutter            = DigitalOut(default_value=0,          name='b1_c14__Cs_RSC_Shutter',            parent_device=NIBox1, connection='port1/line6')
        self.b1_c15__Cs_VImg_Shutter           = DigitalOut(default_value=1,          name='b1_c15__Cs_VImg_Shutter',           parent_device=NIBox1, connection='port1/line7')
        self.b1_c16__Cs_VRep_Shutter           = DigitalOut(default_value=0,          name='b1_c16__Cs_VRep_Shutter',           parent_device=NIBox1, connection='port2/line0')
        self.b1_c17__Cs_Zeeman_Shutter         = DigitalOut(default_value=0,          name='b1_c17__Cs_Zeeman_Shutter',         parent_device=NIBox1, connection='port2/line1')
        self.b1_c18__DMD_AO_FM                 = DigitalOut(default_value=0,          name='b1_c18__DMD_AO_FM',                 parent_device=NIBox1, connection='port2/line2')
        self.b1_c19__DMD_AO_Sw                 = DigitalOut(default_value=1,          name='b1_c19__DMD_AO_Sw',                 parent_device=NIBox1, connection='port2/line3')
        self.b1_c20__DMD_Movie_Trig            = DigitalOut(default_value=0,          name='b1_c20__DMD_Movie_Trig',            parent_device=NIBox1, connection='port2/line4')
        self.b1_c21__DMD_Shutter               = DigitalOut(default_value=1,          name='b1_c21__DMD_Shutter',               parent_device=NIBox1, connection='port2/line5')
        self.b1_c22__Dual_1064_AO_Sw           = DigitalOut(default_value=1,          name='b1_c22__Dual_1064_AO_Sw',           parent_device=NIBox1, connection='port2/line6')
        self.b1_c23__Dual_780_AO_Sw            = DigitalOut(default_value=1,          name='b1_c23__Dual_780_AO_Sw',            parent_device=NIBox1, connection='port2/line7')
        self.b1_c24__FF_Disable                = DigitalOut(default_value=0,          name='b1_c24__FF_Disable',                parent_device=NIBox1, connection='port3/line0')
        self.b1_c25__Li_Andor_Trig             = DigitalOut(default_value=0,          name='b1_c25__Li_Andor_Trig',             parent_device=NIBox1, connection='port3/line1')
        self.b1_c26__Li_EOM_AO_Sw              = DigitalOut(default_value=1,          name='b1_c26__Li_EOM_AO_Sw',              parent_device=NIBox1, connection='port3/line2', inverted=True)
        self.b1_c27__Li_EOM_H_Shutter          = DigitalOut(default_value=0,          name='b1_c27__Li_EOM_H_Shutter',          parent_device=NIBox1, connection='port3/line3')
        self.b1_c28__Li_HImg_Shutter           = DigitalOut(default_value=0,          name='b1_c28__Li_HImg_Shutter',           parent_device=NIBox1, connection='port3/line4')
        self.b1_c29__Li_Img_AO_Sw              = DigitalOut(default_value=1,          name='b1_c29__Li_Img_AO_Sw',              parent_device=NIBox1, connection='port3/line5')
        self.b1_c30__Li_MOT_AO_Sw              = DigitalOut(default_value=1,          name='b1_c30__Li_MOT_AO_Sw',              parent_device=NIBox1, connection='port3/line6')
        self.b1_c31__Li_MOT_Shutter            = DigitalOut(default_value=0,          name='b1_c31__Li_MOT_Shutter',            parent_device=NIBox1, connection='port3/line7')
        
        # Box2 digital outputs
        self.b2_c00__Li_Rep_AO_Sw              = DigitalOut(default_value=1,          name='b2_c00__Li_Rep_AO_Sw',              parent_device=NIBox2, connection='port0/line0')
        self.b2_c01__Li_Rep_Shutter            = DigitalOut(default_value=0,          name='b2_c01__Li_Rep_Shutter',            parent_device=NIBox2, connection='port0/line1')
        self.b2_c02__Li_VImg_Shutter           = DigitalOut(default_value=1,          name='b2_c02__Li_VImg_Shutter',           parent_device=NIBox2, connection='port0/line2')
        self.b2_c03__Li_Zeeman_Shutter         = DigitalOut(default_value=0,          name='b2_c03__Li_Zeeman_Shutter',         parent_device=NIBox2, connection='port0/line3')
        self.b2_c04__MW_Trig                   = DigitalOut(default_value=0,          name='b2_c04__MW_Trig',                   parent_device=NIBox2, connection='port0/line4')
        self.b2_c05__oTOP_Pos_Lock_Enable      = DigitalOut(default_value=0,          name='b2_c05__oTOP_Pos_Lock_Enable',      parent_device=NIBox2, connection='port0/line5')
        self.b2_c06__Pixelfly_Shutter          = DigitalOut(default_value=1,          name='b2_c06__Pixelfly_Shutter',          parent_device=NIBox2, connection='port0/line6')
        self.b2_c07__Pixelfly_Trig             = DigitalOut(default_value=0,          name='b2_c07__Pixelfly_Trig',             parent_device=NIBox2, connection='port0/line7')
        self.b2_c08__Scope_Trig                = DigitalOut(default_value=0,          name='b2_c08__Scope_Trig',                parent_device=NIBox2, connection='port1/line0')
        self.b2_c09__Spec_Analyzer_Trig        = DigitalOut(default_value=0,          name='b2_c09__Spec_Analyzer_Trig',        parent_device=NIBox2, connection='port1/line1')
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
        self.b3_c00__Aerotech_Control          = AnalogOut(default_value=0,           name='b3_c00__Aerotech_Control',          parent_device=NIBox3, connection='ao0')
        self.b3_c01__BFL_AO_Sw                 = AnalogOut(default_value=5,           name='b3_c01__BFL_AO_Sw',                 parent_device=NIBox3, connection='ao1')
        self.b3_c02__BFL_Int_Lock              = AnalogOut(default_value=0.1,         name='b3_c02__BFL_Int_Lock',              parent_device=NIBox3, connection='ao2')
        self.b3_c03__Bias_X_minus              = AnalogOut(default_value=0,           name='b3_c03__Bias_X_minus',                 parent_device=NIBox3, connection='ao3')
        self.b3_c04__Bias_X_plus               = AnalogOut(default_value=0,           name='b3_c04__Bias_X_plus',                 parent_device=NIBox3, connection='ao4')
        self.b3_c05__Bias_Y_minus              = AnalogOut(default_value=0,           name='b3_c05__Bias_Y_minus',                 parent_device=NIBox3, connection='ao5')
        self.b3_c06__Bias_Y_plus               = AnalogOut(default_value=0,           name='b3_c06__Bias_Y_plus',                 parent_device=NIBox3, connection='ao6')
        self.b3_c07__Bias_Z_minus              = AnalogOut(default_value=0,           name='b3_c07__Bias_Z_minus',                 parent_device=NIBox3, connection='ao7')
        self.b3_c08__Bias_Z_plus               = AnalogOut(default_value=0,           name='b3_c08__Bias_Z_plus',                 parent_device=NIBox3, connection='ao8')
        self.b3_c09__Bitter_AH_Upper_FF        = AnalogOut(default_value=0,           name='b3_c09__Bitter_AH_Upper_FF',        parent_device=NIBox3, connection='ao9')
        self.b3_c10__Bitter_HH_Upper_FF        = AnalogOut(default_value=0,           name='b3_c10__Bitter_HH_Upper_FF',        parent_device=NIBox3, connection='ao10')
        self.b3_c11__Bitter_IServo_FB_Sw       = AnalogOut(default_value=0,           name='b3_c11__Bitter_IServo_FB_Sw',       parent_device=NIBox3, connection='ao11')
        self.b3_c12__Bitter_Lower_CC           = AnalogOut(default_value=1,           name='b3_c12__Bitter_Lower_CC',           parent_device=NIBox3, connection='ao12')
        self.b3_c13__Bitter_Lower_CV           = AnalogOut(default_value=1.5,         name='b3_c13__Bitter_Lower_CV',           parent_device=NIBox3, connection='ao13')
        self.b3_c14__Bitter_Lower_FF           = AnalogOut(default_value=0,           name='b3_c14__Bitter_Lower_FF',           parent_device=NIBox3, connection='ao14')
        self.b3_c15__Bitter_Upper_AH_Sw        = AnalogOut(default_value=5,           name='b3_c15__Bitter_Upper_AH_Sw',        parent_device=NIBox3, connection='ao15')
        self.b3_c16__Bitter_Upper_CC           = AnalogOut(default_value=1,           name='b3_c16__Bitter_Upper_CC',           parent_device=NIBox3, connection='ao16')
        self.b3_c17__Bitter_Upper_CV           = AnalogOut(default_value=2,           name='b3_c17__Bitter_Upper_CV',           parent_device=NIBox3, connection='ao17')
        self.b3_c18__Bitter_Upper_HH_Sw        = AnalogOut(default_value=0,           name='b3_c18__Bitter_Upper_HH_Sw',        parent_device=NIBox3, connection='ao18')
        self.b3_c19__Bitter_V_Lower            = AnalogOut(default_value=0,           name='b3_c19__Bitter_V_Lower',               parent_device=NIBox3, connection='ao19')
        self.b3_c20__Bitter_V_Upper            = AnalogOut(default_value=0,           name='b3_c20__Bitter_V_Upper',               parent_device=NIBox3, connection='ao20')
        self.b3_c21__Cs_3DMOT_AO_AM            = AnalogOut(default_value=2.3,         name='b3_c21__Cs_3DMOT_AO_AM',            parent_device=NIBox3, connection='ao21')
        self.b3_c22__CS_HFImg_Freq             = AnalogOut(default_value=-10,         name='b3_c22__CS_HFImg_Freq',             parent_device=NIBox3, connection='ao22')
        self.b3c23                            = AnalogOut(default_value=0,           name='b3c23',                            parent_device=NIBox3, connection='ao23')
        self.b3_c24__Cs_MOT_Freq               = AnalogOut(default_value=-7.15,       name='b3_c24__Cs_MOT_Freq',               parent_device=NIBox3, connection='ao24')
        self.b3_c25__Cs_Rep_AO_AM              = AnalogOut(default_value=5,           name='b3_c25__Cs_Rep_AO_AM',              parent_device=NIBox3, connection='ao25')
        self.b3_c26__Cs_Rep_Freq               = AnalogOut(default_value=6.51,        name='b3_c26__Cs_Rep_Freq',               parent_device=NIBox3, connection='ao26')
        self.b3_c27__Cs_RSC_AO_AM              = AnalogOut(default_value=5,           name='b3_c27__Cs_RSC_AO_AM',              parent_device=NIBox3, connection='ao27')
        self.b3_c28__Cs_VImg_AO_AM             = AnalogOut(default_value=5,           name='b3_c28__Cs_VImg_AO_AM',             parent_device=NIBox3, connection='ao28')
        self.b3_c29__DMD_AO_AM                 = AnalogOut(default_value=3.8,         name='b3_c29__DMD_AO_AM',                 parent_device=NIBox3, connection='ao29')
        self.b3_c30__Dual_780_Int_Lock         = AnalogOut(default_value=2.5,         name='b3_c30__Dual_780_Int_Lock',         parent_device=NIBox3, connection='ao30')
        self.b3_c31__Li_EOM_Freq               = AnalogOut(default_value=-4.5,        name='b3_c31__Li_EOM_Freq',               parent_device=NIBox3, connection='ao31')
        
        # Box4 analog outputs
        self.b4_c00__Li_Img_AO_AM              = AnalogOut(default_value=10,          name='b4_c00__Li_Img_AO_AM',              parent_device=NIBox4, connection='ao0')
        self.b4_c01__Li_Img_Freq               = AnalogOut(default_value=-5.2499,     name='b4_c01__Li_Img_Freq',               parent_device=NIBox4, connection='ao1')
        self.b4_c02__Li_MOT_AO_AM              = AnalogOut(default_value=10,          name='b4_c02__Li_MOT_AO_AM',              parent_device=NIBox4, connection='ao2')
        self.b4_c03__Li_MOT_Freq               = AnalogOut(default_value=5.2844,      name='b4_c03__Li_MOT_Freq',               parent_device=NIBox4, connection='ao3')
        self.b4_c04__Li_MRep_AO_FM             = AnalogOut(default_value=0.4086,      name='b4_c04__Li_MRep_AO_FM',             parent_device=NIBox4, connection='ao4')
        self.b4_c05__Li_Rep_AO_AM              = AnalogOut(default_value=10,          name='b4_c05__Li_Rep_AO_AM',              parent_device=NIBox4, connection='ao5')
        self.b4_c06__oTOP_AO_AM                = AnalogOut(default_value=10,          name='b4_c06__oTOP_AO_AM',                parent_device=NIBox4, connection='ao6')
        self.b4_c07__oTOP_FCarrier             = AnalogOut(default_value=1.7999,      name='b4_c07__oTOP_FCarrier',             parent_device=NIBox4, connection='ao7')
        self.b4_c08__oTOP_Int_Lock             = AnalogOut(default_value=0.3,         name='b4_c08__oTOP_Int_Lock',             parent_device=NIBox4, connection='ao8')
        self.b4_c09__oTOP_Mod_AM               = AnalogOut(default_value=0,           name='b4_c09__oTOP_Mod_AM',               parent_device=NIBox4, connection='ao9')
        self.b4_c10__Zeeman_C1                 = AnalogOut(default_value=0,           name='b4_c10__Zeeman_C1',                 parent_device=NIBox4, connection='ao10')
        self.b4_c11__Zeeman_C2                 = AnalogOut(default_value=0,           name='b4_c11__Zeeman_C2',                 parent_device=NIBox4, connection='ao11')
        self.b4_c12__Zeeman_C3                 = AnalogOut(default_value=0,           name='b4_c12__Zeeman_C3',                 parent_device=NIBox4, connection='ao12')
        self.b4_c13__Zeeman_C4                 = AnalogOut(default_value=0,           name='b4_c13__Zeeman_C4',                 parent_device=NIBox4, connection='ao13')
        self.b4_c14__Zeeman_C5                 = AnalogOut(default_value=0,           name='b4_c14__Zeeman_C5',                 parent_device=NIBox4, connection='ao14')
        self.Cs_EOM_Freq_b4c15                = AnalogOut(default_value=9,           name='b4_c15__Cs_EOM_Freq',               parent_device=NIBox4, connection='ao15')
        self.b4_c16__Dual_1064_Int_Lock        = AnalogOut(default_value=4,           name='b4_c16__Dual_1064_Int_Lock',        parent_device=NIBox4, connection='ao16')
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

        # set up virtual channels for HH/AH control over magnetic fields
        # check Onenote/Control PC/Control PC restart: be careful!! for documentation on these values
        _BITTER_VLOWER_OFFSET = 0.003
        _BITTER_VUPPER_OFFSET = -0.00274
        _BITTER_CONVERSION = lambda hh, ah: (hh + ah + _BITTER_VLOWER_OFFSET, # lower
                                             hh - ah + _BITTER_VUPPER_OFFSET) # upper
        # build bitter coil virtual channel groups
        self.Bitter_V_HH, self.Bitter_V_AH = VirtualAnalogOut(_BITTER_CONVERSION, 
                                                              self.b3_c19__Bitter_V_Lower, 
                                                              self.b3_c20__Bitter_V_Upper)
        
        # shim offsets and AH HH matrices are defined here
        _SHIM_XMINUS_OFFSET = 1
        _SHIM_XPLUS_OFFSET = -1
        _SHIM_YMINUS_OFFSET = 0.3
        _SHIM_YPLUS_OFFSET = -1.8
        _SHIM_ZMINUS_OFFSET = 0.1
        _SHIM_ZPLUS_OFFSET = -0.1
        _SHIMX_CONVERSION = lambda hh, ah: (-0.5*hh + 0.5*ah + _SHIM_XMINUS_OFFSET, # minus
                                            0.5*hh + 0.5*ah + _SHIM_XPLUS_OFFSET)   # plus
        _SHIMY_CONVERSION = lambda hh, ah: (-0.5*hh + 0.5*ah + _SHIM_YMINUS_OFFSET, # minus
                                            0.5*hh + 0.5*ah + _SHIM_YPLUS_OFFSET)   # plus
        _SHIMZ_CONVERSION = lambda hh, ah: (-0.5*hh + 0.5*ah + _SHIM_ZMINUS_OFFSET, # minus
                                            0.5*hh + 0.5*ah + _SHIM_ZPLUS_OFFSET)   # plus

        # build shim virtual channel groups
        self.Bias_X_HH, self.Bias_X_AH = VirtualAnalogOut(_SHIMX_CONVERSION,
                                                          self.b3_c03__Bias_X_minus,
                                                          self.b3_c04__Bias_X_plus)
        self.Bias_Y_HH, self.Bias_Y_AH = VirtualAnalogOut(_SHIMY_CONVERSION,
                                                          self.b3_c05__Bias_Y_minus,
                                                          self.b3_c06__Bias_Y_plus)
        self.Bias_Z_HH, self.Bias_Z_AH = VirtualAnalogOut(_SHIMZ_CONVERSION,
                                                          self.b3_c07__Bias_Z_minus,
                                                          self.b3_c08__Bias_Z_plus)
        



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
