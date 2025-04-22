function GET_INFO()
% pfGET_INFO();
% pfGET_INFO does display some information of all connected cameras 
% it does load the library, open a camera, read information and close the
% camera 
% 2008 June -  MBL PCO AG

% check if library has been already loaded
if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

for n=1:2
 board_number = int32(n-1);
 ph_ptr=libpointer('voidPtrPtr');
 %try to initialize camera
 [error_code,board_handle] = calllib('PCO_PF_SDK', 'INITBOARDP', board_number,ph_ptr);
 if(error_code==-113)
  init=2;
 elseif(error_code~=0) 
  disp('no more cameras connected');
  break;
 else
  init=1;   
 end 
  
 if(init==2)
  disp('Camera head not connected');
 else
  disp(['Camera connected to board ',int2str(board_number)]);

  [error_code, value] = pfGETBOARDVAL(board_handle,'PCC_VAL_CCDTYPE');
  if(error_code == 0) && (bitand(value,hex2dec('01'))==hex2dec('01'))
   disp('Camera Head has a Color CCD')     
  else 
   disp('Camera Head has a BW CCD')     
  end
 
  [error_code, value] = pfGETBOARDVAL(board_handle,'PCC_VAL_EXTMODE');
  if(error_code == 0) && (bitand(value,hex2dec('01'))~=0)
   disp('Camera Head has DOUBLE feature')     
  end
  if(error_code == 0) && (bitand(value,hex2dec('FF00'))~=0)
   disp('Camera Head has PRISMA feature')     
  end
  if(error_code == 0) && (bitand(value,hex2dec('010000'))~=0)
   disp('Camera Head has LOGLUT feature')     
  end
  
  [error_code,ccd_width,ccd_height,image_width,image_height]=pfGETSIZES(board_handle);
  if(error_code == 0)
   disp(['Max. Resolution is: ', int2str(ccd_width), 'x' int2str(ccd_height)]);
   disp(['Act. Resolution is: ', int2str(image_width), 'x' int2str(image_height)]);
  end 
  disp(' ');
  
%read HEAD version     
  text=blanks(100);
  [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,5,text,100);
  if(error_code~=0)
   disp('error in READVERSION');
  else
   disp(strtrim(text));   
  end  
  clear(text);
 end    

%read HW version     
 text=blanks(100);
 [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,4,text,100);
 if(error_code~=0)
  disp('error in READVERSION');
 else
  disp(strtrim(text));   
 end  
 clear(text);
 
%read CPLD version     
 text=blanks(100);
 [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,6,text,100);
 if(error_code~=0)
  disp('error in READVERSION');
 else
  disp(strtrim(text));   
 end  
 clear(text);
 
%read PLUTO version     
 text=blanks(100);
 [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,1,text,100);
 if(error_code~=0)
  disp('error in READVERSION');
 else
  disp(strtrim(text));   
 end  
 clear(text);
 
%read CIRCE version     
 text=blanks(100);
 [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,2,text,100);
 if(error_code~=0)
  disp('error in READVERSION');
 else
  disp(strtrim(text));   
 end  
 clear(text);
 
%read ORION version     
 text=blanks(100);
 [error_code,out_ptr, text]= calllib('PCO_PF_SDK','READVERSION',board_handle,3,text,100);
 if(error_code~=0)
  disp('error in READVERSION');
 else
  disp(strtrim(text));   
 end  
 clear(text);
 
 text=blanks(100);
 text1=blanks(100);
 [error_code,out_ptr, text,text1]= calllib('PCO_PF_SDK','PCC_GET_VERSION',board_handle,text,text1);
 if(error_code~=0)
  disp('error in PCC_GET_VERSION');
 else
  disp(['DLL Version: ',text]);   
  disp(['SYS Version: ',text1]);
 end  
 clear(text);
 clear(text1);
 [error_code] = calllib('PCO_PF_SDK', 'CLOSEBOARD',board_handle);
 if(error_code~=0)
  disp('error in CLOSEBOARD');
 else
  disp(['camera ',int2str(board_number),' closed']);     
 end 
 disp(' '); 
 end
end   
