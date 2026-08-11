function varargout = fitsettings(varargin)
% FITSETTINGS MATLAB code for fitsettings.fig
%      FITSETTINGS, by itself, creates a new FITSETTINGS or raises the existing
%      singleton*.
%
%      H = FITSETTINGS returns the handle to a new FITSETTINGS or the handle to
%      the existing singleton*.
%
%      FITSETTINGS('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in FITSETTINGS.M with the given input arguments.
%
%      FITSETTINGS('Property','Value',...) creates a new FITSETTINGS or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before fitsettings_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to fitsettings_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help fitsettings

% Last Modified by GUIDE v2.5 26-Jul-2023 12:19:27

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @fitsettings_OpeningFcn, ...
                   'gui_OutputFcn',  @fitsettings_OutputFcn, ...
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


% --- Executes just before fitsettings is made visible.
function fitsettings_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to fitsettings (see VARARGIN)

% Choose default command line output for fitsettings
handles.output = hObject;
clc
defringflag = 3;
setappdata(0,'defringflag',defringflag)
if isempty(getappdata(0,'autoguessflag'))
    autoguessflag = 1;%default value
else
    autoguessflag = getappdata(0,'autoguessflag');
end
handles.fitmodel = 1; %default values
setappdata(0,'fitmodel',handles.fitmodel)
if exist('savedinig1D.mat')
    load('savedinig1D.mat')
    handles.gaussian1D.nx=saveinig1D.nx;
    handles.gaussian1D.bg=saveinig1D.bg;
    handles.gaussian1D.wx=saveinig1D.wx;
    handles.gaussian1D.xc=saveinig1D.xc;
    handles.gaussian1D.yc=saveinig1D.yc;
    handles.gaussian1D.wy=saveinig1D.wy;
    handles.gaussian1D.ny=saveinig1D.ny;
else
    handles.gaussian1D.nx=0;
    handles.gaussian1D.bg=0;
    handles.gaussian1D.wx=0;
    handles.gaussian1D.xc=0;
    handles.gaussian1D.yc=0;
    handles.gaussian1D.wy=0;
    handles.gaussian1D.ny=0;
end
if autoguessflag == 0
    set(handles.manualinput,'Value',1)
else
    set(handles.autoguess,'Value',1)
end

set(handles.text3,'String','nx')
set(handles.text4,'String','wx')
set(handles.text5,'String','xc')
set(handles.text6,'String','ny')
set(handles.text7,'String','wy')
set(handles.text8,'String','yc')
set(handles.text17,'String','bg')
set(handles.edit1,'String',num2str(handles.gaussian1D.nx))
set(handles.edit2,'String',num2str(handles.gaussian1D.wx))
set(handles.edit3,'String',num2str(handles.gaussian1D.xc))
set(handles.edit4,'String',num2str(handles.gaussian1D.ny))
set(handles.edit5,'String',num2str(handles.gaussian1D.wy))
set(handles.edit6,'String',num2str(handles.gaussian1D.yc))
set(handles.edit14,'String',num2str(handles.gaussian1D.bg))
set(handles.text18,'Visible','off')
set(handles.text19,'Visible','off')
set(handles.text20,'Visible','off')
set(handles.text21,'Visible','off')
set(handles.text22,'Visible','off')
set(handles.text23,'Visible','off')
set(handles.text24,'Visible','off')
set(handles.edit15,'Enable','off')
set(handles.edit16,'Enable','off')
set(handles.edit17,'Enable','off')
set(handles.edit18,'Enable','off')
set(handles.edit19,'Enable','off')
set(handles.edit20,'Enable','off')
set(handles.edit21,'Enable','off')


% TEXT annotations need an axes as parent so create an invisible axes which
% is as big as the figure
handles.laxis = axes('parent',handles.uipanel3,'units','normalized','position',[0 0 1 1],'visible','off');
% Find all static text UICONTROLS whose 'Tag' starts with latex_
% Get current text, position and tag
set(handles.text2,'units','normalized');
p = get(handles.text2,'Position');
% Remove the UICONTROL
delete(handles.text2)
% Replace it with a TEXT object 
if handles.fitmodel == 1
handles.text2=text(p(1)+p(3)/2,p(2)+p(4)/2,'n_{x}e^{-(x-xc)^2/2w_{x}^{2}}','interpreter','tex','units','normalized');
end

guidata(hObject, handles);

% UIWAIT makes fitsettings wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = fitsettings_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;

% --- Executes on selection change in modelselect.
function modelselect_Callback(hObject, eventdata, handles)

handels.fitmodel=get(hObject,'Value');
setappdata(0,'fitmodel',handles.fitmodel)
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function modelselect_CreateFcn(hObject, eventdata, handles)
% hObject    handle to modelselect (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on button press in fitsaveexit.
function fitsaveexit_Callback(hObject, eventdata, handles)
% hObject    handle to fitsaveexit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
setfitflag=1;
setappdata(0,'setfitflag',setfitflag)
saveini(handles)
defringflag = getappdata(0,'defringflag');
if defringflag == 1
    setappdata(0,'fileno_i',get(handles.fileno_i,'String'))
    setappdata(0,'fileno_f',get(handles.fileno_f,'String'))
    setappdata(0,'no_base',get(handles.no_base,'String'))
    fileno_i = get(handles.fileno_i,'String');
    fileno_f = get(handles.fileno_f,'String');
    fileno_i = str2num(fileno_i{1});
    fileno_f = str2num(fileno_f{1});
    hMainGui = getappdata(0,'hMainGui');
    hxcin=findobj(hMainGui,'Tag','Xcin');
    hycin=findobj(hMainGui,'Tag','Ycin');
    hdx=findobj(hMainGui,'Tag','dX');
    hdy=findobj(hMainGui,'Tag','dY');
    xc=str2double(get(hxcin,'String'));
    yc=str2double(get(hycin,'String'));
    dx=str2double(get(hdx,'String'));
    dy=str2double(get(hdy,'String'));
    ysiz = length(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)));
    xsiz = length(round(xc-((dx-1)/2)):round(xc+((dx-1)/2)));
    bgimg_stack = zeros(ysiz,xsiz,length(fileno_i : fileno_f));
    for i = fileno_i : fileno_f
        loadfilename = sprintf('D:\\LiCs_Data\\Data\\%s\\%s_%s.mat',datestr(now,'yyyymmdd'),datestr(now,'yyyymmdd'),num2str(i));
        load(loadfilename,'imagestack')
        [~,lightimg,~] = ODimg1(imagestack);
        bgimg_stack(:,:,i-fileno_i+1)= lightimg(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)));   
    end
    setappdata(0,'bgimg_stack',bgimg_stack)
    disp('am i here')
end

close fitsettings

% --- Executes on button press in pushbutton3.
function pushbutton3_Callback(hObject, eventdata,handles)
% hObject    handle to pushbutton3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
close fitsettings


function edit13_Callback(hObject, eventdata, handles)
% hObject    handle to edit13 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit13 as text
%        str2double(get(hObject,'String')) returns contents of edit13 as a double


% --- Executes during object creation, after setting all properties.
function edit13_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit13 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Xmin_Callback(hObject, eventdata, handles)
% hObject    handle to Xmin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Xmin as text
%        str2double(get(hObject,'String')) returns contents of Xmin as a double


% --- Executes during object creation, after setting all properties.
function Xmin_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Xmin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Ymin_Callback(hObject, eventdata, handles)
% hObject    handle to Ymin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ymin as text
%        str2double(get(hObject,'String')) returns contents of Ymin as a double


% --- Executes during object creation, after setting all properties.
function Ymin_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ymin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function width_Callback(hObject, eventdata, handles)
% hObject    handle to width (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of width as text
%        str2double(get(hObject,'String')) returns contents of width as a double


% --- Executes during object creation, after setting all properties.
function width_CreateFcn(hObject, eventdata, handles)
% hObject    handle to width (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function height_Callback(hObject, eventdata, handles)
% hObject    handle to height (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of height as text
%        str2double(get(hObject,'String')) returns contents of height as a double


% --- Executes during object creation, after setting all properties.
function height_CreateFcn(hObject, eventdata, handles)
% hObject    handle to height (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function fileno_i_Callback(hObject, eventdata, handles)
% hObject    handle to fileno_i (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of fileno_i as text
%        str2double(get(hObject,'String')) returns contents of fileno_i as a double


% --- Executes during object creation, after setting all properties.
function fileno_i_CreateFcn(hObject, eventdata, handles)
% hObject    handle to fileno_i (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function fileno_f_Callback(hObject, eventdata, handles)
% hObject    handle to fileno_f (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of fileno_f as text
%        str2double(get(hObject,'String')) returns contents of fileno_f as a double


% --- Executes during object creation, after setting all properties.
function fileno_f_CreateFcn(hObject, eventdata, handles)
% hObject    handle to fileno_f (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if handles.fitmodel == 1
    handles.gaussian1D.nx=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function edit1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit2_Callback(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
if handles.fitmodel == 1
    handles.gaussian1D.wx=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function edit2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit3_Callback(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if handles.fitmodel == 1
    handles.gaussian1D.xc=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)


% --- Executes during object creation, after setting all properties.
function edit3_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit3 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit4_Callback(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if handles.fitmodel == 1
    handles.gaussian1D.ny=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)


% --- Executes during object creation, after setting all properties.
function edit4_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit4 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit5_Callback(hObject, eventdata, handles)
% hObject    handle to edit5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if handles.fitmodel == 1
    handles.gaussian1D.wy=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function edit5_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit6_Callback(hObject, eventdata, handles)
if handles.fitmodel == 1
    handles.gaussian1D.yc=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function edit6_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit14_Callback(hObject, eventdata, handles)
if handles.fitmodel == 1
    handles.gaussian1D.bg=str2double(get(hObject,'String'));
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6    
end
guidata(hObject,handles)

% --- Executes during object creation, after setting all properties.
function edit14_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit14 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit15_Callback(hObject, eventdata, handles)
% hObject    handle to edit15 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit15 as text
%        str2double(get(hObject,'String')) returns contents of edit15 as a double


% --- Executes during object creation, after setting all properties.
function edit15_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit15 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit16_Callback(hObject, eventdata, handles)
% hObject    handle to edit16 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit16 as text
%        str2double(get(hObject,'String')) returns contents of edit16 as a double


% --- Executes during object creation, after setting all properties.
function edit16_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit16 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit17_Callback(hObject, eventdata, handles)
% hObject    handle to edit17 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit17 as text
%        str2double(get(hObject,'String')) returns contents of edit17 as a double


% --- Executes during object creation, after setting all properties.
function edit17_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit17 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit18_Callback(hObject, eventdata, handles)
% hObject    handle to edit18 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit18 as text
%        str2double(get(hObject,'String')) returns contents of edit18 as a double


% --- Executes during object creation, after setting all properties.
function edit18_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit18 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit19_Callback(hObject, eventdata, handles)
% hObject    handle to edit19 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit19 as text
%        str2double(get(hObject,'String')) returns contents of edit19 as a double


% --- Executes during object creation, after setting all properties.
function edit19_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit19 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit20_Callback(hObject, eventdata, handles)
% hObject    handle to edit20 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit20 as text
%        str2double(get(hObject,'String')) returns contents of edit20 as a double


% --- Executes during object creation, after setting all properties.
function edit20_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit20 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function edit21_Callback(hObject, eventdata, handles)
% hObject    handle to edit21 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit21 as text
%        str2double(get(hObject,'String')) returns contents of edit21 as a double


% --- Executes during object creation, after setting all properties.
function edit21_CreateFcn(hObject, eventdata, handles)
% hObject    handle to edit21 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in defring1.
function defring1_Callback(hObject, eventdata, handles)
% hObject    handle to defring1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of defring1


% --- Executes on button press in manualinput.
function manualinput_Callback(hObject, eventdata, handles)
% hObject    handle to manualinput (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of manualinput




function saveini(handles)
if handles.fitmodel == 1
saveinig1D.nx=handles.gaussian1D.nx;
saveinig1D.wx=handles.gaussian1D.wx;
saveinig1D.xc=handles.gaussian1D.xc;
saveinig1D.ny=handles.gaussian1D.ny;
saveinig1D.wy=handles.gaussian1D.wy;
saveinig1D.yc=handles.gaussian1D.yc;
saveinig1D.bg=handles.gaussian1D.bg;
save('savedinig1D.mat','saveinig1D')
elseif handles.fitmodel == 2
elseif handles.fitmodel == 3
elseif handles.fitmodel == 4
elseif handles.fitmodel == 5
elseif handles.fitmodel == 6
end
        


% --- Executes when selected object is changed in uipanel6.
function uipanel6_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in uipanel6 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDAT)


    switch get(hObject,'Tag');
        case 'manualinput'
            autoguessflag = 0;
        case 'autoguess'
            autoguessflag = 1;
    end
setappdata(0,'autoguessflag',autoguessflag)

% --- Executes on button press in setrect.
function setrect_Callback(hObject, eventdata, handles)
% hObject    handle to setrect (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
hMainGui = getappdata(0,'hMainGui');
hxcin=findobj(hMainGui,'Tag','Xcin');
hycin=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');
xc=str2double(get(hxcin,'String'));
yc=str2double(get(hycin,'String'));
dx=str2double(get(hdx,'String'));
dy=str2double(get(hdy,'String'));

ODimage = getappdata(0,'ODimage');
if ~isempty(ODimage)
    figure(999)
    [~,rect2] = imcrop(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))));
    rect2 = round(rect2);
    close(figure(999))
    set(handles.Xmin,'String',rect2(1));
    set(handles.Ymin,'String',rect2(2));
    set(handles.width,'String',rect2(3));
    set(handles.height,'String',rect2(4));
    setappdata(0,'rect2',rect2)
else
    rect2 = [1 1 1024 1024];
    set(handles.Xmin,'String',rect2(1));
    set(handles.Ymin,'String',rect2(2));
    set(handles.width,'String',rect2(3));
    set(handles.height,'String',rect2(4));
    setappdata(0,'rect2',rect2)
end

function no_base_Callback(hObject, eventdata, handles)
% hObject    handle to no_base (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of no_base as text
%        str2double(get(hObject,'String')) returns contents of no_base as a double


% --- Executes during object creation, after setting all properties.
function no_base_CreateFcn(hObject, eventdata, handles)
% hObject    handle to no_base (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes when selected object is changed in uipanel4.
function uipanel4_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in uipanel4 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)

switch get(hObject,'Tag');
    case 'defring1'
        defringflag = 1;
    case 'defring2'
        defringflag = 2;
    case 'defring3'
        defringflag = 3;
end
setappdata(0,'defringflag',defringflag)
