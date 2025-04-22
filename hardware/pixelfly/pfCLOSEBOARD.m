function [error_code] = pfCLOSEBOARD(board_handle)
% [error_code] = pfCLOSEBOARD(board_number);
% pfCLOSEBOARD resets the PCI-Controller-Board and closes the driver.
% pixelfly SDK manual p.5.
% input  : board_handle [libpointer] - board_handle from INITBOARD
% output : error_code [int32] - zero on success, nonzero indicates failure,
%                               returned value is the errorcode
% date: 03.2003 / written by S. Zhao, The Cooke Corporation,
% www.cookecorp.com
% revision history:
% 2005 March - first release
% 2005 March - added help comments GHo, PCO AG
% 2008 June - switch to work with handles MBL PCO AG

if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

error_code = calllib('PCO_PF_SDK', 'CLOSEBOARD', board_handle);

end

