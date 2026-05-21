from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

SLOW_FREQ = 1e3   # 1 ms per edge
FAST_FREQ = 50e3  # 20 us per edge

# Cs MOT Zeeman currents
ZEEMAN_C1_CS = 0
ZEEMAN_C2_CS = 0.9
ZEEMAN_C3_CS = 0.4
ZEEMAN_C4_CS = 0.1
ZEEMAN_C5_CS = 0.9

# Li MOT Zeeman currents
ZEEMAN_C1_LI = 5
ZEEMAN_C2_LI = 7
ZEEMAN_C3_LI = 7
ZEEMAN_C4_LI = 8.5
ZEEMAN_C5_LI = 1.6

# header
# ------
# version:4
# timing:100
# never ramp:0
# always_ramp:1
# number of channels:126
# number of procedures:39

# ch no	name						  init val	analog?	new labscript name
# -----	----						  --------	-------	------------------
# 000	3.0_N_V_AH              	    0.1883		1	ct.Bitter_V_AH
# 001	3.1_Dual_1064_Int_Lock  	    3.9999		1	ct.Dual_1064_Int_Lock__b4c16
# 002	3.2_Li_Img_Freq         	   -5.2499		1	ct.Li_Img_Freq__b4c01
# 003	3.3_lower_FF            	    0.0000		1	ct.Bitter_Lower_FF__b3c14
# 004	3.4_oTOP_fcarrier       	    1.7999		1	ct.oTOP_FCarrier__b4c07
# 005	3.5_AH_upper_FF         	    0.0000		1	ct.Bitter_AH_Upper_FF__b3c09
# 006	3.6_HH_upper_FF         	    0.0000		1	ct.Bitter_HH_Upper_FF__b3c10
# 007	3.7_N_V_HH              	   -0.0183		1	ct.Bitter_V_HH
# 008	2.0_Dual_780nm_Int_Lock 	    2.5000		1	# no new channel
# 009	2.1_CS_Rep_AO_AM        	    5.0000		1	# no new channel
# 010	2.2_                    	    0.0000		1	# no new channel
# 011	2.3_Li_MRep_AO_FM       	    0.4086		1	# no new channel
# 012	2.4_                    	    0.0000		1	# no new channel
# 013	2.5_                    	    0.0000		1	# no new channel
# 014	2.6_V_HH                	   -0.0183		1	# no new channel
# 015	2.7_V_AH                	    0.1883		1	# no new channel
# 016	7.0_oTOP_Int_lok        	    0.3000		1	# no new channel
# 017	7.1_CS_Rep_AO_AM        	    5.0000		1	# no new channel
# 018	7.2_Cs_VHF_AO_AM        	    0.4001		1	# no new channel
# 019	7.3_oTOP_AO_AM          	   10.0000		1	# no new channel
# 020	7.4_oTOP_mod_AM         	    0.0000		1	# no new channel
# 021	7.5_Dual_1064_Int_Lock  	    3.9999		1	# no new channel
# 022	7.6_oTOP_fcarrier       	    1.7999		1	# no new channel
# 023	7.7_N_Cs_MOT_Freq       	   -7.1500		1	# no new channel
# 024	1.3_Li_Img_AO_Sw        	    5.0000		0	ct.Li_Img_AO_Sw__b1c29
# 025	1.4_Cs_3DMOT_AO_Sw      	    5.0000		0	# no new channel
# 026	1.5_DMD_AO_Sw           	    5.0000		0	ct.DMD_AO_Sw__b1c19
# 027	1.6_AndorCCD_Trig       	    0.0000		0	ct.Cs_Andor_Trig__b1c04
# 028	1.7_Li_EOM_AO_Sw        	    5.0000		0	ct.Li_EOM_AO_Sw__b1c26
# 029	1.8_Cs_2DMOT_Shutter    	    0.0000		0	# no new channel
# 030	1.9_DMD_AO_FM           	    0.0000		0	ct.DMD_AO_FM__b1c18
# 031	1.10_Cs_Oneshot_Bypass  	    0.0000		0	# no new channel
# 032	1.11_Li_MOT_AO_Sw       	    5.0000		0	ct.Li_MOT_AO_Sw__b1c30
# 033	1.12_Li_Rep_AO_Sw       	    5.0000		0	ct.Li_Rep_AO_Sw__b2c00
# 034	1.13_Li_Rep_Shutter     	    5.0000		0	ct.Li_Rep_Shutter__b2c01
# 035	1.14_Li_MOT_Shutter     	    5.0000		0	ct.Li_MOT_Shutter__b1c31
# 036	1.15_Li_V_Img_Shutter   	    0.0000		0	ct.Li_VImg_Shutter__b2c02
# 037	1.16_Li_Zeeman_Shutter  	    5.0000		0	ct.Li_Zeeman_Shutter__b2c03
# 038	1.17_Cs_H_Img_Shutter   	    0.0000		0	# no new channel
# 039	1.18_Li_EOM_H_Shutter   	    0.0000		0	ct.Li_EOM_H_Shutter__b1c27
# 040	1.19_Cs_ZM_shutter      	    5.0000		0	# no new channel
# 041	1.20_MW_pulse_SW        	    0.0000		0	ct.MW_Trig__b2c04
# 042	1.21_pixelfly trigger   	    0.0000		0	ct.Pixelfly_Trig__b2c07
# 043	1.22_MW_INCR_UP         	    0.0000		0	# no new channel
# 044	1.23_CS_EOM_SW          	    5.0000		0	# no new channel
# 045	1.24_Cs_RSC_AO_SW       	    5.0000		0	# no new channel
# 046	1.25_ZDT_AO_SW          	    5.0000		0	# no new channel
# 047	1.26_MW_SWEEP           	    5.0000		0	# no new channel
# 048	1.27_Real_CS_RSC_AO_SW  	    5.0000		0	ct.Cs_RSC_AO_Sw__b1c13
# 049	1.28_Li_H_Img_shu       	    0.0000		0	ct.Li_HImg_Shutter__b1c28
# 050	1.29_Real_CS_RSC_SHU    	    0.0000		0	ct.Cs_RSC_Shutter__b1c14
# 051	1.30_test trigger       	    0.0000		0	ct.Scope_Trig__b2c08
# 052	1.31_Cs_Li_Zeswitch     	    5.0000		0	(Zeeman logic — see section 8b of conversion note)
# 053	1.32_ZCurrents          	    5.0000		0	(Zeeman logic — see section 8b of conversion note)
# 054	6.0                     	    5.0000		0	# no new channel
# 055	6.1_Mod_AO_Switch       	    5.0000		0	# no new channel
# 056	6.2_XDT_AO_SW           	    5.0000		0	# no new channel
# 057	6.3_Cs_HF_AO_Sw         	    5.0000		0	ct.Cs_HFImg_AO_Sw__b1c05
# 058	6.4_N_V_Rep_Shutter     	    5.0000		0	ct.Cs_VRep_Shutter__b1c16
# 059	6.5_N_Cs_Rep_Shutter    	    5.0000		0	ct.Cs_Rep_Shutter__b1c12
# 060	6.6_N_Cs_V_Img_Shutter  	    0.0000		0	ct.Cs_VImg_Shutter__b1c15
# 061	6.7_N_Cs_H_Img_Shutter  	    0.0000		0	ct.Cs_HImg_Shutter__b1c07
# 062	6.8_Dual_780nm_SW       	    5.0000		0	ct.Dual_780_AO_Sw__b1c23
# 063	6.9_Dual_1064nm_SW      	    5.0000		0	ct.Dual_1064_AO_Sw__b1c22
# 064	6.10                    	    0.0000		0	# no new channel
# 065	6.11_N_Cs_HF_Img_Shutter	    0.0000		0	ct.Cs_HFImg_Shutter__b1c06
# 066	6.12_N_Cs_LF_Img_Shutter	    5.0000		0	ct.Cs_LFImg_Shutter__b1c11
# 067	6.13_N_Cs_Z_Shutter     	    5.0000		0	ct.Cs_Zeeman_Shutter__b1c17
# 068	6.14_N_Cs_2D_MOT_Shutter	    5.0000		0	ct.Cs_2DMOT_Shutter__b1c01
# 069	6.15_N_Cs_3D_MOT_Shutter	    5.0000		0	ct.Cs_3DMOT_Shutter__b1c03
# 070	6.16                    	    0.0000		0	# no new channel
# 071	6.17_Spec_Analysis_Trig 	    0.0000		0	ct.Spec_Analyzer_Trig__b2c09
# 072	6.18                    	    0.0000		0	# no new channel
# 073	6.19_N_Cs_3D_SW         	    5.0000		0	ct.Cs_3DMOT_AO_Sw__b1c02
# 074	6.20_Cs_LF_Img_AO_Sw    	    5.0000		0	ct.Cs_LFImg_AO_Sw__b1c10
# 075	6.21_FF_Disable         	    0.0000		0	ct.FF_Disable__b1c24
# 076	6.22                    	    0.0000		0	# no new channel
# 077	6.23_N_OP_AO_SW         	    5.0000		0	ct.Cs_HOP_AO_Sw__b1c08
# 078	6.24                    	    0.0000		0	# no new channel
# 079	6.25_DMD_Shutter        	    0.0000		0	ct.DMD_Shutter__b1c21
# 080	6.26_N_CsOP_Shut_H      	    5.0000		0	ct.Cs_HOP_Shutter__b1c09
# 081	6.27_DMD_Movie_Trig     	    0.0000		0	ct.DMD_Movie_Trig__b1c20
# 082	6.28                    	    0.0000		0	# no new channel
# 083	6.29_oTOP_Pos_Lock_Enabl	    0.0000		0	ct.oTOP_Pos_Lock_Enable__b2c05
# 084	6.30_Li_Oneshot_Bypass  	    0.0000		0	# no new channel
# 085	6.31_B_Precision_Disable	    5.0000		0	ct.Bitter_Precision_Disable__b1c00
# 086	4.0_Li_MOT_AO_AM        	   10.0000		1	ct.Li_MOT_AO_AM__b4c02
# 087	4.1_Li_Rep_AO_AM        	   10.0000		1	ct.Li_Rep_AO_AM__b4c05
# 088	4.2_Dual_780_AO_AM      	   10.0000		1	# no new channel
# 089	4.3_Dual_1064_AO_AM     	   10.0000		1	# no new channel
# 090	4.4_DMD_AO_AM           	    3.8000		1	ct.DMD_AO_AM__b3c29
# 091	4.5_N_Cs_Repump_Freq    	    6.5100		1	ct.Cs_Rep_Freq__b3c26
# 092	4.6_Li_MRep_AO_FM       	    0.4086		1	ct.Li_MRep_AO_FM__b4c04
# 093	4.7_Li_Img_AO_AM        	   10.0000		1	ct.Li_Img_AO_AM__b4c00
# 094	5.8_Dual_780nm_Int_Lock 	    2.5000		1	ct.Dual_780_Int_Lock__b3c30
# 095	5.9_Cs_LF_Img_AO_AM     	   10.0000		1	# no new channel
# 096	5.10_CS_HF_Img_Freq     	  -10.0000		1	ct.CS_HFImg_Freq__b3c22
# 097	5.11_BFL_AO_AM          	   10.0000		1	# no new channel
# 098	5.12_Bias_1/2_HH_x      	   -1.0000		1	ct.Bias_X_HH
# 099	5.13_Bias_1/2_AH_-x     	    1.0000		1	ct.Bias_X_AH
# 100	5.14_Bias_3/4_AH_-y     	    0.0000		1	ct.Bias_Y_AH
# 101	5.15_Bias_3/4_HH_y      	    1.0000		1	ct.Bias_Y_HH
# 102	5.16_Bias_5/6_AH_z      	   -1.0000		1	ct.Bias_Z_AH
# 103	5.17_Bias_5/6_HH_-z     	   -6.0000		1	ct.Bias_Z_HH
# 104	5.18_COIL_BOT_CC        	    1.0000		1	ct.Bitter_Lower_CC__b3c12
# 105	5.19_COIL_TOP_CV        	    2.0000		1	ct.Bitter_Upper_CV__b3c17
# 106	5.20_COIL_TOP_CC        	    1.0000		1	ct.Bitter_Upper_CC__b3c16
# 107	5.21_COIL_BOT_CV        	    1.5000		1	ct.Bitter_Lower_CV__b3c13
# 108	5.22_BFL_AO_SW          	    5.0000		1	ct.BFL_AO_Sw__b3c01
# 109	5.23_COIL_TOP_AH        	    5.0000		1	ct.Bitter_Upper_AH_Sw__b3c15
# 110	5.24_COIL_TOP_HH        	    0.0000		1	ct.Bitter_Upper_HH_Sw__b3c18
# 111	5.25_N_BFL_INT_LOCK     	    0.1000		1	ct.BFL_Int_Lock__b3c02
# 112	5.26_H_Pixelfly_Shutter 	    5.0000		1	ct.Pixelfly_Shutter__b2c06
# 113	5.27_IServo_FB_Switch   	    0.0000		1	ct.Bitter_IServo_FB_Sw__b3c11
# 114	5.28_aerotech_trigger   	    0.0000		1	ct.Aerotech_Control__b3c00
# 115	5.29_Li_MOT_Freq        	    5.2844		1	ct.Li_MOT_Freq__b4c03
# 116	5.30_Cs_EOM_Freq        	    9.0000		1	ct.Cs_EOM_Freq_b4c15
# 117	5.31_Cs_3D_AO_AM        	    2.3000		1	ct.Cs_3DMOT_AO_AM__b3c21
# 118	8.0_oTOP_Int_lok        	    0.3000		1	ct.oTOP_Int_Lock__b4c08
# 119	8.1_CS_Rep_AO_AM        	    5.0000		1	ct.Cs_Rep_AO_AM__b3c25
# 120	8.2_Cs_VHF_AO_AM        	    5.0000		1	ct.Cs_VImg_AO_AM__b3c28
# 121	8.3_oTOP_AO_AM          	   10.0000		1	ct.oTOP_AO_AM__b4c06
# 122	8.4_oTOP_mod_AM         	    0.0000		1	ct.oTOP_Mod_AM__b4c09
# 123	8.5_Li_EOM_Freq         	   -4.5000		1	ct.Li_EOM_Freq__b3c31
# 124	8.6_Cs_RSC_AO_AM        	    5.0000		1	ct.Cs_RSC_AO_AM__b3c27
# 125	8.7_N_Cs_MOT_Freq       	   -7.1500		1	ct.Cs_MOT_Freq__b3c24

# proc no	name							  time (ms)e-3	enabled
# -------	----							  ------------	------
# 000		Cs_MOT_Loading          	11700e-3		1
# 001		Cs_Molasses_Cooling     	15495e-3		1
# 002		Cs_H_Imaging            	code_65501/1e3		0
# 003		Cs_RSC1                 	15500e-3		1
# 004		Aerotech_return         	15600e-3		1
# 005		Dual_Imaging_H          	code_65501/1e3		0
# 006		Dual_Imaging_V          	code_65501/1e3		1
# 007		FB_Bias_field           	15600e-3		1
# 008		Cs_Dark                 	15534e-3		1
# 009		Li_HF_V_Imaging         	code_65501/1e3		0
# 010		Cs_Evaporation          	15600e-3		1
# 011		Spare                   	29600e-3		1
# 012		Li_Feshbach             	10000e-3		1
# 013		Dual_Evap               	27700e-3		1
# 014		Li_H_Imaging            	code_65501/1e3		0
# 015		Li_V_Imaging            	code_65501/1e3		0
# 016		Cs_Levitation1          	15532e-3		1
# 017		Li_Evaporation          	10000e-3		1
# 018		Li_Dark                 	10000e-3		1
# 019		Cs_V_Imaging            	code_65501/1e3		0
# 020		Li_CMOT                 	10000e-3		1
# 021		Cs_CMOT                 	15445e-3		1
# 022		Li_MOT_Loading          	1e-3		1
# 023		True_TOF                	code_65500/1e3		1
# 024		Li_Killing              	24600e-3		1
# 025		Low_Field_BEC_Field     	7519e-3		0
# 026		FB_Bias_Field_off       	code_65502/1e3		0
# 027		FB_Field_Gentle_off     	code_65502/1e3		1
# 028		Unlevitation            	21600e-3		0
# 029		Cs_HF_H_Imaging         	code_65501/1e3		0
# 030		Cs_HF_V_Imaging         	code_65501/1e3		0
# 031		test_trigger            	code_65501/1e3		0
# 032		Cs_molasses_dark        	12500e-3		0
# 033		Dual_Color_Combine      	24700e-3		1
# 034		Li_Img_Freq_Ramp_Down   	code_65501/1e3		1
# 035		coil_cool_down          	code_65502/1e3		1
# 036		MW_Calibration_load     	18800e-3		0
# 037		MW_Calibration_Molasses 	21850e-3		0
# 038		MW_Calibration_Trap     	21887e-3		0

code_65500 = 29700.5000
#		cur:29700.5000  start:19700.0000  stop:30712.0000  step:    0.0000  every:1  next:0
code_65501 = 29700.0000
#		cur:29700.0000  start:19700.0000  stop:30712.0000  step:    0.0000  every:1  next:0
code_65502 = 29810.0000
#		cur:29810.0000  start:20210.0000  stop:33210.0000  step:    0.0000  every:1  next:0
code_65503 = 4.4003
#		cur:    4.4003  start:   -0.8936  stop:   10.0000  step:    0.0000  every:1  next:0
code_65504 = 1300.0000
#		cur: 1300.0000  start:    0.0000  stop:15000.0000  step:    0.0000  every:1  next:0
code_65505 = 5.0000
#		cur:    5.0000  start:    0.0000  stop:    6.0000  step:    0.0000  every:1  next:0
code_65506 = 5.0000
#		cur:    5.0000  start:    0.0000  stop:    6.0000  step:    0.0000  every:1  next:0
code_65507 = -2.3050
#		cur:   -2.3050  start:   -2.3600  stop:   -2.2500  step:    0.0000  every:1  next:0
code_65508 = -7.9350
#		cur:   -7.9350  start:   -7.9600  stop:   -7.8990  step:    0.0000  every:1  next:0
code_65509 = -0.1822
#		cur:   -0.1822  start:   -0.1000  stop:    2.2000  step:    0.0000  every:1  next:0
code_65510 = 0.0000
#		cur:    0.0000  start:    0.0000  stop:    6.0000  step:    0.0000  every:1  next:0
code_65511 = -5.4500
#		cur:   -5.4500  start:   -5.9000  stop:   -4.9900  step:    0.0000  every:1  next:0
code_65512 = 0.0000
#		cur:    0.0000  start:    0.0000  stop:    0.0000  step:    0.0000  every:1  next:0

if __name__ == '__main__':
    ct = ConnectionTable()

    start()

    # set all channels to LabVIEW init values
    t = 10e-6
    ct.Bitter_V_AH.constant(t, 0.188293)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 3.99994)
    ct.Li_Img_Freq__b4c01.constant(t, -5.24994)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.oTOP_FCarrier__b4c07.constant(t, 1.79993)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_V_HH.constant(t, -0.0183105)
    ct.Li_Img_AO_Sw__b1c29.go_high(t)
    ct.DMD_AO_Sw__b1c19.go_high(t)
    ct.Cs_Andor_Trig__b1c04.go_low(t)
    ct.Li_EOM_AO_Sw__b1c26.go_high(t)
    ct.DMD_AO_FM__b1c18.go_low(t)
    ct.Li_MOT_AO_Sw__b1c30.go_high(t)
    ct.Li_Rep_AO_Sw__b2c00.go_high(t)
    ct.Li_Rep_Shutter__b2c01.go_high(t)
    ct.Li_MOT_Shutter__b1c31.go_high(t)
    ct.Li_VImg_Shutter__b2c02.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_high(t)
    ct.Li_EOM_H_Shutter__b1c27.go_low(t)
    ct.MW_Trig__b2c04.go_low(t)
    ct.Pixelfly_Trig__b2c07.go_low(t)
    ct.Cs_RSC_AO_Sw__b1c13.go_high(t)
    ct.Li_HImg_Shutter__b1c28.go_low(t)
    ct.Cs_RSC_Shutter__b1c14.go_low(t)
    ct.Scope_Trig__b2c08.go_low(t)
    ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    ct.Cs_VRep_Shutter__b1c16.go_high(t)
    ct.Cs_Rep_Shutter__b1c12.go_high(t)
    ct.Cs_VImg_Shutter__b1c15.go_low(t)
    ct.Cs_HImg_Shutter__b1c07.go_low(t)
    ct.Dual_780_AO_Sw__b1c23.go_high(t)
    ct.Dual_1064_AO_Sw__b1c22.go_high(t)
    ct.Cs_HFImg_Shutter__b1c06.go_low(t)
    ct.Cs_LFImg_Shutter__b1c11.go_high(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Spec_Analyzer_Trig__b2c09.go_low(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    ct.FF_Disable__b1c24.go_low(t)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t)
    ct.DMD_Shutter__b1c21.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_high(t)
    ct.DMD_Movie_Trig__b1c20.go_low(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    ct.Bitter_Precision_Disable__b1c00.go_high(t)
    ct.Li_MOT_AO_AM__b4c02.constant(t, 10)
    ct.Li_Rep_AO_AM__b4c05.constant(t, 10)
    ct.DMD_AO_AM__b3c29.constant(t, 3.8)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.51)
    ct.Li_MRep_AO_FM__b4c04.constant(t, 0.40863)
    ct.Li_Img_AO_AM__b4c00.constant(t, 10)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 2.5)
    ct.CS_HFImg_Freq__b3c22.constant(t, -10)
    ct.Bias_X_HH.constant(t, -1)
    ct.Bias_X_AH.constant(t, 1)
    ct.Bias_Y_AH.constant(t, 0)
    ct.Bias_Y_HH.constant(t, 1)
    ct.Bias_Z_AH.constant(t, -1)
    ct.Bias_Z_HH.constant(t, -6)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.5)
    ct.BFL_AO_Sw__b3c01.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.BFL_Int_Lock__b3c02.constant(t, 0.1)
    ct.Pixelfly_Shutter__b2c06.go_high(t)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    ct.Aerotech_Control__b3c00.constant(t, 0)
    ct.Li_MOT_Freq__b4c03.constant(t, 5.28442)
    ct.Cs_EOM_Freq_b4c15.constant(t, 9)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.3)
    ct.oTOP_Int_Lock__b4c08.constant(t, 0.3)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, 5)
    ct.oTOP_AO_AM__b4c06.constant(t, 10)
    ct.oTOP_Mod_AM__b4c09.constant(t, 0)
    ct.Li_EOM_Freq__b3c31.constant(t, -4.5)
    ct.Cs_RSC_AO_AM__b3c27.constant(t, 5)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.15)

    # pause for line trigger at 1 us, with a timeout of 100 ms
    add_time_marker(t, 'Waiting for line trigger')
    wait('line_trigger', t, timeout=0.1)

    # procedure 000: Cs_MOT_Loading
    t = 11700e-3
    add_time_marker(t, 'Cs_MOT_Loading')
    # 6.1_Mod_AO_Switch: 0 JUMP — no new channel
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.30011)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.21008)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.51001)
    # 1.32_ZCurrents → 5 (Zeeman: 1.31=5, 1.32=5)
    ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    # 1.31_Cs_Li_Zeswitch → 5 (Zeeman: 1.31=5, 1.32=5)
    ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    ct.Li_Rep_Shutter__b2c01.go_low(t)
    ct.Li_MOT_Shutter__b1c31.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_low(t)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)  # COARSE with no prior cmd, treated as constant
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.Bias_X_HH.constant(t, -2.5)
    ct.Bias_X_AH.constant(t, 1.00006)
    ct.Bias_Y_HH.constant(t, 2.6001)
    ct.Bias_Y_AH.constant(t, -3.59985)
    ct.Bias_Z_HH.constant(t, -0.499878)
    ct.Bias_Z_AH.constant(t, -0.599976)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Bitter_Lower_CV__b3c13.constant(t, 2.30011)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.3999)
    ct.Bitter_Upper_CC__b3c16.constant(t, 5)
    ct.Bitter_Lower_CC__b3c12.constant(t, 5)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    ct.oTOP_Int_Lock__b4c08.constant(t, 0.599976)
    ct.oTOP_FCarrier__b4c07.constant(t, 1.79993)
    ct.oTOP_Mod_AM__b4c09.constant(t, 5.49988)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 2.5)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 3.75)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, 0.400085)
    # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 1e-3)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 2e-3, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 2e-3, 5)
    # ct.Bitter_V_AH.constant(t + 5e-3, -0.0619507)  # replaced by ramp at t + 50e-3 in proc 000
    # ct.Bitter_V_HH.constant(t + 5e-3, 0.0469971)  # replaced by ramp at t + 50e-3 in proc 000
    ct.Bitter_V_AH.ramp(t=t + 5e-3, duration=45e-3, initial=-0.0619507, final=0.188293, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 5e-3, duration=45e-3, initial=0.0469971, final=-0.0201416, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 100e-3)

    # procedure 001: Cs_Molasses_Cooling
    t = 15495e-3
    add_time_marker(t, 'Cs_Molasses_Cooling')
    # ct.Cs_MOT_Freq__b3c24.constant(t - 2e-3, -6.79993)  # replaced by ramp at t + 4e-3 in proc 001
    # ct.Cs_Rep_Freq__b3c26.constant(t - 1e-3, 5.36011)  # replaced by ramp at t + 1e-3 in proc 001
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.700073)  # replaced by ramp at t + 5e-3 in proc 001
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Bias_X_HH.constant(t, 0.499878)
    ct.Bias_X_AH.constant(t, -1.00006)
    ct.Bias_Y_HH.constant(t, -1.38)
    ct.Bias_Y_AH.constant(t, 2.86438)
    ct.Bias_Z_HH.constant(t, -0.400085)
    ct.Bias_Z_AH.constant(t, -1.00006)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t - 1e-3, duration=2e-3, initial=5.36011, final=6.4801, samplerate=FAST_FREQ)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t - 2e-3, duration=6e-3, initial=-6.79993, final=-5.79987, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t, duration=5e-3, initial=0.700073, final=0.100098, samplerate=FAST_FREQ)

    # # procedure 002: Cs_H_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Cs_H_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 413e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 412.9e-3)
    # # ct.Cs_MOT_Freq__b3c24.constant(t - 50e-3, -7.7301)  # replaced by ramp at t - 5e-3 in proc 002
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 15e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 13e-3)
    # ct.Cs_VRep_Shutter__b1c16.go_high(t - 12e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t - 10e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t - 10e-3)
    # ct.Bias_X_HH.constant(t - 10e-3, 3.99994)
    # ct.Bias_X_AH.constant(t - 10e-3, -3.99994)
    # ct.Bias_Y_AH.constant(t - 10e-3, 2.69989)
    # ct.Bias_Z_HH.constant(t - 10e-3, 0.499878)
    # ct.Bias_Z_AH.constant(t - 10e-3, 0)
    # ct.Bias_Y_HH.constant(t - 7e-3, -2.3999)
    # ct.Cs_MOT_Freq__b3c24.ramp(t=t - 50e-3, duration=45e-3, initial=-7.7301, final=-7.77008, samplerate=FAST_FREQ)
    # ct.Cs_VRep_Shutter__b1c16.go_low(t - 1e-3)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t - 1e-3, 2.99988)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t - 0.1e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t - 0.02e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t)
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.06e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 0.06e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.1e-3)
    # ct.oTOP_Mod_AM__b4c09.constant(t + 5e-3, 0)
    # # 6.1_Mod_AO_Switch: 0 JUMP — no new channel
    # # 6.2_XDT_AO_SW: 0 JUMP — no new channel
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # ct.oTOP_AO_AM__b4c06.constant(t + 5e-3, 0)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 7e-3)
    # # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 10e-3)
    # # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 15e-3)  # replaced by ramp at t + 630e-3 in proc 002
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 625e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t + 630e-3)
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # ct.Cs_LFImg_AO_Sw__b1c10.ramp(t=t + 15e-3, duration=615e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 639.98e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 640e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 640e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 640.06e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 640.06e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 647e-3)
    # # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 655e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 1750e-3)

    # procedure 003: Cs_RSC1
    t = 15500e-3
    add_time_marker(t, 'Cs_RSC1')
    ct.Cs_Rep_Shutter__b1c12.go_low(t - 16e-3)
    ct.Cs_HOP_Shutter__b1c09.go_high(t - 10e-3)
    ct.Cs_RSC_AO_Sw__b1c13.go_low(t - 10e-3)
    ct.Cs_RSC_Shutter__b1c14.go_high(t - 9e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 5e-3)
    ct.Cs_RSC_AO_AM__b3c27.constant(t - 4.5e-3, 0)
    ct.Cs_RSC_AO_Sw__b1c13.go_high(t - 4e-3)
    # ct.Cs_Rep_Freq__b3c26.constant(t - 2.5e-3, 6.4801)  # replaced by ramp at t in proc 003
    # ct.Cs_RSC_AO_AM__b3c27.constant(t - 1e-3, 0)  # replaced by ramp at t - 0.5e-3 in proc 003
    ct.Spec_Analyzer_Trig__b2c09.go_low(t - 1e-3)
    # ct.Cs_MOT_Freq__b3c24.constant(t - 0.98e-3, -5.79987)  # replaced by ramp at t + 1.5e-3 in proc 003
    ct.Cs_RSC_AO_AM__b3c27.ramp(t=t - 1e-3, duration=0.5e-3, initial=0, final=2.09991, samplerate=FAST_FREQ)
    ct.Cs_Rep_AO_AM__b3c25.constant(t - 0.3e-3, 0)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t - 2.5e-3, duration=2.5e-3, initial=6.4801, final=3.82996, samplerate=FAST_FREQ)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 1.40991)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 0.02e-3, 0)
    ct.Bias_X_HH.constant(t + 0.02e-3, 0.950012)
    ct.Bias_X_AH.constant(t + 0.02e-3, -0.499878)
    ct.Bias_Y_HH.constant(t + 0.02e-3, -1.38)
    ct.Bias_Y_AH.constant(t + 0.02e-3, 2.76001)
    ct.Bias_Z_HH.constant(t + 0.02e-3, -0.499878)
    ct.Bias_Z_AH.constant(t + 0.02e-3, -0.350037)
    ct.Spec_Analyzer_Trig__b2c09.go_high(t + 0.02e-3)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 1.5e-3, 0.0250244)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t - 0.98e-3, duration=2.48e-3, initial=-5.79987, final=-0.289917, samplerate=FAST_FREQ)
    ct.Spec_Analyzer_Trig__b2c09.go_low(t + 5e-3)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 31.6e-3, 0)
    ct.Cs_Rep_AO_AM__b3c25.constant(t + 31.6e-3, 0)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 31.7e-3)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 31.7e-3)
    # ct.Cs_RSC_AO_AM__b3c27.constant(t + 32.6e-3, 2.09991)  # replaced by ramp at t + 37.6e-3 in proc 003
    ct.Cs_RSC_AO_AM__b3c27.ramp(t=t + 32.6e-3, duration=5e-3, initial=2.09991, final=0, samplerate=FAST_FREQ)
    ct.Cs_RSC_AO_Sw__b1c13.go_low(t + 38e-3)

    # procedure 004: Aerotech_return
    t = 15600e-3
    add_time_marker(t, 'Aerotech_return')
    ct.BFL_Int_Lock__b3c02.constant(t - 250e-3, 0.710144)
    ct.Aerotech_Control__b3c00.constant(t - 100e-3, 5)
    ct.Aerotech_Control__b3c00.constant(t + 750e-3, 7.00012)
    # ct.BFL_Int_Lock__b3c02.constant(t + 1000e-3, 0.710144)  # replaced by ramp at t + 1100e-3 in proc 004
    ct.Dual_780_Int_Lock__b3c30.constant(t + 1000e-3, 2.00012)
    # ct.Dual_1064_Int_Lock__b4c16.constant(t + 1000e-3, 2.5)  # replaced by ramp at t + 1500e-3 in proc 004
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 1000e-3, duration=100e-3, initial=0.710144, final=0.318909, samplerate=SLOW_FREQ)
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 1100e-3, duration=100e-3, initial=0.318909, final=0.219116, samplerate=SLOW_FREQ)
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 1200e-3, duration=100e-3, initial=0.219116, final=0.0775146, samplerate=FAST_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1000e-3, duration=500e-3, initial=2.5, final=2.5, samplerate=SLOW_FREQ)
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 1300e-3, duration=400e-3, initial=0.0775146, final=0, samplerate=FAST_FREQ)
    # ct.Dual_780_Int_Lock__b3c30.constant(t + 1700e-3, 2.00012)  # replaced by ramp at t + 9100e-3 in proc 004
    # ct.Dual_1064_Int_Lock__b4c16.constant(t + 1700e-3, 2.5)  # replaced by ramp at t + 3700e-3 in proc 004
    # 5.11_BFL_AO_AM: 0 JUMP — no new channel
    ct.BFL_AO_Sw__b3c01.constant(t + 1701e-3, 0)
    ct.Aerotech_Control__b3c00.constant(t + 2000e-3, 8.99994)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1700e-3, duration=2000e-3, initial=2.5, final=1.45386, samplerate=SLOW_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 3700e-3, duration=1000e-3, initial=1.45386, final=0.768127, samplerate=SLOW_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 4700e-3, duration=1000e-3, initial=0.768127, final=0.405884, samplerate=SLOW_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 5700e-3, duration=1000e-3, initial=0.405884, final=0.215149, samplerate=SLOW_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 6700e-3, duration=2250e-3, initial=0.215149, final=0.0750732, samplerate=SLOW_FREQ)
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t + 1700e-3, duration=7400e-3, initial=2.00012, final=1.79993, samplerate=SLOW_FREQ)

    # # procedure 005: Dual_Imaging_H
    # t = code_65501/1e3
    # add_time_marker(t, 'Dual_Imaging_H')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 500.02e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 499.06e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 50e-3, 6.00006)
    # ct.Li_EOM_AO_Sw__b1c26.go_high(t - 20e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 17e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # ct.Li_HImg_Shutter__b1c28.go_high(t - 8e-3)
    # ct.Li_EOM_Freq__b3c31.constant(t - 0.4e-3, -4.8999)
    # ct.Li_EOM_AO_Sw__b1c26.go_low(t - 0.08e-3)
    # ct.Li_EOM_AO_Sw__b1c26.go_high(t - 0.06e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t - 0.02e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_HImg_Shutter__b1c28.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Pixelfly_Shutter__b2c06.go_low(t)
    # # 5.9_Cs_LF_Img_AO_AM: 8.50006 JUMP — no new channel
    # ct.Li_EOM_H_Shutter__b1c27.go_low(t)
    # ct.Li_EOM_Freq__b3c31.constant(t, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.02e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 0.02e-3, 0)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.06e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 17e-3)
    # ct.Cs_VRep_Shutter__b1c16.go_high(t + 18e-3)
    # ct.Bias_Y_HH.constant(t + 18e-3, -2.00012)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 20e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 20e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 20e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t + 20e-3)
    # ct.Li_EOM_AO_Sw__b1c26.go_low(t + 20e-3)
    # ct.Cs_VRep_Shutter__b1c16.go_low(t + 29e-3)
    # # 7.1_CS_Rep_AO_AM: 2.00012 JUMP — no new channel
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 29.9e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 30e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 30e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 30e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 30.06e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 30.1e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 35e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 37e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 50e-3, 6.00006)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 55e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 150e-3, 6.00006)
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 182e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 190e-3)
    # ct.Li_HImg_Shutter__b1c28.go_high(t + 192e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 199.98e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 200e-3)
    # ct.Li_HImg_Shutter__b1c28.go_low(t + 200e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 200e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 200.02e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 200.02e-3, 0)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 200.06e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 215e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 218e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t + 218e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 220e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 228e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 228e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 228.06e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 235e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 255e-3)
    # # 7.7_N_Cs_MOT_Freq: -7.66998 JUMP — no new channel
    # # 5.9_Cs_LF_Img_AO_AM: 10 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.14996 COARSE — no new channel

    # procedure 006: Dual_Imaging_V 
    t = code_65501/1e3
    add_time_marker(t, 'Dual_Imaging_V ')
    # ct.Cs_Rep_Freq__b3c26.constant(t - 1000e-3, 6.51001)  # replaced by ramp at t - 50e-3 in proc 006
    # ct.CS_HFImg_Freq__b3c22.constant(t - 1000e-3, -10)  # replaced by ramp at t - 100e-3 in proc 006
    ct.Cs_LFImg_Shutter__b1c11.go_low(t - 100e-3)
    ct.CS_HFImg_Freq__b3c22.ramp(t=t - 1000e-3, duration=900e-3, initial=-10, final=code_65511, samplerate=FAST_FREQ)
    ct.Cs_HFImg_Shutter__b1c06.go_high(t - 80e-3)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t - 1000e-3, duration=950e-3, initial=6.51001, final=7.00012, samplerate=SLOW_FREQ)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 40e-3)
    ct.Cs_VImg_AO_AM__b3c28.constant(t - 35e-3, 0)
    ct.Li_Img_AO_AM__b4c00.constant(t - 20e-3, 3.99994)
    ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    ct.Li_VImg_Shutter__b2c02.go_high(t - 10e-3)
    ct.Li_EOM_H_Shutter__b1c27.go_high(t - 10e-3)
    ct.Li_EOM_AO_Sw__b1c26.go_low(t - 10e-3)
    ct.Li_EOM_Freq__b3c31.constant(t - 10e-3, -1.25)
    ct.Cs_HFImg_AO_Sw__b1c05.go_low(t - 10e-3)
    ct.Cs_VImg_Shutter__b1c15.go_high(t - 10e-3)
    # 1.10_Cs_Oneshot_Bypass: 5 JUMP — no new channel
    ct.Cs_HOP_Shutter__b1c09.go_high(t - 6e-3)
    ct.Cs_VImg_AO_AM__b3c28.constant(t - 5e-3, 0.899963)
    # 6.30_Li_Oneshot_Bypass: 5 JUMP — no new channel
    ct.Cs_Andor_Trig__b1c04.go_high(t - 0.44e-3)
    ct.Cs_Andor_Trig__b1c04.go_low(t - 0.4e-3)
    ct.Li_Img_AO_Sw__b1c29.go_high(t)
    ct.Li_EOM_AO_Sw__b1c26.go_high(t)
    ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.02e-3)
    ct.Li_EOM_AO_Sw__b1c26.go_low(t + 0.02e-3)
    ct.Cs_Rep_AO_AM__b3c25.constant(t + 0.4e-3, 2.99988)
    ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 0.46e-3)
    ct.MW_Trig__b2c04.go_low(t + 0.46e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 0.46e-3)
    ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 0.48e-3)
    ct.Cs_HOP_Shutter__b1c09.go_low(t + 0.48e-3)
    ct.Cs_Rep_AO_AM__b3c25.constant(t + 0.48e-3, 0)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.48e-3)
    ct.Li_Img_AO_Sw__b1c29.go_high(t + 0.9e-3)
    ct.Li_Img_AO_Sw__b1c29.go_low(t + 1e-3)
    ct.Li_EOM_H_Shutter__b1c27.go_low(t + 1e-3)
    ct.Li_EOM_Freq__b3c31.constant(t + 1e-3, -5)
    ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 1.36e-3)
    ct.Cs_VImg_Shutter__b1c15.go_low(t + 1.36e-3)
    ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 1.38e-3)
    # 1.10_Cs_Oneshot_Bypass: 0 JUMP — no new channel
    ct.Li_VImg_Shutter__b2c02.go_low(t + 1.72e-3)
    # 6.30_Li_Oneshot_Bypass: 0 JUMP — no new channel
    ct.Li_Img_AO_AM__b4c00.constant(t + 2e-3, 3.99994)
    # ct.CS_HFImg_Freq__b3c22.constant(t + 3e-3, code_65511)  # replaced by ramp at t + 1000e-3 in proc 006
    # ct.Cs_MOT_Freq__b3c24.constant(t + 3e-3, -7.7301)  # replaced by ramp at t + 100e-3 in proc 006
    ct.Li_Img_AO_Sw__b1c29.go_high(t + 20e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 20e-3)
    ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 30e-3)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t + 3e-3, duration=97e-3, initial=-7.7301, final=-7.14996, samplerate=SLOW_FREQ)
    ct.CS_HFImg_Freq__b3c22.ramp(t=t + 3e-3, duration=997e-3, initial=code_65511, final=-10, samplerate=FAST_FREQ)

    # procedure 007: FB_Bias_field
    t = 15600e-3
    add_time_marker(t, 'FB_Bias_field')
    ct.Bitter_Lower_CC__b3c12.constant(t - 100e-3, 5)
    ct.Bitter_Upper_CC__b3c16.constant(t - 100e-3, 5)
    ct.Bitter_Upper_CV__b3c17.constant(t - 100e-3, 2.20001)
    ct.Bitter_Lower_CV__b3c13.constant(t - 100e-3, 1.79993)
    # ct.Bitter_V_HH.constant(t - 60e-3, 0.669861)  # replaced by ramp at t + 50e-3 in proc 007
    # ct.Bitter_V_AH.constant(t - 60e-3, -0.669861)  # replaced by ramp at t + 50e-3 in proc 007
    ct.Bitter_Upper_CV__b3c17.constant(t - 50e-3, 2.3999)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 4.46014)  # replaced by ramp at t + 400e-3 in proc 007
    ct.Bitter_V_HH.ramp(t=t - 60e-3, duration=110e-3, initial=0.669861, final=2.77893, samplerate=SLOW_FREQ)
    ct.Bitter_V_AH.ramp(t=t - 60e-3, duration=110e-3, initial=-0.669861, final=-0.826416, samplerate=FAST_FREQ)
    ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t, duration=400e-3, initial=4.46014, final=0, samplerate=SLOW_FREQ)
    ct.FF_Disable__b1c24.go_high(t + 401e-3)
    # ct.Bitter_V_HH.constant(t + 750e-3, 2.77893)  # replaced by ramp at t + 917.7e-3 in proc 007
    # ct.Bias_X_HH.constant(t + 750e-3, 6.00006)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bias_Y_HH.constant(t + 750e-3, -3.591)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bias_Z_HH.constant(t + 750e-3, -5)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bitter_Upper_CV__b3c17.constant(t + 750e-3, 2.3999)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bitter_Lower_CV__b3c13.constant(t + 750e-3, 1.79993)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bias_X_AH.constant(t + 750e-3, 0.202637)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bias_Y_AH.constant(t + 750e-3, 3.52295)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bias_Z_AH.constant(t + 750e-3, -0.400085)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bitter_V_AH.constant(t + 750e-3, -0.140686)  # replaced by ramp at t + 917.7e-3 in proc 007
    ct.Bitter_V_HH.ramp(t=t + 750e-3, duration=167.7e-3, initial=2.77893, final=6.43982, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 750e-3, duration=167.7e-3, initial=-0.140686, final=-0.291443, samplerate=FAST_FREQ)
    # ct.Bitter_V_HH.constant(t + 917.72e-3, 6.43188)  # replaced by ramp at t + 950e-3 in proc 007
    # ct.Bitter_V_AH.constant(t + 917.72e-3, 3.1015)  # replaced by ramp at t + 950e-3 in proc 007
    ct.Bitter_Precision_Disable__b1c00.go_low(t + 917.72e-3)
    ct.Bitter_V_HH.ramp(t=t + 917.72e-3, duration=32.28e-3, initial=6.43188, final=-2.00012, samplerate=FAST_FREQ)
    ct.Bias_X_HH.ramp(t=t + 750e-3, duration=200e-3, initial=6.00006, final=0.390015, samplerate=SLOW_FREQ)
    ct.Bias_Y_HH.ramp(t=t + 750e-3, duration=200e-3, initial=-3.591, final=3.99994, samplerate=SLOW_FREQ)
    ct.Bias_Z_HH.ramp(t=t + 750e-3, duration=200e-3, initial=-5, final=-0.302429, samplerate=SLOW_FREQ)
    ct.Bitter_Upper_CV__b3c17.ramp(t=t + 750e-3, duration=200e-3, initial=2.3999, final=3.09998, samplerate=SLOW_FREQ)
    ct.Bitter_Lower_CV__b3c13.ramp(t=t + 750e-3, duration=200e-3, initial=1.79993, final=2.69989, samplerate=SLOW_FREQ)
    ct.Bias_X_AH.ramp(t=t + 750e-3, duration=200e-3, initial=0.202637, final=-0.319519, samplerate=SLOW_FREQ)
    ct.Bias_Y_AH.ramp(t=t + 750e-3, duration=200e-3, initial=3.52295, final=2.7533, samplerate=SLOW_FREQ)
    ct.Bias_Z_AH.ramp(t=t + 750e-3, duration=200e-3, initial=-0.400085, final=-0.400085, samplerate=SLOW_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 917.72e-3, duration=32.28e-3, initial=3.1015, final=3.8501, samplerate=FAST_FREQ)
    # ct.Bitter_V_HH.constant(t + 1300e-3, -2.00012)  # replaced by ramp at t + 2000e-3 in proc 007
    ct.Bitter_V_HH.ramp(t=t + 1300e-3, duration=700e-3, initial=-2.00012, final=-0.849915, samplerate=SLOW_FREQ)
    # ct.Bias_Y_HH.constant(t + 9000e-3, 3.99994)  # replaced by ramp at t + 9100e-3 in proc 007
    ct.Bias_Y_HH.ramp(t=t + 9000e-3, duration=100e-3, initial=3.99994, final=-5, samplerate=SLOW_FREQ)

    # procedure 008: Cs_Dark
    t = 15534e-3
    add_time_marker(t, 'Cs_Dark')
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t - 50e-3)
    ct.Cs_2DMOT_Shutter__b1c01.go_low(t - 20e-3)
    ct.Cs_HOP_Shutter__b1c09.go_low(t - 12e-3)
    ct.Cs_RSC_Shutter__b1c14.go_low(t - 8e-3)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t)
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t)
    # ct.Cs_Rep_Freq__b3c26.constant(t, 3.82996)  # replaced by ramp at t + 10e-3 in proc 008
    ct.Cs_Rep_Shutter__b1c12.go_low(t)
    # ct.Cs_MOT_Freq__b3c24.constant(t + 1e-3, -0.289917)  # replaced by ramp at t + 9e-3 in proc 008
    ct.Cs_MOT_Freq__b3c24.ramp(t=t + 1e-3, duration=8e-3, initial=-0.289917, final=-7.7301, samplerate=FAST_FREQ)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t, duration=10e-3, initial=3.82996, final=6.51001, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 505e-3)
    ct.Cs_RSC_AO_Sw__b1c13.go_high(t + 505e-3)
    ct.Cs_RSC_AO_AM__b3c27.constant(t + 505e-3, 5)
    ct.Cs_Rep_AO_AM__b3c25.constant(t + 505e-3, 0)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 505e-3)

    # # procedure 009: Li_HF_V_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_HF_V_Imaging')
    # ct.Li_EOM_H_Shutter__b1c27.go_high(t - 20e-3)
    # ct.Li_EOM_AO_Sw__b1c26.go_high(t - 20e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 10e-3, 0)
    # ct.Li_VImg_Shutter__b2c02.go_high(t - 7e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 5e-3)
    # # 1.10_Cs_Oneshot_Bypass: 5 JUMP — no new channel
    # ct.Li_EOM_AO_Sw__b1c26.go_low(t - 0.12e-3)
    # ct.Li_EOM_Freq__b3c31.constant(t - 0.12e-3, -8.59985)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 0.06e-3, 3.99994)
    # ct.Cs_Andor_Trig__b1c04.go_high(t)
    # ct.Li_VImg_Shutter__b2c02.go_low(t)
    # ct.Li_EOM_H_Shutter__b1c27.go_low(t)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 0.02e-3)
    # ct.Li_EOM_AO_Sw__b1c26.go_high(t + 0.02e-3)
    # ct.Li_EOM_Freq__b3c31.constant(t + 0.02e-3, -5)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.04e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 0.04e-3, 0)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 0.1e-3)
    # # 1.10_Cs_Oneshot_Bypass: 0 JUMP — no new channel
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 30e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 30e-3, 6.00006)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 490e-3, 0)
    # ct.Li_VImg_Shutter__b2c02.go_high(t + 493e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 495e-3)
    # # 1.10_Cs_Oneshot_Bypass: 5 JUMP — no new channel
    # ct.Li_Img_AO_AM__b4c00.constant(t + 499.94e-3, 3.99994)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 500e-3)
    # ct.Cs_Andor_Trig__b1c04.go_high(t + 500e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 500.02e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 500.04e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 500.04e-3, 0)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 500.1e-3)
    # # 1.10_Cs_Oneshot_Bypass: 0 JUMP — no new channel
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 530e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 530e-3, 5)
    # ct.Cs_Andor_Trig__b1c04.go_high(t + 990e-3)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 990.1e-3)

    # procedure 010: Cs_Evaporation
    t = 15600e-3
    add_time_marker(t, 'Cs_Evaporation')
    # ct.oTOP_Mod_AM__b4c09.constant(t - 40e-3, 2.5)  # replaced by ramp at t + 350e-3 in proc 010
    # ct.oTOP_Int_Lock__b4c08.constant(t, 2.90009)  # replaced by ramp at t + 150e-3 in proc 010
    # ct.oTOP_FCarrier__b4c07.constant(t + 100e-3, 1.79993)  # replaced by ramp at t + 200e-3 in proc 010
    ct.oTOP_Int_Lock__b4c08.ramp(t=t, duration=150e-3, initial=2.90009, final=2.25006, samplerate=SLOW_FREQ)
    ct.oTOP_FCarrier__b4c07.ramp(t=t + 100e-3, duration=100e-3, initial=1.79993, final=2.6001, samplerate=FAST_FREQ)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    ct.oTOP_Mod_AM__b4c09.ramp(t=t - 40e-3, duration=390e-3, initial=2.5, final=0.799866, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 150e-3, duration=350e-3, initial=2.25006, final=1.26587, samplerate=SLOW_FREQ)
    # ct.Bitter_V_AH.constant(t + 650e-3, -0.826416)  # replaced by ramp at t + 749e-3 in proc 010
    ct.oTOP_Mod_AM__b4c09.ramp(t=t + 350e-3, duration=350e-3, initial=0.799866, final=0, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 650e-3, duration=99e-3, initial=-0.826416, final=-0.140686, samplerate=FAST_FREQ)
    # ct.oTOP_FCarrier__b4c07.constant(t + 750e-3, 2.6001)  # replaced by ramp at t + 950e-3 in proc 010
    ct.oTOP_FCarrier__b4c07.ramp(t=t + 750e-3, duration=200e-3, initial=2.6001, final=2.99988, samplerate=FAST_FREQ)
    # ct.oTOP_Int_Lock__b4c08.constant(t + 2000e-3, 1.26587)  # replaced by ramp at t + 3000e-3 in proc 010
    # ct.oTOP_FCarrier__b4c07.constant(t + 2100e-3, 2.99988)  # replaced by ramp at t + 2250e-3 in proc 010
    ct.oTOP_FCarrier__b4c07.ramp(t=t + 2100e-3, duration=150e-3, initial=2.99988, final=2.09991, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 2000e-3, duration=1000e-3, initial=1.26587, final=0.88623, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 3000e-3, duration=1000e-3, initial=0.88623, final=0.683594, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 4000e-3, duration=1000e-3, initial=0.683594, final=0.549927, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 5000e-3, duration=1000e-3, initial=0.549927, final=0.458069, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 6000e-3, duration=1000e-3, initial=0.458069, final=0.389099, samplerate=SLOW_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 7000e-3, duration=1000e-3, initial=0.389099, final=0.239868, samplerate=SLOW_FREQ)

    # procedure 011: Spare
    t = 29600e-3
    add_time_marker(t, 'Spare')
    ct.Li_Img_AO_AM__b4c00.constant(t - 20e-3, 6.00006)
    ct.Li_Img_AO_Sw__b1c29.go_low(t - 16e-3)
    ct.Li_HImg_Shutter__b1c28.go_low(t - 15e-3)
    ct.Li_Img_AO_Sw__b1c29.go_high(t)
    ct.Li_HImg_Shutter__b1c28.go_low(t)
    ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.14e-3)
    ct.Li_Img_AO_AM__b4c00.constant(t + 20e-3, 6.00006)
    ct.Li_Img_AO_Sw__b1c29.go_high(t + 20e-3)

    # procedure 012: Li_Feshbach
    t = 10000e-3
    add_time_marker(t, 'Li_Feshbach')
    ct.Bitter_Lower_CC__b3c12.constant(t - 500e-3, 3.69995)
    ct.Bitter_Upper_CC__b3c16.constant(t - 500e-3, 3.90015)
    ct.Bitter_Lower_CC__b3c12.constant(t - 20e-3, 5)
    ct.Bitter_Upper_CC__b3c16.constant(t - 20e-3, 5)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.69989)
    ct.Bitter_Lower_CV__b3c13.constant(t, 2.20001)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 0.22e-3, 5)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 0.32e-3, 0)
    # ct.Bitter_V_HH.constant(t + 0.32e-3, 0)  # replaced by ramp at t + 8e-3 in proc 012
    # ct.Bitter_V_AH.constant(t + 0.32e-3, 0)  # replaced by ramp at t + 8e-3 in proc 012
    ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1e-3, 4.10004)
    # ct.Bitter_Lower_FF__b3c14.constant(t + 1e-3, 2.55005)  # replaced by ramp at t + 2.2e-3 in proc 012
    ct.Bitter_Lower_FF__b3c14.ramp(t=t + 1e-3, duration=1.2e-3, initial=2.55005, final=2.20001, samplerate=FAST_FREQ)
    # ct.Bitter_Upper_CV__b3c17.constant(t + 3e-3, 2.5)  # replaced by ramp at t + 8e-3 in proc 012
    # ct.Bitter_Lower_CV__b3c13.constant(t + 3e-3, 2.20001)  # replaced by ramp at t + 8e-3 in proc 012
    ct.Bitter_Upper_CV__b3c17.ramp(t=t + 3e-3, duration=5e-3, initial=2.5, final=2.85004, samplerate=FAST_FREQ)
    ct.Bitter_Lower_CV__b3c13.ramp(t=t + 3e-3, duration=5e-3, initial=2.20001, final=2.69989, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 0.32e-3, duration=7.68e-3, initial=0, final=6.60004, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 0.32e-3, duration=7.68e-3, initial=0, final=-0.0650024, samplerate=FAST_FREQ)
    # ct.Bitter_Upper_CV__b3c17.constant(t + 1450e-3, 2.85004)  # replaced by ramp at t + 1500e-3 in proc 012
    # ct.Bitter_Lower_CV__b3c13.constant(t + 1450e-3, 2.69989)  # replaced by ramp at t + 1500e-3 in proc 012
    # ct.Bitter_Lower_FF__b3c14.constant(t + 1470e-3, 2.20001)  # replaced by ramp at t + 1500e-3 in proc 012
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1470e-3, 4.10004)  # replaced by ramp at t + 1500e-3 in proc 012
    # ct.Bitter_V_HH.constant(t + 1470e-3, 6.60004)  # replaced by ramp at t + 1500e-3 in proc 012
    ct.Bitter_Upper_CV__b3c17.ramp(t=t + 1450e-3, duration=50e-3, initial=2.85004, final=2.20001, samplerate=FAST_FREQ)
    ct.Bitter_Lower_CV__b3c13.ramp(t=t + 1450e-3, duration=50e-3, initial=2.69989, final=2.09991, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 1470e-3, duration=30e-3, initial=6.60004, final=0, samplerate=FAST_FREQ)
    ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1470e-3, duration=30e-3, initial=4.10004, final=0, samplerate=FAST_FREQ)
    ct.Bitter_Lower_FF__b3c14.ramp(t=t + 1470e-3, duration=30e-3, initial=2.20001, final=-0.0750732, samplerate=FAST_FREQ)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 1500e-3, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 1500e-3, 5)

    # procedure 013: Dual_Evap
    t = 27700e-3
    add_time_marker(t, 'Dual_Evap')
    ct.Bias_Y_HH.constant(t, -5)
    ct.Bias_Y_HH.constant(t + 5e-3, -0.799866)
    # ct.Dual_1064_Int_Lock__b4c16.constant(t + 100e-3, 0.950012)  # replaced by ramp at t + 600e-3 in proc 013
    # ct.Dual_780_Int_Lock__b3c30.constant(t + 100e-3, 0.799866)  # replaced by ramp at t + 1400e-3 in proc 013
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 100e-3, duration=500e-3, initial=0.950012, final=0.78186, samplerate=SLOW_FREQ)
    ct.DMD_AO_AM__b3c29.constant(t + 980e-3, 0)
    ct.DMD_AO_Sw__b1c19.go_low(t + 980e-3)
    ct.DMD_Shutter__b1c21.go_high(t + 990e-3)
    # ct.DMD_AO_AM__b3c29.constant(t + 1000e-3, 0)  # replaced by ramp at t + 1500e-3 in proc 013
    ct.DMD_AO_Sw__b1c19.go_high(t + 1000e-3)
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t + 100e-3, duration=1300e-3, initial=0.799866, final=0.0201416, samplerate=SLOW_FREQ)
    # 4.2_Dual_780_AO_AM: 0 JUMP — no new channel
    ct.Dual_780_AO_Sw__b1c23.go_low(t + 1400.1e-3)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 600e-3, duration=900e-3, initial=0.78186, final=0.580139, samplerate=FAST_FREQ)
    # ct.Bias_Y_HH.constant(t + 1500e-3, -0.799866)  # replaced by ramp at t + 1550e-3 in proc 013
    ct.DMD_AO_AM__b3c29.ramp(t=t + 1000e-3, duration=500e-3, initial=0, final=3.80005, samplerate=FAST_FREQ)
    ct.Bias_Y_HH.ramp(t=t + 1500e-3, duration=50e-3, initial=-0.799866, final=-5, samplerate=SLOW_FREQ)
    ct.DMD_AO_AM__b3c29.constant(t + 2002e-3, 0)
    ct.DMD_Shutter__b1c21.go_low(t + 2002e-3)
    ct.DMD_AO_Sw__b1c19.go_low(t + 2002e-3)

    # # procedure 014: Li_H_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_H_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 400e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 399e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 12e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 10e-3, 2.99988)
    # ct.Li_HImg_Shutter__b1c28.go_high(t - 6e-3)
    # ct.Li_Rep_Shutter__b2c01.go_high(t - 3e-3)
    # ct.Bias_X_HH.constant(t - 1e-3, 0.599976)
    # ct.Bias_Z_HH.constant(t - 1e-3, 0.499878)
    # ct.Li_MOT_AO_Sw__b1c30.go_low(t - 0.4e-3)
    # ct.Li_Rep_AO_AM__b4c05.constant(t - 0.08e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t - 0.04e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t)
    # ct.Li_Rep_Shutter__b2c01.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Li_Rep_AO_AM__b4c05.constant(t, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.1e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Li_HImg_Shutter__b1c28.go_low(t + 1e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 1e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 10e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 10e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 20e-3)
    # ct.Li_Rep_AO_AM__b4c05.constant(t + 20e-3, 10)
    # # 2.3_Li_MRep_AO_FM: -1.00006 JUMP — no new channel
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 488e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 490e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 490e-3, 2.99988)
    # ct.Li_HImg_Shutter__b1c28.go_high(t + 494e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 496e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 500e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 500e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 500e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 500e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 500.1e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 500.1e-3)
    # ct.Li_HImg_Shutter__b1c28.go_low(t + 501e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 501e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 510e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 510e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 520e-3)

    # # procedure 015: Li_V_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_V_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 400e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 399e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 10e-3, 1.00006)
    # ct.Cs_EOM_Freq_b4c15.constant(t - 8e-3, 5)
    # ct.Li_VImg_Shutter__b2c02.go_high(t - 5e-3)
    # ct.Li_Rep_Shutter__b2c01.go_high(t - 3e-3)
    # ct.Li_MOT_AO_Sw__b1c30.go_low(t - 0.4e-3)
    # ct.Li_Rep_AO_AM__b4c05.constant(t - 0.08e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t - 0.04e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t)
    # ct.Li_Rep_Shutter__b2c01.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Li_Rep_AO_AM__b4c05.constant(t, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.08e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 2e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 2e-3, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 10e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 10e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 20e-3)
    # # 2.3_Li_MRep_AO_FM: -1.00006 JUMP — no new channel
    # ct.Li_Rep_AO_AM__b4c05.constant(t + 20e-3, 10)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 490e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 490e-3, 1.00006)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 492e-3, 5)
    # ct.Li_VImg_Shutter__b2c02.go_high(t + 495e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 496e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 500e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 500e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 500e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 500.04e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 500.08e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 500.1e-3)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 502e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 502e-3, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 510e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 510e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 520e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 1032e-3, 5)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 1040e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 1041e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 1042e-3, 0)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 1499.98e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 1500e-3)
    # ct.Li_Rep_Shutter__b2c01.go_low(t + 1500e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 1500e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 1501e-3)

    # procedure 016: Cs_Levitation1
    t = 15532e-3
    add_time_marker(t, 'Cs_Levitation1')
    ct.Bitter_Lower_CV__b3c13.constant(t - 32e-3, 1.79993)
    ct.Bitter_Lower_CC__b3c12.constant(t - 32e-3, 5)
    ct.Bitter_Upper_CC__b3c16.constant(t - 32e-3, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t - 5e-3, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t - 3e-3, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t - 0.5e-3, 5)
    # ct.Bias_X_HH.constant(t - 0.2e-3, 0.700073)  # replaced by ramp at t in proc 016
    # ct.Bias_X_AH.constant(t - 0.2e-3, -0.290527)  # replaced by ramp at t in proc 016
    # ct.Bias_Y_HH.constant(t - 0.2e-3, -1.61011)  # replaced by ramp at t in proc 016
    # ct.Bias_Y_AH.constant(t - 0.2e-3, 2.78717)  # replaced by ramp at t in proc 016
    # ct.Bias_Z_HH.constant(t - 0.2e-3, -0.499878)  # replaced by ramp at t in proc 016
    # ct.Bias_Z_AH.constant(t - 0.2e-3, -0.400085)  # replaced by ramp at t in proc 016
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t - 0.1e-3, 3.50006)  # replaced by ramp at t + 0.1e-3 in proc 016
    ct.Bitter_V_HH.constant(t, 0.669861)
    ct.Bitter_V_AH.constant(t, -0.669861)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    ct.Scope_Trig__b2c08.go_high(t)
    ct.Bias_X_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=0.700073, final=6.00006, samplerate=FAST_FREQ)
    ct.Bias_X_AH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-0.290527, final=0.202637, samplerate=FAST_FREQ)
    ct.Bias_Y_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-1.61011, final=-3.591, samplerate=FAST_FREQ)
    ct.Bias_Y_AH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=2.78717, final=3.52295, samplerate=FAST_FREQ)
    ct.Bias_Z_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-0.499878, final=-5, samplerate=FAST_FREQ)
    ct.Bias_Z_AH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-0.400085, final=-0.400085, samplerate=FAST_FREQ)
    ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t - 0.1e-3, duration=0.2e-3, initial=3.50006, final=5.49988, samplerate=FAST_FREQ)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t + 0.8e-3, 4.58008)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1e-3, 4.70001)  # replaced by ramp at t + 1.2e-3 in proc 016
    ct.Scope_Trig__b2c08.go_low(t + 1e-3)
    ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1e-3, duration=0.2e-3, initial=4.70001, final=4.54987, samplerate=FAST_FREQ)
    ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1.2e-3, duration=0.3e-3, initial=4.54987, final=4.54987, samplerate=FAST_FREQ)

    # procedure 017: Li_Evaporation
    t = 10000e-3
    add_time_marker(t, 'Li_Evaporation')
    ct.BFL_Int_Lock__b3c02.constant(t, 2.99988)
    # 5.11_BFL_AO_AM: 10 JUMP — no new channel
    ct.Bias_Y_HH.constant(t, -0.499878)
    # ct.BFL_Int_Lock__b3c02.constant(t + 100e-3, 2.99988)  # replaced by ramp at t + 500e-3 in proc 017
    # ct.Dual_780_Int_Lock__b3c30.constant(t + 100e-3, 2.5)  # replaced by ramp at t + 1500e-3 in proc 017
    # ct.Dual_1064_Int_Lock__b4c16.constant(t + 100e-3, 3.75)  # replaced by ramp at t + 1500e-3 in proc 017
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 100e-3, duration=400e-3, initial=2.99988, final=1.84204, samplerate=SLOW_FREQ)
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 500e-3, duration=500e-3, initial=1.84204, final=1.14014, samplerate=SLOW_FREQ)
    ct.BFL_Int_Lock__b3c02.ramp(t=t + 1000e-3, duration=500e-3, initial=1.14014, final=0.710144, samplerate=SLOW_FREQ)
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t + 100e-3, duration=1400e-3, initial=2.5, final=0, samplerate=SLOW_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 100e-3, duration=1400e-3, initial=3.75, final=0, samplerate=SLOW_FREQ)
    ct.Aerotech_Control__b3c00.constant(t + 1600e-3, 2.99988)

    # procedure 018: Li_Dark
    t = 10000e-3
    add_time_marker(t, 'Li_Dark')
    ct.Li_Zeeman_Shutter__b2c03.go_low(t - 15e-3)
    ct.Li_MOT_Shutter__b1c31.go_low(t - 3e-3)
    ct.Li_Rep_Shutter__b2c01.go_low(t - 2e-3)
    ct.Li_MOT_AO_Sw__b1c30.go_low(t)
    ct.Li_Rep_AO_AM__b4c05.constant(t, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_V_HH.constant(t, 0)
    ct.Bitter_V_AH.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    # ct.Li_MOT_Freq__b4c03.constant(t + 1e-3, 5.71991)  # replaced by ramp at t + 1000e-3 in proc 018
    ct.Li_MOT_Freq__b4c03.ramp(t=t + 1e-3, duration=999e-3, initial=5.71991, final=6.09985, samplerate=SLOW_FREQ)

    # # procedure 019: Cs_V_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Cs_V_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 313e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 312.9e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t - 13e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t - 12e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_high(t - 12e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t - 8e-3, 5)
    # # 5.9_Cs_LF_Img_AO_AM: 2.99988 JUMP — no new channel
    # # 2.1_CS_Rep_AO_AM: 10 JUMP — no new channel
    # ct.Cs_HOP_Shutter__b1c09.go_low(t - 1e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t - 0.5e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.1e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 0.3e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 2e-3, 0)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 10e-3)
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    # ct.Cs_VImg_Shutter__b1c15.go_high(t + 628e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 632e-3, 5)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 640e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 640e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t + 640e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 640.1e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 640.3e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 642e-3, 0)
    # ct.Bitter_V_AH.constant(t + 750e-3, 0)

    # procedure 020: Li_CMOT
    t = 10000e-3
    add_time_marker(t, 'Li_CMOT')
    ct.Bitter_Upper_CV__b3c17.constant(t - 200e-3, 3.59985)
    ct.Bitter_Lower_CV__b3c13.constant(t - 200e-3, 3.29987)
    # ct.BFL_Int_Lock__b3c02.constant(t - 80e-3, 2.99988)  # replaced by ramp at t in proc 020
    ct.Li_Zeeman_Shutter__b2c03.go_low(t - 58e-3)
    # 1.32_ZCurrents → 0 (Zeeman: 1.31=5, 1.32=0)
    ct.Zeeman_C1__b4c10.constant(t - 50e-3, 0)
    ct.Zeeman_C2__b4c11.constant(t - 50e-3, 0)
    ct.Zeeman_C3__b4c12.constant(t - 50e-3, 0)
    ct.Zeeman_C4__b4c13.constant(t - 50e-3, 0)
    ct.Zeeman_C5__b4c14.constant(t - 50e-3, 0)
    # ct.Bias_X_HH.constant(t - 50e-3, 5)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bias_X_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bias_Y_HH.constant(t - 50e-3, -3.99994)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bias_Y_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bias_Z_HH.constant(t - 50e-3, -6.00006)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bias_Z_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bitter_V_HH.constant(t - 50e-3, -0.00946045)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Bitter_V_AH.constant(t - 50e-3, 0.347595)  # replaced by ramp at t - 5e-3 in proc 020
    # ct.Li_MOT_Freq__b4c03.constant(t - 18e-3, 5.34485)  # replaced by ramp at t in proc 020
    # ct.Li_MRep_AO_FM__b4c04.constant(t - 18e-3, 0.400085)  # replaced by ramp at t in proc 020
    # ct.Li_Rep_AO_AM__b4c05.constant(t - 13.5e-3, 5)  # replaced by ramp at t - 3e-3 in proc 020
    # ct.Li_MOT_AO_AM__b4c02.constant(t - 13.5e-3, 1.90002)  # replaced by ramp at t - 3e-3 in proc 020
    ct.Bias_X_HH.ramp(t=t - 50e-3, duration=45e-3, initial=5, final=2.5, samplerate=FAST_FREQ)
    ct.Bias_X_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=0, samplerate=FAST_FREQ)
    ct.Bias_Y_HH.ramp(t=t - 50e-3, duration=45e-3, initial=-3.99994, final=-2.3999, samplerate=FAST_FREQ)
    ct.Bias_Y_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=-0.799866, samplerate=FAST_FREQ)
    ct.Bias_Z_HH.ramp(t=t - 50e-3, duration=45e-3, initial=-6.00006, final=0.100098, samplerate=FAST_FREQ)
    ct.Bias_Z_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=-1.40015, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t - 50e-3, duration=45e-3, initial=-0.00946045, final=-0.0601196, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0.347595, final=1.00006, samplerate=FAST_FREQ)
    ct.Li_MOT_AO_AM__b4c02.ramp(t=t - 13.5e-3, duration=10.5e-3, initial=1.90002, final=1.90002, samplerate=FAST_FREQ)
    ct.Li_Rep_AO_AM__b4c05.ramp(t=t - 13.5e-3, duration=10.5e-3, initial=5, final=2.65015, samplerate=FAST_FREQ)
    ct.Li_Rep_AO_Sw__b2c00.go_low(t - 0.04e-3)
    ct.Li_Rep_AO_AM__b4c05.ramp(t=t - 3e-3, duration=2.96e-3, initial=2.65015, final=0, samplerate=FAST_FREQ)
    ct.Li_Rep_AO_AM__b4c05.constant(t - 0.02e-3, 0)
    ct.BFL_Int_Lock__b3c02.ramp(t=t - 80e-3, duration=80e-3, initial=2.99988, final=2.99988, samplerate=FAST_FREQ)
    ct.Li_MOT_AO_AM__b4c02.ramp(t=t - 3e-3, duration=3e-3, initial=1.90002, final=0, samplerate=FAST_FREQ)
    ct.Li_MRep_AO_FM__b4c04.ramp(t=t - 18e-3, duration=18e-3, initial=0.400085, final=0.480042, samplerate=FAST_FREQ)
    ct.Li_MOT_Freq__b4c03.ramp(t=t - 18e-3, duration=18e-3, initial=5.34485, final=5.71991, samplerate=FAST_FREQ)

    # procedure 021: Cs_CMOT
    t = 15445e-3
    add_time_marker(t, 'Cs_CMOT')
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t - 30e-3, 2.30011)  # replaced by ramp at t in proc 021
    # 1.32_ZCurrents → 0 (Zeeman: 1.31=5, 1.32=0)
    ct.Zeeman_C1__b4c10.constant(t - 10e-3, 0)
    ct.Zeeman_C2__b4c11.constant(t - 10e-3, 0)
    ct.Zeeman_C3__b4c12.constant(t - 10e-3, 0)
    ct.Zeeman_C4__b4c13.constant(t - 10e-3, 0)
    ct.Zeeman_C5__b4c14.constant(t - 10e-3, 0)
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t - 10e-3)
    ct.Cs_2DMOT_Shutter__b1c01.go_low(t - 10e-3)
    # ct.Bias_X_HH.constant(t - 10e-3, -2.5)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_X_AH.constant(t - 10e-3, 1.79993)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Y_HH.constant(t - 10e-3, 2.6001)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Y_AH.constant(t - 10e-3, -3.59985)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Z_HH.constant(t - 10e-3, -0.499878)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Z_AH.constant(t - 10e-3, -0.599976)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Dual_780_Int_Lock__b3c30.constant(t - 10e-3, 2.5)  # replaced by ramp at t in proc 021
    # ct.Dual_1064_Int_Lock__b4c16.constant(t - 10e-3, 3.75)  # replaced by ramp at t in proc 021
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t - 30e-3, duration=30e-3, initial=2.30011, final=0.499878, samplerate=FAST_FREQ)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Cs_VRep_Shutter__b1c16.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_low(t)
    # ct.Bitter_V_HH.constant(t, -0.0201416)  # replaced by ramp at t + 40e-3 in proc 021
    # ct.Bitter_V_AH.constant(t, 0.188293)  # replaced by ramp at t + 40e-3 in proc 021
    # ct.Cs_MOT_Freq__b3c24.constant(t, -7.21008)  # replaced by ramp at t + 40e-3 in proc 021
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t - 10e-3, duration=10e-3, initial=2.5, final=0, samplerate=FAST_FREQ)
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t - 10e-3, duration=10e-3, initial=3.75, final=0, samplerate=FAST_FREQ)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 40e-3, 0.499878)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Cs_Rep_Freq__b3c26.constant(t + 40e-3, 6.51001)  # replaced by ramp at t + 48.98e-3 in proc 021
    ct.Bitter_V_HH.ramp(t=t, duration=40e-3, initial=-0.0201416, final=-0.000915527, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t, duration=40e-3, initial=0.188293, final=0.11261, samplerate=FAST_FREQ)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t, duration=40e-3, initial=-7.21008, final=-6.79993, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t + 40e-3, duration=8e-3, initial=0.499878, final=0.299988, samplerate=FAST_FREQ)
    ct.Bias_X_HH.ramp(t=t - 10e-3, duration=58e-3, initial=-2.5, final=2.00012, samplerate=FAST_FREQ)
    ct.Bias_X_AH.ramp(t=t - 10e-3, duration=58e-3, initial=1.79993, final=0, samplerate=FAST_FREQ)
    ct.Bias_Y_HH.ramp(t=t - 10e-3, duration=58e-3, initial=2.6001, final=-0.899963, samplerate=FAST_FREQ)
    ct.Bias_Y_AH.ramp(t=t - 10e-3, duration=58e-3, initial=-3.59985, final=0, samplerate=FAST_FREQ)
    ct.Bias_Z_HH.ramp(t=t - 10e-3, duration=58e-3, initial=-0.499878, final=-1.19995, samplerate=FAST_FREQ)
    ct.Bias_Z_AH.ramp(t=t - 10e-3, duration=58e-3, initial=-0.599976, final=0.599976, samplerate=FAST_FREQ)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t + 40e-3, duration=8.98e-3, initial=6.51001, final=5.36011, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 40e-3, duration=8.98e-3, initial=-0.000915527, final=0.0100708, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 40e-3, duration=8.98e-3, initial=0.11261, final=0.0756836, samplerate=FAST_FREQ)
    # ct.oTOP_Int_Lock__b4c08.constant(t + 85e-3, 0.599976)  # replaced by ramp at t + 90e-3 in proc 021
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 85e-3, duration=5e-3, initial=0.599976, final=2.90009, samplerate=FAST_FREQ)

    # procedure 022: Li_MOT_Loading
    t = 1e-3
    add_time_marker(t, 'Li_MOT_Loading')
    # ct.Li_Img_Freq__b4c01.constant(t, -5.24994)  # replaced by ramp at t + 5000e-3 in proc 022
    ct.Li_MOT_Freq__b4c03.constant(t, 5.34485)
    # 1.8_Cs_2DMOT_Shutter: 0 JUMP — no new channel
    ct.Cs_HOP_Shutter__b1c09.go_low(t)
    # 1.19_Cs_ZM_shutter: 0 JUMP — no new channel
    ct.Bias_X_HH.constant(t, 5)
    ct.Bias_X_AH.constant(t, 0)
    ct.Bias_Y_HH.constant(t, -3.99994)
    ct.Bias_Y_AH.constant(t, 0)
    ct.Bias_Z_HH.constant(t, -6.00006)
    ct.Bias_Z_AH.constant(t, 0)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    ct.oTOP_Int_Lock__b4c08.constant(t, -1.00006)
    ct.Li_Rep_Shutter__b2c01.go_high(t)
    ct.Li_MOT_Shutter__b1c31.go_high(t)
    ct.Li_Zeeman_Shutter__b2c03.go_high(t)
    # 1.32_ZCurrents → 5 (Zeeman: 1.31=5, 1.32=5)
    ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 2.5)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 3.75)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.00012)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.49994)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1.00006)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1.00006)
    ct.Cs_VRep_Shutter__b1c16.go_low(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_low(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_low(t)
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_V_HH.constant(t, 0)
    ct.Bitter_V_AH.constant(t, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 2e-3, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 2e-3, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 5e-3, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 40e-3, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 40e-3, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 40.2e-3, 5)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 45e-3, 0)
    ct.Li_MOT_AO_AM__b4c02.constant(t + 50e-3, 8.99994)
    # 1.31_Cs_Li_Zeswitch → 0 (Zeeman: 1.31=0, 1.32=5)
    ct.Zeeman_C1__b4c10.constant(t + 50e-3, ZEEMAN_C1_CS)
    ct.Zeeman_C2__b4c11.constant(t + 50e-3, ZEEMAN_C2_CS)
    ct.Zeeman_C3__b4c12.constant(t + 50e-3, ZEEMAN_C3_CS)
    ct.Zeeman_C4__b4c13.constant(t + 50e-3, ZEEMAN_C4_CS)
    ct.Zeeman_C5__b4c14.constant(t + 50e-3, ZEEMAN_C5_CS)
    ct.Bitter_V_HH.constant(t + 50e-3, -0.00946045)
    ct.Bitter_V_AH.constant(t + 50e-3, 0.347595)
    ct.Li_Img_Freq__b4c01.ramp(t=t, duration=5000e-3, initial=-5.24994, final=code_65507, samplerate=SLOW_FREQ)

    # procedure 023: True_TOF
    t = code_65500/1e3
    add_time_marker(t, 'True_TOF')
    ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # 5.11_BFL_AO_AM: 0 JUMP — no new channel
    ct.BFL_Int_Lock__b3c02.constant(t, 0)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    ct.oTOP_AO_AM__b4c06.constant(t, 0)
    # 6.2_XDT_AO_SW: 0 JUMP — no new channel
    ct.oTOP_Int_Lock__b4c08.constant(t, -1.00006)
    # 4.2_Dual_780_AO_AM: 0 JUMP — no new channel
    # 4.3_Dual_1064_AO_AM: 0 JUMP — no new channel
    ct.Dual_780_AO_Sw__b1c23.go_low(t)
    ct.Dual_1064_AO_Sw__b1c22.go_low(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t + 0.02e-3)

    # procedure 024: Li_Killing
    t = 24600e-3
    add_time_marker(t, 'Li_Killing')
    ct.Li_Img_AO_AM__b4c00.constant(t - 20e-3, 7.00012)
    ct.Li_EOM_Freq__b3c31.constant(t - 20e-3, -3.15002)
    ct.Li_Img_AO_Sw__b1c29.go_low(t - 8e-3)
    ct.Li_HImg_Shutter__b1c28.go_high(t - 6e-3)
    ct.Li_Img_AO_Sw__b1c29.go_high(t)
    ct.Li_EOM_H_Shutter__b1c27.go_low(t)
    ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.04e-3)
    ct.Li_HImg_Shutter__b1c28.go_low(t + 0.04e-3)
    ct.Li_Img_AO_Sw__b1c29.go_high(t + 12e-3)
    # ct.Li_Img_Freq__b4c01.constant(t + 12e-3, code_65507)  # replaced by ramp at t + 4500e-3 in proc 024
    ct.Li_EOM_Freq__b3c31.constant(t + 20e-3, -3.15002)
    ct.Li_Img_AO_AM__b4c00.constant(t + 200e-3, 6.00006)
    ct.Li_Img_Freq__b4c01.ramp(t=t + 12e-3, duration=4488e-3, initial=code_65507, final=code_65508, samplerate=SLOW_FREQ)

    # # procedure 025: Low_Field_BEC_Field
    # t = 7519e-3
    # add_time_marker(t, 'Low_Field_BEC_Field')
    # ct.Bias_X_HH.constant(t, 0.390015)
    # ct.Bias_X_AH.constant(t, -0.319519)
    # ct.Bias_Y_HH.constant(t, -1.37604)
    # ct.Bias_Y_AH.constant(t, 2.7533)
    # ct.Bias_Z_HH.constant(t, -0.0302124)
    # ct.Bias_Z_AH.constant(t, -0.039978)
    # # 2.6_V_HH: 0.180054 JUMP — no new channel
    # # 2.6_V_HH: 0.100098 COARSE — no new channel
    # # 2.6_V_HH: 0.0799561 JUMP — no new channel
    # # 2.6_V_HH: 0.0552368 COARSE — no new channel
    # # 2.6_V_HH: 0.0500488 FINE — no new channel
    # # 2.6_V_HH: 0.0460815 FINE — no new channel

    # # procedure 026: FB_Bias_Field_off
    # t = code_65502/1e3
    # add_time_marker(t, 'FB_Bias_Field_off')
    # ct.Bitter_V_HH.constant(t, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    # ct.Bitter_V_AH.constant(t, 0)
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Precision_Disable__b1c00.go_high(t)

    # procedure 027: FB_Field_Gentle_off
    t = code_65502/1e3
    add_time_marker(t, 'FB_Field_Gentle_off')
    # ct.Bitter_V_AH.constant(t, 3.8501)  # replaced by ramp at t + 6e-3 in proc 027
    # ct.Bitter_V_HH.constant(t, -0.849915)  # replaced by ramp at t + 6e-3 in proc 027
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Upper_CV__b3c17.constant(t, 3.09998)  # replaced by ramp at t + 6e-3 in proc 027
    # ct.Bitter_Lower_CV__b3c13.constant(t, 2.69989)  # replaced by ramp at t + 6e-3 in proc 027
    ct.Scope_Trig__b2c08.go_high(t)
    ct.Scope_Trig__b2c08.go_low(t + 1e-3)
    ct.Bitter_V_AH.ramp(t=t, duration=6e-3, initial=3.8501, final=3.1015, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t, duration=6e-3, initial=-0.849915, final=6.43188, samplerate=FAST_FREQ)
    ct.Bitter_Upper_CV__b3c17.ramp(t=t, duration=6e-3, initial=3.09998, final=2.00012, samplerate=FAST_FREQ)
    ct.Bitter_Lower_CV__b3c13.ramp(t=t, duration=6e-3, initial=2.69989, final=2.00012, samplerate=FAST_FREQ)
    # ct.Bitter_V_AH.constant(t + 6.02e-3, -0.291443)  # replaced by ramp at t + 30e-3 in proc 027
    # ct.Bitter_V_HH.constant(t + 6.02e-3, 6.43982)  # replaced by ramp at t + 30e-3 in proc 027
    ct.Bitter_Precision_Disable__b1c00.go_high(t + 6.02e-3)
    ct.Bitter_V_AH.ramp(t=t + 6.02e-3, duration=23.98e-3, initial=-0.291443, final=0, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 6.02e-3, duration=23.98e-3, initial=6.43982, final=0, samplerate=FAST_FREQ)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 30e-3, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 30e-3, 0)
    ct.Bitter_Upper_CV__b3c17.ramp(t=t + 6e-3, duration=24e-3, initial=2.00012, final=1.60004, samplerate=SLOW_FREQ)
    ct.Bitter_Lower_CV__b3c13.ramp(t=t + 6e-3, duration=24e-3, initial=2.00012, final=1.60004, samplerate=SLOW_FREQ)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 40e-3, 0)

    # # procedure 028: Unlevitation
    # t = 21600e-3
    # add_time_marker(t, 'Unlevitation')
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    # # 2.6_V_HH: 0 JUMP — no new channel

    # # procedure 029: Cs_HF_H_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Cs_HF_H_Imaging')
    # # ct.CS_HFImg_Freq__b3c22.constant(t - 1000e-3, -10)  # replaced by ramp at t - 20e-3 in proc 029
    # # 7.7_N_Cs_MOT_Freq: -7.60986 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -2.99988 COARSE — no new channel
    # ct.Pixelfly_Trig__b2c07.go_high(t - 100e-3)
    # ct.Cs_LFImg_Shutter__b1c11.go_low(t - 100e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 99.9e-3)
    # ct.Cs_HFImg_Shutter__b1c06.go_high(t - 80e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 30e-3)
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t - 1000e-3, duration=980e-3, initial=-10, final=code_65511, samplerate=FAST_FREQ)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t - 10e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t - 10e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t - 10e-3)
    # ct.MW_Trig__b2c04.go_high(t - 1e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    # ct.MW_Trig__b2c04.go_low(t)
    # ct.DMD_Movie_Trig__b1c20.go_high(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 0.08e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 0.08e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 0.08e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 7e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 15e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 15e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 70e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t + 90e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 90e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 90e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 100e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 100e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 100e-3)
    # # ct.CS_HFImg_Freq__b3c22.constant(t + 100e-3, code_65511)  # replaced by ramp at t + 2000e-3 in proc 029
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 100.08e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 100.08e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 100.08e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 100.1e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 107e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 115e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 115e-3)
    # # 7.7_N_Cs_MOT_Freq: -2.99988 JUMP — no new channel
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t + 100e-3, duration=1900e-3, initial=code_65511, final=-10, samplerate=FAST_FREQ)
    # # 7.7_N_Cs_MOT_Freq: -7.60986 COARSE — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.14996 COARSE — no new channel

    # # procedure 030: Cs_HF_V_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Cs_HF_V_Imaging')
    # # ct.CS_HFImg_Freq__b3c22.constant(t - 1300e-3, -10)  # replaced by ramp at t - 100e-3 in proc 030
    # # 7.7_N_Cs_MOT_Freq: -7.60986 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -2.99988 COARSE — no new channel
    # # ct.Cs_Rep_Freq__b3c26.constant(t - 1000e-3, 7.55005)  # replaced by ramp at t - 50e-3 in proc 030
    # ct.Cs_EOM_Freq_b4c15.constant(t - 100e-3, 8.90015)
    # ct.Cs_LFImg_Shutter__b1c11.go_low(t - 100e-3)
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t - 1300e-3, duration=1200e-3, initial=-10, final=code_65511, samplerate=FAST_FREQ)
    # ct.Cs_HFImg_Shutter__b1c06.go_high(t - 80e-3)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t - 1000e-3, duration=950e-3, initial=7.55005, final=8.29987, samplerate=SLOW_FREQ)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 40e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t - 35e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_high(t - 7e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t - 5e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t - 5e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t - 5e-3)
    # # 1.10_Cs_Oneshot_Bypass: 5 JUMP — no new channel
    # # 1.23_CS_EOM_SW: 0 JUMP — no new channel
    # ct.Cs_Rep_AO_AM__b3c25.constant(t - 0.02e-3, 2.99988)
    # ct.Cs_Andor_Trig__b1c04.go_high(t)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t)
    # ct.Cs_HOP_Shutter__b1c09.go_low(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 0.02e-3)
    # # 1.23_CS_EOM_SW: 5 JUMP — no new channel
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 0.02e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 0.04e-3)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t + 0.04e-3, 0)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.04e-3)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 0.1e-3)
    # # 1.10_Cs_Oneshot_Bypass: 0 JUMP — no new channel
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 30e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 60e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t + 495e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 495e-3)
    # # 1.10_Cs_Oneshot_Bypass: 5 JUMP — no new channel
    # ct.Cs_VImg_Shutter__b1c15.go_low(t + 500e-3)
    # ct.Cs_Andor_Trig__b1c04.go_high(t + 500e-3)
    # # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 500.02e-3)  # replaced by ramp at t + 500.04e-3 in proc 030
    # ct.Cs_HFImg_AO_Sw__b1c05.ramp(t=t + 500.02e-3, duration=0.02e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 500.1e-3)
    # # 1.10_Cs_Oneshot_Bypass: 0 JUMP — no new channel
    # # ct.CS_HFImg_Freq__b3c22.constant(t + 600e-3, code_65511)  # replaced by ramp at t + 2000e-3 in proc 030
    # ct.Cs_Andor_Trig__b1c04.go_high(t + 990e-3)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 990.1e-3)
    # # 7.7_N_Cs_MOT_Freq: -2.99988 JUMP — no new channel
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t + 600e-3, duration=1400e-3, initial=code_65511, final=-10, samplerate=FAST_FREQ)
    # # 7.7_N_Cs_MOT_Freq: -7.6001 COARSE — no new channel

    # # procedure 031: test_trigger
    # t = code_65501/1e3
    # add_time_marker(t, 'test_trigger')
    # ct.Spec_Analyzer_Trig__b2c09.go_low(t)
    # ct.Spec_Analyzer_Trig__b2c09.go_low(t + 1e-3)

    # # procedure 032: Cs_molasses_dark
    # t = 12500e-3
    # add_time_marker(t, 'Cs_molasses_dark')
    # ct.Cs_3DMOT_Shutter__b1c03.go_low(t - 12e-3)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t)
    # # 7.7_N_Cs_MOT_Freq: -3.99994 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.6535 FINE — no new channel

    # procedure 033: Dual_Color_Combine
    t = 24700e-3
    add_time_marker(t, 'Dual_Color_Combine')
    # ct.oTOP_FCarrier__b4c07.constant(t - 500e-3, 2.09991)  # replaced by ramp at t + 500e-3 in proc 033
    ct.oTOP_FCarrier__b4c07.ramp(t=t - 500e-3, duration=1000e-3, initial=2.09991, final=1.05011, samplerate=FAST_FREQ)
    # ct.Dual_1064_Int_Lock__b4c16.constant(t + 500e-3, 0.0750732)  # replaced by ramp at t + 1000e-3 in proc 033
    # ct.Dual_780_Int_Lock__b3c30.constant(t + 500e-3, 1.79993)  # replaced by ramp at t + 1000e-3 in proc 033
    # ct.oTOP_Int_Lock__b4c08.constant(t + 1000e-3, 0.239868)  # replaced by ramp at t + 3000e-3 in proc 033
    ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 500e-3, duration=500e-3, initial=0.0750732, final=0.950012, samplerate=FAST_FREQ)
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t + 500e-3, duration=500e-3, initial=1.79993, final=0.799866, samplerate=FAST_FREQ)
    ct.oTOP_Int_Lock__b4c08.ramp(t=t + 1000e-3, duration=2000e-3, initial=0.239868, final=0.00305176, samplerate=FAST_FREQ)
    ct.oTOP_AO_AM__b4c06.constant(t + 3000.02e-3, 0)
    ct.oTOP_FCarrier__b4c07.constant(t + 3001e-3, 2.00012)
    ct.oTOP_AO_AM__b4c06.constant(t + 3002e-3, 10)

    # procedure 034: Li_Img_Freq_Ramp_Down
    t = code_65501/1e3
    add_time_marker(t, 'Li_Img_Freq_Ramp_Down')
    ct.BFL_Int_Lock__b3c02.constant(t + 20e-3, 0)
    # ct.Li_Img_Freq__b4c01.constant(t + 501e-3, code_65508)  # replaced by ramp at t + 2501e-3 in proc 034
    ct.Li_Img_Freq__b4c01.ramp(t=t + 501e-3, duration=2000e-3, initial=code_65508, final=-5.24994, samplerate=SLOW_FREQ)
    ct.Li_Img_Freq__b4c01.constant(t + 2502e-3, -5.24994)

    # procedure 035: coil_cool_down
    t = code_65502/1e3
    add_time_marker(t, 'coil_cool_down')
    ct.Scope_Trig__b2c08.go_low(t + 2000e-3)

    # # procedure 036: MW_Calibration_load
    # t = 18800e-3
    # add_time_marker(t, 'MW_Calibration_load')
    # ct.Bitter_Lower_FF__b3c14.constant(t - 2e-3, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t - 2e-3, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t - 2e-3, 0)
    # # 2.7_V_AH: 0.188293 JUMP — no new channel
    # # 2.6_V_HH: -0.0201416 JUMP — no new channel
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.30011)
    # # 7.7_N_Cs_MOT_Freq: -7.30011 JUMP — no new channel
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
    # ct.Cs_Rep_Freq__b3c26.constant(t, 9.37012)
    # # 1.31_Cs_Li_Zeswitch → 5 (Zeeman: 1.31=5, 1.32=5)
    # ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    # ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    # ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    # ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    # ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    # # 1.32_ZCurrents → 5 (Zeeman: 1.31=5, 1.32=5)
    # ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    # ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    # ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    # ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    # ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 5)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    # ct.Bias_X_HH.constant(t, -1.00006)
    # ct.Bias_X_AH.constant(t, 1.00006)
    # ct.Bias_Y_HH.constant(t, 1.00006)
    # ct.Bias_Y_AH.constant(t, 0)
    # ct.Bias_Z_HH.constant(t, -3.99994)
    # ct.Bias_Z_AH.constant(t, 0.19989)
    # ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    # ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    # ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    # ct.Bitter_Lower_CV__b3c13.constant(t, 2.30011)
    # ct.Bitter_Upper_CV__b3c17.constant(t, 2.3999)
    # ct.Bitter_Upper_CC__b3c16.constant(t, 5)
    # ct.Bitter_Lower_CC__b3c12.constant(t, 5)
    # # 7.0_oTOP_Int_lok: 0.599976 JUMP — no new channel
    # # 7.6_oTOP_fcarrier: 1.75598 JUMP — no new channel
    # # 7.4_oTOP_mod_AM: 1.19995 JUMP — no new channel
    # # 2.1_CS_Rep_AO_AM: 5 JUMP — no new channel
    # # 7.3_oTOP_AO_AM: 10 JUMP — no new channel
    # # 7.2_Cs_VHF_AO_AM: 10 JUMP — no new channel
    # # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    # ct.Cs_Rep_Shutter__b1c12.go_high(t)
    # # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 2970e-3, 2.30011)  # replaced by ramp at t + 3000e-3 in proc 036
    # # 1.32_ZCurrents → 0 (Zeeman: 1.31=5, 1.32=0)
    # ct.Zeeman_C1__b4c10.constant(t + 2990e-3, 0)
    # ct.Zeeman_C2__b4c11.constant(t + 2990e-3, 0)
    # ct.Zeeman_C3__b4c12.constant(t + 2990e-3, 0)
    # ct.Zeeman_C4__b4c13.constant(t + 2990e-3, 0)
    # ct.Zeeman_C5__b4c14.constant(t + 2990e-3, 0)
    # ct.Cs_Zeeman_Shutter__b1c17.go_low(t + 2990e-3)
    # ct.Cs_2DMOT_Shutter__b1c01.go_low(t + 2990e-3)
    # # ct.Bias_X_HH.constant(t + 2990e-3, -2.5)  # replaced by ramp at t + 3048e-3 in proc 036
    # # ct.Bias_X_AH.constant(t + 2990e-3, 1.00006)  # replaced by ramp at t + 3048e-3 in proc 036
    # # ct.Bias_Y_HH.constant(t + 2990e-3, 1.00006)  # replaced by ramp at t + 3048e-3 in proc 036
    # # ct.Bias_Y_AH.constant(t + 2990e-3, 0)  # replaced by ramp at t + 3048e-3 in proc 036
    # # ct.Bias_Z_HH.constant(t + 2990e-3, 0.299988)  # replaced by ramp at t + 3048e-3 in proc 036
    # ct.Bias_Z_AH.constant(t + 2990e-3, 0.19989)
    # ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t + 2970e-3, duration=30e-3, initial=2.30011, final=0.499878, samplerate=FAST_FREQ)
    # # 2.1_CS_Rep_AO_AM: 5 JUMP — no new channel
    # ct.Cs_VRep_Shutter__b1c16.go_low(t + 3000e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_low(t + 3000e-3)
    # # 2.6_V_HH: -0.0201416 JUMP — no new channel
    # # 2.7_V_AH: 0.188293 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.30011 JUMP — no new channel
    # # 7.0_oTOP_Int_lok: 0.599976 JUMP — no new channel
    # # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 3040e-3, 0.499878)  # replaced by ramp at t + 3049e-3 in proc 036
    # # ct.Cs_Rep_Freq__b3c26.constant(t + 3040e-3, 9.37012)  # replaced by ramp at t + 3048.98e-3 in proc 036
    # # 2.6_V_HH: -0.000915527 COARSE — no new channel
    # # 2.7_V_AH: 0.11261 COARSE — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.00012 FINE — no new channel
    # ct.Bias_X_HH.ramp(t=t + 2990e-3, duration=58e-3, initial=-2.5, final=2.00012, samplerate=SLOW_FREQ)
    # ct.Bias_X_AH.ramp(t=t + 2990e-3, duration=58e-3, initial=1.00006, final=1.00006, samplerate=SLOW_FREQ)
    # ct.Bias_Y_HH.ramp(t=t + 2990e-3, duration=58e-3, initial=1.00006, final=-0.750122, samplerate=SLOW_FREQ)
    # ct.Bias_Y_AH.ramp(t=t + 2990e-3, duration=58e-3, initial=0, final=0.499878, samplerate=SLOW_FREQ)
    # ct.Bias_Z_HH.ramp(t=t + 2990e-3, duration=58e-3, initial=0.299988, final=-0.499878, samplerate=SLOW_FREQ)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t + 3040e-3, duration=8.98e-3, initial=9.37012, final=8.37494, samplerate=FAST_FREQ)
    # # 2.6_V_HH: 0.0140381 COARSE — no new channel
    # # 2.7_V_AH: 0.0756836 COARSE — no new channel
    # ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t + 3040e-3, duration=9e-3, initial=0.499878, final=0.299988, samplerate=FAST_FREQ)
    # # 7.0_oTOP_Int_lok: 2.00012 COARSE — no new channel

    # # procedure 037: MW_Calibration_Molasses
    # t = 21850e-3
    # add_time_marker(t, 'MW_Calibration_Molasses')
    # ct.Cs_Rep_Shutter__b1c12.go_low(t - 11e-3)
    # ct.Cs_RSC_AO_Sw__b1c13.go_low(t - 5e-3)
    # ct.Cs_RSC_Shutter__b1c14.go_high(t - 4e-3)
    # # ct.Cs_Rep_Freq__b3c26.constant(t - 1e-3, 8.37494)  # replaced by ramp at t in proc 037
    # ct.Cs_HOP_Shutter__b1c09.go_high(t - 1e-3)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # # 7.7_N_Cs_MOT_Freq: -7.00012 JUMP — no new channel
    # # ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.700073)  # replaced by ramp at t + 5e-3 in proc 037
    # ct.Bias_X_HH.constant(t, 0.249939)
    # ct.Bias_X_AH.constant(t, -0.390015)
    # ct.Bias_Y_HH.constant(t, -1.70013)
    # ct.Bias_Y_AH.constant(t, 2.86438)
    # ct.Bias_Z_HH.constant(t, -0.299988)
    # ct.Bias_Z_AH.constant(t, -1.00006)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t - 1e-3, duration=1e-3, initial=8.37494, final=9.37012, samplerate=FAST_FREQ)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t)
    # # 2.7_V_AH: -3.99994 JUMP — no new channel
    # ct.oTOP_FCarrier__b4c07.constant(t + 0.5e-3, 0)
    # ct.Cs_RSC_AO_Sw__b1c13.go_high(t + 1e-3)
    # # ct.Cs_Rep_Freq__b3c26.constant(t + 3.5e-3, 9.37012)  # replaced by ramp at t + 5e-3 in proc 037
    # # ct.oTOP_FCarrier__b4c07.constant(t + 4e-3, 0)  # replaced by ramp at t + 4.5e-3 in proc 037
    # ct.oTOP_FCarrier__b4c07.ramp(t=t + 4e-3, duration=0.5e-3, initial=0, final=5, samplerate=FAST_FREQ)
    # # 2.1_CS_Rep_AO_AM: 0 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -3.25012 FINE — no new channel
    # ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t, duration=5e-3, initial=0.700073, final=0.100098, samplerate=FAST_FREQ)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t + 3.5e-3, duration=1.5e-3, initial=9.37012, final=5.66986, samplerate=FAST_FREQ)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 5e-3)
    # # 7.7_N_Cs_MOT_Freq: -3.25012 JUMP — no new channel
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 5.02e-3, 0)
    # ct.Bias_X_HH.constant(t + 5.02e-3, 0.700073)
    # ct.Bias_X_AH.constant(t + 5.02e-3, -0.290527)
    # ct.Bias_Y_HH.constant(t + 5.02e-3, -1.61011)
    # ct.Bias_Y_AH.constant(t + 5.02e-3, 2.78717)
    # ct.Bias_Z_HH.constant(t + 5.02e-3, -0.499878)
    # ct.Bias_Z_AH.constant(t + 5.02e-3, -0.400085)
    # # 7.7_N_Cs_MOT_Freq: 0 FINE — no new channel
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 6.5e-3, 0.0250244)
    # # 2.1_CS_Rep_AO_AM: 0 JUMP — no new channel
    # # 2.1_CS_Rep_AO_AM: 1.74988 FINE — no new channel
    # ct.Cs_HOP_Shutter__b1c09.go_low(t + 21e-3)
    # ct.Cs_RSC_Shutter__b1c14.go_low(t + 31e-3)
    # # 2.1_CS_Rep_AO_AM: 1.74988 JUMP — no new channel
    # # ct.Cs_Rep_Freq__b3c26.constant(t + 34e-3, 5.66986)  # replaced by ramp at t + 35e-3 in proc 037
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t + 34e-3, duration=1e-3, initial=5.66986, final=5.75012, samplerate=FAST_FREQ)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 36.6e-3, 0)
    # # 2.1_CS_Rep_AO_AM: 0 FINE — no new channel
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 36.7e-3)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 36.7e-3)
    # # ct.oTOP_FCarrier__b4c07.constant(t + 37.6e-3, 5)  # replaced by ramp at t + 38.6e-3 in proc 037
    # ct.oTOP_FCarrier__b4c07.ramp(t=t + 37.6e-3, duration=1e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Cs_RSC_AO_Sw__b1c13.go_low(t + 39e-3)
    # ct.Cs_3DMOT_Shutter__b1c03.go_low(t + 39e-3)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 39e-3)
    # # ct.Cs_Rep_Freq__b3c26.constant(t + 39e-3, 5.75012)  # replaced by ramp at t + 69e-3 in proc 037
    # # 7.7_N_Cs_MOT_Freq: 0 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -7.65015 FINE — no new channel
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t + 39e-3, duration=30e-3, initial=5.75012, final=9.37012, samplerate=FAST_FREQ)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 539e-3)
    # ct.Cs_RSC_AO_Sw__b1c13.go_high(t + 539e-3)
    # ct.oTOP_FCarrier__b4c07.constant(t + 539e-3, 5)
    # # 2.1_CS_Rep_AO_AM: 0 JUMP — no new channel
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 539e-3)

    # # procedure 038: MW_Calibration_Trap
    # t = 21887e-3
    # add_time_marker(t, 'MW_Calibration_Trap')
    # ct.Bitter_Upper_CV__b3c17.constant(t - 32e-3, 2.30011)
    # ct.Bitter_Lower_CV__b3c13.constant(t - 32e-3, 1.79993)
    # ct.Bitter_Lower_CC__b3c12.constant(t - 32e-3, 5)
    # ct.Bitter_Upper_CC__b3c16.constant(t - 32e-3, 5)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t - 5e-3, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t - 0.5e-3, 5)
    # # ct.Bias_X_HH.constant(t - 0.2e-3, 0.650024)  # replaced by ramp at t in proc 038
    # # ct.Bias_X_AH.constant(t - 0.2e-3, -0.290527)  # replaced by ramp at t in proc 038
    # # ct.Bias_Y_HH.constant(t - 0.2e-3, -1.48499)  # replaced by ramp at t in proc 038
    # # ct.Bias_Y_AH.constant(t - 0.2e-3, 2.78717)  # replaced by ramp at t in proc 038
    # # ct.Bias_Z_HH.constant(t - 0.2e-3, -0.450134)  # replaced by ramp at t in proc 038
    # ct.FF_Disable__b1c24.go_low(t - 0.2e-3)
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t - 0.1e-3, 3.50006)  # replaced by ramp at t + 0.1e-3 in proc 038
    # # 2.6_V_HH: 0.713501 JUMP — no new channel
    # # 2.7_V_AH: -0.713501 JUMP — no new channel
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    # ct.Bias_X_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=0.650024, final=6.00006, samplerate=FAST_FREQ)
    # ct.Bias_X_AH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-0.290527, final=0.19989, samplerate=FAST_FREQ)
    # ct.Bias_Y_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-1.48499, final=-3.591, samplerate=FAST_FREQ)
    # ct.Bias_Y_AH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=2.78717, final=3.52295, samplerate=FAST_FREQ)
    # ct.Bias_Z_HH.ramp(t=t - 0.2e-3, duration=0.2e-3, initial=-0.450134, final=-5, samplerate=FAST_FREQ)
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t - 0.1e-3, duration=0.2e-3, initial=3.50006, final=5.49988, samplerate=FAST_FREQ)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 0.8e-3, 4.58008)
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1e-3, 4.70001)  # replaced by ramp at t + 1.2e-3 in proc 038
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1e-3, duration=0.2e-3, initial=4.70001, final=4.57001, samplerate=FAST_FREQ)
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1.2e-3, duration=0.3e-3, initial=4.57001, final=4.46014, samplerate=FAST_FREQ)
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 8e-3, 4.46014)  # replaced by ramp at t + 408e-3 in proc 038
    # # 2.6_V_HH: 0.713501 JUMP — no new channel
    # # 2.7_V_AH: -0.713501 JUMP — no new channel
    # # 7.4_oTOP_mod_AM: 1.19995 JUMP — no new channel
    # # 2.6_V_HH: 2.77893 COARSE — no new channel
    # # 2.7_V_AH: -0.826416 COARSE — no new channel
    # # 7.4_oTOP_mod_AM: -0.650024 COARSE — no new channel
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 8e-3, duration=400e-3, initial=4.46014, final=0, samplerate=SLOW_FREQ)
    # ct.FF_Disable__b1c24.go_high(t + 409e-3)
    # # 7.0_oTOP_Int_lok: 2.00012 JUMP — no new channel
    # # 7.4_oTOP_mod_AM: -0.964966 FINE — no new channel
    # # 2.7_V_AH: -0.140686 COARSE — no new channel
    # # 7.6_oTOP_fcarrier: 1.75598 JUMP — no new channel
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # # 2.6_V_HH: 2.77893 JUMP — no new channel
    # # 2.7_V_AH: -0.140686 JUMP — no new channel
    # # ct.Bias_X_AH.constant(t + 600e-3, 0.202637)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bias_Y_AH.constant(t + 600e-3, 3.52295)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bias_X_HH.constant(t + 600e-3, 6.00006)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bitter_Upper_CV__b3c17.constant(t + 600e-3, 2.30011)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bitter_Lower_CV__b3c13.constant(t + 600e-3, 1.79993)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bias_Y_HH.constant(t + 600e-3, -3.591)  # replaced by ramp at t + 800e-3 in proc 038
    # # ct.Bias_Z_HH.constant(t + 600e-3, -5)  # replaced by ramp at t + 800e-3 in proc 038
    # # 7.0_oTOP_Int_lok: 1.79993 COARSE — no new channel
    # # 2.6_V_HH: 6.43982 COARSE — no new channel
    # # 2.7_V_AH: -0.291443 COARSE — no new channel
    # # 2.6_V_HH: 6.43188 JUMP — no new channel
    # # 2.7_V_AH: 3.1015 JUMP — no new channel
    # ct.Bitter_Precision_Disable__b1c00.go_low(t + 767.72e-3)
    # # 7.6_oTOP_fcarrier: 0.899963 COARSE — no new channel
    # # 2.6_V_HH: -0.539856 COARSE — no new channel
    # # 2.7_V_AH: 3.51593 COARSE — no new channel
    # ct.Bias_X_AH.ramp(t=t + 600e-3, duration=200e-3, initial=0.202637, final=-0.319519, samplerate=SLOW_FREQ)
    # ct.Bias_Y_AH.ramp(t=t + 600e-3, duration=200e-3, initial=3.52295, final=2.7533, samplerate=SLOW_FREQ)
    # ct.Bias_X_HH.ramp(t=t + 600e-3, duration=200e-3, initial=6.00006, final=0.390015, samplerate=SLOW_FREQ)
    # ct.Bitter_Upper_CV__b3c17.ramp(t=t + 600e-3, duration=200e-3, initial=2.30011, final=3.20007, samplerate=SLOW_FREQ)
    # ct.Bitter_Lower_CV__b3c13.ramp(t=t + 600e-3, duration=200e-3, initial=1.79993, final=2.69989, samplerate=SLOW_FREQ)
    # ct.Bias_Y_HH.ramp(t=t + 600e-3, duration=200e-3, initial=-3.591, final=5, samplerate=SLOW_FREQ)
    # ct.Bias_Z_HH.ramp(t=t + 600e-3, duration=200e-3, initial=-5, final=-0.302429, samplerate=SLOW_FREQ)

    # set all channels back to LabVIEW init values
    t = 32203e-3
    ct.Bitter_V_AH.constant(t, 0.188293)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 3.99994)
    ct.Li_Img_Freq__b4c01.constant(t, -5.24994)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.oTOP_FCarrier__b4c07.constant(t, 1.79993)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_V_HH.constant(t, -0.0183105)
    ct.Li_Img_AO_Sw__b1c29.go_high(t)
    ct.DMD_AO_Sw__b1c19.go_high(t)
    ct.Cs_Andor_Trig__b1c04.go_low(t)
    ct.Li_EOM_AO_Sw__b1c26.go_high(t)
    ct.DMD_AO_FM__b1c18.go_low(t)
    ct.Li_MOT_AO_Sw__b1c30.go_high(t)
    ct.Li_Rep_AO_Sw__b2c00.go_high(t)
    ct.Li_Rep_Shutter__b2c01.go_high(t)
    ct.Li_MOT_Shutter__b1c31.go_high(t)
    ct.Li_VImg_Shutter__b2c02.go_low(t)
    ct.Li_Zeeman_Shutter__b2c03.go_high(t)
    ct.Li_EOM_H_Shutter__b1c27.go_low(t)
    ct.MW_Trig__b2c04.go_low(t)
    ct.Pixelfly_Trig__b2c07.go_low(t)
    ct.Cs_RSC_AO_Sw__b1c13.go_high(t)
    ct.Li_HImg_Shutter__b1c28.go_low(t)
    ct.Cs_RSC_Shutter__b1c14.go_low(t)
    ct.Scope_Trig__b2c08.go_low(t)
    ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_LI)
    ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_LI)
    ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_LI)
    ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_LI)
    ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_LI)
    ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    ct.Cs_VRep_Shutter__b1c16.go_high(t)
    ct.Cs_Rep_Shutter__b1c12.go_high(t)
    ct.Cs_VImg_Shutter__b1c15.go_low(t)
    ct.Cs_HImg_Shutter__b1c07.go_low(t)
    ct.Dual_780_AO_Sw__b1c23.go_high(t)
    ct.Dual_1064_AO_Sw__b1c22.go_high(t)
    ct.Cs_HFImg_Shutter__b1c06.go_low(t)
    ct.Cs_LFImg_Shutter__b1c11.go_high(t)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t)
    ct.Spec_Analyzer_Trig__b2c09.go_low(t)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    ct.FF_Disable__b1c24.go_low(t)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t)
    ct.DMD_Shutter__b1c21.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_high(t)
    ct.DMD_Movie_Trig__b1c20.go_low(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    ct.Bitter_Precision_Disable__b1c00.go_high(t)
    ct.Li_MOT_AO_AM__b4c02.constant(t, 10)
    ct.Li_Rep_AO_AM__b4c05.constant(t, 10)
    ct.DMD_AO_AM__b3c29.constant(t, 3.8)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.51)
    ct.Li_MRep_AO_FM__b4c04.constant(t, 0.40863)
    ct.Li_Img_AO_AM__b4c00.constant(t, 10)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 2.5)
    ct.CS_HFImg_Freq__b3c22.constant(t, -10)
    ct.Bias_X_HH.constant(t, -1)
    ct.Bias_X_AH.constant(t, 1)
    ct.Bias_Y_AH.constant(t, 0)
    ct.Bias_Y_HH.constant(t, 1)
    ct.Bias_Z_AH.constant(t, -1)
    ct.Bias_Z_HH.constant(t, -6)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.5)
    ct.BFL_AO_Sw__b3c01.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.BFL_Int_Lock__b3c02.constant(t, 0.1)
    ct.Pixelfly_Shutter__b2c06.go_high(t)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    ct.Aerotech_Control__b3c00.constant(t, 0)
    ct.Li_MOT_Freq__b4c03.constant(t, 5.28442)
    ct.Cs_EOM_Freq_b4c15.constant(t, 9)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.3)
    ct.oTOP_Int_Lock__b4c08.constant(t, 0.3)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, 5)
    ct.oTOP_AO_AM__b4c06.constant(t, 10)
    ct.oTOP_Mod_AM__b4c09.constant(t, 0)
    ct.Li_EOM_Freq__b3c31.constant(t, -4.5)
    ct.Cs_RSC_AO_AM__b3c27.constant(t, 5)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.15)
    stop(t+10e-6)
