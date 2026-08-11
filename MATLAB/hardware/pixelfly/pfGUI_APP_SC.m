function varargout = pfGUI_APP_SC(varargin)
% PFGUI_APP M-file for pfGUI_APP.fig
%      PFGUI_APP, creates a GUI application, where single and continuous
%      grab of images can be started. 
%      The images are scaled and displayed using Matlab graphics functions.
%      Only BW-Display is supported at the moment. (Color cameras also
%      display grayscale images)
%      The following parameter of  the camera can be changed:
%        Mode 
%        Exposuretime
%        Horizontal and vertical binning
%        Analog gain
%
% 2008 June - MBL PCO AG


% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @pfGUI_APP_OpeningFcn, ...
                   'gui_OutputFcn',  @pfGUI_APP_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before pfGUI_APP is made visible.
function pfGUI_APP_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to pfGUI_APP (see VARARGIN)

if not(libisloaded('PCO_PF_SDK'))
 loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end

if(eventdata)
end    

% Choose default command line output for matlab4pixelfly_v3
handles.output = hObject;

% default parameters for camera setmode
handles.hbin = 0; % horizontal binning 1
handles.vbin = 0; % vertical binning 1
handles.exposure = 5; % exposure time in ms
handles.gain = 0;
handles.mode = 49;	% video mode and software trigger
handles.bit_pix = 12;
handles.color=0;
board_number=0;


[error_code,board_handle] = pfINITBOARD(board_number);
if(error_code~=0) 
 error(['Could not initialize camera. Error is ',int2str(error_code)]);
 return;
end 
handles.board_handle=board_handle;

%disp(['mode is ' num2str(handles.mode,'%08X')]);
 
error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);

if error_code ~= 0
    error('....initial setmode failed!');
end

[error_code,ccd_width,ccd_height,image_width,image_height,bit_pix]=...
    pfGETSIZES(handles.board_handle);
handles.ccd_width = ccd_width;
handles.ccd_height = ccd_height;
handles.image_width = image_width;
handles.image_height = image_height;
handles.imagesize=image_width*image_height*floor((bit_pix+7)/8);
handles.bit_pix=bit_pix;
[error_code,temp_ccd] = pfREADTEMPERATURE(handles.board_handle);
if error_code == 0
 handles.temp_ccd = temp_ccd;
else
 handles.temp_ccd = -1;
end

handles.depth=2; 

[error_code, value] = pfGETBOARDVAL(handles.board_handle,'PCC_VAL_BOARD_INFO');
if (error_code == 0) && (bitand(value,hex2dec('00200000'))==hex2dec('00200000'))
 handles.max_exptime=65535.0;   
 handles.min_exptime=0.005;   
else
 handles.max_exptime=10000.0;   
 handles.min_exptime=0.010;   
end    

set(handles.exp_slider,'Max',handles.max_exptime);
set(handles.exp_slider,'Min',1.0);
step=1/(handles.max_exptime-1.0);
set(handles.exp_slider,'SliderStep',[step step*10]);

%we start with bw image also for color cameras
handles.color=0;
handles.image = zeros(double(handles.image_height), double(handles.image_width),'uint16');
handles.image_buffer_map = imagesc(handles.image);
colormap(gray);
handles.gamma=1.0; 
handles.dgain=75;

[error_code, value] = pfGETBOARDVAL(handles.board_handle,'PCC_VAL_EXTMODE');
if (error_code == 0) && (bitand(value,hex2dec('80'))==hex2dec('80'))
 handles.colorcam=1;   
 set(handles.Color,'Enable', 'on');
 set(handles.whitebalance,'Visible', 'off');
 if not(libisloaded('PCO_CNV_SDK'))
%  disp('Load lib PCO_CNV_SDK');   
  loadlibrary('pcocnv','pcocnv.h','alias','PCO_CNV_SDK');
 end 
 handles.colorlutptr=libpointer('voidPtr');
 handles.colorlutptr=calllib('PCO_CNV_SDK', 'CREATE_COLORLUT_EX', handles.bit_pix,0,255,0);
 handles.maxred=3072;
 handles.maxgreen=3072;
 handles.maxblue=3072;
 
 calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
else
 handles.colorcam=0;   
 set(handles.Color,'Enable', 'off');
 set(handles.whitebalance,'Visible', 'off');
end 

bufnr=-1;
bufsize=ccd_width*ccd_height*2;
[error_code,bufnr] = pfALLOCATE_BUFFER(handles.board_handle,bufnr,bufsize);
if error_code ~= 0
    error('....memory allocation failed!');
end
handles.bufnr=bufnr;

[error_code,bufaddress] = pfMAP_BUFFER_EX(handles.board_handle,bufnr,bufsize);
if error_code ~= 0
    error('....map buffer error!');
end
handles.bufaddress = bufaddress; 

bufnr1=-1;
[error_code,bufnr1] = pfALLOCATE_BUFFER(handles.board_handle,bufnr1,bufsize);
handles.bufnr1=bufnr1;
[error_code,bufaddress] = pfMAP_BUFFER_EX(handles.board_handle,bufnr1,bufsize);
if error_code ~= 0
    error('....map buffer error!');
end
handles.bufaddress1 = bufaddress; 

%no start here, it is done before single_image or grab images

%************************************************************************
handles.image_in_buffer = 'no';

maxlut=(2^handles.bit_pix)-1;
set(handles.display,'Clim',[10 (maxlut*handles.dgain)/100]); 
set(handles.display,'Visible', 'off','Units', 'pixels'); 

axis off
hold on

exposure_time=handles.exposure;
handles.exposure_str = num2str(exposure_time, '%12u');
exposure_str = num2str(exposure_time, '%8.3f');
set(handles.exptime, 'String', exposure_str);
set(handles.exp_slider,'Value',exposure_time);

set(handles.stopgrab,'Visible', 'off');
set(handles.stopgrab,'Enable', 'off');

set(handles.gammatxt,'String', num2str(handles.gamma,1));
set(handles.dgaintxt,'String', strcat(int2str(100-handles.dgain),'%'));

% Choose default command line output for pfGUI_APP
handles.output = hObject;

infotext(handles);

set(handles.BW,'Interruptible', 'off');
set(handles.Color,'Interruptible', 'off');
set(handles.gain_low,'Interruptible', 'off');
set(handles.gain_high,'Interruptible', 'off');
set(handles.vbin_1,'Interruptible', 'off');
set(handles.vbin_2,'Interruptible', 'off');
set(handles.vbin_4,'Interruptible', 'off');
set(handles.hbin_1,'Interruptible', 'off');
set(handles.hbin_2,'Interruptible', 'off');
set(handles.Mode,'Interruptible', 'off');
set(handles.exptime,'Interruptible', 'off');
set(handles.exp_slider,'Interruptible', 'off');

% Update handles structure
guidata(hObject, handles);



% --- Outputs from this function are returned to the command line.
function varargout = pfGUI_APP_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(eventdata)
end    
if(hObject)
end    
    
% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in CloseButton.
function Close_Callback(hObject, eventdata, handles)
% hObject    handle to CloseButton (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(eventdata)
end    

CloseCamera(handles);

delete(hObject);
close all


% --- Executes on selection change in Mode.
function Mode_Callback(hObject, eventdata, handles)
% hObject    handle to Mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(eventdata)
end    

% Hints: contents = get(hObject,'String') returns Mode contents as cell array
%        contents{get(hObject,'Value')} returns selected item from Mode
mode_index = get(hObject,'Value');
exposure_time = str2double(get(handles.exptime,'String'));

if mode_index==1
%    handles.mode = bitor(handles.mode,hex2dec('30'));
    %set(handles.exposure_unit_text, 'String', '[ms]');
    exposure_time=round(exposure_time);
    handles.mode = hex2dec('31');
    if(exposure_time<1.0)
     exposure_time=1.0;
    end 
    if(exposure_time>handles.max_exptime)
     exposure_time=handles.max_exptime;
    end    
    handles.exposure=uint32(exposure_time);
    set(handles.exp_slider,'Max',handles.max_exptime);
    set(handles.exp_slider,'Min',1.0);
elseif mode_index==2
    exposure_time=round(exposure_time);
    handles.mode = hex2dec('30');
    if(exposure_time<1.0)
     exposure_time=1.0;
    end 
    if(exposure_time>handles.max_exptime)
     exposure_time=handles.max_exptime;
    end    
    handles.exposure=uint32(exposure_time);
    set(handles.exp_slider,'Max',handles.max_exptime);
    set(handles.exp_slider,'Min',1.0);
elseif mode_index==3
    handles.mode = hex2dec('11');
    if(exposure_time<handles.min_exptime)||isnan(exposure_time)
     exposure_time=handles.min_exptime;
    end 
    if(exposure_time>65.535)
     exposure_time=65.535;
    end    
    handles.exposure=uint32(exposure_time*1000);
    set(handles.exp_slider,'Max',65.535);
    set(handles.exp_slider,'Min',handles.min_exptime);
elseif mode_index==4
    handles.mode = hex2dec('10');
    if(exposure_time>65.535)
     exposure_time=65.535;
    end    
    if(exposure_time<handles.min_exptime)||isnan(exposure_time)
     exposure_time=handles.min_exptime;
    end 
    handles.exposure=uint32(exposure_time*1000);
    set(handles.exp_slider,'Max',65.535);
    set(handles.exp_slider,'Min',handles.min_exptime);
end

handles.exposure_str = num2str(exposure_time, '%12u');
exposure_str = num2str(exposure_time, '%8.3f');
set(handles.exptime, 'String', exposure_str);
set(handles.exp_slider,'Value',exposure_time);

% error_code = pfSTOP_CAMERA(handles.board_handle);
% if error_code ~= 0
%      error('....camera_utility_trigger_external_Callback: pfSTOP_CAMERA error!')
% end

error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
      error('....camera_utility_trigger_auto_Callback: pfSETMODE error!');
end

% error_code = pfSTART_CAMERA(handles.board_handle);
% if error_code ~= 0
%        error('....camera_utility_trigger_auto_Callback: pfSTART_CAMERA error!')
% end
infotext(handles);

guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function Mode_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

if(eventdata)
end    
% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function exptime_Callback(hObject, eventdata, handles)
% hObject    handle to exptime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(eventdata)
end    

% Hints: get(hObject,'String') returns contents of exptime as text
%        str2double(get(hObject,'String')) returns contents of exptime as a double
exposure_time = str2double(get(handles.exptime,'String'));
%video mode from 1 to 10000ms, async mode from 0.01 to 10 ms
if bitand(handles.mode,hex2dec('0f0'))==hex2dec('030')
    if (exposure_time > handles.max_exptime)
       exposure_time = handles.max_exptime;
    end
    if (exposure_time < 1)||isnan(exposure_time)
       exposure_time = 1;  
    end
    handles.exposure=cast(exposure_time,'uint32');
else
    if (exposure_time > 65.535)
       exposure_time = 65.535;
    end
    if (exposure_time < handles.min_exptime)||isnan(exposure_time)
       exposure_time = handles.min_exptime;  
    end
   handles.exposure=cast(exposure_time*1000,'uint32');
end     

handles.exposure_str = num2str(exposure_time, '%12u');
exposure_str = num2str(exposure_time, '%8.3f');
set(handles.exptime, 'String', exposure_str);
set(handles.exp_slider,'Value',exposure_time);

error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
      error('....exposure_edit_Callback: pfSETMODE error!');
end

infotext(handles);
guidata(hObject, handles);


% --- Executes during object creation, after setting all properties.
function exptime_CreateFcn(hObject, eventdata, handles)
% hObject    handle to exptime (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

if(eventdata)
end    

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes when selected object is changed in gainpanel.
function gainpanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in gainpanel 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end    

switch get(hObject,'Tag')   % Get Tag of selected object
    case 'gain_low'
     handles.gain=0;
    case 'gain_high'
     handles.gain=1;
end        

error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
      error('....gain_Selection: pfSETMODE error!');
end

guidata(hObject, handles);

% --- Executes when selected object is changed in hbinpanel.
function hbinpanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in hbinpanel 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end    


switch get(hObject,'Tag')   % Get Tag of selected object
    case 'hbin_1'
     handles.hbin=0;
    case 'hbin_2'
     handles.hbin=1;
end
error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
      error('....hbin_Selection: pfSETMODE error!');
end

if(handles.colorcam>0)
 if(handles.hbin>0)
%  disp('disable color settings');
  handles.color=0;
  if(get(handles.Color,'Value')==1)
   set(handles.BW,'Value',1);
  end
  set(handles.whitebalance,'Visible', 'off');
  set(handles.Color,'Enable', 'off');
 elseif(handles.vbin==0)
  set(handles.Color,'Enable', 'on');
 end
end 


[error_code,ccd_width, ccd_height, image_width, image_height, bit_pix] = pfGETSIZES(handles.board_handle);
handles.image_width = image_width;
handles.image_height = image_height;
handles.bit_pix = bit_pix;

if bit_pix==8
 handles.imagesize=image_width*image_height;
else
 handles.imagesize=image_width*image_height*2;
end

hold off
if(handles.color==0)
 handles.image = zeros(double(handles.image_height), double(handles.image_width),'uint16');
 handles.image_buffer_map = imagesc(handles.image);
 colormap(gray);
else
 handles.image = zeros(double(handles.image_height), double(handles.image_width),3,'uint8');
 handles.image_buffer_map = imagesc(handles.image);
end 
set(handles.image_buffer_map,'CData',handles.image);
set(handles.display,'Visible', 'off','Units', 'pixels'); 
hold on

handles.image_in_buffer='no';
%handles.res_str = [' resolution: ' num2str(double(handles.image_width)) ' x ' num2str(double(handles.image_height)) ' pixel '];

infotext(handles);

guidata(hObject, handles);


% --- Executes when selected object is changed in vbinpanel.
function vbinpanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in vbinpanel 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end    

switch get(hObject,'Tag')   % Get Tag of selected object
    case 'vbin_1'
     handles.vbin=0;
    case 'vbin_2'
     handles.vbin=1;
    case 'vbin_4'
     handles.vbin=2;
end
error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
 if(handles.vbin>1)
  handles.vbin=1;   
  set(handles.vbin_2,'Value',1);
  error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
  if error_code ~= 0
   error('....vbin_Selection: pfSETMODE error!');
  end 
 end
end

if(handles.colorcam>0)
 if(handles.vbin>0)
%  disp('disable color settings');
  handles.color=0;
  if(get(handles.Color,'Value')==1)
   set(handles.BW,'Value',1);
  end
  set(handles.whitebalance,'Visible', 'off');
  set(handles.Color,'Enable', 'off');
 elseif(handles.hbin==0)
  set(handles.Color,'Enable', 'on');
 end
end 
     
[error_code,ccd_width, ccd_height, image_width, image_height, bit_pix] = pfGETSIZES(handles.board_handle);
handles.image_width = image_width;
handles.image_height = image_height;
handles.bit_pix = bit_pix;

if bit_pix==8
 handles.imagesize=image_width*image_height;
else
 handles.imagesize=image_width*image_height*2;
end

%axes(handles.display);
%hold off
%handles.image= zeros(double(handles.image_height), double(handles.image_width));
%handles.image_buffer_map = image(handles.image, 'EraseMode', 'none');
%handles.image_buffer_map = imagesc(handles.image);
%set(handles.display,'Visible', 'off','Units', 'pixels'); 
%hold on

hold off
if(handles.color==0)
 handles.image = zeros(double(handles.image_height), double(handles.image_width),'uint16');
 handles.image_buffer_map = imagesc(handles.image);
 colormap(gray);
else
 handles.image = zeros(double(handles.image_height), double(handles.image_width),3,'uint8');
 handles.image_buffer_map = imagesc(handles.image);
end 
set(handles.image_buffer_map,'CData',handles.image);
set(handles.display,'Visible', 'off','Units', 'pixels'); 
hold on

handles.image_in_buffer='no';

infotext(handles);
guidata(hObject, handles);


function imagetypepanel_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in gainpanel 
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end    

switch get(hObject,'Tag')   % Get Tag of selected object
    case 'BW'
     handles.color=0;
     set(handles.whitebalance,'Visible', 'off');
     
    case 'Color'
     handles.color=1;
     set(handles.whitebalance,'Visible', 'on');
end        

if(handles.color==0)
 handles.image = zeros(double(handles.image_height), double(handles.image_width),'uint16');
 handles.image_buffer_map = imagesc(handles.image);
 if(strcmp(handles.image_in_buffer,'yes'))
  [error_code,result_image]= pfCOPY_BUFFER(handles.bufaddress,handles.bit_pix,handles.image_width,handles.image_height);
  handles.image = result_image';   
  set(handles.image_buffer_map,'CData',handles.image);
 end     
 colormap(gray);
else
 handles.image = zeros(double(handles.image_height), double(handles.image_width),3,'uint8');
% handles.image(:,:,2)=uint8(hex2dec('F0'));
% handles.image(:,:,1)=uint8(hex2dec('80'));
 handles.image_buffer_map = imagesc(handles.image);
 if(strcmp(handles.image_in_buffer,'yes'))
  rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
  result_image_ptr = libpointer('uint8Ptr',rgb_image);
  calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
  rgb_image=get(result_image_ptr,'Value'); 
  handles.image(:,:,3)=rgb_image(1:3:end,:)';      
  handles.image(:,:,2)=rgb_image(2:3:end,:)';      
  handles.image(:,:,1)=rgb_image(3:3:end,:)';      
  set(handles.image_buffer_map,'CData',handles.image);
 end  
end 

guidata(hObject, handles);



% --- Executes on button press in single.
function single_Callback(hObject, eventdata, handles)
% hObject    handle to single (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if(eventdata)
end    
if(hObject)
end    
dispon=0;

if(dispon==1)
 disp(['single mode is ' num2str(handles.mode,'%08X')]);
 disp(['single image_size is ' int2str(handles.imagesize)]);
 disp(['single exposure is ' int2str(handles.exposure)]);
 disp(['single hbin is ' int2str(handles.hbin)]);
 disp(['single vbin is ' int2str(handles.vbin)]); 
end

exposure_time = str2double(get(handles.exptime,'String'));
exposure_time = uint32(exposure_time);

error_code = pfSTART_CAMERA(handles.board_handle);
if error_code ~= 0
 error(['....grab_Callback: START_CAMERA error!',int2str(error_code)]);
end

error_code =pfADD_BUFFER_TO_LIST(handles.board_handle,handles.bufnr, handles.imagesize,0,0);
if error_code ~= 0
    error('....takeimage_pushbutton_Callback: add buffer error!')
end

error_code = pfTRIGGER_CAMERA(handles.board_handle);
if error_code ~= 0
    error('....takeimage_pushbutton_Callback: pfTRIGGER_CAMERA error!')
end

% wait for buffer
[error_code,ima_bufnr]=pfWAIT_FOR_BUFFER(handles.board_handle,exposure_time+500,handles.bufnr);
if(error_code~=0) 
 error(['WAIT_FOR_BUFFER failed. Error is ',int2str(error_code)]);
end

if(ima_bufnr<0)
 error_code=1;    
end

if(error_code==0)
 if(handles.color==0)
  [error_code,result_image]= pfCOPY_BUFFER(handles.bufaddress,handles.bit_pix,handles.image_width,handles.image_height);
  handles.image = result_image';   
  set(handles.image_buffer_map,'CData',handles.image);
  colormap(gray);
 else
  rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
  result_image_ptr = libpointer('uint8Ptr',rgb_image);
  calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
  rgb_image=get(result_image_ptr,'Value'); 
  handles.image(:,:,3)=rgb_image(1:3:end,:)';      
  handles.image(:,:,2)=rgb_image(2:3:end,:)';      
  handles.image(:,:,1)=rgb_image(3:3:end,:)';      
  set(handles.image_buffer_map,'CData',handles.image);
 end    
else
 error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr);
 if error_code ~= 0
  error(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
 end
end

error_code = pfSTOP_CAMERA(handles.board_handle);
if error_code ~= 0
 error(['....grab_Callback:  STOP_CAMERA error!',int2str(error_code)]);
end
handles.image_in_buffer='yes';
guidata(hObject, handles);



% --- Executes on button press in grab.
function grab_Callback(hObject, eventdata, handles)
% hObject    handle to grab (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end

global grabstop;

dispon=0;

set(handles.stopgrab,'Visible', 'on');
set(handles.stopgrab,'Enable', 'on');
set(handles.grab,'Visible', 'off');
set(handles.grab,'Enable', 'off');
set(handles.single,'Enable', 'off');
set(handles.Close,'Enable', 'off');
set(handles.BW,'Enable', 'off');
set(handles.Color,'Enable', 'off');
set(handles.gain_low,'Enable', 'off');
set(handles.gain_high,'Enable', 'off');
set(handles.vbin_1,'Enable', 'off');
set(handles.vbin_2,'Enable', 'off');
set(handles.vbin_4,'Enable', 'off');
set(handles.hbin_1,'Enable', 'off');
set(handles.hbin_2,'Enable', 'off');
set(handles.Mode,'Enable', 'off');
set(handles.exptime,'Enable', 'off');

grabstop=0;

exposure_time = str2double(get(handles.exptime,'String'));
exposure_time = uint32(exposure_time);

rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');

error_code = pfSTART_CAMERA(handles.board_handle);
if error_code ~= 0
 disp(['....grab_Callback: START_CAMERA error!',int2str(error_code)]);
 return;
end

error_code =pfADD_BUFFER_TO_LIST(handles.board_handle,handles.bufnr, handles.imagesize,0,0);
if error_code ~= 0
 disp(['....grab_Callback: add buffer error!',int2str(error_code)]) 
 return
end
 
error_code =pfADD_BUFFER_TO_LIST(handles.board_handle,handles.bufnr1, handles.imagesize,0,0);
if error_code ~= 0
 disp(['....grab_Callback: add buffer1 error!',int2str(error_code)]) 
 error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr);
 if error_code ~= 0
  disp(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
 end
 return;
end

%trigger first image and video sequence respectively 
if bitand(handles.mode,hex2dec('0F'))==hex2dec('01')
 error_code = pfTRIGGER_CAMERA(handles.board_handle);
 if error_code ~= 0
  disp(['....grab_Callback:: pfTRIGGER_CAMERA error!',int2str(error_code)])
  error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr);
  if error_code ~= 0
   disp(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
  end
  error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr1);
  if error_code ~= 0
   disp(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
  end
 end
end 

loop=1;
%for loop=1:100
while(1)
 loop=loop+1;   
 pause(0.001);
% wait for buffer
 [error_code,ima_bufnr,ima_bufnr1]=pfWAIT_FOR_BUFFER(handles.board_handle,exposure_time+500,handles.bufnr,handles.bufnr1);
 if(error_code~=0) 
  disp(['...grab_Callback: pfWAIT_FOR_BUFFER error ',int2str(error_code)]);
  break;
 end

if(dispon==1) 
 disp(['wait returned bufnr: ' int2str(ima_bufnr) ' bufnr1: ' int2str(ima_bufnr1)]);   
end

%async mode does needs a trigger for every image 
 if bitand(handles.mode,hex2dec('FF'))==hex2dec('11')
  error_code = pfTRIGGER_CAMERA(handles.board_handle);
  if error_code ~= 0
   disp(['....grab_Callback:: pfTRIGGER_CAMERA error!',int2str(error_code)])
   break;
  end
 end
 
 if(ima_bufnr<0)
  error(['....grab_Callback:: error waiting for buffer ima_bufnr: ',int2str(ima_bufnr)])
  break;
 end

 if(handles.color==0)
  [error_code,result_image]= pfCOPY_BUFFER(handles.bufaddress,handles.bit_pix,handles.image_width,handles.image_height);
  if error_code ~= 0
   disp(['...grab_Callback: pfCOPY_BUFFER error ',int2str(error_code)]);
   break;
  end
 else
  result_image_ptr = libpointer('uint8Ptr',rgb_image);
  calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
 end    
 
%work with this buffer is done, we can add it again into the queue 
 error_code =pfADD_BUFFER_TO_LIST(handles.board_handle,ima_bufnr, handles.imagesize,0,0);
 if error_code ~= 0
  disp(['....grab_Callback: add buffer error!',int2str(error_code)]) 
  break;
 end
 
%if both buffers have been done, also add the second buffer into the queue 
 if(ima_bufnr1>=0)
  error_code =pfADD_BUFFER_TO_LIST(handles.board_handle,ima_bufnr1, handles.imagesize,0,0);
  if error_code ~= 0
   disp(['....grab_Callback: add buffer error!',int2str(error_code)]) 
   break;
  end
 end 
 
 if(handles.color==0)
  handles.image = result_image';   
  set(handles.image_buffer_map,'CData',handles.image);
  colormap(gray);
 else 
  rgb_image=get(result_image_ptr,'Value'); 
  handles.image(:,:,3)=rgb_image(1:3:end,:)';      
  handles.image(:,:,2)=rgb_image(2:3:end,:)';      
  handles.image(:,:,1)=rgb_image(3:3:end,:)';      
  set(handles.image_buffer_map,'CData',handles.image);
 end
 
 if(dispon==1) 
  disp(['copy done loop is' int2str(loop) ' grabstop is' int2str(grabstop)]);   
 end 
 drawnow expose update
 if(grabstop>0)
  if(dispon)   
   disp(['before break grabstop is ' int2str(grabstop)]);   
  end
  break;   
 end
end 

grabstop=2;
error_code = pfSTOP_CAMERA(handles.board_handle);
if error_code ~= 0
 disp(['....grab_Callback:  STOP_CAMERA error!',int2str(error_code)]);
end

error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr);
if error_code ~= 0
 disp(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
end

error_code =pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr1);
if error_code ~= 0
 disp(['....grab_Callback: REMOVE_BUFFER_FROM_LIST error!',int2str(error_code)]) 
end

set(handles.stopgrab,'Visible', 'off');
set(handles.stopgrab,'Enable', 'off');
set(handles.grab,'Visible', 'on');
set(handles.grab,'Enable', 'on');
set(handles.single,'Enable', 'on');
set(handles.Close,'Enable', 'on');
set(handles.BW,'Enable', 'on');
if(handles.colorcam==1)
 set(handles.Color,'Enable', 'on');
end
set(handles.gain_low,'Enable', 'on');
set(handles.gain_high,'Enable', 'on');
set(handles.vbin_1,'Enable', 'on');
set(handles.vbin_2,'Enable', 'on');
set(handles.vbin_4,'Enable', 'on');
set(handles.hbin_1,'Enable', 'on');
set(handles.hbin_2,'Enable', 'on');
set(handles.Mode,'Enable', 'on');
set(handles.exptime,'Enable', 'on');

handles.image_in_buffer='yes';
guidata(hObject, handles);


% --- Executes on button press in stopgrab.
function stopgrab_Callback(hObject, eventdata, handles)
% hObject    handle to stopgrab (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(hObject)
end
if(eventdata)
end

global grabstop;

grabstop=1;


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
global grabstop;

if(grabstop==0)
 disp('Please stop continuous grab, before closing the pfGUI_APP')   
 %pos_size = get(handles.figure1,'Position');
 % Call modaldlg with the argument 'Position'.
 close_message('Title','GUI Message');
 return;
end

if(libisloaded('PCO_PF_SDK'))
 CloseCamera(handles);
end

delete(hObject);


% --- Executes on button press in whitebalance.
function whitebalance_Callback(hObject, eventdata, handles)
% hObject    handle to whitebalance (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

sredgain=int16(0);
sredgain_ptr=libpointer('int16Ptr', sredgain);
sgreengain=int16(0);
sgreengain_ptr=libpointer('int16Ptr', sgreengain);
sbluegain=int16(0);
sbluegain_ptr=libpointer('int16Ptr', sbluegain);

calllib('PCO_CNV_SDK', 'AUTOBALANCE',0,handles.image_width,handles.image_height,...
                                    handles.bufaddress,handles.colorlutptr,0,... 
                                    10,90,30,...
                                    sredgain_ptr,sgreengain_ptr,sbluegain_ptr);
sredgain = int16(get(sredgain_ptr, 'Value'));
sgreengain = int16(get(sgreengain_ptr, 'Value'));
sbluegain = int16(get(sbluegain_ptr, 'Value'));

oldlut=(handles.maxred+handles.maxgreen+handles.maxblue)/3;

handles.maxred=(oldlut/double(sredgain))*100;
handles.maxgreen=(oldlut/double(sgreengain))*100;
handles.maxblue=(oldlut/double(sbluegain))*100;

maxlut=(2^handles.bit_pix)-1;
while((handles.maxred>maxlut)||(handles.maxgreen>maxlut)||(handles.maxblue>maxlut))
% disp('decrease values 2%');   
 handles.maxred=(handles.maxred*98)/100;
 handles.maxgreen=(handles.maxgreen*98)/100;
 handles.maxblue=(handles.maxblue*98)/100;
end 

%disp(['red:   ' int2str(handles.maxred)]);
%disp(['green: ' int2str(handles.maxgreen)]);
%disp(['blue:  ' int2str(handles.maxblue)]);

calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
result_image_ptr = libpointer('uint8Ptr',rgb_image);
calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
rgb_image=get(result_image_ptr,'Value'); 
handles.image(:,:,3)=rgb_image(1:3:end,:)';      
handles.image(:,:,2)=rgb_image(2:3:end,:)';      
handles.image(:,:,1)=rgb_image(3:3:end,:)';      
set(handles.image_buffer_map,'CData',handles.image);
guidata(hObject, handles);


% --- Executes on button press in dgainminus.
function dgainminus_Callback(hObject, eventdata, handles)
% hObject    handle to dgainminus (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.dgain=handles.dgain+5;
set(handles.dgainplus,'Enable', 'on');
if(handles.dgain>95)
 set(handles.dgainminus,'Enable', 'off');
end
maxlut=(2^handles.bit_pix)-1;
set(handles.dgaintxt,'String', strcat(int2str(100-handles.dgain),'%'));

if(handles.color==0)
 hold off
 if(((maxlut*handles.dgain)/100)>10)
  caxis ([10 (maxlut*handles.dgain)/100])
 else 
  caxis ([10 50])
 end 
 hold on
else    
 handles.maxred= handles.maxred + (handles.maxred*0.05);   
 handles.maxgreen= handles.maxgreen + (handles.maxgreen*0.05);   
 handles.maxblue= handles.maxblue + (handles.maxblue*0.05);   
 
 while((handles.maxred>maxlut)||(handles.maxgreen>maxlut)||(handles.maxblue>maxlut))
  handles.maxred=(handles.maxred*98)/100;
  handles.maxgreen=(handles.maxgreen*98)/100;
  handles.maxblue=(handles.maxblue*98)/100;
 end 
 
 calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
 rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
 result_image_ptr = libpointer('uint8Ptr',rgb_image);
 calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
 rgb_image=get(result_image_ptr,'Value'); 
 handles.image(:,:,3)=rgb_image(1:3:end,:)';      
 handles.image(:,:,2)=rgb_image(2:3:end,:)';      
 handles.image(:,:,1)=rgb_image(3:3:end,:)';      
 set(handles.image_buffer_map,'CData',handles.image);
end    
guidata(hObject, handles);

% --- Executes on button press in dgainplus.
function dgainplus_Callback(hObject, eventdata, handles)
% hObject    handle to dgainplus (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
%disp(['in dgain plus old ' int2str(handles.dgain)])
handles.dgain=handles.dgain-5;
set(handles.dgainminus,'Enable', 'on');
if(handles.dgain<5)
 set(handles.dgainplus,'Enable', 'off');
end 
set(handles.dgaintxt,'String', strcat(int2str(100-handles.dgain),'%'));

if(handles.color==0)
 maxlut=(2^handles.bit_pix)-1;
 hold off
 if(handles.dgain<0.5)
  caxis ([10 (maxlut*0.5)/100])
 else 
  caxis ([10 (maxlut*handles.dgain)/100])
 end 
 hold on
else    
 handles.maxred= handles.maxred - (handles.maxred*0.05);   
 handles.maxgreen= handles.maxgreen - (handles.maxgreen*0.05);   
 handles.maxblue= handles.maxblue - (handles.maxblue*0.05);   
 
 while((handles.maxred<100)||(handles.maxgreen<100)||(handles.maxblue<100))
  handles.maxred=handles.maxred*1.02;
  handles.maxgreen=handles.maxgreen*1.02;
  handles.maxblue=handles.maxblue*1.02;
 end 
 
 calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
 rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
 result_image_ptr = libpointer('uint8Ptr',rgb_image);
 calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
 rgb_image=get(result_image_ptr,'Value'); 
 handles.image(:,:,3)=rgb_image(1:3:end,:)';      
 handles.image(:,:,2)=rgb_image(2:3:end,:)';      
 handles.image(:,:,1)=rgb_image(3:3:end,:)';      
 set(handles.image_buffer_map,'CData',handles.image);
end    
guidata(hObject, handles);

function gammamin_Callback(hObject, eventdata, handles)
% hObject    handle to gammamin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.gamma=handles.gamma-0.1;
set(handles.gammaplus,'Enable', 'on');
if(handles.gamma<0.2)
 set(handles.gammamin,'Enable', 'off');
end
set(handles.gammatxt,'String', num2str(handles.gamma,2));

if(handles.color==0)
 colormap(gray)
 if(handles.gamma>1)
  beta=1-1/handles.gamma;   
 else 
  beta=handles.gamma-1;
 end
 hold off
 brighten(beta);
 hold on
else    
 calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
 if(strcmp(handles.image_in_buffer,'yes'))
  rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
  result_image_ptr = libpointer('uint8Ptr',rgb_image);
  calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
  rgb_image=get(result_image_ptr,'Value'); 
  handles.image(:,:,3)=rgb_image(1:3:end,:)';      
  handles.image(:,:,2)=rgb_image(2:3:end,:)';      
  handles.image(:,:,1)=rgb_image(3:3:end,:)';      
  set(handles.image_buffer_map,'CData',handles.image);
 end
end    
guidata(hObject, handles);



% --- Executes on button press in gammaplus.
function gammaplus_Callback(hObject, eventdata, handles)
% hObject    handle to gammaplus (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
handles.gamma=handles.gamma+0.1;
set(handles.gammamin,'Enable', 'on');
if(handles.gamma>5)
 set(handles.gammaplus,'Enable', 'off');
end
set(handles.gammatxt,'String', num2str(handles.gamma,2));

if(handles.color==0)
 colormap(gray)
 if(handles.gamma>1)
  beta=1-1/handles.gamma;   
 else 
  beta=handles.gamma-1;
 end
 hold off
 brighten(beta);
 hold on 
else    
 calllib('PCO_CNV_SDK', 'CONVERT_SET_COL_EX',handles.colorlutptr,...
                                             100,100,100,...
                                             handles.maxred,handles.maxgreen,handles.maxblue,...
                                             0,handles.gamma,50);
 if(strcmp(handles.image_in_buffer,'yes'))
  rgb_image = zeros(handles.image_width*3,handles.image_height,'uint8');
  result_image_ptr = libpointer('uint8Ptr',rgb_image);
  calllib('PCO_CNV_SDK','CONV_BUF_12TOCOL_EX',0,handles.image_width,handles.image_height,...
                                         handles.bufaddress,result_image_ptr,handles.colorlutptr);      
  rgb_image=get(result_image_ptr,'Value'); 
  handles.image(:,:,3)=rgb_image(1:3:end,:)';      
  handles.image(:,:,2)=rgb_image(2:3:end,:)';      
  handles.image(:,:,1)=rgb_image(3:3:end,:)';      
  set(handles.image_buffer_map,'CData',handles.image);
 end
end    
guidata(hObject, handles);

function CloseCamera(handles)
error_code = pfSTOP_CAMERA(handles.board_handle);
if error_code ~= 0
     error('....quit_Callback: pfSTOP_CAMERA error!')
end

error_code = pfUNMAP_BUFFER(handles.board_handle,handles.bufnr1);
if error_code ~= 0
    error('....unmap buffer error!')
end
error_code = pfFREE_BUFFER(handles.board_handle,handles.bufnr1);
if error_code ~= 0
    error('....unmap buffer error!')
end

error_code = pfUNMAP_BUFFER(handles.board_handle,handles.bufnr);
if error_code ~= 0
    error('....unmap buffer error!')
end
error_code = pfFREE_BUFFER(handles.board_handle,handles.bufnr);
if error_code ~= 0
    error('....unmap buffer error!')
end
error_code = pfCLOSEBOARD(handles.board_handle);
if error_code ~= 0
    error('....disconnected error!');
end

%if (libisloaded('Pcocnv'))
%   calllib('Pcocnv','DELETE_COLORLUT',handles.colorlutptr);
 %   unloadlibrary('Pcocnv');
%end

if (libisloaded('PCO_PF_SDK'))
 unloadlibrary('PCO_PF_SDK');
end

if (libisloaded('PCO_CNV_SDK'))
  calllib('PCO_CNV_SDK','DELETE_COLORLUT_EX',handles.colorlutptr);
  unloadlibrary('PCO_CNV_SDK');
end

clear all


 
function infotext(handles)
[error_code,ccd_width,ccd_height,image_width,image_height,bit_pix]=pfGETSIZES(handles.board_handle);
if(error_code == 0)
 t1=['Max. Res.: ', int2str(ccd_width), 'x' int2str(ccd_height)];
 t2=['Act. Res.:  ', int2str(image_width), 'x' int2str(image_height)];
else
 t1=' ';   
 t2=' ';   
end 

[error_code, value] = pfGETBOARDVAL(handles.board_handle,'PCC_VAL_FRAMETIME');
if(error_code == 0)
 fps=1000000;
 fps=fps/double(value);
 t3=['Act. Fps:    ',num2str(fps,'%3.2f')];
else
 t3=' ';   
end

t=strvcat(t1,t2,t3);
set(handles.camera_info,'String',t);


% --- Executes on slider movement.
function exp_slider_Callback(hObject, eventdata, handles)
% hObject    handle to exp_slider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider
exposure_time=get(hObject,'Value');

if bitand(handles.mode,hex2dec('0f0'))==hex2dec('030')
%    exposure_time=double((round(exposure_time*10))/10);
    exposure_time=round(exposure_time);
    if (exposure_time > handles.max_exptime)
       exposure_time = handles.max_exptime;
    end
    if (exposure_time < 1)||isnan(exposure_time)
       exposure_time = 1;  
    end
    handles.exposure=cast(exposure_time,'uint32');
else
    exposure_time=double((round(exposure_time*1000))/1000);
    if (exposure_time > 65.535)
       exposure_time = 65.535;
    end
    if (exposure_time < handles.min_exptime)||isnan(exposure_time)
       exposure_time = handles.min_exptime;  
    end
   handles.exposure=cast(exposure_time*1000,'uint32');
end     

handles.exposure_str = num2str(exposure_time, '%12u');
exposure_str = num2str(exposure_time, '%8.3f');
set(handles.exptime, 'String', exposure_str);
set(handles.exp_slider,'Value',exposure_time);

error_code = pfSETMODE(handles.board_handle, handles.mode, 0, handles.exposure,...
						handles.hbin,handles.vbin,handles.gain, 0,handles.bit_pix,0);
if error_code ~= 0
      error('....exposure_edit_Callback: pfSETMODE error!');
end

infotext(handles);
guidata(hObject, handles);

% --- Executes during object creation, after setting all properties.
function exp_slider_CreateFcn(hObject, eventdata, handles)
% hObject    handle to exp_slider (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end


% --- If Enable == 'on', executes on mouse press in 5 pixel border.
% --- Otherwise, executes on mouse press in 5 pixel border or over gain_low.
function gain_low_ButtonDownFcn(hObject, eventdata, handles)
% hObject    handle to gain_low (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


