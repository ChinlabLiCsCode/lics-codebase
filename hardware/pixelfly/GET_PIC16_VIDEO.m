function GET_PIC16_VIDEO(board_number)
% pfGET_PIC16_VIDEO();
% pfGET_PIC16_VIDEO does display one image grabbed from the camera in video mode
% It does load the library, open a camera, read information and close the
% camera 
% 2008 June - MBL PCO AG

if(~exist('board_num','var'))
 board_number=0;   
end

% check if library has been already loaded
if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

%try to initialize camera
[error_code,board_handle] = pfINITBOARD(board_number);
if(error_code~=0) 
 disp(['Could not initialize camera. Error is ',int2str(error_code)]);
 return;
end 

%set mode=VIDEO, exposuretime=10ms, no horizontal and vertical binning,
%12bit readout
error_code=pfSETMODE(board_handle,49,50,10,0,0,0,0,12,0);
if(error_code~=0) 
 disp(['SETMODE failed. Error is ',int2str(error_code)]);
 pfCLOSEBOARD(board_handle);
 return;
end 

[error_code,ccd_width,ccd_height,image_width,image_height,bit_pix]=...
    pfGETSIZES(board_handle);
if(error_code~=0) 
 disp(['GETSIZES failed. Error is ',int2str(error_code)]);
 pfCLOSEBOARD(board_handle);
 return;
end

size=image_width*image_height*floor((bit_pix+7)/8);
bufnr=-1;
[error_code, ret_bufnr] = ...
                      pfALLOCATE_BUFFER(board_handle, bufnr, size);
if(error_code~=0) 
 disp(['ALLOCATE_BUFFER failed. Error is ',int2str(error_code)]);
 pfCLOSEBOARD(board_handle);
 return;
end

[error_code,bufaddress] = pfMAP_BUFFER_EX(board_handle,ret_bufnr,size);
if(error_code~=0) 
 disp(['MAP_BUFFER_EX failed. Error is ',int2str(error_code)]);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

error_code=pfSTART_CAMERA(board_handle);
if(error_code~=0) 
 disp(['START_CAMERA failed. Error is ',int2str(error_code)]);
 pfUNMAP_BUFFER(board_handle,ret_bufnr);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

%now grab one image out of the video stream
error_code=pfADD_BUFFER_TO_LIST(board_handle,ret_bufnr,size,0,0);
if(error_code~=0) 
 disp(['ADD_BUFFER_TO_LIST failed. Error is ',int2str(error_code)]);
 pfSTOP_CAMERA(board_handle);
 pfUNMAP_BUFFER(board_handle,ret_bufnr);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

error_code=pfTRIGGER_CAMERA(board_handle);
if(error_code~=0) 
 disp(['TRIGGER_CAMERA failed. Error is ',int2str(error_code)]);
 pfSTOP_CAMERA(board_handle);
 pfUNMAP_BUFFER(board_handle,ret_bufnr);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

[error_code,image_status] = pfGETBUFFER_STATUS(board_handle,ret_bufnr,0,4);
if(error_code~=0) 
 disp(['GETBUFFER_STATUS failed. Error is ',int2str(error_code)]);
else
 if(image_status<0)
  status=double(image_status)+hex2dec('80000000');   
  status=status+hex2dec('80000000');   
 else
  status=double(image_status);     
 end
 disp(['image status is ',num2str(status,'%08X')]);
end

[error_code,ima_bufnr]=pfWAIT_FOR_BUFFER(board_handle,1000,ret_bufnr);
if(error_code~=0) 
 disp(['WAIT_FOR_BUFFER failed. Error is ',int2str(error_code)]);
else
 disp(['image grabbed to buffer ',int2str(ima_bufnr)]);
end

if(ima_bufnr<0)
 error_code=1;    
end

if(error_code==0) 
 [error_code,ima]= pfCOPY_BUFFER(bufaddress,bit_pix,image_width,image_height);

 m=max(max(ima(:,:)));
 imshow(ima',[0,m+100]);
 disp('Press "Enter" to close window and proceed')
 pause();
 close();
 pause(1);
 clear ima;
else
 [error_code]=pfREMOVE_BUFFER_FROM_LIST(board_handle,ret_bufnr);
 if(error_code~=0) 
  disp(['REMOVE_BUFFER_FROM_LIST failed. Error is ',int2str(error_code)]);
 end
end 

error_code=pfSTOP_CAMERA(board_handle);
if(error_code~=0) 
 disp(['STOP_CAMERA failed. Error is ',int2str(error_code)]);
end

error_code=pfUNMAP_BUFFER(board_handle,ret_bufnr);
if(error_code~=0) 
 disp(['UNMAP_BUFFER failed. Error is ',int2str(error_code)]);
end

error_code=pfFREE_BUFFER(board_handle,ret_bufnr);
if(error_code~=0) 
 disp(['FREEBUFFER failed. Error is ',int2str(error_code)]);
end

error_code=pfCLOSEBOARD(board_handle);
if(error_code~=0) 
 disp(['CLOSEBOARD failed. Error is ',int2str(error_code)]);
end

end
  
