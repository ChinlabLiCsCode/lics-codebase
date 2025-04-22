function [error_code, result_image] = pfCOPY_BUFFER(source_bufadr,...
                                       bit_pix, image_width, image_height,...
                                       varargin)
% [error_code,result_image] = pfCOPY_BUFFER(source_bufadr,...
%                                       bit_pix, image_width, image_height);
% pfCOPY_BUFFER is a Matlab only function, which has NO corresponding
% function in the pixefly SDK, because if the recorded image is in the
% buffer, PC memory, it is the duty of the application to take it from
% there. In Matlab the pointer-address handling is more difficult, this
% funtion pfCOPY_BUFFER provide a mean to copy the image from the memory
% into the Matlab environment.
% input  : source_bufadr [ptr]  - buffer_address returned from MAP_BUFFER_EX
%          bit_pix [int32]      - number of bits per pixel
%                                  8 =  8bit
%                                 12 = 12bit
%          image_width [int32]  - width of image in pixel
%          image_height [int32] - height of image in pixel
% output : error_code [int32] - zero on success, nonzero indicates failure,
%                               returned value is the errorcode
%          result_image       - Matlab array of either [uint8] or [uint16]
%                       
%          
% date: 03.2003 / written by S. Zhao, The Cooke Corporation,
% www.cookecorp.com
% revision history:
% 2005 March - first release
% 2005/03 - change variable name mode to bit_pix, because this reflects
%           more the use within the SDK manual, "mode" was not clear,
%           GHo, PCO AG
% The camera only produces either 8 bit pixels or 12 bit. 
% a 12 bit pixel occupies 16 bits (two bytes)
% When the sensor is colored, color information can be extracted from the 
% 12 bit data array in post-acquisation processing. 
% this function transfer the raw pixels, in one byte or two bytes def only
% 2008 June - new function, wehich usses PCC_MEMCPY from SDK MBL PCO AG

image_height = double(image_height);
image_width = double(image_width);
if(nargin==4)
 if (bit_pix == 8)
    result_image = uint8(zeros(image_width, image_height));
    result_image_ptr = libpointer('uint8Ptr', result_image);
    size=uint32(image_width*image_height);
 else
    result_image = uint16(zeros(image_width, image_height));
    result_image_ptr = libpointer('uint16Ptr', result_image);
    size=uint32(image_width*image_height*2);
 end
else
 if (bit_pix == 8)
  result_image_ptr = libpointer('uint16Ptr', varargin{1});   
  size=uint32(image_width*image_height);
 else
  result_image_ptr = libpointer('uint16Ptr', varargin{1});   
  size=uint32(image_width*image_height*2);
 end
end
error_code =calllib('PCO_PF_SDK','PCC_MEMCPY',result_image_ptr,source_bufadr,size);

result_image=get(result_image_ptr,'Value');      
end
