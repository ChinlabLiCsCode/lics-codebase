function varargout = image_console(varargin)
% IMAGE_CONSOLE MATLAB code for image_console.fig
%      IMAGE_CONSOLE, by itself, creates a new IMAGE_CONSOLE or raises the existing
%      singleton*.
%
%      H = IMAGE_CONSOLE returns the handle to a new IMAGE_CONSOLE or the handle to
%      the existing singleton*.
%
%      IMAGE_CONSOLE('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in IMAGE_CONSOLE.M with the given input arguments.
%
%      IMAGE_CONSOLE('Property','Value',...) creates a new IMAGE_CONSOLE or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before image_console_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to image_console_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help image_console

% Last Modified by GUIDE v2.5 21-Jun-2012 14:35:07

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @image_console_OpeningFcn, ...
                   'gui_OutputFcn',  @image_console_OutputFcn, ...
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

% --- Executes just before image_console is made visible.
function image_console_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to image_console (see VARARGIN)

% Choose default command line output for image_console
handles.output = hObject;

handles.experiment_list = struct([]);

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes image_console wait for user response (see UIRESUME)
% uiwait(handles.image_console);


% --- Outputs from this function are returned to the command line.
function varargout = image_console_OutputFcn(hObject, eventdata, handles)
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in auto_acquire.
function auto_acquire_Callback(hObject, eventdata, handles)
% hObject    handle to auto_acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of auto_acquire

set(handles.single_acquire,'Enable','off');
looping_val = true;
setappdata(handles.stop_acquire,'looping',true);
while looping_val
    update_all(handles);
    handles = guidata(hObject);
    pause(0.1);
    looping_val = getappdata(handles.stop_acquire,'looping');
end
set(handles.single_acquire,'Enable','on');

% --- Executes on button press in single_acquire.
function single_acquire_Callback(hObject, eventdata, handles)
% hObject    handle to single_acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
update_all(handles);

function update_all(handles)

if ~handles.working
    file_template = 'D:\\LiCs_Data\\Data\\%1$04d%2$02d%3$02d\\%1$04d%2$02d%3$02d_%4$d.mat';
    my_clock = handles.var_expt_date;
    file_name = sprintf(file_template,my_clock(1),my_clock(2),my_clock(3),handles.var_file_num);
    keep_going = false;
    if ~isempty(ls(file_name))
        try
            vars = load(file_name,'imagestack');
            imagestack = vars.imagestack;
            keep_going = true;
        catch err
            keep_going = false;
        end
    end
    if keep_going
        handles.working = true;
        guidata(image_console,handles);
        set(handles.single_acquire,'Enable','off');
        drawnow expose update;
        handles.var_file_num = handles.var_file_num + 1;
        set(handles.file_num,'String',sprintf('%d',handles.var_file_num));
        xmid = str2double(get(handles.xmid,'String'));
        xsize = str2double(get(handles.xsize,'String'));
        ymid = str2double(get(handles.ymid,'String'));
        ysize= str2double(get(handles.ysize,'String'));
        xlow = round(xmid-xsize/2);
        xhigh = round(xmid+xsize/2);
        ylow = round(ymid-ysize/2);
        yhigh = round(ymid+ysize/2);
        imagestack = imagestack(ylow:yhigh,xlow:xhigh,:);
        new_sz = size(imagestack);
        if numel(handles.experiment_list) > 0 && size(handles.experiment_list(end).images,1) > 0
            old_sz = size(handles.experiment_list(end).images);
            old_sz = old_sz(2:end);
            if any(new_sz-old_sz)
                setappdata(handles.new_expt,'var_new_expt',true);
            end
        end
        if getappdata(handles.new_expt,'var_new_expt');
            handles.experiment_list(end+1).images = zeros([0 new_sz],'uint16');
            if length(handles.experiment_list) > 1
                handles.experiment_list(end-1).images = [];
            end
            setappdata(handles.new_expt,'var_new_expt',false);
        end
        my_images = handles.experiment_list(end).images;
        my_images(end+1,:,:,:) = imagestack;
        if numel(my_images) > 7*4*1392*1024
            my_images = my_images(2:end,:,:,:);
        end
        [fit_params od_image] = process_imagestack(my_images,671,8.4);
        handles.experiment_list(end).images = my_images;
        handles.experiment_list(end).od_image = od_image;
        handles.experiment_list(end).fit_params = fit_params;
        axes(handles.main_axes);
        imagesc(od_image);
        axis image off;
        plot(handles.x_fit_axes,fit_params.xdist,fit_params.tracex,fit_params.xdist,fit_params.fittracex);
        plot(handles.y_fit_axes,fit_params.ydist,fit_params.tracey,fit_params.ydist,fit_params.fittracey);
        results_data = get(handles.results_table,'Data');
        if iscell(results_data)
            results_data = [length(handles.experiment_list) fit_params.sensible_output];
        else
            if length(handles.experiment_list) > size(results_data,1)
                results_data(2:(end+1),:) = results_data;
            end
            results_data(1,:) = [length(handles.experiment_list) fit_params.sensible_output];
        end
        set(handles.results_table,'Data',results_data);
        if ~getappdata(handles.stop_acquire,'looping')
            set(handles.single_acquire,'Enable','on');
        end
        handles.working = false;
        guidata(image_console,handles);
    end
    
end

% --- Executes on button press in stop_acquire.
function stop_acquire_Callback(hObject, eventdata, handles)
% hObject    handle to stop_acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

setappdata(hObject,'looping',false);

% --- Executes on button press in new_expt.
function new_expt_Callback(hObject, eventdata, handles)
% hObject    handle to new_expt (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

setappdata(hObject,'var_new_expt',true);

function caxis_max_Callback(hObject, eventdata, handles)
% hObject    handle to caxis_max (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of caxis_max as text
%        str2double(get(hObject,'String')) returns contents of caxis_max as a double


% --- Executes during object creation, after setting all properties.
function caxis_max_CreateFcn(hObject, eventdata, handles)
% hObject    handle to caxis_max (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function caxis_min_Callback(hObject, eventdata, handles)
% hObject    handle to caxis_min (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of caxis_min as text
%        str2double(get(hObject,'String')) returns contents of caxis_min as a double


% --- Executes during object creation, after setting all properties.
function caxis_min_CreateFcn(hObject, eventdata, handles)
% hObject    handle to caxis_min (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in caxis_auto.
function caxis_auto_Callback(hObject, eventdata, handles)
% hObject    handle to caxis_auto (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of caxis_auto


% --- Executes on button press in copy_caxis_auto.
function copy_caxis_auto_Callback(hObject, eventdata, handles)
% hObject    handle to copy_caxis_auto (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function xmid_Callback(hObject, eventdata, handles)
% hObject    handle to xmid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of xmid as text
%        str2double(get(hObject,'String')) returns contents of xmid as a double


% --- Executes during object creation, after setting all properties.
function xmid_CreateFcn(hObject, eventdata, handles)
% hObject    handle to xmid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
set(hObject,'String','915');


function ymid_Callback(hObject, eventdata, handles)
% hObject    handle to ymid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of ymid as text
%        str2double(get(hObject,'String')) returns contents of ymid as a double


% --- Executes during object creation, after setting all properties.
function ymid_CreateFcn(hObject, eventdata, handles)
% hObject    handle to ymid (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
set(hObject,'String','412');


function ysize_Callback(hObject, eventdata, handles)
% hObject    handle to ysize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of ysize as text
%        str2double(get(hObject,'String')) returns contents of ysize as a double


% --- Executes during object creation, after setting all properties.
function ysize_CreateFcn(hObject, eventdata, handles)
% hObject    handle to ysize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
set(hObject,'String','75');

% --- Executes on button press in full_scr.
function full_scr_Callback(hObject, eventdata, handles)
% hObject    handle to full_scr (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of full_scr


% --- Executes on button press in make_full.
function make_full_Callback(hObject, eventdata, handles)
% hObject    handle to make_full (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function xsize_Callback(hObject, eventdata, handles)
% hObject    handle to xsize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of xsize as text
%        str2double(get(hObject,'String')) returns contents of xsize as a double


% --- Executes during object creation, after setting all properties.
function xsize_CreateFcn(hObject, eventdata, handles)
% hObject    handle to xsize (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end
set(hObject,'String',200);

% --- Executes on button press in quit.
function quit_Callback(hObject, eventdata, handles)
% hObject    handle to quit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

setappdata(hObject,'looping',false);
close image_console;

function expt_date_Callback(hObject, eventdata, handles)
% hObject    handle to expt_date (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of expt_date as text
%        str2double(get(hObject,'String')) returns contents of expt_date as a double

try
    date_entered_str = get(hObject,'String');
    date_entered = datevec(date_entered_str);
    new_str = datestr(date_entered,'yyyy-mm-dd');
    if size(new_str,1) > 1
        date_entered = handles.var_expt_date;
    end
catch err
    date_entered = handles.var_expt_date;
end
new_str = datestr(date_entered,'yyyy-mm-dd');
if any(handles.var_expt_date ~= date_entered)
    setappdata(handles.new_expt,'var_new_expt',true);
end
handles.var_expt_date = date_entered;
guidata(hObject,handles);
set(hObject,'String',new_str);

% --- Executes during object creation, after setting all properties.
function expt_date_CreateFcn(hObject, eventdata, handles)
% hObject    handle to expt_date (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

date_now = datestr(now,'yyyy-mm-dd');
set(hObject,'String',date_now);
handles.var_expt_date = datevec(now);
guidata(hObject,handles);

function file_num_Callback(hObject, eventdata, handles)
% hObject    handle to file_num (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of file_num as text
%        str2double(get(hObject,'String')) returns contents of file_num as a double


try
    my_num = round(str2double(get(hObject,'String')));
    if ~isfinite(my_num) || my_num <= 0
        my_num = handles.var_file_num;
    end
catch err
    my_num = handles.var_file_num;
end
if any(handles.var_file_num ~= my_num)
    setappdata(handles.new_expt,'var_new_expt',true);
end
handles.var_file_num = my_num;
guidata(hObject,handles);
set(hObject,'String',sprintf('%d',my_num));

% --- Executes during object creation, after setting all properties.
function file_num_CreateFcn(hObject, eventdata, handles)
% hObject    handle to file_num (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

set(hObject,'String',1);
handles.var_file_num = 1;
guidata(hObject,handles);

% --- Executes on button press in date_today.
function date_today_Callback(hObject, eventdata, handles)
% hObject    handle to date_today (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

date_box = handles.expt_date;

date_now = datestr(now,'yyyy-mm-dd');
set(date_box,'String',date_now);
now_vec = datevec(date_now);
if any(handles.var_expt_date ~= now_vec)
    setappdata(handles.new_expt,'var_new_expt',true);
end
handles.var_expt_date = now_vec;
guidata(hObject,handles);

% --- Executes on button press in num_latest.
function num_latest_Callback(hObject, eventdata, handles)
% hObject    handle to num_latest (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


% --- Executes during object creation, after setting all properties.
function new_expt_CreateFcn(hObject, eventdata, handles)
% hObject    handle to new_expt (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
 
setappdata(hObject,'var_new_expt',true);


% --- Executes during object creation, after setting all properties.
function single_acquire_CreateFcn(hObject, eventdata, handles)
% hObject    handle to single_acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

handles.working = false;
guidata(hObject,handles);


% --- Executes during object creation, after setting all properties.
function stop_acquire_CreateFcn(hObject, eventdata, handles)
% hObject    handle to stop_acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

setappdata(hObject,'looping',false);


% --- Executes during object creation, after setting all properties.
function results_table_CreateFcn(hObject, eventdata, handles)
% hObject    handle to results_table (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject,'ColumnName',{'Exp. Num','Num Shots','Num X','Num Y','Sz X', 'Sz Y'});


% --- Executes on button press in save_button.
function save_button_Callback(hObject, eventdata, handles)
% hObject    handle to save_button (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


file_template = 'D:\\LiCs_Data\\Data\\%1$04d%2$02d%3$02d\\image_console';
my_clock = handles.var_expt_date;
save_dir = sprintf(file_template,my_clock(1),my_clock(2),my_clock(3),handles.var_file_num);

go_ahead = false;
try
    if ~isdir(save_dir)
        mkdir(save_dir);
    end
    go_ahead = true;
catch my_err
    
end

exp_num = numel(handles.experiment_list);
if go_ahead && exp_num > 0
   
   out_experiment = handles.experiment_list(end);
   save_file_name = sprintf('%s\\exp_%04d.mat',save_dir,exp_num);
   save(save_file_name,'out_experiment');
end
