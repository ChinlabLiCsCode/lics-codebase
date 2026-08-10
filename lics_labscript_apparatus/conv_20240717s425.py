from labscript import start, stop, add_time_marker, wait
from lics_labscript_apparatus.connection_table import ConnectionTable

SLOW_FREQ = 1e3   # 1 ms per edge
FAST_FREQ = 50e3  # 20 us per edge

# Cs MOT Zeeman currents
ZEEMAN_C1_CS = 0
ZEEMAN_C2_CS = 0.45
ZEEMAN_C3_CS = 0.2
ZEEMAN_C4_CS = 0.05
ZEEMAN_C5_CS = 0.45

# Li MOT Zeeman currents
ZEEMAN_C1_LI = 2.5
ZEEMAN_C2_LI = 3.5
ZEEMAN_C3_LI = 3.5
ZEEMAN_C4_LI = 4.25
ZEEMAN_C5_LI = 0.8

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
# 001	3.1_Dual_1064_Int_Lock  	    0.0000		1	ct.Dual_1064_Int_Lock__b4c16
# 002	3.2_Li_Img_Freq         	    1.0001		1	ct.Li_Img_Freq__b4c01
# 003	3.3_lower_FF            	    0.0000		1	ct.Bitter_Lower_FF__b3c14
# 004	3.4_oTOP_fcarrier       	    5.0000		1	ct.oTOP_FCarrier__b4c07
# 005	3.5_AH_upper_FF         	    0.0000		1	ct.Bitter_AH_Upper_FF__b3c09
# 006	3.6_HH_upper_FF         	    0.0000		1	ct.Bitter_HH_Upper_FF__b3c10
# 007	3.7_N_V_HH              	   -0.0183		1	ct.Bitter_V_HH
# 008	2.0_Dual_780nm_Int_Lock 	    5.0000		1	# no new channel
# 009	2.1_CS_Rep_AO_AM        	    5.0000		1	# no new channel
# 010	2.2_                    	    0.0000		1	# no new channel
# 011	2.3_Li_MRep_AO_FM       	    0.4086		1	# no new channel
# 012	2.4_                    	    0.0000		1	# no new channel
# 013	2.5_                    	    0.0000		1	# no new channel
# 014	2.6_V_HH                	   -0.0183		1	# no new channel
# 015	2.7_V_AH                	    0.1883		1	# no new channel
# 016	7.0_oTOP_Int_lok        	    0.0000		1	# no new channel
# 017	7.1_CS_Rep_AO_AM        	    5.0000		1	# no new channel
# 018	7.2_ZDT_AO_AM           	   10.0000		1	# no new channel
# 019	7.3_oTOP_AO_AM          	   10.0000		1	# no new channel
# 020	7.4_oTOP_mod_AM         	    0.0000		1	# no new channel
# 021	7.5_Dual_1064_Int_Lock  	    0.0000		1	# no new channel
# 022	7.6_oTOP_fcarrier       	    0.9000		1	# no new channel
# 023	7.7_N_Cs_MOT_Freq       	   -7.1500		1	# no new channel
# 024	1.3_Li_Img_AO_Sw        	    5.0000		0	ct.Li_Img_AO_Sw__b1c29
# 025	1.4_Cs_3DMOT_AO_Sw      	    5.0000		0	# no new channel
# 026	1.5_Li_Img_OneShot_Sw   	    5.0000		0	ct.DMD_AO_Sw__b1c19
# 027	1.6_Andor_Trigger       	    0.0000		0	ct.Cs_Andor_Trig__b1c04
# 028	1.7_Cs_2DMOT_AO_Sw      	    5.0000		0	ct.Li_EOM_AO_Sw__b1c26
# 029	1.8_Cs_2DMOT_Shutter    	    0.0000		0	# no new channel
# 030	1.9_Cs_2DR_Shutter      	    0.0000		0	ct.DMD_AO_FM__b1c18
# 031	1.10_Cs_V_Img_Shutter   	    0.0000		0	# no new channel
# 032	1.11_Li_MOT_AO_Sw       	    5.0000		0	ct.Li_MOT_AO_Sw__b1c30
# 033	1.12_Li_Rep_AO_Sw       	    5.0000		0	ct.Li_Rep_AO_Sw__b2c00
# 034	1.13_Li_Rep_Shutter     	    5.0000		0	ct.Li_Rep_Shutter__b2c01
# 035	1.14_Li_MOT_Shutter     	    5.0000		0	ct.Li_MOT_Shutter__b1c31
# 036	1.15_Li_V_Img_Shutter   	    0.0000		0	ct.Li_VImg_Shutter__b2c02
# 037	1.16_Li_Zeeman_Shutter  	    5.0000		0	ct.Li_Zeeman_Shutter__b2c03
# 038	1.17_Cs_H_Img_Shutter   	    0.0000		0	# no new channel
# 039	1.18_Cs_Opt_Pump_Shutter	    0.0000		0	ct.Li_EOM_H_Shutter__b1c27
# 040	1.19_Cs_ZM_shutter      	    5.0000		0	# no new channel
# 041	1.20_MW_pulse_SW        	    0.0000		0	ct.MW_Trig__b2c04
# 042	1.21_pixelfly trigger   	    0.0000		0	ct.Pixelfly_Trig__b2c07
# 043	1.22_MW_INCR_UP         	    5.0000		0	# no new channel
# 044	1.23_CS_ZM_rep_Sh       	    5.0000		0	# no new channel
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
# 079	6.25_N_2DMOT_AO_Sw      	    5.0000		0	ct.DMD_Shutter__b1c21
# 080	6.26_N_CsOP_Shut_H      	    5.0000		0	ct.Cs_HOP_Shutter__b1c09
# 081	6.27_Cs_HF_AO_AM        	    5.0000		0	ct.DMD_Movie_Trig__b1c20
# 082	6.28                    	    0.0000		0	# no new channel
# 083	6.29_oTOP_Pos_Lock_Enabl	    0.0000		0	ct.oTOP_Pos_Lock_Enable__b2c05
# 084	6.30                    	    0.0000		0	# no new channel
# 085	6.31_B_Precision_Disable	    5.0000		0	ct.Bitter_Precision_Disable__b1c00
# 086	4.0_Li_MOT_AO_AM        	   10.0000		1	ct.Li_MOT_AO_AM__b4c02
# 087	4.1_Li_Rep_AO_AM        	   10.0000		1	ct.Li_Rep_AO_AM__b4c05
# 088	4.2_Dual_780_AO_AM      	   10.0000		1	# no new channel
# 089	4.3_Dual_1064_AO_AM     	   10.0000		1	# no new channel
# 090	4.4_Cs_2DMOT_AO_AM      	    3.8000		1	ct.DMD_AO_AM__b3c29
# 091	4.5_N_Cs_Repump_Freq    	    6.4900		1	ct.Cs_Rep_Freq__b3c26
# 092	4.6_Li_MRep_AO_FM       	    0.4086		1	ct.Li_MRep_AO_FM__b4c04
# 093	4.7_Li_Img_AO_AM        	   10.0000		1	ct.Li_Img_AO_AM__b4c00
# 094	5.8_Dual_780nm_Int_Lock 	    5.0000		1	ct.Dual_780_Int_Lock__b3c30
# 095	5.9_Cs_LF_Img_AO_AM     	   10.0000		1	# no new channel
# 096	5.10_CS_HF_Img_Freq     	  -10.0000		1	ct.CS_HFImg_Freq__b3c22
# 097	5.11_BFL_AO_AM          	   10.0000		1	# no new channel
# 098	5.12_Bias_1/2_HH_x      	   -0.5000		1	ct.Bias_X_HH
# 099	5.13_Bias_1/2_AH_-x     	    1.0000		1	ct.Bias_X_AH
# 100	5.14_Bias_3/4_AH_-y     	    0.5000		1	ct.Bias_Y_AH
# 101	5.15_Bias_3/4_HH_y      	    0.8000		1	ct.Bias_Y_HH
# 102	5.16_Bias_5/6_AH_z      	    0.2000		1	ct.Bias_Z_AH
# 103	5.17_Bias_5/6_HH_-z     	   -0.8000		1	ct.Bias_Z_HH
# 104	5.18_COIL_BOT_CC        	    1.0000		1	ct.Bitter_Lower_CC__b3c12
# 105	5.19_COIL_TOP_CV        	    2.0000		1	ct.Bitter_Upper_CV__b3c17
# 106	5.20_COIL_TOP_CC        	    1.0000		1	ct.Bitter_Upper_CC__b3c16
# 107	5.21_COIL_BOT_CV        	    1.5000		1	ct.Bitter_Lower_CV__b3c13
# 108	5.22_BFL_AO_SW          	    5.0000		1	ct.BFL_AO_Sw__b3c01
# 109	5.23_COIL_TOP_AH        	    5.0000		1	ct.Bitter_Upper_AH_Sw__b3c15
# 110	5.24_COIL_TOP_HH        	    0.0000		1	ct.Bitter_Upper_HH_Sw__b3c18
# 111	5.25_Li_Img_AO_FM       	   -2.0000		1	ct.BFL_Int_Lock__b3c02
# 112	5.26_H_Pixelfly_Shutter 	    0.0000		1	ct.Pixelfly_Shutter__b2c06
# 113	5.27_IServo_FB_Switch   	    0.0000		1	ct.Bitter_IServo_FB_Sw__b3c11
# 114	5.28_aerotech_trigger   	    0.0000		1	ct.Aerotech_Control__b3c00
# 115	5.29_Li_MOT_Freq        	    5.2844		1	ct.Li_MOT_Freq__b4c03
# 116	5.30_V_Pixelfly_Shutter 	    0.0000		1	ct.Cs_EOM_Freq_b4c15
# 117	5.31_Cs_3D_AO_AM        	    2.3000		1	ct.Cs_3DMOT_AO_AM__b3c21
# 118	8.0_oTOP_Int_lok        	    0.0000		1	ct.oTOP_Int_Lock__b4c08
# 119	8.1_Cs_Rep_AO_AM        	    3.0000		1	ct.Cs_Rep_AO_AM__b3c25
# 120	8.2_Cs_VHF_AO_AM        	    0.0000		1	ct.Cs_VImg_AO_AM__b3c28
# 121	8.3_oTOP_AO_AM          	    0.0000		1	ct.oTOP_AO_AM__b4c06
# 122	8.4_oTOP_MOD_AM         	    0.0000		1	ct.oTOP_Mod_AM__b4c09
# 123	8.5                     	    0.0000		1	ct.Li_EOM_Freq__b3c31
# 124	8.6_Cs_RSC_AO_AM        	    5.0000		1	ct.Cs_RSC_AO_AM__b3c27
# 125	8.7_N_CS_MOT_FREQ       	   -7.1500		1	ct.Cs_MOT_Freq__b3c24

# proc no	name							  time (ms)e-3	enabled
# -------	----							  ------------	------
# 000		Cs_MOT_Loading          	3700e-3		1
# 001		Cs_Molasses_Cooling     	7495e-3		1
# 002		Cs_H_Imaging            	code_65501/1e3		1
# 003		Cs_RSC1                 	7500e-3		0
# 004		Aerotech_return         	12600e-3		0
# 005		Dual_Imaging_H          	code_65501/1e3		0
# 006		MW                      	16116e-3		0
# 007		FB_Bias_field           	12600e-3		0
# 008		Cs_Dark                 	7534e-3		0
# 009		Li_V_Imaging_2          	code_65501/1e3		0
# 010		Cs_Evaporation          	7600e-3		0
# 011		Spare                   	code_65510/1e3		0
# 012		Li_Feshbach             	7000e-3		0
# 013		Dual_Evap               	24700e-3		0
# 014		Li_H_Imaging            	code_65501/1e3		0
# 015		Li_V_Imaging            	code_65501/1e3		0
# 016		Cs_Levitation1          	7532e-3		0
# 017		Li_Evaporation          	7000e-3		0
# 018		Li_Dark                 	7000e-3		0
# 019		Cs_V_Imaging            	code_65501/1e3		0
# 020		Li_CMOT                 	6999.98e-3		0
# 021		Cs_CMOT                 	7445e-3		1
# 022		Li_MOT_Loading          	2015e-3		0
# 023		True_TOF                	code_65500/1e3		1
# 024		Li_Killing              	21600e-3		0
# 025		Low_Field_BEC_Field     	7519e-3		0
# 026		FB_Bias_Field_off       	code_65502/1e3		1
# 027		Magnetizer              	1e-3		1
# 028		Unlevitation            	21600e-3		0
# 029		Cs_HF_H_Imaging         	code_65501/1e3		0
# 030		Cs_HF_V_Imaging         	code_65501/1e3		0
# 031		test_trigger            	code_65501/1e3		0
# 032		Cs_molasses_dark        	7500e-3		1
# 033		Dual_Color_Combine      	21700e-3		0
# 034		Li_Img_Freq_Ramp_Down   	code_65501/1e3		0
# 035		MW_Calibration_Imaging  	22800e-3		0
# 036		MW_Calibration_Load     	18800e-3		0
# 037		MW_Calibration_Molasses 	21850e-3		0
# 038		MW_Calibration_Trap     	21887e-3		0

code_65500 = 0.0000
#		cur:    0.0000  start: 1000.0000  stop:33001.0000  step:    0.0000  every:1  next:0
code_65501 = 7525.0000
#		cur: 7525.0000  start:12584.0000  stop:12604.0000  step:    0.0000  every:1  next:0
code_65502 = 0.0000
#		cur:    0.0000  start: 1000.0000  stop:33011.0000  step:    0.0000  every:1  next:0
code_65503 = 4.4003
#		cur:    4.4003  start:   -0.8936  stop:   10.0000  step:    0.0000  every:1  next:0
code_65504 = 1300.0000
#		cur: 1300.0000  start:    0.0000  stop:15000.0000  step:    0.0000  every:1  next:0
code_65505 = 0.0000
#		cur:    0.0000  start:    0.0000  stop:    6.0000  step:    0.0000  every:1  next:0
code_65506 = 5.0000
#		cur:    5.0000  start:    0.0000  stop:    6.0000  step:    0.0000  every:1  next:0
code_65507 = 7.0000
#		cur:    7.0000  start:    8.8000  stop:    7.1100  step:    0.0000  every:1  next:0
code_65508 = 6.2600
#		cur:    6.2600  start:    6.1000  stop:    6.3100  step:    0.0000  every:1  next:0
code_65509 = -0.1822
#		cur:   -0.1822  start:   -0.1000  stop:    2.2000  step:    0.0000  every:1  next:0
code_65510 = 27995.0000
#		cur:27995.0000  start:    0.0000  stop:30000.0000  step:    0.0000  every:1  next:0
code_65511 = -6.4000
#		cur:   -6.4000  start:   -6.4000  stop:   -5.6900  step:    0.0000  every:1  next:0
code_65512 = 0.0000
#		cur:    0.0000  start:    0.0000  stop:    0.0000  step:    0.0000  every:1  next:0

if __name__ == '__main__':
    ct = ConnectionTable()

    start()

    # set all channels to LabVIEW init values
    t = 10e-6
    ct.Bitter_V_AH.constant(t, 0.188293)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 0)
    ct.Li_Img_Freq__b4c01.constant(t, 1.00006)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.oTOP_FCarrier__b4c07.constant(t, 5)
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
    ct.DMD_Shutter__b1c21.go_high(t)
    ct.Cs_HOP_Shutter__b1c09.go_high(t)
    ct.DMD_Movie_Trig__b1c20.go_high(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    ct.Bitter_Precision_Disable__b1c00.go_high(t)
    ct.Li_MOT_AO_AM__b4c02.constant(t, 10)
    ct.Li_Rep_AO_AM__b4c05.constant(t, 10)
    ct.DMD_AO_AM__b3c29.constant(t, 3.8)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.49)
    ct.Li_MRep_AO_FM__b4c04.constant(t, 0.40863)
    ct.Li_Img_AO_AM__b4c00.constant(t, 10)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    ct.CS_HFImg_Freq__b3c22.constant(t, -10)
    ct.Bias_X_HH.constant(t, -0.5)
    ct.Bias_X_AH.constant(t, 1)
    ct.Bias_Y_AH.constant(t, 0.5)
    ct.Bias_Y_HH.constant(t, 0.8)
    ct.Bias_Z_AH.constant(t, 0.2)
    ct.Bias_Z_HH.constant(t, -0.8)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.5)
    ct.BFL_AO_Sw__b3c01.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.BFL_Int_Lock__b3c02.constant(t, -2)
    ct.Pixelfly_Shutter__b2c06.go_low(t)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    ct.Aerotech_Control__b3c00.constant(t, 0)
    ct.Li_MOT_Freq__b4c03.constant(t, 5.28442)
    ct.Cs_EOM_Freq_b4c15.constant(t, 0)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.3)
    ct.oTOP_Int_Lock__b4c08.constant(t, 0)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 3)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, 0)
    ct.oTOP_AO_AM__b4c06.constant(t, 0)
    ct.oTOP_Mod_AM__b4c09.constant(t, 0)
    ct.Li_EOM_Freq__b3c31.constant(t, 0)
    ct.Cs_RSC_AO_AM__b3c27.constant(t, 5)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.15)

    # pause for line trigger at 1 us, with a timeout of 100 ms
    add_time_marker(t, 'Waiting for line trigger')
    wait('line_trigger', t, timeout=0.1)

    # procedure 000: Cs_MOT_Loading
    t = 3700e-3
    add_time_marker(t, 'Cs_MOT_Loading')
    ct.Cs_MOT_Freq__b3c24.constant(t - 100e-3, -7.20001)  # COARSE with no prior cmd, treated as constant
    # 6.1_Mod_AO_Switch: 0 JUMP — no new channel
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.30011)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.20001)
    # 1.23_CS_ZM_rep_Sh: 0 JUMP — no new channel
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.49994)
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
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t)
    ct.Bitter_Lower_CV__b3c13.constant(t, 2.30011)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2.3999)
    ct.Bitter_Upper_CC__b3c16.constant(t, 5)
    ct.Bitter_Lower_CC__b3c12.constant(t, 5)
    ct.Cs_Zeeman_Shutter__b1c17.go_high(t)
    ct.Cs_2DMOT_Shutter__b1c01.go_high(t)
    # 7.4_oTOP_mod_AM: 5 JUMP — no new channel
    ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    # 7.2_ZDT_AO_AM: 10 JUMP — no new channel
    # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 1e-3)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 2e-3, 0)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 2e-3, 5)
    # ct.Bitter_V_AH.constant(t + 5e-3, -0.0619507)  # replaced by ramp at t + 50e-3 in proc 000
    # ct.Bitter_V_HH.constant(t + 5e-3, 0.0469971)  # replaced by ramp at t + 50e-3 in proc 000
    ct.Bitter_V_AH.ramp(t=t + 5e-3, duration=45e-3, initial=-0.0619507, final=0.188293, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 5e-3, duration=45e-3, initial=0.0469971, final=-0.0201416, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 100e-3)
    ct.Cs_3DMOT_Shutter__b1c03.go_high(t + 3600e-3)

    # procedure 001: Cs_Molasses_Cooling
    t = 7495e-3
    add_time_marker(t, 'Cs_Molasses_Cooling')
    # ct.Cs_MOT_Freq__b3c24.constant(t - 2e-3, -6.79993)  # replaced by ramp at t + 4e-3 in proc 001
    # ct.Cs_Rep_Freq__b3c26.constant(t - 1e-3, 5.46692)  # replaced by ramp at t + 1e-3 in proc 001
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 0.700073)  # replaced by ramp at t + 5e-3 in proc 001
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Bias_X_HH.constant(t, 0.499878)
    ct.Bias_X_AH.constant(t, -1.00006)
    ct.Bias_Y_HH.constant(t, -1.49994)
    ct.Bias_Y_AH.constant(t, 2.86407)
    ct.Bias_Z_HH.constant(t, -0.400085)
    ct.Bias_Z_AH.constant(t, -1.00006)
    ct.Spec_Analyzer_Trig__b2c09.go_high(t)
    ct.Scope_Trig__b2c08.go_high(t)
    ct.Spec_Analyzer_Trig__b2c09.go_low(t + 1e-3)
    ct.Scope_Trig__b2c08.go_low(t + 1e-3)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t - 1e-3, duration=2e-3, initial=5.46692, final=6.40015, samplerate=FAST_FREQ)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t - 2e-3, duration=6e-3, initial=-6.79993, final=-5.79987, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t, duration=5e-3, initial=0.700073, final=0.100098, samplerate=FAST_FREQ)

    # procedure 002: Cs_H_Imaging
    t = code_65501/1e3
    add_time_marker(t, 'Cs_H_Imaging')
    ct.Pixelfly_Trig__b2c07.go_high(t - 413e-3)
    ct.Pixelfly_Trig__b2c07.go_low(t - 412.9e-3)
    ct.Pixelfly_Shutter__b2c06.go_high(t - 15e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 13e-3)
    ct.Cs_VRep_Shutter__b1c16.go_high(t - 12e-3)
    ct.Cs_HImg_Shutter__b1c07.go_high(t - 10e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t - 10e-3)
    ct.Bias_Z_AH.constant(t - 10e-3, 0.499878)
    ct.Bias_Y_HH.constant(t - 5e-3, -1.95007)
    ct.Cs_VRep_Shutter__b1c16.go_low(t - 1e-3)
    ct.Cs_Rep_AO_AM__b3c25.constant(t - 1e-3, 2.99988)
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t - 0.1e-3)
    ct.Pixelfly_Trig__b2c07.go_high(t - 0.02e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    ct.Cs_HImg_Shutter__b1c07.go_low(t)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    ct.Pixelfly_Trig__b2c07.go_low(t + 0.06e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 0.06e-3)
    ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.1e-3)
    # 7.4_oTOP_mod_AM: 0 JUMP — no new channel
    # 6.1_Mod_AO_Switch: 0 JUMP — no new channel
    # 6.2_XDT_AO_SW: 0 JUMP — no new channel
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # 7.3_oTOP_AO_AM: 0 JUMP — no new channel
    ct.Pixelfly_Shutter__b2c06.go_low(t + 7e-3)
    # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 10e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 15e-3)  # replaced by ramp at t + 630e-3 in proc 002
    ct.Pixelfly_Shutter__b2c06.go_high(t + 625e-3)
    ct.Cs_HImg_Shutter__b1c07.go_high(t + 630e-3)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    ct.Cs_LFImg_AO_Sw__b1c10.ramp(t=t + 15e-3, duration=615e-3, initial=5, final=0, samplerate=FAST_FREQ)
    ct.Pixelfly_Trig__b2c07.go_high(t + 639.98e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 640e-3)
    ct.Cs_HImg_Shutter__b1c07.go_low(t + 640e-3)
    ct.Pixelfly_Trig__b2c07.go_low(t + 640.06e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 640.06e-3)
    ct.Pixelfly_Shutter__b2c06.go_low(t + 647e-3)
    # 1.25_ZDT_AO_SW: 5 JUMP — no new channel
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 655e-3)
    ct.Cs_LFImg_AO_Sw__b1c10.go_high(t + 1750e-3)

    # # procedure 003: Cs_RSC1
    # t = 7500e-3
    # add_time_marker(t, 'Cs_RSC1')
    # ct.Cs_Rep_Shutter__b1c12.go_low(t - 16e-3)
    # ct.Cs_RSC_AO_Sw__b1c13.go_low(t - 10e-3)
    # ct.Cs_RSC_Shutter__b1c14.go_high(t - 9e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_high(t - 6e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t - 5e-3)
    # ct.Cs_RSC_AO_AM__b3c27.constant(t - 4.5e-3, 0)
    # ct.Cs_RSC_AO_Sw__b1c13.go_high(t - 4e-3)
    # # ct.Cs_Rep_Freq__b3c26.constant(t - 2.5e-3, 7.37)  # replaced by ramp at t in proc 003
    # # ct.Cs_RSC_AO_AM__b3c27.constant(t - 1e-3, 0)  # replaced by ramp at t - 0.5e-3 in proc 003
    # ct.Spec_Analyzer_Trig__b2c09.go_low(t - 1e-3)
    # # ct.Cs_MOT_Freq__b3c24.constant(t - 0.98e-3, -5.79987)  # replaced by ramp at t + 1.5e-3 in proc 003
    # ct.Cs_RSC_AO_AM__b3c27.ramp(t=t - 1e-3, duration=0.5e-3, initial=0, final=2.09991, samplerate=FAST_FREQ)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t - 0.3e-3, 0)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t - 2.5e-3, duration=2.5e-3, initial=7.37, final=3.69995, samplerate=FAST_FREQ)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t, 1.3501)
    # ct.Scope_Trig__b2c08.go_high(t)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 0.02e-3, 0)
    # ct.Bias_X_HH.constant(t + 0.02e-3, 0.899963)
    # ct.Bias_X_AH.constant(t + 0.02e-3, -0.750122)
    # ct.Bias_Y_HH.constant(t + 0.02e-3, -2.04987)
    # ct.Bias_Y_AH.constant(t + 0.02e-3, 2.78717)
    # ct.Bias_Z_HH.constant(t + 0.02e-3, -0.469971)
    # ct.Bias_Z_AH.constant(t + 0.02e-3, -0.350037)
    # ct.Spec_Analyzer_Trig__b2c09.go_high(t + 0.02e-3)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 1.5e-3, 0.0250244)
    # ct.Cs_MOT_Freq__b3c24.ramp(t=t - 0.98e-3, duration=2.48e-3, initial=-5.79987, final=0.0500488, samplerate=FAST_FREQ)
    # ct.Scope_Trig__b2c08.go_low(t + 5e-3)
    # ct.Spec_Analyzer_Trig__b2c09.go_low(t + 5e-3)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 31.6e-3, 0)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t + 31.7e-3, 0)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 31.7e-3)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 31.7e-3)
    # # ct.Cs_RSC_AO_AM__b3c27.constant(t + 32.6e-3, 2.09991)  # replaced by ramp at t + 37.6e-3 in proc 003
    # ct.Cs_RSC_AO_AM__b3c27.ramp(t=t + 32.6e-3, duration=5e-3, initial=2.09991, final=0, samplerate=FAST_FREQ)
    # ct.Cs_RSC_AO_Sw__b1c13.go_low(t + 38e-3)

    # # procedure 004: Aerotech_return
    # t = 12600e-3
    # add_time_marker(t, 'Aerotech_return')
    # ct.Dual_1064_Int_Lock__b4c16.constant(t - 250e-3, 1.3501)
    # ct.Aerotech_Control__b3c00.constant(t - 100e-3, 5)
    # ct.Aerotech_Control__b3c00.constant(t + 750e-3, 7.00012)
    # # ct.Dual_1064_Int_Lock__b4c16.constant(t + 1000e-3, 1.3501)  # replaced by ramp at t + 1100e-3 in proc 004
    # # 2.0_Dual_780nm_Int_Lock: 3.50006 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 2.5 JUMP — no new channel
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1000e-3, duration=100e-3, initial=1.3501, final=0.606995, samplerate=SLOW_FREQ)
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1100e-3, duration=100e-3, initial=0.606995, final=0.41687, samplerate=SLOW_FREQ)
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1200e-3, duration=100e-3, initial=0.41687, final=0.147095, samplerate=SLOW_FREQ)
    # # 7.5_Dual_1064_Int_Lock: 2.5 COARSE — no new channel
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1300e-3, duration=400e-3, initial=0.147095, final=0, samplerate=FAST_FREQ)
    # # 2.0_Dual_780nm_Int_Lock: 3.50006 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 2.5 JUMP — no new channel
    # ct.Bitter_V_HH.constant(t + 1701e-3, 0)
    # ct.BFL_AO_Sw__b3c01.constant(t + 1701e-3, 0)
    # ct.Aerotech_Control__b3c00.constant(t + 2000e-3, 8.99994)
    # # 7.5_Dual_1064_Int_Lock: 1.45386 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.768127 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.405884 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.215149 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.0750732 COARSE — no new channel
    # # 2.0_Dual_780nm_Int_Lock: 2.5 COARSE — no new channel

    # # procedure 005: Dual_Imaging_H
    # t = code_65501/1e3
    # add_time_marker(t, 'Dual_Imaging_H')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 500.02e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 499.06e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 50e-3, 6.00006)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 17e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # ct.Li_HImg_Shutter__b1c28.go_high(t - 8e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t - 0.02e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_HImg_Shutter__b1c28.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Pixelfly_Shutter__b2c06.go_low(t)
    # # 5.9_Cs_LF_Img_AO_AM: 8.50006 JUMP — no new channel
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
    # ct.Cs_VRep_Shutter__b1c16.go_low(t + 29e-3)
    # # 2.1_CS_Rep_AO_AM: 2.00012 JUMP — no new channel
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

    # # procedure 006: MW 
    # t = 16116e-3
    # add_time_marker(t, 'MW ')
    # ct.Bias_X_HH.constant(t - 30e-3, 0.390015)
    # ct.Bias_X_AH.constant(t - 30e-3, -0.319519)
    # ct.Bias_Y_HH.constant(t - 30e-3, -1.37604)
    # ct.Bias_Y_AH.constant(t - 30e-3, 2.7533)
    # ct.Bias_Z_HH.constant(t - 30e-3, -0.302429)
    # ct.Bias_Z_AH.constant(t - 30e-3, -0.400085)
    # ct.MW_Trig__b2c04.go_high(t - 20e-3)
    # # ct.Bias_Y_HH.constant(t - 20e-3, -1.37604)  # replaced by ramp at t in proc 006
    # ct.MW_Trig__b2c04.go_low(t)
    # ct.Bias_Y_HH.ramp(t=t - 20e-3, duration=20e-3, initial=-1.37604, final=-1.17615, samplerate=FAST_FREQ)
    # # 1.22_MW_INCR_UP: 0 JUMP — no new channel
    # # 1.22_MW_INCR_UP: 5 JUMP — no new channel

    # # procedure 007: FB_Bias_field
    # t = 12600e-3
    # add_time_marker(t, 'FB_Bias_field')
    # ct.Bitter_Lower_CC__b3c12.constant(t - 100e-3, 5)
    # ct.Bitter_Upper_CC__b3c16.constant(t - 100e-3, 5)
    # ct.Bitter_Upper_CV__b3c17.constant(t - 100e-3, 2.30011)
    # ct.Bitter_Lower_CV__b3c13.constant(t - 100e-3, 1.79993)
    # # 2.6_V_HH: 0.669861 JUMP — no new channel
    # # 2.7_V_AH: -0.669861 JUMP — no new channel
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 4.46014)  # replaced by ramp at t + 400e-3 in proc 007
    # # 2.6_V_HH: 2.77893 COARSE — no new channel
    # # 2.7_V_AH: -0.826416 FINE — no new channel
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t, duration=400e-3, initial=4.46014, final=0, samplerate=SLOW_FREQ)
    # ct.FF_Disable__b1c24.go_high(t + 401e-3)
    # # 2.6_V_HH: 2.77893 JUMP — no new channel
    # # ct.Bias_X_HH.constant(t + 750e-3, 6.00006)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bias_Y_HH.constant(t + 750e-3, -3.591)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bias_Z_HH.constant(t + 750e-3, -5)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bitter_Upper_CV__b3c17.constant(t + 750e-3, 2.30011)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bitter_Lower_CV__b3c13.constant(t + 750e-3, 1.79993)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bias_X_AH.constant(t + 750e-3, 0.202637)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bias_Y_AH.constant(t + 750e-3, 3.52295)  # replaced by ramp at t + 950e-3 in proc 007
    # # ct.Bias_Z_AH.constant(t + 750e-3, -0.400085)  # replaced by ramp at t + 950e-3 in proc 007
    # # 2.7_V_AH: -0.140686 JUMP — no new channel
    # # 2.6_V_HH: 6.43982 FINE — no new channel
    # # 2.7_V_AH: -0.291443 FINE — no new channel
    # # 2.6_V_HH: 6.43188 JUMP — no new channel
    # # 2.7_V_AH: 3.1015 JUMP — no new channel
    # ct.Bitter_Precision_Disable__b1c00.go_low(t + 917.72e-3)
    # # 2.6_V_HH: -2.00012 FINE — no new channel
    # ct.Bias_X_HH.ramp(t=t + 750e-3, duration=200e-3, initial=6.00006, final=0.390015, samplerate=SLOW_FREQ)
    # ct.Bias_Y_HH.ramp(t=t + 750e-3, duration=200e-3, initial=-3.591, final=5.49988, samplerate=SLOW_FREQ)
    # ct.Bias_Z_HH.ramp(t=t + 750e-3, duration=200e-3, initial=-5, final=-0.302429, samplerate=SLOW_FREQ)
    # ct.Bitter_Upper_CV__b3c17.ramp(t=t + 750e-3, duration=200e-3, initial=2.30011, final=3.20007, samplerate=SLOW_FREQ)
    # ct.Bitter_Lower_CV__b3c13.ramp(t=t + 750e-3, duration=200e-3, initial=1.79993, final=2.69989, samplerate=SLOW_FREQ)
    # ct.Bias_X_AH.ramp(t=t + 750e-3, duration=200e-3, initial=0.202637, final=-0.319519, samplerate=SLOW_FREQ)
    # ct.Bias_Y_AH.ramp(t=t + 750e-3, duration=200e-3, initial=3.52295, final=2.7533, samplerate=SLOW_FREQ)
    # ct.Bias_Z_AH.ramp(t=t + 750e-3, duration=200e-3, initial=-0.400085, final=-0.400085, samplerate=SLOW_FREQ)
    # # 2.7_V_AH: 3.8501 FINE — no new channel
    # # 2.6_V_HH: -2.00012 JUMP — no new channel
    # # 2.6_V_HH: -0.700073 COARSE — no new channel

    # # procedure 008: Cs_Dark
    # t = 7534e-3
    # add_time_marker(t, 'Cs_Dark')
    # ct.Cs_Zeeman_Shutter__b1c17.go_low(t - 50e-3)
    # ct.Cs_2DMOT_Shutter__b1c01.go_low(t - 20e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_low(t - 18e-3)
    # ct.Cs_RSC_Shutter__b1c14.go_low(t - 8e-3)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t)
    # ct.Cs_3DMOT_Shutter__b1c03.go_low(t)
    # # ct.Cs_Rep_Freq__b3c26.constant(t, 3.69995)  # replaced by ramp at t + 10e-3 in proc 008
    # ct.Cs_Rep_Shutter__b1c12.go_low(t)
    # # ct.Cs_MOT_Freq__b3c24.constant(t + 1e-3, 0.0500488)  # replaced by ramp at t + 9e-3 in proc 008
    # ct.Cs_MOT_Freq__b3c24.ramp(t=t + 1e-3, duration=8e-3, initial=0.0500488, final=-7.7301, samplerate=FAST_FREQ)
    # ct.Cs_Rep_Freq__b3c26.ramp(t=t, duration=10e-3, initial=3.69995, final=7.55005, samplerate=FAST_FREQ)
    # ct.Cs_3DMOT_AO_Sw__b1c02.go_high(t + 505e-3)
    # ct.Cs_RSC_AO_Sw__b1c13.go_high(t + 505e-3)
    # ct.Cs_RSC_AO_AM__b3c27.constant(t + 505e-3, 5)
    # ct.Cs_Rep_AO_AM__b3c25.constant(t + 505e-3, 0)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 505e-3)

    # # procedure 009: Li_V_Imaging_2
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_V_Imaging_2')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 100e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 99e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t - 10e-3, 5)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 5e-3)
    # ct.Li_VImg_Shutter__b2c02.go_high(t - 5e-3)
    # # 2.4_: 5.40009 JUMP — no new channel
    # # 2.3_Li_MRep_AO_FM: -1.09985 JUMP — no new channel
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t - 0.04e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t)
    # ct.Li_Rep_Shutter__b2c01.go_low(t)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.04e-3)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 0.04e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 2e-3, 0)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 20e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 20e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 134e-3)
    # ct.Li_Rep_Shutter__b2c01.go_high(t + 134e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 135e-3, 5)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 135e-3)
    # ct.Li_VImg_Shutter__b2c02.go_high(t + 135e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 139.96e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 140e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 140e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 140e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 140.04e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 140.1e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 142e-3, 0)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 142e-3)
    # ct.Li_Rep_Shutter__b2c01.go_low(t + 142e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 162e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 162e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 330e-3, 5)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 334e-3)
    # ct.Li_Rep_Shutter__b2c01.go_high(t + 334e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 339.96e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 340e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 340e-3)
    # ct.Li_Rep_Shutter__b2c01.go_low(t + 340e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 340.1e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 342.1e-3, 0)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 360e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 1000e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 1001e-3)

    # # procedure 010: Cs_Evaporation
    # t = 7600e-3
    # add_time_marker(t, 'Cs_Evaporation')
    # # 7.4_oTOP_mod_AM: 5 JUMP — no new channel
    # # ct.Bitter_V_AH.constant(t + 50.02e-3, -0.826416)  # replaced by ramp at t + 499.98e-3 in proc 010
    # # 7.4_oTOP_mod_AM: 1.27014 COARSE — no new channel
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # ct.Bitter_V_AH.ramp(t=t + 50.02e-3, duration=449.96e-3, initial=-0.826416, final=-0.140686, samplerate=FAST_FREQ)

    # # procedure 011: Spare
    # t = code_65510/1e3
    # add_time_marker(t, 'Spare')
    # ct.Li_Img_AO_AM__b4c00.constant(t - 10e-3, 10)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # # 2.1_CS_Rep_AO_AM: 5 JUMP — no new channel
    # ct.Cs_VRep_Shutter__b1c16.go_high(t - 10e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t - 10e-3)
    # ct.Li_VImg_Shutter__b2c02.go_high(t - 6e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t - 2e-3)
    # ct.Li_MRep_AO_FM__b4c04.constant(t - 0.1e-3, 5)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t - 0.1e-3)
    # ct.Cs_VRep_Shutter__b1c16.go_low(t)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t)
    # ct.Li_MRep_AO_FM__b4c04.constant(t + 0.1e-3, 0)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 0.1e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 3e-3)
    # ct.Li_VImg_Shutter__b2c02.go_low(t + 3e-3)

    # # procedure 012: Li_Feshbach
    # t = 7000e-3
    # add_time_marker(t, 'Li_Feshbach')
    # ct.Bitter_Lower_CC__b3c12.constant(t - 500e-3, 3.69995)
    # ct.Bitter_Upper_CC__b3c16.constant(t - 500e-3, 3.90015)
    # ct.Bitter_Lower_CC__b3c12.constant(t - 20e-3, 5)
    # ct.Bitter_Upper_CC__b3c16.constant(t - 20e-3, 5)
    # ct.Bitter_Upper_CV__b3c17.constant(t, 2.69989)
    # ct.Bitter_Lower_CV__b3c13.constant(t, 2.20001)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 0.22e-3, 5)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 0.32e-3, 0)
    # # 2.6_V_HH: 0 JUMP — no new channel
    # # 2.7_V_AH: 0 JUMP — no new channel
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1e-3, 4.10004)
    # # ct.Bitter_Lower_FF__b3c14.constant(t + 1e-3, 2.55005)  # replaced by ramp at t + 2.2e-3 in proc 012
    # ct.Bitter_Lower_FF__b3c14.ramp(t=t + 1e-3, duration=1.2e-3, initial=2.55005, final=2.20001, samplerate=FAST_FREQ)
    # # ct.Bitter_Upper_CV__b3c17.constant(t + 3e-3, 2.5)  # replaced by ramp at t + 8e-3 in proc 012
    # # ct.Bitter_Lower_CV__b3c13.constant(t + 3e-3, 2.20001)  # replaced by ramp at t + 8e-3 in proc 012
    # ct.Bitter_Upper_CV__b3c17.ramp(t=t + 3e-3, duration=5e-3, initial=2.5, final=2.99988, samplerate=FAST_FREQ)
    # ct.Bitter_Lower_CV__b3c13.ramp(t=t + 3e-3, duration=5e-3, initial=2.20001, final=2.69989, samplerate=FAST_FREQ)
    # # 2.6_V_HH: 6.60004 FINE — no new channel
    # # 2.7_V_AH: -0.0650024 FINE — no new channel
    # # 2.6_V_HH: 6.60004 JUMP — no new channel
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1500e-3, 0)
    # ct.Bitter_Lower_FF__b3c14.constant(t + 1500e-3, -0.0750732)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 1500e-3, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 1500e-3, 5)
    # # 2.6_V_HH: 0 FINE — no new channel

    # # procedure 013: Dual_Evap
    # t = 24700e-3
    # add_time_marker(t, 'Dual_Evap')
    # # ct.Bias_Y_HH.constant(t, -3.99994)  # replaced by ramp at t + 10e-3 in proc 013
    # ct.Bias_Y_HH.ramp(t=t, duration=10e-3, initial=-3.99994, final=1.30005, samplerate=SLOW_FREQ)
    # # 2.6_V_HH: -0.700073 JUMP — no new channel
    # # ct.Bias_Y_HH.constant(t + 1700e-3, 1.30005)  # replaced by ramp at t + 3000e-3 in proc 013
    # # 2.6_V_HH: -0.039978 FINE — no new channel
    # # 2.6_V_HH: -0.00701904 FINE — no new channel
    # ct.Bias_Y_HH.ramp(t=t + 1700e-3, duration=1300e-3, initial=1.30005, final=code_65512, samplerate=SLOW_FREQ)
    # # 2.6_V_HH: 0.100098 FINE — no new channel

    # # procedure 014: Li_H_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_H_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 400e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 399e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 17e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 10e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t - 10e-3, 3.99994)
    # ct.Li_HImg_Shutter__b1c28.go_high(t - 6e-3)
    # ct.Li_MOT_AO_Sw__b1c30.go_low(t - 5e-3)
    # ct.Li_Rep_AO_AM__b4c05.constant(t - 5e-3, 10)
    # ct.Li_Rep_Shutter__b2c01.go_high(t - 3e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t - 0.06e-3)
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
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 83e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 90e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 90e-3, 3.99994)
    # ct.Li_HImg_Shutter__b1c28.go_high(t + 94e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 96e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 100e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 100e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 100e-3)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t + 100e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 100.1e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 100.1e-3)
    # ct.Li_HImg_Shutter__b1c28.go_low(t + 101e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 101e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 110e-3)
    # ct.Li_Img_AO_AM__b4c00.constant(t + 110e-3, 10)
    # ct.Li_Rep_AO_Sw__b2c00.go_high(t + 120e-3)

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

    # # procedure 016: Cs_Levitation1
    # t = 7532e-3
    # add_time_marker(t, 'Cs_Levitation1')
    # ct.Bitter_Upper_CV__b3c17.constant(t - 32e-3, 2.30011)
    # ct.Bitter_Lower_CV__b3c13.constant(t - 32e-3, 1.79993)
    # ct.Bitter_Lower_CC__b3c12.constant(t - 32e-3, 5)
    # ct.Bitter_Upper_CC__b3c16.constant(t - 32e-3, 5)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t - 5e-3, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t - 3e-3, 5)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t - 0.5e-3, 5)
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t - 0.1e-3, 3.50006)  # replaced by ramp at t + 0.1e-3 in proc 016
    # ct.Bitter_V_HH.constant(t, 0.669861)
    # ct.Bitter_V_AH.constant(t, -0.669861)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t - 0.1e-3, duration=0.2e-3, initial=3.50006, final=5.49988, samplerate=FAST_FREQ)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 0.8e-3, 4.58008)
    # # ct.Bitter_HH_Upper_FF__b3c10.constant(t + 1e-3, 4.70001)  # replaced by ramp at t + 1.2e-3 in proc 016
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1e-3, duration=0.2e-3, initial=4.70001, final=4.57001, samplerate=FAST_FREQ)
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 1.2e-3, duration=0.3e-3, initial=4.57001, final=4.46014, samplerate=FAST_FREQ)

    # # procedure 017: Li_Evaporation
    # t = 7000e-3
    # add_time_marker(t, 'Li_Evaporation')
    # ct.Dual_1064_Int_Lock__b4c16.constant(t, 5.70007)
    # ct.Bitter_V_HH.constant(t, 10)
    # ct.Bias_Y_HH.constant(t, -0.499878)
    # # ct.Dual_1064_Int_Lock__b4c16.constant(t + 100e-3, 5.70007)  # replaced by ramp at t + 500e-3 in proc 017
    # # 2.0_Dual_780nm_Int_Lock: 5 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 3.75 JUMP — no new channel
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 100e-3, duration=400e-3, initial=5.70007, final=3.50006, samplerate=SLOW_FREQ)
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 500e-3, duration=500e-3, initial=3.50006, final=2.16003, samplerate=SLOW_FREQ)
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t + 1000e-3, duration=500e-3, initial=2.16003, final=1.3501, samplerate=SLOW_FREQ)
    # # 2.0_Dual_780nm_Int_Lock: 0 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0 COARSE — no new channel
    # ct.Aerotech_Control__b3c00.constant(t + 1600e-3, 2.99988)

    # # procedure 018: Li_Dark
    # t = 7000e-3
    # add_time_marker(t, 'Li_Dark')
    # ct.Li_Zeeman_Shutter__b2c03.go_low(t - 15e-3)
    # ct.Li_MOT_Shutter__b1c31.go_low(t - 3e-3)
    # ct.Li_Rep_Shutter__b2c01.go_low(t - 2e-3)
    # ct.Li_MOT_AO_Sw__b1c30.go_low(t)
    # ct.Li_Rep_AO_AM__b4c05.constant(t, 0)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    # # 2.6_V_HH: 0 JUMP — no new channel
    # # 2.7_V_AH: 0 JUMP — no new channel
    # ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    # # ct.Bitter_V_AH.constant(t + 1e-3, 5.65002)  # replaced by ramp at t + 1000e-3 in proc 018
    # ct.Bitter_V_AH.ramp(t=t + 1e-3, duration=999e-3, initial=5.65002, final=6.09985, samplerate=SLOW_FREQ)

    # # procedure 019: Cs_V_Imaging
    # t = code_65501/1e3
    # add_time_marker(t, 'Cs_V_Imaging')
    # ct.Pixelfly_Trig__b2c07.go_high(t - 313e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 312.9e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t - 13e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t - 12e-3)
    # ct.Cs_HOP_Shutter__b1c09.go_high(t - 12e-3)
    # # 5.9_Cs_LF_Img_AO_AM: 2.99988 JUMP — no new channel
    # # 2.1_CS_Rep_AO_AM: 10 JUMP — no new channel
    # ct.Cs_HOP_Shutter__b1c09.go_low(t - 1e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t - 0.5e-3)
    # ct.Cs_Andor_Trig__b1c04.go_high(t - 0.1e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_high(t)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t)
    # ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # ct.Cs_Andor_Trig__b1c04.go_low(t + 0.1e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_low(t + 0.1e-3)
    # ct.Cs_LFImg_AO_Sw__b1c10.go_low(t + 0.3e-3)
    # ct.Cs_HOP_AO_Sw__b1c08.go_high(t + 10e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 640e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 640.1e-3)

    # # procedure 020: Li_CMOT
    # t = 6999.98e-3
    # add_time_marker(t, 'Li_CMOT')
    # ct.Bitter_Upper_CV__b3c17.constant(t - 200e-3, 3.59985)
    # ct.Bitter_Lower_CV__b3c13.constant(t - 200e-3, 3.29987)
    # # ct.Dual_1064_Int_Lock__b4c16.constant(t - 80e-3, 5.70007)  # replaced by ramp at t in proc 020
    # # 7.1_CS_Rep_AO_AM: 0 JUMP — no new channel
    # ct.Li_Zeeman_Shutter__b2c03.go_low(t - 58e-3)
    # # 1.32_ZCurrents → 0 (Zeeman: 1.31=5, 1.32=0)
    # ct.Zeeman_C1__b4c10.constant(t - 50e-3, 0)
    # ct.Zeeman_C2__b4c11.constant(t - 50e-3, 0)
    # ct.Zeeman_C3__b4c12.constant(t - 50e-3, 0)
    # ct.Zeeman_C4__b4c13.constant(t - 50e-3, 0)
    # ct.Zeeman_C5__b4c14.constant(t - 50e-3, 0)
    # # ct.Bias_X_HH.constant(t - 50e-3, 5)  # replaced by ramp at t - 5e-3 in proc 020
    # # ct.Bias_X_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # # ct.Bias_Y_HH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # # ct.Bias_Y_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # # ct.Bias_Z_HH.constant(t - 50e-3, -6.00006)  # replaced by ramp at t - 5e-3 in proc 020
    # # ct.Bias_Z_AH.constant(t - 50e-3, 0)  # replaced by ramp at t - 5e-3 in proc 020
    # # 2.6_V_HH: -0.00946045 JUMP — no new channel
    # # 2.7_V_AH: 0.347595 JUMP — no new channel
    # # ct.Bitter_V_AH.constant(t - 18e-3, 5.32013)  # replaced by ramp at t in proc 020
    # # 2.3_Li_MRep_AO_FM: 0.400085 JUMP — no new channel
    # # ct.Li_Rep_AO_AM__b4c05.constant(t - 13.5e-3, 5)  # replaced by ramp at t - 3e-3 in proc 020
    # # ct.Li_MOT_AO_AM__b4c02.constant(t - 13.5e-3, 1.90002)  # replaced by ramp at t - 3e-3 in proc 020
    # ct.Bias_X_HH.ramp(t=t - 50e-3, duration=45e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Bias_X_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=0, samplerate=FAST_FREQ)
    # ct.Bias_Y_HH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=-5, samplerate=FAST_FREQ)
    # ct.Bias_Y_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=0, samplerate=FAST_FREQ)
    # ct.Bias_Z_HH.ramp(t=t - 50e-3, duration=45e-3, initial=-6.00006, final=0, samplerate=FAST_FREQ)
    # ct.Bias_Z_AH.ramp(t=t - 50e-3, duration=45e-3, initial=0, final=-5, samplerate=FAST_FREQ)
    # # 2.6_V_HH: -0.0601196 FINE — no new channel
    # # 2.7_V_AH: 1.00006 FINE — no new channel
    # ct.Li_MOT_AO_AM__b4c02.ramp(t=t - 13.5e-3, duration=10.5e-3, initial=1.90002, final=1.90002, samplerate=FAST_FREQ)
    # ct.Li_Rep_AO_AM__b4c05.ramp(t=t - 13.5e-3, duration=10.5e-3, initial=5, final=2.65015, samplerate=FAST_FREQ)
    # ct.Li_Rep_AO_Sw__b2c00.go_low(t - 0.04e-3)
    # ct.Li_Rep_AO_AM__b4c05.ramp(t=t - 3e-3, duration=2.96e-3, initial=2.65015, final=0, samplerate=FAST_FREQ)
    # ct.Li_Rep_AO_AM__b4c05.constant(t - 0.02e-3, 0)
    # ct.Dual_1064_Int_Lock__b4c16.ramp(t=t - 80e-3, duration=80e-3, initial=5.70007, final=5.70007, samplerate=FAST_FREQ)
    # ct.Li_MOT_AO_AM__b4c02.ramp(t=t - 3e-3, duration=3e-3, initial=1.90002, final=0, samplerate=FAST_FREQ)
    # # 2.3_Li_MRep_AO_FM: 0.480042 FINE — no new channel
    # ct.Bitter_V_AH.ramp(t=t - 18e-3, duration=18e-3, initial=5.32013, final=5.67993, samplerate=FAST_FREQ)
    # ct.Scope_Trig__b2c08.go_high(t)
    # ct.Scope_Trig__b2c08.go_low(t + 5e-3)

    # procedure 021: Cs_CMOT
    t = 7445e-3
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
    # ct.Bias_X_AH.constant(t - 10e-3, 1.00006)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Y_HH.constant(t - 10e-3, 2.6001)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Y_AH.constant(t - 10e-3, -3.59985)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Z_HH.constant(t - 10e-3, -0.499878)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Bias_Z_AH.constant(t - 10e-3, -0.599976)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Dual_780_Int_Lock__b3c30.constant(t - 10e-3, 5)  # replaced by ramp at t in proc 021
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t - 30e-3, duration=30e-3, initial=2.30011, final=0.499878, samplerate=FAST_FREQ)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 5)
    ct.Cs_VRep_Shutter__b1c16.go_low(t)
    ct.Cs_HOP_Shutter__b1c09.go_low(t)
    # ct.Bitter_V_HH.constant(t, -0.0201416)  # replaced by ramp at t + 40e-3 in proc 021
    # ct.Bitter_V_AH.constant(t, 0.188293)  # replaced by ramp at t + 40e-3 in proc 021
    # ct.Cs_MOT_Freq__b3c24.constant(t, -7.20001)  # replaced by ramp at t + 40e-3 in proc 021
    ct.Dual_780_Int_Lock__b3c30.ramp(t=t - 10e-3, duration=10e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Cs_3DMOT_AO_AM__b3c21.constant(t + 40e-3, 0.499878)  # replaced by ramp at t + 48e-3 in proc 021
    # ct.Cs_Rep_Freq__b3c26.constant(t + 40e-3, 6.49994)  # replaced by ramp at t + 48.98e-3 in proc 021
    ct.Bitter_V_HH.ramp(t=t, duration=40e-3, initial=-0.0201416, final=-0.000915527, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t, duration=40e-3, initial=0.188293, final=0.11261, samplerate=FAST_FREQ)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t, duration=40e-3, initial=-7.20001, final=-6.79993, samplerate=FAST_FREQ)
    ct.Cs_3DMOT_AO_AM__b3c21.ramp(t=t + 40e-3, duration=8e-3, initial=0.499878, final=0.299988, samplerate=FAST_FREQ)
    ct.Bias_X_HH.ramp(t=t - 10e-3, duration=58e-3, initial=-2.5, final=2.00012, samplerate=FAST_FREQ)
    ct.Bias_X_AH.ramp(t=t - 10e-3, duration=58e-3, initial=1.00006, final=0, samplerate=FAST_FREQ)
    ct.Bias_Y_HH.ramp(t=t - 10e-3, duration=58e-3, initial=2.6001, final=-0.700073, samplerate=FAST_FREQ)
    ct.Bias_Y_AH.ramp(t=t - 10e-3, duration=58e-3, initial=-3.59985, final=0, samplerate=FAST_FREQ)
    ct.Bias_Z_HH.ramp(t=t - 10e-3, duration=58e-3, initial=-0.499878, final=-1.19995, samplerate=FAST_FREQ)
    ct.Bias_Z_AH.ramp(t=t - 10e-3, duration=58e-3, initial=-0.599976, final=0.599976, samplerate=FAST_FREQ)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t + 40e-3, duration=8.98e-3, initial=6.49994, final=5.46692, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 40e-3, duration=8.98e-3, initial=-0.000915527, final=0.0100708, samplerate=FAST_FREQ)
    ct.Bitter_V_AH.ramp(t=t + 40e-3, duration=8.98e-3, initial=0.11261, final=0.0756836, samplerate=FAST_FREQ)

    # # procedure 022: Li_MOT_Loading
    # t = 2015e-3
    # add_time_marker(t, 'Li_MOT_Loading')
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 0)
    # ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    # ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    # ct.Li_MOT_AO_AM__b4c02.constant(t, 8.99994)
    # # 1.31_Cs_Li_Zeswitch → 0 (Zeeman: 1.31=0, 1.32=0)
    # ct.Zeeman_C1__b4c10.constant(t, 0)
    # ct.Zeeman_C2__b4c11.constant(t, 0)
    # ct.Zeeman_C3__b4c12.constant(t, 0)
    # ct.Zeeman_C4__b4c13.constant(t, 0)
    # ct.Zeeman_C5__b4c14.constant(t, 0)
    # # 2.7_V_AH: 0.347595 JUMP — no new channel
    # # 2.6_V_HH: -0.00946045 JUMP — no new channel
    # ct.Cs_Andor_Trig__b1c04.go_low(t)
    # # 1.8_Cs_2DMOT_Shutter: 0 JUMP — no new channel
    # ct.DMD_AO_FM__b1c18.go_low(t)
    # ct.Cs_HOP_Shutter__b1c09.go_low(t)
    # # 1.19_Cs_ZM_shutter: 0 JUMP — no new channel
    # # 1.23_CS_ZM_rep_Sh: 5 JUMP — no new channel
    # ct.Bias_X_HH.constant(t, 5)
    # ct.Bias_X_AH.constant(t, 0)
    # ct.Bias_Y_HH.constant(t, 0)
    # ct.Bias_Y_AH.constant(t, 0)
    # ct.Bias_Z_HH.constant(t, -6.00006)
    # ct.Bias_Z_AH.constant(t, 0)
    # # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # # 7.0_oTOP_Int_lok: -1.00006 JUMP — no new channel
    # # 7.2_ZDT_AO_AM: -1.00006 JUMP — no new channel
    # ct.Li_Rep_Shutter__b2c01.go_high(t)
    # ct.Li_MOT_Shutter__b1c31.go_low(t)
    # ct.Li_Zeeman_Shutter__b2c03.go_high(t)
    # # 1.32_ZCurrents → 5 (Zeeman: 1.31=0, 1.32=5)
    # ct.Zeeman_C1__b4c10.constant(t, ZEEMAN_C1_CS)
    # ct.Zeeman_C2__b4c11.constant(t, ZEEMAN_C2_CS)
    # ct.Zeeman_C3__b4c12.constant(t, ZEEMAN_C3_CS)
    # ct.Zeeman_C4__b4c13.constant(t, ZEEMAN_C4_CS)
    # ct.Zeeman_C5__b4c14.constant(t, ZEEMAN_C5_CS)
    # # 2.0_Dual_780nm_Int_Lock: 5 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 3.75 JUMP — no new channel
    # ct.Bitter_Upper_CV__b3c17.constant(t, 2.00012)
    # ct.Bitter_Lower_CV__b3c13.constant(t, 1.49994)
    # ct.Bitter_Lower_CC__b3c12.constant(t, 1.00006)
    # ct.Bitter_Upper_CC__b3c16.constant(t, 1.00006)
    # ct.Cs_VRep_Shutter__b1c16.go_low(t)
    # ct.Cs_Zeeman_Shutter__b1c17.go_low(t)
    # ct.Cs_2DMOT_Shutter__b1c01.go_low(t)
    # ct.Cs_3DMOT_Shutter__b1c03.go_low(t)
    # ct.Bitter_V_AH.constant(t, 5.32013)
    # # ct.Li_Img_Freq__b4c01.constant(t, -9.04999)  # replaced by ramp at t + 5000e-3 in proc 022
    # # 7.1_CS_Rep_AO_AM: 0 JUMP — no new channel
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 2e-3, 0)
    # ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 10e-3, 5)
    # ct.Li_Img_Freq__b4c01.ramp(t=t, duration=5000e-3, initial=-9.04999, final=code_65507, samplerate=FAST_FREQ)

    # procedure 023: True_TOF
    t = code_65500/1e3
    add_time_marker(t, 'True_TOF')
    ct.BFL_AO_Sw__b3c01.constant(t, 0)
    # 5.11_BFL_AO_AM: 0 JUMP — no new channel
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 0)
    # 1.25_ZDT_AO_SW: 0 JUMP — no new channel
    # 7.3_oTOP_AO_AM: 0 JUMP — no new channel
    # 6.2_XDT_AO_SW: 0 JUMP — no new channel
    ct.Cs_Rep_AO_AM__b3c25.constant(t, -1.00006)
    # 7.2_ZDT_AO_AM: 0 JUMP — no new channel
    ct.Dual_780_AO_Sw__b1c23.go_low(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t + 0.02e-3)

    # # procedure 024: Li_Killing
    # t = 21600e-3
    # add_time_marker(t, 'Li_Killing')
    # ct.Li_Img_AO_AM__b4c00.constant(t - 20e-3, 7.00012)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t - 8e-3)
    # ct.Li_HImg_Shutter__b1c28.go_high(t - 6e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t)
    # ct.Li_Img_AO_Sw__b1c29.go_low(t + 0.02e-3)
    # ct.Li_HImg_Shutter__b1c28.go_low(t + 0.02e-3)
    # ct.Li_Img_AO_Sw__b1c29.go_high(t + 12e-3)
    # # ct.Li_Img_Freq__b4c01.constant(t + 12e-3, code_65507)  # replaced by ramp at t + 450e-3 in proc 024
    # ct.Li_Img_AO_AM__b4c00.constant(t + 200e-3, 6.00006)
    # ct.Li_Img_Freq__b4c01.ramp(t=t + 12e-3, duration=438e-3, initial=code_65507, final=code_65508, samplerate=FAST_FREQ)

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

    # procedure 026: FB_Bias_Field_off
    t = code_65502/1e3
    add_time_marker(t, 'FB_Bias_Field_off')
    ct.Bitter_V_HH.constant(t, 0)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_V_AH.constant(t, 0)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Precision_Disable__b1c00.go_high(t)

    # procedure 027: Magnetizer
    t = 1e-3
    add_time_marker(t, 'Magnetizer')
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 5)
    ct.Bitter_HH_Upper_FF__b3c10.constant(t, 0)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.Bitter_AH_Upper_FF__b3c09.constant(t, 0)
    ct.Bitter_V_AH.constant(t, 0)
    ct.Bitter_V_HH.constant(t, 0)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    # 5.11_BFL_AO_AM: 0 JUMP — no new channel
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 50e-3, 0)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 50.02e-3, 5)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 60e-3, 0)
    ct.Bitter_Upper_CV__b3c17.constant(t + 100e-3, 2.91992)
    ct.Bitter_Lower_CV__b3c13.constant(t + 100e-3, 2.5)
    ct.Bitter_Lower_CC__b3c12.constant(t + 100e-3, 3.99994)
    ct.Bitter_Upper_CC__b3c16.constant(t + 100e-3, 3.99994)
    # ct.Bitter_V_AH.constant(t + 300e-3, 0)  # replaced by ramp at t + 310e-3 in proc 027
    # ct.Bitter_V_HH.constant(t + 300e-3, 0)  # replaced by ramp at t + 310e-3 in proc 027
    ct.Bitter_V_AH.ramp(t=t + 300e-3, duration=10e-3, initial=0, final=0, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 300e-3, duration=10e-3, initial=0, final=7.5, samplerate=FAST_FREQ)
    # ct.Bitter_V_AH.constant(t + 1897e-3, 0)  # replaced by ramp at t + 1997e-3 in proc 027
    # ct.Bitter_V_HH.constant(t + 1897e-3, 7.5)  # replaced by ramp at t + 1997e-3 in proc 027
    ct.Bitter_V_AH.ramp(t=t + 1897e-3, duration=100e-3, initial=0, final=0, samplerate=FAST_FREQ)
    ct.Bitter_V_HH.ramp(t=t + 1897e-3, duration=100e-3, initial=7.5, final=0, samplerate=FAST_FREQ)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 1998e-3, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 1999e-3, 0)
    ct.Bitter_Lower_CC__b3c12.constant(t + 1999e-3, 1.00006)
    ct.Bitter_Upper_CC__b3c16.constant(t + 1999e-3, 1.00006)
    ct.Bitter_Upper_CV__b3c17.constant(t + 1999e-3, 2.30011)
    ct.Bitter_Lower_CV__b3c13.constant(t + 1999e-3, 2.30011)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t + 1999.2e-3, 5)

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
    # # ct.Bias_Y_HH.constant(t - 5e-3, -6.19995)  # replaced by ramp at t in proc 029
    # ct.MW_Trig__b2c04.go_high(t - 5e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    # ct.Bias_Y_HH.ramp(t=t - 5e-3, duration=5e-3, initial=-6.19995, final=-6.09985, samplerate=FAST_FREQ)
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
    # # ct.CS_HFImg_Freq__b3c22.constant(t - 1300e-3, -10)  # replaced by ramp at t - 20e-3 in proc 030
    # # 7.7_N_Cs_MOT_Freq: -7.60986 JUMP — no new channel
    # # 7.7_N_Cs_MOT_Freq: -2.99988 COARSE — no new channel
    # ct.Pixelfly_Trig__b2c07.go_high(t - 100e-3)
    # ct.Cs_LFImg_Shutter__b1c11.go_low(t - 100e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t - 99.9e-3)
    # ct.Cs_HFImg_Shutter__b1c06.go_high(t - 80e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t - 30e-3, 5)
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t - 1300e-3, duration=1280e-3, initial=-10, final=code_65511, samplerate=FAST_FREQ)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t - 10e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t - 10e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t - 10e-3)
    # ct.MW_Trig__b2c04.go_high(t - 0.02e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    # ct.MW_Trig__b2c04.go_low(t)
    # ct.DMD_Movie_Trig__b1c20.go_high(t)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 0.1e-3)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t + 0.1e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 0.1e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 7e-3, 0)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 15e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 15e-3)
    # # ct.CS_HFImg_Freq__b3c22.constant(t + 20e-3, code_65511)  # replaced by ramp at t + 2000e-3 in proc 030
    # ct.Cs_EOM_Freq_b4c15.constant(t + 70e-3, 5)
    # ct.Cs_VImg_Shutter__b1c15.go_high(t + 90e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 90e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 90e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 100e-3)
    # # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 100e-3)  # replaced by ramp at t + 100.1e-3 in proc 030
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 100e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 100.1e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.ramp(t=t + 100e-3, duration=0.1e-3, initial=5, final=0, samplerate=FAST_FREQ)
    # ct.Cs_VImg_Shutter__b1c15.go_low(t + 100.1e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 100.1e-3)
    # ct.Cs_EOM_Freq_b4c15.constant(t + 107e-3, 0)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 115e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 115e-3)
    # # 7.7_N_Cs_MOT_Freq: -2.99988 JUMP — no new channel
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t + 20e-3, duration=1980e-3, initial=code_65511, final=-10, samplerate=FAST_FREQ)
    # # 7.7_N_Cs_MOT_Freq: -7.6001 COARSE — no new channel

    # # procedure 031: test_trigger
    # t = code_65501/1e3
    # add_time_marker(t, 'test_trigger')
    # ct.Scope_Trig__b2c08.go_high(t)
    # ct.Spec_Analyzer_Trig__b2c09.go_high(t)
    # ct.Scope_Trig__b2c08.go_low(t + 1e-3)
    # ct.Spec_Analyzer_Trig__b2c09.go_low(t + 1e-3)

    # procedure 032: Cs_molasses_dark
    t = 7500e-3
    add_time_marker(t, 'Cs_molasses_dark')
    ct.Cs_3DMOT_Shutter__b1c03.go_low(t - 10e-3)
    # ct.Cs_Rep_Freq__b3c26.constant(t, 6.40015)  # replaced by ramp at t + 10e-3 in proc 032
    # ct.Cs_MOT_Freq__b3c24.constant(t, -5.79987)  # replaced by ramp at t + 10e-3 in proc 032
    ct.Cs_3DMOT_AO_Sw__b1c02.go_low(t + 0.02e-3)
    ct.Cs_MOT_Freq__b3c24.ramp(t=t, duration=10e-3, initial=-5.79987, final=-7.70996, samplerate=FAST_FREQ)
    ct.Cs_Rep_Freq__b3c26.ramp(t=t, duration=10e-3, initial=6.40015, final=7.79999, samplerate=FAST_FREQ)

    # # procedure 033: Dual_Color_Combine
    # t = 21700e-3
    # add_time_marker(t, 'Dual_Color_Combine')
    # # 7.6_oTOP_fcarrier: 2.09991 JUMP — no new channel
    # # 7.6_oTOP_fcarrier: 0.899963 FINE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.0750732 JUMP — no new channel
    # # 2.0_Dual_780nm_Int_Lock: 2.5 JUMP — no new channel
    # # 7.0_oTOP_Int_lok: 1.1499 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.899963 FINE — no new channel
    # # 2.0_Dual_780nm_Int_Lock: 0.700073 FINE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 2.00012 FINE — no new channel
    # # 7.0_oTOP_Int_lok: 0.0100708 FINE — no new channel
    # # 7.3_oTOP_AO_AM: 0 JUMP — no new channel
    # # 7.6_oTOP_fcarrier: 1.49994 JUMP — no new channel
    # # 7.3_oTOP_AO_AM: 10 JUMP — no new channel

    # # procedure 034: Li_Img_Freq_Ramp_Down
    # t = code_65501/1e3
    # add_time_marker(t, 'Li_Img_Freq_Ramp_Down')
    # ct.BFL_Int_Lock__b3c02.constant(t - 50e-3, 0)
    # # ct.Li_Img_Freq__b4c01.constant(t + 800e-3, code_65508)  # replaced by ramp at t + 2300e-3 in proc 034
    # ct.Li_Img_Freq__b4c01.ramp(t=t + 800e-3, duration=1500e-3, initial=code_65508, final=-9.04999, samplerate=SLOW_FREQ)
    # ct.Li_Img_Freq__b4c01.constant(t + 2301e-3, -9.04999)

    # # procedure 035: MW_Calibration_Imaging
    # t = 22800e-3
    # add_time_marker(t, 'MW_Calibration_Imaging')
    # # ct.CS_HFImg_Freq__b3c22.constant(t - 300e-3, -5.20996)  # replaced by ramp at t - 20e-3 in proc 035
    # # 2.0_Dual_780nm_Int_Lock: 0 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0 JUMP — no new channel
    # ct.Cs_LFImg_Shutter__b1c11.go_low(t - 100e-3)
    # ct.Cs_HFImg_Shutter__b1c06.go_high(t - 80e-3)
    # ct.oTOP_Pos_Lock_Enable__b2c05.go_high(t - 50e-3)
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t - 300e-3, duration=280e-3, initial=-5.20996, final=code_65511, samplerate=SLOW_FREQ)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t - 10e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t - 10e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t - 10e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t - 10e-3)
    # # 2.0_Dual_780nm_Int_Lock: 0.400085 COARSE — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0.180054 COARSE — no new channel
    # ct.MW_Trig__b2c04.go_high(t - 1e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t)
    # # 2.0_Dual_780nm_Int_Lock: 0 JUMP — no new channel
    # # 7.5_Dual_1064_Int_Lock: 0 JUMP — no new channel
    # ct.MW_Trig__b2c04.go_low(t)
    # ct.DMD_Movie_Trig__b1c20.go_high(t)
    # # 7.3_oTOP_AO_AM: 0 JUMP — no new channel
    # # 7.0_oTOP_Int_lok: -1.00006 JUMP — no new channel
    # ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 0.1e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 0.1e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 0.1e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 7e-3)
    # # 2.6_V_HH: 0 JUMP — no new channel
    # # 2.7_V_AH: 0 JUMP — no new channel
    # ct.Bitter_Precision_Disable__b1c00.go_high(t + 10e-3)
    # ct.Bitter_IServo_FB_Sw__b3c11.constant(t + 10e-3, 5)
    # ct.Bitter_Upper_HH_Sw__b3c18.constant(t + 10e-3, 0)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 15e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 15e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_high(t + 630e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 630e-3)
    # ct.Pixelfly_Shutter__b2c06.go_high(t + 630e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 630e-3)
    # ct.Pixelfly_Trig__b2c07.go_high(t + 640e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 640e-3)
    # ct.Cs_HImg_Shutter__b1c07.go_low(t + 640e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 640e-3)
    # ct.Pixelfly_Trig__b2c07.go_low(t + 640.1e-3)
    # ct.Cs_HFImg_AO_Sw__b1c05.go_low(t + 640.1e-3)
    # ct.DMD_Movie_Trig__b1c20.go_low(t + 640.1e-3)
    # ct.Pixelfly_Shutter__b2c06.go_low(t + 647e-3)
    # # ct.CS_HFImg_Freq__b3c22.constant(t + 650e-3, code_65511)  # replaced by ramp at t + 950e-3 in proc 035
    # ct.Cs_HFImg_AO_Sw__b1c05.go_high(t + 655e-3)
    # ct.DMD_Movie_Trig__b1c20.go_high(t + 655e-3)
    # ct.CS_HFImg_Freq__b3c22.ramp(t=t + 650e-3, duration=300e-3, initial=code_65511, final=-5.20996, samplerate=SLOW_FREQ)
    # ct.CS_HFImg_Freq__b3c22.constant(t + 951e-3, -5.20996)

    # # procedure 036: MW_Calibration_Load
    # t = 18800e-3
    # add_time_marker(t, 'MW_Calibration_Load')
    # # 5.11_BFL_AO_AM: 5.19989 JUMP — no new channel
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
    # # 7.1_CS_Rep_AO_AM: 3.50006 JUMP — no new channel
    # # 7.4_oTOP_mod_AM: 1.19995 JUMP — no new channel
    # # 2.1_CS_Rep_AO_AM: 5 JUMP — no new channel
    # # 7.3_oTOP_AO_AM: 10 JUMP — no new channel
    # # 7.2_ZDT_AO_AM: 10 JUMP — no new channel
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
    # # 7.1_CS_Rep_AO_AM: 3.50006 JUMP — no new channel
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
    # # 7.1_CS_Rep_AO_AM: 2.00012 COARSE — no new channel
    # ct.Bitter_HH_Upper_FF__b3c10.ramp(t=t + 8e-3, duration=400e-3, initial=4.46014, final=0, samplerate=SLOW_FREQ)
    # ct.FF_Disable__b1c24.go_high(t + 409e-3)
    # # 7.0_oTOP_Int_lok: 2.00012 JUMP — no new channel
    # # 7.4_oTOP_mod_AM: -0.964966 FINE — no new channel
    # # 2.7_V_AH: -0.140686 COARSE — no new channel
    # # 7.1_CS_Rep_AO_AM: -0.100098 COARSE — no new channel
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
    t = 9276e-3
    ct.Bitter_V_AH.constant(t, 0.188293)
    ct.Dual_1064_Int_Lock__b4c16.constant(t, 0)
    ct.Li_Img_Freq__b4c01.constant(t, 1.00006)
    ct.Bitter_Lower_FF__b3c14.constant(t, 0)
    ct.oTOP_FCarrier__b4c07.constant(t, 5)
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
    ct.DMD_Shutter__b1c21.go_high(t)
    ct.Cs_HOP_Shutter__b1c09.go_high(t)
    ct.DMD_Movie_Trig__b1c20.go_high(t)
    ct.oTOP_Pos_Lock_Enable__b2c05.go_low(t)
    ct.Bitter_Precision_Disable__b1c00.go_high(t)
    ct.Li_MOT_AO_AM__b4c02.constant(t, 10)
    ct.Li_Rep_AO_AM__b4c05.constant(t, 10)
    ct.DMD_AO_AM__b3c29.constant(t, 3.8)
    ct.Cs_Rep_Freq__b3c26.constant(t, 6.49)
    ct.Li_MRep_AO_FM__b4c04.constant(t, 0.40863)
    ct.Li_Img_AO_AM__b4c00.constant(t, 10)
    ct.Dual_780_Int_Lock__b3c30.constant(t, 5)
    ct.CS_HFImg_Freq__b3c22.constant(t, -10)
    ct.Bias_X_HH.constant(t, -0.5)
    ct.Bias_X_AH.constant(t, 1)
    ct.Bias_Y_AH.constant(t, 0.5)
    ct.Bias_Y_HH.constant(t, 0.8)
    ct.Bias_Z_AH.constant(t, 0.2)
    ct.Bias_Z_HH.constant(t, -0.8)
    ct.Bitter_Lower_CC__b3c12.constant(t, 1)
    ct.Bitter_Upper_CV__b3c17.constant(t, 2)
    ct.Bitter_Upper_CC__b3c16.constant(t, 1)
    ct.Bitter_Lower_CV__b3c13.constant(t, 1.5)
    ct.BFL_AO_Sw__b3c01.constant(t, 5)
    ct.Bitter_Upper_AH_Sw__b3c15.constant(t, 5)
    ct.Bitter_Upper_HH_Sw__b3c18.constant(t, 0)
    ct.BFL_Int_Lock__b3c02.constant(t, -2)
    ct.Pixelfly_Shutter__b2c06.go_low(t)
    ct.Bitter_IServo_FB_Sw__b3c11.constant(t, 0)
    ct.Aerotech_Control__b3c00.constant(t, 0)
    ct.Li_MOT_Freq__b4c03.constant(t, 5.28442)
    ct.Cs_EOM_Freq_b4c15.constant(t, 0)
    ct.Cs_3DMOT_AO_AM__b3c21.constant(t, 2.3)
    ct.oTOP_Int_Lock__b4c08.constant(t, 0)
    ct.Cs_Rep_AO_AM__b3c25.constant(t, 3)
    ct.Cs_VImg_AO_AM__b3c28.constant(t, 0)
    ct.oTOP_AO_AM__b4c06.constant(t, 0)
    ct.oTOP_Mod_AM__b4c09.constant(t, 0)
    ct.Li_EOM_Freq__b3c31.constant(t, 0)
    ct.Cs_RSC_AO_AM__b3c27.constant(t, 5)
    ct.Cs_MOT_Freq__b3c24.constant(t, -7.15)
    stop(t+10e-6)
