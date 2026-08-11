function varargout = camsettings(varargin)
% CAMSETTINGS MATLAB code for camsettings.fig
%      CAMSETTINGS, by itself, creates a new CAMSETTINGS or raises the existing
%      singleton*.
%
%      H = CAMSETTINGS returns the handle to a new CAMSETTINGS or the handle to
%      the existing singleton*.
%
%      CAMSETTINGS('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in CAMSETTINGS.M with the given input arguments.
%
%      CAMSETTINGS('Property','Value',...) creates a new CAMSETTINGS or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before camsettings_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to camsettings_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help camsettings

% Last Modified by GUIDE v2.5 24-Apr-2012 15:08:48

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @camsettings_OpeningFcn, ...
                   'gui_OutputFcn',  @camsettings_OutputFcn, ...
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


% --- Executes just before camsettings is made visible.
function camsettings_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to camsettings (see VARARGIN)
if not(libisloaded('PCO_PF_SDK'))
    loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end
clc
% Choose default command line output for camsettings
handles.output = hObject;
%-----------get params from the root-----------------------

    exposure_time  = getappdata(0,'exposure_time');
    vbinselect     = getappdata(0,'vbinselect');
    hbinselect     = getappdata(0,'hbinselect');
    gainselect     = getappdata(0,'gainselect');
    mode_index     = getappdata(0,'mode_index');
    bit_pix        = 12;
    max_num_of_images=20;
    board_handle   = getappdata(0,'board_handle');
    num_of_images  = getappdata(0,'num_of_images');
    handles.exposure_time = exposure_time;
    handles.vbinselect    = vbinselect;
    handles.hbinselect    = hbinselect;
    handles.gainselect    = gainselect;
    handles.mode_index    = mode_index;
    handles.bit_pix       = bit_pix;
    handles.num_of_images = num_of_images;
    handles.max_num_of_images=max_num_of_images;
    if     mode_index == 1
        handles.modeselect=hex2dec('10');
    elseif mode_index == 2
        handles.modeselect=hex2dec('11');
    elseif mode_index == 3
        handles.modeselect=hex2dec('30');
    elseif mode_index == 4
        handles.modeselect=hex2dec('31');
    elseif mode_index == 5
        handles.modeselect=hex2dec('20');
    elseif mode_index == 6
        handles.modeselect=hex2dec('21');
    end
%--------------------------------------------------------------------------
%Set initial values(or stings) displayed on the front panel when GUI is 
%called--------------------------------------------------------------------
set(handles.mode,'Value',mode_index);
set(handles.exposure,'String',num2str(exposure_time));
set(handles.num_images,'String',num2str(num_of_images));
if vbinselect == 0
    set(handles.vbin1,'Value',1)
elseif vbinselect == 1
    set(handles.vbin2,'Value',1)
end
if hbinselect == 0
    set(handles.hbin1,'Value',1)
elseif hbinselect == 1
    set(handles.hbin2,'Value',1)
end
if gainselect == 0
    set(handles.lowgain,'Value',1)
elseif gainselect == 1
    set(handles.highgain,'Value',1)
end
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes camsettings wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = camsettings_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on selection change in mode.
function mode_Callback(hObject, eventdata, handles)
% hObject    handle to mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns mode contents as cell array
%        contents{get(hObject,'Value')} returns selected item from mode
handles.mode_index=get(hObject,'Value');
handles.exposure_time=str2double(get(handles.exposure,'String'));
num_of_images=str2double(get(handles.num_images,'String'));
if handles.mode_index == 1
    handles.modeselect=hex2dec('10');
    if handles.exposure_time > 65.535
        handles.exposure_time = 65.535;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if handles.exposure_time < 0.01
        handles.exposure_time = 0.01;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if num_of_images > handles.max_num_of_images
        set(handles.num_images,'String',num2str(handles.num_of_images))
    end
elseif handles.mode_index == 2
    handles.modeselect=hex2dec('11');
    handles.num_of_images=1;
    set(handles.num_images,'String',handles.num_of_images)
    if handles.exposure_time > 65.535
        handles.exposure_time = 65.535;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if handles.exposure_time < 0.01
        handles.exposure_time = 0.01;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
elseif handles.mode_index == 3
    handles.num_of_images = 1;
    set(handles.num_images,'String',handles.num_of_images)
    handles.modeselect=hex2dec('30');
elseif handles.mode_index == 4
    handles.num_of_images = 1;
    set(handles.num_images,'String',handles.num_of_images)
    handles.modeselect=hex2dec('31');
elseif handles.mode_index == 5
    handles.modeselect=hex2dec('20');
    if handles.exposure_time > 65.535
        handles.exposure_time = 65.535;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if handles.exposure_time < 0.01
        handles.exposure_time = 0.01;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if num_of_images > handles.max_num_of_images
        set(handles.num_images,'String',num2str(handles.num_of_images))
    end
elseif handles.mode_index == 6
    handles.modeselect=hex2dec('21');
    handles.num_of_images=1;
    set(handles.num_images,'String',handles.num_of_images)
    if handles.exposure_time > 65.535
        handles.exposure_time = 65.535;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
    if handles.exposure_time < 0.01
        handles.exposure_time = 0.01;
        set(handles.exposure,'String',num2str(handles.exposure_time));
    end
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function mode_CreateFcn(hObject, eventdata, handles)
% hObject    handle to mode (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function exposure_Callback(hObject, eventdata, handles)
% hObject    handle to exposure (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of exposure as text
%        str2double(get(hObject,'String')) returns contents of exposure as a double
handles.exposure_time=str2double(get(hObject,'String'));
handles.mode_index = get(handles.mode,'Value');
if handles.mode_index == 1 || handles.mode_index == 2 || handles.mode_index == 5 || handles.mode_index == 6
    if handles.exposure_time > 65.535 
        handles.exposure_time = 65.535;
        set(hObject,'String',num2str(handles.exposure_time));
    end
    if handles.exposure_time < 0.01
        handles.exposure_time = 0.01;
        set(hObject,'String',num2str(handles.exposure_time))
    end
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function exposure_CreateFcn(hObject, eventdata, handles)
% hObject    handle to exposure (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in saveexit.
function saveexit_Callback(hObject, eventdata, handles)
% hObject    handle to saveexit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
savestate(handles)
%Set params(appdata) to the root-------------------------------------------
setappdata(0,'mode_index',handles.mode_index);
setappdata(0,'modeselect',handles.modeselect);
setappdata(0,'exposure_time',handles.exposure_time);
setappdata(0,'vbinselect',handles.vbinselect);
setappdata(0,'hbinselect',handles.hbinselect);
setappdata(0,'gainselect',handles.gainselect);
setappdata(0,'num_of_images',handles.num_of_images);
%Setmode / set params------------------------------------------------------
board_handle=getappdata(0,'board_handle');
if handles.mode_index == 1 || handles.mode_index == 2 || handles.mode_index == 5 || handles.mode_index == 6
    error_code=pfSETMODE(board_handle, handles.modeselect, 0, ...
        handles.exposure_time*1000, handles.hbinselect, handles.vbinselect, ...
        handles.gainselect, 0, handles.bit_pix, 0);
elseif handles.mode_index == 3 || handles.mode_index == 4
    error_code=pfSETMODE(board_handle, handles.modeselect, 0, ...
        handles.exposure_time, handles.hbinselect, handles.vbinselect, ...
        handles.gainselect, 0, handles.bit_pix, 0);
end
if error_code ~= 0
    error('...initial setmode failed')
end

hupdate_popupmenu1=getappdata(0,'hupdate_popupmenu1');
feval(hupdate_popupmenu1)
%--------------------------------------------------------------------------
%Get sizes of CCD and images------------------------------------------------
[error_code, ccd_width, ccd_height, image_width, image_height, bit_pix]=...
    pfGETSIZES(board_handle);
imagesize=image_width*image_height*2;
if error_code ~=0
    error('Fail to get SIZES')
end
setappdata(0,'ccd_width',ccd_width);
setappdata(0,'ccd_height',ccd_height);
setappdata(0,'image_width',image_width);
setappdata(0,'image_height',image_height);
setappdata(0,'imagesize',imagesize);

hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

%set(hxc,'String',num2str((double(image_width)+1)/2));
%set(hyc,'String',num2str((double(image_height)+1)/2));
%set(hdx,'String',num2str(double(image_width)));
%set(hdy,'String',num2str(double(image_height)));

%--------------------------------------------------------------------------


% [error_code, value1]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_EXPTIME')
% [error_code, value2]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_MODE')
% [error_code, value3]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_AGAIN')
% [error_code, value4]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_VBIN')
% [error_code, value5]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_HBIN')
% [error_code, value6]=pfGETBOARDVAL(handles.board_handle,'PCC_VAL_CCDTYPE')
% handles.image_width
% handles.image_height 

% handles
% disp('ishandle(handles.vbin)')
% ishandle(handles.vbin)
% disp('ishandle(handles.vbinselect)')
% ishandle(handles.vbinselect)
% disp('get(handles.vbin)')
% get(handles.vbin)

close camsettings


% --- Executes on button press in exitnosave.
function exitnosave_Callback(hObject, eventdata, handles)
% hObject    handle to exitnosave (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if(eventdata)
end

close camsettings

% --- Executes when selected object is changed in vbin.
function vbin_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in vbin 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(hObject,'Tag')   % Get Tag of selected object
    case 'vbin1'
     handles.vbinselect=0;
    case 'vbin2'
     handles.vbinselect=1;
end
guidata(hObject, handles);


% --- Executes when selected object is changed in hbin.
function hbin_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in hbin 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(hObject,'Tag')   % Get Tag of selected object
    case 'hbin1'
     handles.hbinselect=0;
    case 'hbin2'
     handles.hbinselect=1;
end
guidata(hObject, handles);


% --- Executes when selected object is changed in gain.
function gain_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in gain 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)
switch get(hObject,'Tag')   % Get Tag of selected object
    case 'highgain'
     handles.gainselect=1;
    case 'lowgain'
     handles.gainselect=0;
end
guidata(hObject, handles);

% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the figure
%error_code=pfCLOSEBOARD(handles.board_handle);
delete(hObject);


function savestate(handles)
savepar.exposure_time=handles.exposure_time;
savepar.vbinselect=handles.vbinselect;
savepar.hbinselect=handles.hbinselect;
savepar.gainselect=handles.gainselect;
savepar.mode_index=handles.mode_index;
savepar.modeselect=handles.modeselect;
savepar.num_of_images=handles.num_of_images;
save('savedcamset.mat','savepar')



function num_images_Callback(hObject, eventdata, handles)
% hObject    handle to num_images (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of num_images as text
%        str2double(get(hObject,'String')) returns contents of num_images as a double
handles.num_of_images=str2double(get(hObject,'String'));
if handles.mode_index == 2 || handles.mode_index == 3 || handles.mode_index == 4 || handles.mode_index == 6
    if handles.num_of_images ~= 1
        handles.num_of_images = 1;
        set(hObject,'String',num2str(handles.num_of_images));
    end
elseif handles.mode_index == 1 || handles.mode_index == 5
    if handles.num_of_images > handles.max_num_of_images
        handles.num_of_images = handles.max_num_of_images;
        set(hObject,'String',num2str(handles.num_of_images));
    elseif handles.num_of_images < 1
        set(hObject,'String',num2str(1));
    end
end
guidata(hObject,handles);

% --- Executes during object creation, after setting all properties.
function num_images_CreateFcn(hObject, eventdata, handles)
% hObject    handle to num_images (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --------------------------------------------------------------------
function Untitled_1_Callback(hObject, eventdata, handles)
% hObject    handle to Untitled_1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
