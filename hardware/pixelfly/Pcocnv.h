//-----------------------------------------------------------------//
// Name        | Pcoconv.h                   | Type: ( ) source    //
//-------------------------------------------|       (*) header    //
// Project     | PCO                         |       ( ) others    //
//-----------------------------------------------------------------//
// Platform    | PC                                                //
//-----------------------------------------------------------------//
// Environment | Visual 'C++'                                      //
//-----------------------------------------------------------------//
// Purpose     | PCO - Convert DLL function call definitions       //
//-----------------------------------------------------------------//
// Author      | MBL, PCO AG                                       //
//-----------------------------------------------------------------//
// Revision    |  rev. 1.15 rel. 1.15                              //
//-----------------------------------------------------------------//
// Notes       |                                                   //
//-----------------------------------------------------------------//
// (c) 2002 PCO AG * Donaupark 11 *                                //
// D-93309      Kelheim / Germany * Phone: +49 (0)9441 / 2005-0 *  //
// Fax: +49 (0)9441 / 2005-20 * Email: info@pco.de                 //
//-----------------------------------------------------------------//


//-----------------------------------------------------------------//
// Revision History:                                               //
//-----------------------------------------------------------------//
// Rev.:     | Date:      | Changed:                               //
// --------- | ---------- | ---------------------------------------//
//  1.10     | 03.07.2003 |  gamma, alignement added, FRE          //
//-----------------------------------------------------------------//
//  1.12     | 16.03.2005 |  PCO_CNV_COL_SET added, FRE            //
//-----------------------------------------------------------------//
//  1.14     | 12.05.2006 |  conv24 and conv16 added, FRE          //
//-----------------------------------------------------------------//
//  1.15     | 23.10.2007 |  PCO_CNV_COL_SET removed, FRE          //
//           |            |  Adapted all structures due to merging //
//           |            |  the data sets of the dialoges         //
//-----------------------------------------------------------------//
//  0.0      |   .  .2003 |                                        //
//           |            |                                        //
//-----------------------------------------------------------------//
/*
// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the PCOCNV_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// PCOCNV_API functions as being imported from a DLL, wheras this DLL sees symbols
// defined with this macro as being exported.
*/


//#include "cnv_s.h"

#ifdef PCOCNV_EXPORTS
#define PCOCNV_API __declspec(dllexport)
#define PCOCNV_API_EX __declspec(dllexport) WINAPI
#else
#define PCOCNV_API __declspec(dllimport)
#define PCOCNV_API_EX __declspec(dllimport) WINAPI
#endif
 
#ifndef _WIN32
#define PCOCNV_API_EX
#define PCOCNV_API
#endif


#ifdef __cplusplus
extern "C" {
#endif  /* __cplusplus */


void* PCOCNV_API CREATE_BWLUT(int bitpix, int min_out, int max_out);
//creates a structure BWLUT
//allocates memory for the structure and for 2^bitpix bytes 
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255

void* PCOCNV_API_EX CREATE_BWLUT_EX(int bitpix, int min_out, int max_out, int ialign);
//creates a structure BWLUT
//allocates memory for the structure and for 2^bitpix bytes 
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255
//ialign: flag for alignment; 0: right(LSB) aligned values (bit bitpix...0);
//                            1: left(MSB) aligned(bit 16...16-bitpix)

int PCOCNV_API DELETE_BWLUT(void *lut);
int PCOCNV_API_EX DELETE_BWLUT_EX(void *lut);
//delete the LUT 
//free all allocated memory

void* PCOCNV_API CREATE_COLORLUT(int bitpix, int min_out, int max_out);
//creates a structure COLORLUT, which exists of three BWLUT's
//one for each color red, green and blue 
//allocates memory for the structure and for 2^bitpix bytes 
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255 

void* PCOCNV_API_EX CREATE_COLORLUT_EX(int bitpix, int min_out, int max_out, int ialign);
//creates a structure COLORLUT, which exists of three BWLUT's
//one for each color red, green and blue 
//allocates memory for the structure and for 2^bitpix bytes 
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255 
//ialign: flag for alignment; 0: right(LSB) aligned values (bit bitpix...0);
//                            1: left(MSB) aligned(bit 16...16-bitpix)

int PCOCNV_API DELETE_COLORLUT(void* lut);
int PCOCNV_API_EX DELETE_COLORLUT_EX(void* lut);
//delete the LUT 
//free all allocated memory

void* PCOCNV_API CREATE_PSEUDOLUT(int bitpix, int min_out, int max_out);
//creates a structure PSEUDOLUT, which exists of one BWLUT
//and one table for each color red, green and blue 
//allocates memory for the structure and for 3 * ( 2^bitpix ) bytes  
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255

void* PCOCNV_API_EX CREATE_PSEUDOLUT_EX(int bitpix, int min_out, int max_out, int ialign);
//creates a structure PSEUDOLUT, which exists of one BWLUT
//and one table for each color red, green and blue 
//allocates memory for the structure and for 3 * ( 2^bitpix ) bytes  
//bitpix: bits per pixel of the picture data (i.e. 12)
//min_out: lowest value of output in table  0...254
//max_out: highest value of output in table 1...255
//ialign: flag for alignment; 0: right(LSB) aligned values (bit bitpix...0);
//                            1: left(MSB) aligned(bit 16...16-bitpix)

int PCOCNV_API DELETE_PSEUDOLUT(void *lut);
int PCOCNV_API_EX DELETE_PSEUDOLUT_EX(void *lut);
//delete the LUT 
//free all allocated memory

void PCOCNV_API CONVERT_SET(void *lut,int min,int max,int typ);
//set the range within which the data of the picture is 
//to be converted into 8bit data. 
//New values for the table are calculated
//lut: BWLUT to set 
//min: minimal value of input 0...2^bitpix-2
//max: maximal value of input 1...2^bitpix-1
//condition: min<max
//typ: 0x00 = linear table
//     0x01 = logarithmic table
//     0x80 = invers linear table
//     0x81 = invers logarithmic table

void PCOCNV_API_EX CONVERT_SET_EX(void *lut,int min,int max, int typ, double dgamma);
//set the range within which the data of the picture is 
//to be converted into 8bit data. 
//New values for the table are calculated
//lut: BWLUT to set 
//min: minimal value of input 0...2^bitpix-2
//max: maximal value of input 1...2^bitpix-1
//condition: min<max
//typ: 0x80 = invers table
//dgamma: gamma value for conversion

void PCOCNV_API_EX CONVERT_SET_COL_EX(void *clut, int rmin, int gmin, int bmin, int rmax, int gmax, int bmax,
                                      int typ, double dgamma, double dsaturation);
//set the range within which the data of the picture is 
//to be converted into 8bit data. 
//New values for the table are calculated
//clut: COLORLUT to set 
//(rgb)min: minimal value of input 0...2^bitpix-2
//(rgb)max: maximal value of input 1...2^bitpix-1
//condition: min<max
//typ: 0x00 = linear table
//     0x01 = logarithmic table
//     0x80 = invers linear table
//     0x81 = invers logarithmic table
//dgamma: gamma value for conversion

int PCOCNV_API LOAD_PSEUDO_LUT(void *plut, int format, char *filename);
int PCOCNV_API_EX LOAD_PSEUDO_LUT_EX(void *plut, int format, char *filename);
//load the three pseudolut color tables of plut
//from the file filename
//which includes data in the following formats

//plut:   PSEUDOLUT to write data in 
//filename: name of file with data
//format: 0 = binary 256*RGB
//        1 = binary 256*R,256*G,256*R
//        2 = ASCII  256*RGB 
//        3 = ASCII  256*R,256*G,256*R

 
int PCOCNV_API CONV_BUF_12TO8(int mode, int width,int height, word *b12, byte *b8,void *lut);
//int PCOCNV_API_EX CONV_BUF_12TO8_EX(int mode, int width,int height, word *b12, byte *b8,void *lut);
//convert picture data in b12 to 8bit data in b8
//through table in structure of BWLUT
//mode:   0       = normal
//        bit0: 1 = flip
//        bit3: 1 = mirror  
//width:  width of picture
//height: height of picture
//b12:    pointer to picture data array
//b8:     pointer to byte data array (bw, 1 byte per pixel)
//lut:    pointer to structure of typ BWLUT

int PCOCNV_API CONV_BUF_12TO24(int mode, int width,int height, word *b12, byte *b24,void *lut);
//int PCOCNV_API_EX CONV_BUF_12TO24_EX(int mode, int width,int height, word *b12, byte *b24,void *lut);
//convert picture data in b12 to 8bit data in b8
//through table in structure of BWLUT
//mode:   0       = normal
//        bit0: 1 = flip
//        bit3: 1 = mirror  
//width:  width of picture
//height: height of picture
//b12:    pointer to picture data array
//b24:    pointer to byte data array (RGB, 3 byte per pixel, grayscale)
//lut:    pointer to structure of typ BWLUT

int PCOCNV_API CONV_BUF_12TOCOL(int mode, int width, int height, word *gb12, byte *gb8,void *clut);
int PCOCNV_API_EX CONV_BUF_12TOCOL_EX(int mode, int width, int height, word *gb12, byte *gb8,void *clut);
//convert picture data in b12 to 24bit or 32bit data in b8
//through tables in structure COLORLUT
//mode:   0       = normal to 24bit BGR
//        bit0: 1 = flip
//        bit1: 1 = 32bit BGR0
//        bit3: 1 = mirror  
//        bit5: 1 = low average
//width:  width of picture
//height: height of picture
//b12:    pointer to picture data array
//b8:     pointer to byte data array (RGBx)
//lut:    pointer to structure of typ COLORLUT

int PCOCNV_API CONV_BUF_12TOPSEUDO(int mode, int width, int height, word *gb12, byte *gb8,void *plut);
int PCOCNV_API_EX CONV_BUF_12TOPSEUDO_EX(int mode, int width, int height, word *gb12, byte *gb8,void *plut);
//convert picture data in b12 to 24bit or 32bit data in b8
//through tables in structure PSEUDOLUT
//mode:   0       = normal to 24bit BGR
//        bit0: 1 = flip
//        bit1: 1 = 32bit BGR0
//        bit3: 1 = mirror  

//width:  width of picture
//height: height of picture
//b12:    pointer to picture data array
//b8:     pointer to byte data array (RGBx)
//lut:    pointer to structure of typ PSEUDOLUT

int PCOCNV_API_EX CONV_BUF_16TOCOL16(int mode, int width, int height, word *gb16in, word *gb16out, void *clut);
//convert picture data in b12 to R16,G16,B16 in gb16out
//through tables in structure COLORLUT
//mode:   0       = normal to RGB
//        bit0: 1 = flip
//        bit3: 1 = mirror  
//width:  width of picture
//height: height of picture
//gb16in:  pointer to raw picture data array
//gb16out: pointer to converted data array (RGB 16bit)
//lut:    pointer to structure of typ COLORLUT

int PCOCNV_API_EX AUTOBALANCE(int mode, int iwidth, int iheight, word *gb16in, void* collut, BOOL bdouble, 
                              int ilowerlimitprz, int iupperlimitprz, int idarkoffset,
                              SHORT* sredgain, SHORT* sgreengain, SHORT* sbluegain);
//gets the gain values for red, green and blue for a white image
//mode: demosaicking value
//width: image width
//height: image height
//*bg16in:  pointer to raw picture data array
//*COLORLUT: pointer to the colorlut; holds neccessary information about the raw image
//bdouble: info about the raw image; set to TRUE in case of a doubleshutter image
//ilowerlimitprz: only pixelvalues above this limit will be used (limit in %, e.g. 7%)
//iupperlimitprz: only pixelvalues below this limit will be used (limit in %, e.g. 97%)
//*sxyzgain: pointer to receive the gain values

#ifdef __cplusplus
}
#endif
