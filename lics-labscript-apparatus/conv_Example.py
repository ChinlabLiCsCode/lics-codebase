from labscript import start, stop, add_time_marker, wait
from labscriptlib.LiCs_ExperimentApparatus.connection_table import ConnectionTable

SLOW_FREQ = 1e3  # slow ramp frequency: 1 ms per edge
FAST_FREQ = 50e3  # fast ramp frequency: 20 us per edge

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

# ch no	name						  init val	analog?
# -----	----						  --------	-------
# 000		3.0_N_V_AH              	    0.1883		1
# 001		3.1_Dual_1064_Int_Lock  	    3.9999		1
# 002		3.2_Li_Img_Freq         	   -5.2499		1
# 003		3.3_lower_FF            	    0.0000		1
# 004		3.4_oTOP_fcarrier       	    1.7999		1
# 005		3.5_AH_upper_FF         	    0.0000		1
# 006		3.6_HH_upper_FF         	    0.0000		1
# 007		3.7_N_V_HH              	   -0.0183		1
# 008		2.0_Dual_780nm_Int_Lock 	    2.5000		1
# 009		2.1_CS_Rep_AO_AM        	    5.0000		1
# 010		2.2_                    	    0.0000		1
# 011		2.3_Li_MRep_AO_FM       	    0.4086		1
# 012		2.4_                    	    0.0000		1
# 013		2.5_                    	    0.0000		1
# 014		2.6_V_HH                	   -0.0183		1
# 015		2.7_V_AH                	    0.1883		1
# 016		7.0_oTOP_Int_lok        	    0.3000		1
# 017		7.1_CS_Rep_AO_AM        	    5.0000		1
# 018		7.2_Cs_VHF_AO_AM        	    0.4001		1
# 019		7.3_oTOP_AO_AM          	   10.0000		1
# 020		7.4_oTOP_mod_AM         	    0.0000		1
# 021		7.5_Dual_1064_Int_Lock  	    3.9999		1
# 022		7.6_oTOP_fcarrier       	    1.7999		1
# 023		7.7_N_Cs_MOT_Freq       	   -7.1500		1
# 024		1.3_Li_Img_AO_Sw        	    5.0000		0
# 025		1.4_Cs_3DMOT_AO_Sw      	    5.0000		0
# 026		1.5_DMD_AO_Sw           	    5.0000		0
# 027		1.6_AndorCCD_Trig       	    0.0000		0
# 028		1.7_Li_EOM_AO_Sw        	    5.0000		0
# 029		1.8_Cs_2DMOT_Shutter    	    0.0000		0
# 030		1.9_DMD_AO_FM           	    0.0000		0
# 031		1.10_Cs_Oneshot_Bypass  	    0.0000		0
# 032		1.11_Li_MOT_AO_Sw       	    5.0000		0
# 033		1.12_Li_Rep_AO_Sw       	    5.0000		0
# 034		1.13_Li_Rep_Shutter     	    5.0000		0
# 035		1.14_Li_MOT_Shutter     	    5.0000		0
# 036		1.15_Li_V_Img_Shutter   	    0.0000		0
# 037		1.16_Li_Zeeman_Shutter  	    5.0000		0
# 038		1.17_Cs_H_Img_Shutter   	    0.0000		0
# 039		1.18_Li_EOM_H_Shutter   	    0.0000		0
# 040		1.19_Cs_ZM_shutter      	    5.0000		0
# 041		1.20_MW_pulse_SW        	    0.0000		0
# 042		1.21_pixelfly trigger   	    0.0000		0
# 043		1.22_MW_INCR_UP         	    0.0000		0
# 044		1.23_CS_EOM_SW          	    5.0000		0
# 045		1.24_Cs_RSC_AO_SW       	    5.0000		0
# 046		1.25_ZDT_AO_SW          	    5.0000		0
# 047		1.26_MW_SWEEP           	    5.0000		0
# 048		1.27_Real_CS_RSC_AO_SW  	    5.0000		0
# 049		1.28_Li_H_Img_shu       	    0.0000		0
# 050		1.29_Real_CS_RSC_SHU    	    0.0000		0
# 051		1.30_test trigger       	    0.0000		0
# 052		1.31_Cs_Li_Zeswitch     	    5.0000		0
# 053		1.32_ZCurrents          	    5.0000		0
# 054		6.0                     	    5.0000		0
# 055		6.1_Mod_AO_Switch       	    5.0000		0
# 056		6.2_XDT_AO_SW           	    5.0000		0
# 057		6.3_Cs_HF_AO_Sw         	    5.0000		0
# 058		6.4_N_V_Rep_Shutter     	    5.0000		0
# 059		6.5_N_Cs_Rep_Shutter    	    5.0000		0
# 060		6.6_N_Cs_V_Img_Shutter  	    0.0000		0
# 061		6.7_N_Cs_H_Img_Shutter  	    0.0000		0
# 062		6.8_Dual_780nm_SW       	    5.0000		0
# 063		6.9_Dual_1064nm_SW      	    5.0000		0
# 064		6.10                    	    0.0000		0
# 065		6.11_N_Cs_HF_Img_Shutter	    0.0000		0
# 066		6.12_N_Cs_LF_Img_Shutter	    5.0000		0
# 067		6.13_N_Cs_Z_Shutter     	    5.0000		0
# 068		6.14_N_Cs_2D_MOT_Shutter	    5.0000		0
# 069		6.15_N_Cs_3D_MOT_Shutter	    5.0000		0
# 070		6.16                    	    0.0000		0
# 071		6.17_Spec_Analysis_Trig 	    0.0000		0
# 072		6.18                    	    0.0000		0
# 073		6.19_N_Cs_3D_SW         	    5.0000		0
# 074		6.20_Cs_LF_Img_AO_Sw    	    5.0000		0
# 075		6.21_FF_Disable         	    0.0000		0
# 076		6.22                    	    0.0000		0
# 077		6.23_N_OP_AO_SW         	    5.0000		0
# 078		6.24                    	    0.0000		0
# 079		6.25_DMD_Shutter        	    0.0000		0
# 080		6.26_N_CsOP_Shut_H      	    5.0000		0
# 081		6.27_DMD_Movie_Trig     	    0.0000		0
# 082		6.28                    	    0.0000		0
# 083		6.29_oTOP_Pos_Lock_Enabl	    0.0000		0
# 084		6.30_Li_Oneshot_Bypass  	    0.0000		0
# 085		6.31_B_Precision_Disable	    5.0000		0
# 086		4.0_Li_MOT_AO_AM        	   10.0000		1
# 087		4.1_Li_Rep_AO_AM        	   10.0000		1
# 088		4.2_Dual_780_AO_AM      	   10.0000		1
# 089		4.3_Dual_1064_AO_AM     	   10.0000		1
# 090		4.4_DMD_AO_AM           	    3.8000		1
# 091		4.5_N_Cs_Repump_Freq    	    6.5100		1
# 092		4.6_Li_MRep_AO_FM       	    0.4086		1
# 093		4.7_Li_Img_AO_AM        	   10.0000		1
# 094		5.8_Dual_780nm_Int_Lock 	    2.5000		1
# 095		5.9_Cs_LF_Img_AO_AM     	   10.0000		1
# 096		5.10_CS_HF_Img_Freq     	  -10.0000		1
# 097		5.11_BFL_AO_AM          	   10.0000		1
# 098		5.12_Bias_1/2_HH_x      	   -1.0000		1
# 099		5.13_Bias_1/2_AH_-x     	    1.0000		1
# 100		5.14_Bias_3/4_AH_-y     	    0.0000		1
# 101		5.15_Bias_3/4_HH_y      	    1.0000		1
# 102		5.16_Bias_5/6_AH_z      	   -1.0000		1
# 103		5.17_Bias_5/6_HH_-z     	   -6.0000		1
# 104		5.18_COIL_BOT_CC        	    1.0000		1
# 105		5.19_COIL_TOP_CV        	    2.0000		1
# 106		5.20_COIL_TOP_CC        	    1.0000		1
# 107		5.21_COIL_BOT_CV        	    1.5000		1
# 108		5.22_BFL_AO_SW          	    5.0000		1
# 109		5.23_COIL_TOP_AH        	    5.0000		1
# 110		5.24_COIL_TOP_HH        	    0.0000		1
# 111		5.25_N_BFL_INT_LOCK     	    0.1000		1
# 112		5.26_H_Pixelfly_Shutter 	    5.0000		1
# 113		5.27_IServo_FB_Switch   	    0.0000		1
# 114		5.28_aerotech_trigger   	    0.0000		1
# 115		5.29_Li_MOT_Freq        	    5.2844		1
# 116		5.30_Cs_EOM_Freq        	    9.0000		1
# 117		5.31_Cs_3D_AO_AM        	    2.3000		1
# 118		8.0_oTOP_Int_lok        	    0.3000		1
# 119		8.1_CS_Rep_AO_AM        	    5.0000		1
# 120		8.2_Cs_VHF_AO_AM        	    5.0000		1
# 121		8.3_oTOP_AO_AM          	   10.0000		1
# 122		8.4_oTOP_mod_AM         	    0.0000		1
# 123		8.5_Li_EOM_Freq         	   -4.5000		1
# 124		8.6_Cs_RSC_AO_AM        	    5.0000		1
# 125		8.7_N_Cs_MOT_Freq       	   -7.1500		1

# proc no	name							  time		enabled
# -------	----							  ----		------
# 000		Cs_MOT_Loading          	11700.0000		1
# 001		Cs_Molasses_Cooling     	15495.0000		1
# 002		Cs_H_Imaging            	65501.0000		0
# 003		Cs_RSC1                 	15500.0000		1
# 004		Aerotech_return         	15600.0000		1
# 005		Dual_Imaging_H          	65501.0000		0
# 006		Dual_Imaging_V          	65501.0000		1
# 007		FB_Bias_field           	15600.0000		1
# 008		Cs_Dark                 	15534.0000		1
# 009		Li_HF_V_Imaging         	65501.0000		0
# 010		Cs_Evaporation          	15600.0000		1
# 011		Spare                   	29600.0000		1
# 012		Li_Feshbach             	10000.0000		1
# 013		Dual_Evap               	27700.0000		1
# 014		Li_H_Imaging            	65501.0000		0
# 015		Li_V_Imaging            	65501.0000		0
# 016		Cs_Levitation1          	15532.0000		1
# 017		Li_Evaporation          	10000.0000		1
# 018		Li_Dark                 	10000.0000		1
# 019		Cs_V_Imaging            	65501.0000		0
# 020		Li_CMOT                 	10000.0000		1
# 021		Cs_CMOT                 	15445.0000		1
# 022		Li_MOT_Loading          	    1.0000		1
# 023		True_TOF                	65500.0000		1
# 024		Li_Killing              	24600.0000		1
# 025		Low_Field_BEC_Field     	 7519.0000		0
# 026		FB_Bias_Field_off       	65502.0000		0
# 027		FB_Field_Gentle_off     	65502.0000		1
# 028		Unlevitation            	21600.0000		0
# 029		Cs_HF_H_Imaging         	65501.0000		0
# 030		Cs_HF_V_Imaging         	65501.0000		0
# 031		test_trigger            	65501.0000		0
# 032		Cs_molasses_dark        	12500.0000		0
# 033		Dual_Color_Combine      	24700.0000		1
# 034		Li_Img_Freq_Ramp_Down   	65501.0000		1
# 035		coil_cool_down          	65502.0000		1
# 036		MW_Calibration_load     	18800.0000		0
# 037		MW_Calibration_Molasses 	21850.0000		0
# 038		MW_Calibration_Trap     	21887.0000		0

if __name__ == '__main__':
    ct = ConnectionTable()


    start()

    # pause for line trigger at 1 us, with a timeout of 100 ms
    t = 20e-6
    add_time_marker(t, "Waiting for line trigger")
    wait('line_trigger', t, timeout=0.1)

    # procedure 000: Cs_MOT_Loading
    with 11.700 as t:
        add_time_marker(t, "Cs MOT Loading")
        # list all commands here, with times defined relative to t at the procedure start
    
    # stop sequence at the end of the full sequence time
    stop(t)