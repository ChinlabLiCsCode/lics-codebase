function varargout = autosave(varargin)
% AUTOSAVE MATLAB code for autosave.fig
%      AUTOSAVE, by itself, creates a new AUTOSAVE or raises the existing
%      singleton*.
%
%      H = AUTOSAVE returns the handle to a new AUTOSAVE or the handle to
%      the existing singleton*.
%
%      AUTOSAVE('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in AUTOSAVE.M with the given input arguments.
%
%      AUTOSAVE('Property','Value',...) creates a new AUTOSAVE or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before autosave_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to autosave_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help autosave

% Last Modified by GUIDE v2.5 21-Aug-2011 01:46:42

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @autosave_OpeningFcn, ...
                   'gui_OutputFcn',  @autosave_OutputFcn, ...
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


% --- Executes just before autosave is made visible.
function autosave_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to autosave (see VARARGIN)

% Choose default command line output for autosave
handles.output = hObject;

foldername=datestr(now,'yyyymmdd');
handles.folderdir=strcat('D:\LiCs_Data\Data\',foldername);
if not(exist(handles.folderdir))
    mkdir(handles.folderdir)
end
%handles.folderdir2=strcat('\\LICS_NAS\Data\',foldername);
%handles.folderdir2=strcat('W:\Data\',foldername);
%handles.folderdir2=strcat('\\CS_LI_ANALYSIS\Users\THE_PASSWORD_IS_abcd\Desktop\LiCs_Data_Backup_Temp\',foldername);
handles.folderdir2=strcat('\\LiCs_NAS\Data_Backup\Data\',foldername);

if not(exist(handles.folderdir2))
    mkdir(handles.folderdir2)
end

set(handles.date,'String',datestr(now,'yyyymmdd'))
handles.filedate=get(handles.date,'String');
a=dir(strcat(handles.folderdir,'\*.mat'));
set(handles.fileno,'String',numel(a))
if not(isempty(getappdata(0,'autosavimgflag')))
    set(handles.autosaveimage,'Value',getappdata(0,'autosavimgflag'));
    handles.autosavimgflag=getappdata(0,'autosavimgflag');
else
    set(handles.autosaveimage,'Value',1);
    handles.autosavimgflag=1;
end
if not(isempty(getappdata(0,'autosavfitflag')))
    set(handles.autosavefit,'Value',getappdata(0,'autosavfitflag'));
    handles.autosavfitflag=getappdata(0,'autosavfitflag');
else
    set(handles.autosavefit,'Value',1);
    handles.autosavfitflag=1;
end
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes autosave wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = autosave_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in autosaveimage.
function autosaveimage_Callback(hObject, eventdata, handles)
% hObject    handle to autosaveimage (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

handles.autosavimgflag = get(hObject,'Value');
guidata(hObject,handles)


function date_Callback(hObject, eventdata, handles)
% hObject    handle to date (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

handles.filedate=get(hObject,'String');
guidata(hObject,handles)


% --- Executes during object creation, after setting all properties.
function date_CreateFcn(hObject, eventdata, handles)
% hObject    handle to date (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function fileno_Callback(hObject, eventdata, handles)
% hObject    handle to fileno (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of fileno as text
%        str2double(get(hObject,'String')) returns contents of fileno as a double
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function fileno_CreateFcn(hObject, eventdata, handles)
% hObject    handle to fileno (see GCBO)
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


handles.savefilename=strcat(handles.folderdir,'\',get(handles.date,'String'),'_',get(handles.fileno,'String'),'.mat');
setappdata(0,'autosavimgflag',handles.autosavimgflag)
setappdata(0,'autosavfitflag',handles.autosavfitflag)
setappdata(0,'savefolderdir',handles.folderdir)
setappdata(0,'savefolderdir2',handles.folderdir2)
setappdata(0,'savedate',get(handles.date,'String'))
setappdata(0,'saveno',get(handles.fileno,'String'))
%get(handles.fileno,'String')
%get(handles.fileno,'String')
close autosave

% --- Executes on button press in autosavefit.
function autosavefit_Callback(hObject, eventdata, handles)
% hObject    handle to autosavefit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of autosavefit
handles.autosavfitflag=get(hObject,'Value');
guidata(hObject,handles)
