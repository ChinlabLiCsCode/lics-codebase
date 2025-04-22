function GET_SEQ16_ASYNC(board_number,nr_of_images)
% GET_SEQ16_ASYNC();
% GET_SEQ16_ASYNC does grab 'nr_of_images' in ASYNC mode from the camera 
% to a Matlab image stack
% It does load the library, open a camera, read information and close the
% camera 
% 2008 June - MBL PCO AG

if(~exist('board_num','var'))
 board_number=0;   
end

if(~exist('nr_of_images','var'))
 nr_of_images=10;   
end

comment=0;

if(comment)
 disp('load library pccamvb as PCO_PF_SDK');
end

% check if library has been already loaded
if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

if(comment)
 disp('call pfINITBOARD, open driver and initialize camera');
end
[error_code,board_handle] = pfINITBOARD(board_number);
if(error_code~=0) 
 disp(['Could not initialize camera. Error is ',int2str(error_code)]);
 return;
end 

if(comment)
 disp('call pfSETMODE, set mode ASYNC SW trigger, exposuretime=5ms ');
 disp('                no horizontal and vertical binning, 12bit readout');
end

exptime=5000; 
waittime_ms=exptime/1000+1000;
error_code=pfSETMODE(board_handle,hex2dec('11'),50,exptime,0,0,0,0,12,0);
if(error_code~=0) 
 disp(['SETMODE failed. Error is ',int2str(error_code)]);
 pfCLOSEBOARD(board_handle);
 return;
end 

if(comment)
 disp('call pfGETSIZES, does return actual resolution of the camera');
end

[error_code,ccd_width,ccd_height,image_width,image_height,bit_pix]=...
    pfGETSIZES(board_handle);
if(error_code~=0) 
 disp(['GETSIZES failed. Error is ',int2str(error_code)]);
 pfCLOSEBOARD(board_handle);
 return;
end

if(comment)
 disp('call pfALLOCATE_BUFFER, allocate one buffer for the camera');
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

if(comment)
 disp('call pfMAP_BUFFER, map this buffer to user memory');
end

[error_code,bufaddress] = pfMAP_BUFFER_EX(board_handle,ret_bufnr,size);
if(error_code~=0) 
 disp(['MAP_BUFFER_EX failed. Error is ',int2str(error_code)]);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

if(comment)
 disp('call pfSTART_CAMERA, start the camera');
end

error_code=pfSTART_CAMERA(board_handle);
if(error_code~=0) 
 disp(['START_CAMERA failed. Error is ',int2str(error_code)]);
 pfUNMAP_BUFFER(board_handle,ret_bufnr);
 pfFREE_BUFFER(board_handle,ret_bufnr);
 pfCLOSEBOARD(board_handle);
 return;
end

if(comment)
 disp('allocate Matlab image stack');
end

if(bit_pix==8)
 image_stack=zeros(image_width,image_height,nr_of_images,'uint8');
else 
 image_stack=zeros(image_width,image_height,nr_of_images,'uint16');
end 

if(comment)
 disp('begin grab loop');
end

for imanr=1:nr_of_images
%now grab one image out of the video stream
 if(comment)
  disp('call pfADD_BUFFER_TO_LIST, set the buffer in the working list of the driver');
 end

 error_code=pfADD_BUFFER_TO_LIST(board_handle,ret_bufnr,size,0,0);
 if(error_code~=0) 
  disp(['ADD_BUFFER_TO_LIST failed. Error is ',int2str(error_code)]);
  break;
 end

 if(comment)
  disp('call pfTRIGGER_CAMERA, trigger the camera to start image exposure');
 end
 
 error_code=pfTRIGGER_CAMERA(board_handle);
 if(error_code~=0) 
  disp(['TRIGGER_CAMERA failed. Error is ',int2str(error_code)]);
  break;
 end

 if(comment)
  disp('call pfGETBUFFER_STATUS, to get status of the buffer in the list');
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
  if(comment)
   disp(['image status is ',num2str(status,'%08X')]);
  end 
 end

 if((status&hex2dec('2'))~=hex2dec('2'))
  if(comment)
   disp('call pfWAIT_FOR_BUFFER, to wait until the image is transferred to the buffer');
  end
     
  [error_code,ima_bufnr]=pfWAIT_FOR_BUFFER(board_handle,waittime_ms,ret_bufnr);
  if(error_code~=0) 
   disp(['WAIT_FOR_BUFFER failed. Error is ',int2str(error_code)]);
  else
   if(comment)
    disp([int2str(imanr),'. image grabbed to buffer ',int2str(ima_bufnr)]);
   else
    disp([int2str(imanr),'. image grabbed ']);
   end 
  end
  if(ima_bufnr<0)
   error_code=1;    
  end
 end
 
 if(error_code==0) 
  if(comment)
   disp('call pfCOPY_BUFFER, copy the data from the buffer to the Matlab image stack');
  end
  [error_code,image_stack(:,:,imanr)]= pfCOPY_BUFFER(bufaddress,bit_pix,image_width,image_height,image_stack(:,:,imanr));
 else
  if(comment)
   disp('call pfREMOVE_BUFFER_FROM_LIST, an error occured remove the buffer from the working list');
  end
  [error_code]=pfREMOVE_BUFFER_FROM_LIST(board_handle,ret_bufnr);
  if(error_code~=0) 
   disp(['REMOVE_BUFFER_FROM_LIST failed. Error is ',int2str(error_code)]);
  end
 end 
end

if(error_code==0) 
 if(comment)
  disp('create an average image and show it ');
 end
 result_ima=zeros(image_width,image_height);
 for imanr=1:nr_of_images
  result_ima(:,:)= result_ima(:,:) + double(image_stack(:,:,imanr));
  maxval=max(max(image_stack(:,:,imanr)));
  minval=min(min(image_stack(:,:,imanr)));
  if(comment)
   disp(['maximum value in image ', int2str(maxval)]);   
   disp(['minimum value in image ', int2str(minval)]);   
  end
 end
 result_ima(:,:) = result_ima(:,:) / nr_of_images;
 result_ima=uint16(result_ima');
 maxval=max(max(result_ima(:,:)));
 minval=min(min(result_ima(:,:)));
 if(comment)
  disp(['maximum value in image ', int2str(maxval)]);   
  disp(['minimum value in image ', int2str(minval)]);   
 end
 
 imshow(result_ima,[0,maxval+10]);
 
 disp('Press "Enter" to close window and proceed')
 pause();
 close();
 pause(1);
end

if(comment)
 disp('call pfSTOP_CAMERA, stop the camera');
end

error_code=pfSTOP_CAMERA(board_handle);
if(error_code~=0) 
 disp(['STOP_CAMERA failed. Error is ',int2str(error_code)]);
end

if(comment)
 disp('call pfUNMAP_BUFFER, unmap the mapped buffer before call to FREE_BUFFER');
end

error_code=pfUNMAP_BUFFER(board_handle,ret_bufnr);
if(error_code~=0) 
 disp(['UNMAP_BUFFER failed. Error is ',int2str(error_code)]);
end

if(comment)
 disp('call pfFREE_BUFFER, free buffer memory');
end

error_code=pfFREE_BUFFER(board_handle,ret_bufnr);
if(error_code~=0) 
 disp(['FREEBUFFER failed. Error is ',int2str(error_code)]);
end

if(comment)
 disp('call pfCLOSEBOARD, close the driver');
end

error_code=pfCLOSEBOARD(board_handle);
if(error_code~=0) 
 disp(['CLOSEBOARD failed. Error is ',int2str(error_code)]);
end

end
  
