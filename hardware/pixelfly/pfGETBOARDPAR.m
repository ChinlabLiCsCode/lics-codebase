function [error_code,parabuf] = pfGETBOARDPAR(board_handle, len)
% [parabuf, error_code] = pfGETBOARDPAR(board_number, len)
% pfGETBOARDPAR returns len status bytes from the BOARDVAL structure of the
% board into buffer pointer. In the header file pccamdef.h there are macro
% definitions to extract certain information from this structure. Ensure
% that the buffer is large enough to transfer all values you need in the
% macros. (The structure BOARDVAL is only defined in the driver). pixelfly
% SDK manual p.6.
% input  : board_handle [libpointer] - board_handle from INITBOARD
%          len [int32]          - bytes to read
% output : error_code [int32] - zero on success, nonzero indicates failure,
%                               returned value is the errorcode
%          parabuf [uint16]     - values of structure BOARDVAL
% date: 03.2003 / written by S. Zhao, The Cooke Corporation,
% www.cookecorp.com
% revision history:
% 2005 March - first release
% 2005 March - added help comments GHo, PCO AG
% 2008 June - switch to work with handles MBL PCO AG

%this function is obsolet and should not be used any longer
%use pfGETBOARDVAL instead


if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

len = int32(len);
parabuf = uint32(zeros(len/4,1));
parabuf_ptr = libpointer('uint32Ptr', parabuf);
error_code =calllib('PCO_PF_SDK', 'GETBOARDPAR', board_handle, parabuf_ptr, len);
parabuf = uint32(get(parabuf_ptr, 'Value'))';

end

