function varargout = SKHpixelfly(varargin)
% SKHpixelfly MATLAB code for SKHpixelfly.fig
%      SKHpixelfly, by itself, creates a new SKHpixelfly or raises the existing
%      singleton*.
%
%      H = SKHpixelfly returns the handle to a new SKHpixelfly or the handle to
%      the existing singleton*.
%
%      SKHpixelfly('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SKHpixelfly.M with the given input arguments.
%
%      SKHpixelfly('Property','Value',...) creates a new SKHpixelfly or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before SKpixelfly_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to SKpixelfly_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help SKHpixelfly

% Last Modified by GUIDE v2.5 27-Sep-2023 13:04:03

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @SKHpixelfly_OpeningFcn, ...
                   'gui_OutputFcn',  @SKHpixelfly_OutputFcn, ...
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


% --- Executes just before SKHpixelfly is made visible.
function SKHpixelfly_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to SKHpixelfly (see VARARGIN)

if not(libisloaded('PCO_PF_SDK'))
    loadlibrary('pccamvb','pccamvb.h','alias','PCO_PF_SDK');
end
clc

% Choose default command line output for SKHpixelfly
handles.output = hObject;
set(handles.mesg,'String',['Hello, Chicago. Today is ',datestr(now,'mmmm dd, yyyy')])

setfitflag = 0;
setappdata(0,'setfitflag',setfitflag)
%-----------load saved params or load default values-----------------------
if exist('savedcamset.mat')
    load('savedcamset.mat');
    setappdata(0,'exposure_time',savepar.exposure_time);
    exposure_time=getappdata(0,'exposure_time');
    setappdata(0,'vbinselect',savepar.vbinselect);
    vbinselect=getappdata(0,'vbinselect');
    setappdata(0,'hbinselect',savepar.hbinselect);
    hbinselect=getappdata(0,'hbinselect');
    setappdata(0,'gainselect',savepar.gainselect);
    gainselect=getappdata(0,'gainselect');
    setappdata(0,'mode_index',savepar.mode_index);
    mode_index=getappdata(0,'mode_index');
    setappdata(0,'modeselect',savepar.modeselect);
    modeselect=getappdata(0,'modeselect');
    %modeselect=33;
    setappdata(0,'num_of_images',savepar.num_of_images);
    num_of_images=getappdata(0,'num_of_images');
    bit_pix=12;
    setappdata(0,'bit_pix',bit_pix);
    color=0;
    setappdata(0,'color',0);
else
    exposure_time  = 65; %default values
    setappdata(0,'exposure_time',exposure_time);
    vbinselect     = 0;
    setappdata(0,'vbinselect',vbinselect);
    hbinselect     = 0;
    setappdata(0,'hbinselect',hbinselect);
    gainselect     = 0;
    setappdata(0,'gainselect',gainselect);
    mode_index     = 2;
    setappdata(0,'mode_index',mode_index);
    modeselect     = 33;
    setappdata(0,'modeselect',modeselect);
    bit_pix        = 12;
    setappdata(0,'bit_pix',bit_pix);
    color          = 0;
    setappdata(0,'color',color);
    num_of_images  = 1;
    setappdata(0,'num_of_images',num_of_images);
end
%--------------------------------------------------------------------------
%Initialize board----------------------------------------------------------
board_number = 0;
[error_code, board_handle]=pfINITBOARD(board_number);
if (error_code~=0)
    error(['Could not initialize camera. Error is ',int2str(error_code)]);
end
handles.board_handle=board_handle;
setappdata(0,'board_handle',board_handle);
%--------------------------------------------------------------------------
%Setmode / set params------------------------------------------------------
if mode_index == 1 || mode_index == 2 || mode_index == 5 || mode_index == 6
    error_code=pfSETMODE(handles.board_handle, modeselect, 0, ...
        exposure_time*1000, hbinselect, vbinselect, ...
        gainselect, 0, bit_pix, 0);
elseif mode_index == 3 || mode_index == 4
    error_code=pfSETMODE(handles.board_handle, modeselect, 0, ...
        exposure_time, hbinselect, vbinselect, ...
        gainselect, 0, bit_pix, 0);
end
if error_code ~= 0
    error('...initial setmode failed')
end
%--------------------------------------------------------------------------
%Get sizes of CCD and images------------------------------------------------
[error_code, ccd_width, ccd_height, image_width, image_height, bit_pix]=...
    pfGETSIZES(handles.board_handle);
imagesize=image_width*image_height*2;
if error_code ~=0
    error('Fail to get SIZES')
end
setappdata(0,'ccd_width',ccd_width);
setappdata(0,'ccd_height',ccd_height);
setappdata(0,'image_width',image_width);
setappdata(0,'image_height',image_height);
setappdata(0,'imagesize',imagesize);
%--------------------------------------------------------------------------
%Read temperatures---------------------------------------------------------
[error_code, temp_ccd]=pfREADTEMPERATURE(handles.board_handle);
if error_code ~= 0
    error('Fail to read temperature.');
end
if error_code ~= 0
    handles.temp_ccd = -1;
end
setappdata(0,'temp_ccd',temp_ccd);
%--------------------------------------------------------------------------

set(handles.Xcin,'String',num2str((double(image_width)+1)/2));
set(handles.Ycin,'String',num2str((double(image_height)+1)/2));
set(handles.dX,'String',num2str(double(image_width)));
set(handles.dY,'String',num2str(double(image_height)));
set(handles.colorbar_max,'String',num2str(2));
set(handles.colorbar_min,'String',num2str(0));

%--------------------------------------------------------------------------

setappdata(0,'hMainGui',gcf);
setappdata(0,'hupdate_popupmenu1',@update_popupmenu1);
%--------------------------------------------------------------------------
hax1=findobj(gcf,'Tag','axes1');
hax2=findobj(gcf,'Tag','axes2');
hax5=findobj(gcf,'Tag','axes5');
hax6=findobj(gcf,'Tag','axes6');
setappdata(0,'hax1',hax1);
setappdata(0,'hax2',hax2);
setappdata(0,'hax5',hax5);
setappdata(0,'hax6',hax6);
%--------------------------------------------------------------------------
autofitflag = 1;
setappdata(0,'autofitflag',autofitflag);
autoacqflag = 1;
setappdata(0,'autofitflag',autoacqflag);
autoguessflag = 1;
setappdata(0,'autoguessflag',autoguessflag);
autosavimgflag = 1;
setappdata(0,'autosavimgflag',autosavimgflag);
autosavfitflag = 1;
setappdata(0,'autosavfitflag',autosavfitflag);
acqexitflag = 0;
setappdata(0,'acqexitflag',acqexitflag)
%--------------------------------------------------------------------------
% Update handles structure
guidata(hObject, handles);

% UIWAIT makes SKHpixelfly wait for user response (see UIRESUME)
% uiwait(handles.figure1);


% --- Outputs from this function are returned to the command line.
function varargout = SKHpixelfly_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;


% --- Executes on button press in Acquire.
function Acquire_Callback(hObject, eventdata, handles)
% hObject    handle to Acquire (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


set(handles.Acquire,'Enable','off')
%Get params from the root--------------------------------------------------
exposure_time=getappdata(0,'exposure_time');
vbinselect=getappdata(0,'vbinselect');
hbinselect=getappdata(0,'hbinselect');
gainselect=getappdata(0,'gainselect');
modeselect=getappdata(0,'modeselect');
mode_index=getappdata(0,'mode_index');
num_of_images=getappdata(0,'num_of_images');
bit_pix=getappdata(0,'bit_pic');
ccd_width=getappdata(0,'ccd_width');
ccd_height=getappdata(0,'ccd_height');
image_width=getappdata(0,'image_width');
image_height=getappdata(0,'image_height');
imagesize=getappdata(0,'imagesize');
exposure_time=uint32(exposure_time);
setfitflag=getappdata(0,'setfitflag');
autofitflag=getappdata(0,'autofitflag');
autoacqflag=getappdata(0,'autoacqflag');
acqexitflag = 0;
setappdata(0,'acqexitflag',acqexitflag)
xc=str2double(get(handles.Xcin,'String'));
yc=str2double(get(handles.Ycin,'String'));
dx=str2double(get(handles.dX,'String'));
dy=str2double(get(handles.dY,'String'));
%--------------------------------------------------------------------------
while acqexitflag == 0
    
    savefolderdir=getappdata(0,'savefolderdir');
    savefolderdir2=getappdata(0,'savefolderdir2');
    savedate=getappdata(0,'savedate');
    saveno=getappdata(0,'saveno');
    
    if mode_index == 4 || mode_index == 2 || mode_index == 6
        %Allocate buffer-----------------------------------------------------------
        bufnr=-1;
        bufsize=ccd_width*ccd_height*2;
        [error_code, bufnr]=pfALLOCATE_BUFFER(handles.board_handle, bufnr, bufsize);
        %if error_code ~=0
        %    disp('memory allocating filed')
        %end
        handles.bufnr=bufnr;
        set(handles.mesg,'String','Allocating buffer for images...')
        
        [error_code, bufaddress]=pfMAP_BUFFER_EX(handles.board_handle, bufnr, bufsize);
        %if error_code ~=0
        %    disp('buffer mapping filed')
        %end
        handles.bufaddress=bufaddress;
        set(handles.mesg,'String','Mapping buffer...')
        
        %--------------------------------------------------------------------------
        %-------------------------------------------------------------------------
        error_code=pfSTART_CAMERA(handles.board_handle);
        %if error_code ~=0
        %    disp('Starting camera failed')
        %end
        set(handles.mesg,'String','Camera started...')
        
        error_code=pfADD_BUFFER_TO_LIST(handles.board_handle, handles.bufnr, ...
            imagesize, 0, 0);
        %if error_code ~=0
        %    disp('adding buffer to the list failed')
        %end
        set(handles.mesg,'String','Adding buffer to list...')
        
        error_code=pfTRIGGER_CAMERA(handles.board_handle);
        %if error_code ~=0
        %    disp('Triggering camera failed')
        %end
        set(handles.mesg,'String','Camera triggered...')
        
        [error_code, ima_bufnr]=pfWAIT_FOR_BUFFER(handles.board_handle, exposure_time+500, handles.bufnr);
        set(handles.mesg,'String','Waiting for buffer...')
        
        if error_code ~=0
            %disp(['Waiting for buffer failed, error_code is ',int2str(error_code)])
            error_code2=pfREMOVE_BUFFER_FROM_LIST(handles.board_handle,handles.bufnr);
            %if error_code2 ~=0
            %    disp('Removing buffer from list failed')
            %end
        end
        [error_code, result_image]=pfCOPY_BUFFER(handles.bufaddress, bit_pix, image_width, image_height);
        %if error_code ~=0
        %    disp('Copying buffer failed')
        %end
        set(handles.mesg,'String','Copying buffer...')
        
        imagestack=result_image';
        hax1=getappdata(0,'hax1');
        axes(hax1)
        colormap(gray)
        imagesc(imagestack)
        axis image;
        colorbar
        impixelinfo(hax1)
        Clim=get(hax1,'CLim');
        hMainGui=getappdata(0,'hMainGui');
        h=findobj(hMainGui,'Tag','colorbar_max');
        set(h,'String',num2str(Clim(2)));
        h=findobj(hMainGui,'Tag','colorbar_min');
        set(h,'String',num2str(Clim(1)));
        
        setappdata(0,'imagestack',imagestack)
        error_code = pfFREE_BUFFER(handles.board_handle, handles.bufnr);
        set(handles.mesg,'String','Buffer is freed')
        
        
        error_code = pfSTOP_CAMERA(handles.board_handle);
        %if error_code ~=0
        %    disp('Stopping camera failed')
        %end
        set(handles.mesg,'String','Camera Stopped. Single image is taken')
        set(handles.Acquire,'Enable','on')
        
    elseif mode_index == 1 || mode_index == 5
        %----create bufnr and bufaddress for allocating and mapping----------------
        %num_of_images = 3;
        imagestack=zeros(image_height,image_width,num_of_images,'uint16');
        for i = 1 : num_of_images
            bufnr=-1;
            if mode_index == 5
                bufsize = imagesize;
            else
                bufsize=ccd_width*ccd_height*2;
            end
            %imagesize
            %disp('allocating buffer');
            [error_code, bufnrs]=pfALLOCATE_BUFFER(handles.board_handle, bufnr, bufsize);
            %error_code
            %disp('mapping buffer');
            [error_code, bufaddress]=pfMAP_BUFFER_EX(handles.board_handle, bufnrs, bufsize);
            %error_code
            handles.bufnrs(i)=bufnrs;
            handles.bufaddress(i)=bufaddress;
            %disp('adding buffer to list');
            error_code=pfADD_BUFFER_TO_LIST(handles.board_handle, handles.bufnrs(i), ...
                imagesize, 0, 0);
        end;
        %disp('starting camera');
        error_code=pfSTART_CAMERA(handles.board_handle);
        for i = 1 : num_of_images
            acqexitflag = getappdata(0,'acqexitflag');
            deathflag = 1;
            if acqexitflag == 0
                set(handles.mesg,'String','Waiting for external trigger...')
                stopflag=0;
                setappdata(0,'stopflag',stopflag);
                %error_code=pfTRIGGER_CAMERA(handles.board_handle);
                while stopflag==0
                    % 	  disp('we are waiting');
                    [error_code, ima_bufnr]=pfWAIT_FOR_BUFFER(handles.board_handle,50+exposure_time, handles.bufnrs(i));
                    %         disp('we made it!');
                    if error_code ~= -2
                        if error_code == 0
                            deathflag = 0;
                            setappdata(0,'stopflag', 1);
                        else
                            fprintf('error during acquisition: %d\n',error_code);
                            setappdata(0,'stopflag', 1);
                            setappdata(0,'acqexitflag',1);
                        end
                    end
                    pause(0.001)
                    stopflag=getappdata(0,'stopflag');
                end
                %     disp('we even made it here');
            end
        end
        % disp('we really made it');
        if deathflag == 0
            for i = 1 : num_of_images
                if acqexitflag == 0
                    % 	  disp('attempt to copy buffer');
                    [error_code, result_image]=pfCOPY_BUFFER(handles.bufaddress(i), bit_pix, image_width, image_height);
                    imagestack(:,:,i)=result_image';
                    % 	  disp('survived');
                end
            end
            if acqexitflag == 0
                set(handles.mesg,'String','Imagestack is taken')
            end
        else
            set(handles.mesg,'String','Imagestack aborted/error');
        end
        for i = 1:num_of_images
            error_code = pfFREE_BUFFER(handles.board_handle, handles.bufnrs(i));
        end
        error_code = pfSTOP_CAMERA(handles.board_handle);
        
        %acqexitflag
        
        if acqexitflag == 0
            %ODimage=real(log(double(imagestack(:,:,3))./double(imagestack(:,:,2))));
            [ODimage,Img_light,Img_shadow] = ODimg1(imagestack);
            setappdata(0,'ODimage',ODimage)
            popmenustr= {'ODimage'; num2str((1 : num_of_images)')};
            set(handles.showframe,'String',popmenustr)
            setappdata(0,'imagestack',imagestack);
            
            defringflag = getappdata(0,'defringflag');
            if defringflag == 1
                rect2 = getappdata(0,'rect2');
                fileno_i = getappdata(0,'fileno_i');
                fileno_f = getappdata(0,'fileno_f');
                no_base = getappdata(0,'no_base');
                bgimg_stack = getappdata(0,'bgimg_stack');
                [Odimg_df, ~] = SK_defringer(Img_shadow(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),bgimg_stack,rect2);
                Odimg = zeros(size(Img_shadow,1),size(Img_shadow,2));
                Odimg(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)))= Odimg_df;
                
                setappdata(0,'ODimage',Odimg)
                
            elseif defringflag == 2
            elseif defringflag == 3
            end
            updateAxes1
            
            hax2=getappdata(0,'hax2');
            hax5=getappdata(0,'hax5');
            axes(hax2)
            imagesc(Img_shadow);
            axis off;
            axes(hax5)
            imagesc(Img_light);
            axis off;
        end
    end
    
    % henry addition
    saveno = getappdata(0, 'saveno');
    % end henry
    
    %if acqexitflag == 0
    if setfitflag ==1 && autofitflag == 1 && acqexitflag == 0
        hh=handles.fit;
        fit_Callback(hh,[],handles);
        % new added by henry in 2023
        curr = get(handles.fitdisplay,'Data');
        fitdata = getappdata(0,'fitdata');
        new = fitdata_conversion(fitdata, getappdata(0, 'imgtype'));
        new = cat(2, {getappdata(0, 'saveno')}, new);
        try 
            new = cat(1, new, curr);
        catch
            new = new;
        end
        set(handles.fitdisplay,'Data', new);
        % end henry addition
    end
    autosavimgflag=getappdata(0,'autosavimgflag');
    autosavfitflag=getappdata(0,'autosavfitflag');
    if deathflag == 0
    if autosavimgflag == 1 && autosavfitflag == 0
        savfilename=strcat(savefolderdir,'\',savedate,'_',saveno,'.mat');
        savfilename2=strcat(savefolderdir2,'\',savedate,'_',saveno,'.mat');
        save(savfilename,'imagestack')
        save(savfilename2,'imagestack')
        setappdata(0,'saveno',num2str(str2double(saveno)+1))
        set(handles.edit1,'String',['Imagestack saved to : ',savfilename])
        set(handles.imgnum,'String',num2str(str2num(saveno)+1))
    elseif autosavimgflag == 1 && autosavfitflag == 1
        savfilename=strcat(savefolderdir,'\',savedate,'_',saveno,'.mat');
        savfilename2=strcat(savefolderdir2,'\',savedate,'_',saveno,'.mat');
        fitdata=getappdata(0,'fitdata');
        save(savfilename,'imagestack','fitdata')
        save(savfilename2,'imagestack','fitdata')
        setappdata(0,'saveno',num2str(str2double(saveno)+1))
        set(handles.edit1,'String',['Imagestack and fitdata saved to : ',savfilename])
        set(handles.imgnum,'String',num2str(str2num(saveno)+1))
    elseif autosavimgflag == 0 && autosavfitflag == 1
        savfilename=strcat(savefolderdir,'\',savedate,'_',saveno,'.mat');
        savfilename2=strcat(savefolderdir2,'\',savedate,'_',saveno,'.mat');
        fitdata=getappdata(0,'fitdata');
        save(savfilename,'fitdata')
        save(savfilename2,'fitdata')
        setappdata(0,'saveno',num2str(str2double(saveno)+1))
        set(handles.edit1,'String',['Fitdata saved to : ',savfilename])
        set(handles.imgnum,'String',num2str(str2num(saveno)+1))
    else
    end
    end
    
    set(handles.Acquire,'Enable','on')
    
    guidata(hObject, handles);
    
    if autoacqflag == 1
        set(handles.Acquire,'Enable','off')
    else
        set(handles.Acquire,'Enable','on')
        setappdata(0,'acqexitflag',1)
    end
    %if autoacqflag == 1
    %    Acquire_Callback(handles.Acquire,[],handles);
    %end
    %else
end
Stop_Callback(handles.Stop,[],handles)
%end
clear imagestack ODimage
%rmappdata(0,'ODimage')
%rmappdata(0,'imagestack')

%if autoacqflag == 1
%    setappdata(0,'stopflag',0);
%    set(handles.autoacq,'value',1)
%    setappdata(0,'autoacqflag',1)
%    setappdata(0,'acqexitflag',0)
%    set(handles.Acquire,'Enable','off')
%    Acquire_Callback(handles.Acquire,[],handles);
%end

% --- Executes on button press in Stop.
function Stop_Callback(hObject, eventdata, handles)
% hObject    handle to Stop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
num_of_images=getappdata(0,'num_of_images');
%for i = 1 : num_of_images
    %error_code=pfREMOVE_BUFFER_FROM_LIST(handles.board_handle, handles.bufnrs(i), ...
    %    imagesize, 0, 0);
    %error_code = pfFREE_BUFFER(handles.board_handle, handles.bufnrs(i));
    %error_code=pfSTOP_CAMERA(handles.board_handle);
%end;
set(handles.mesg,'String','image acquisition stopped')
setappdata(0,'stopflag',1);
% Commented out by Henry
% set(handles.autoacq,'value',0)
% setappdata(0,'autoacqflag',0)
setappdata(0,'acqexitflag',1)
set(handles.Acquire,'Enable','on')
guidata(hObject,handles)

% --- Executes on button press in Loadimg.
function Loadimg_Callback(hObject, eventdata, handles)
clc
if isempty(getappdata(0,'PName'))
    foldername=datestr(now,'yyyymmdd');%datestr(now,'yyyymmdd');
    folderdir=strcat('D:\LiCs_Data\Data\',foldername);
else
    pathname = getappdata(0,'PName');
    folderdir=pathname;
end
[FileName,PathName,FilterIndex]=uigetfile(folderdir);
if isequal(PathName,0)
    PathName = strcat('D:\LiCs_Data\Data\',datestr(now,'yyyymmdd'),'\');
    setappdata(0,'PName',folderdir);
else
    setappdata(0,'PName',PathName);
end
if FileName > 0
load([PathName FileName],'imagestack')
[height width]=size(imagestack(:,:,1));
setappdata(0,'imagestack',imagestack)
hMainGui=getappdata(0,'hMainGui');
%set(handles.Xcin,'String',num2str((width+1)/2));
%set(handles.Ycin,'String',num2str((height+1)/2));
%set(handles.dX,'String',num2str(width));
%set(handles.dY,'String',num2str(height));
if not(isempty(imagestack))
    if size(imagestack,3) > 1
        set(handles.showframe,'Enable','on')
        num_of_images = size(imagestack,3);
        setappdata(0,'num_of_images',num_of_images)
        ODimage=ODimg1(imagestack);
        setappdata(0,'ODimage',ODimage)
        updateAxes1
        popmenustr= {'ODimage'; num2str((1 : num_of_images)')};
        set(handles.showframe,'String',popmenustr)
    elseif size(imagestack,3) == 1
        set(handles.showframe,'String',num2str(int8(1)))
        hax1=getappdata(0,'hax1');
        axes(hax1)
        colormap(gray)
        imagesc(imagestack)
        axis image;
        colorbar
        %impixelinfo(hax1)
        Clim=get(hax1,'CLim');
        hMainGui=getappdata(0,'hMainGui');
        h=findobj(hMainGui,'Tag','colorbar_max');
        set(h,'String',num2str(Clim(2)));
        h=findobj(hMainGui,'Tag','colorbar_min');
        set(h,'String',num2str(Clim(1)));
        setappdata(0,'imagestack',imagestack)
        
    end
    set(handles.edit1,'String',['Load image : ',PathName, FileName])
else
    set(handles.mesg,'String','No imagestack in the loaded mat file')
end
end


function edit1_Callback(hObject, eventdata, handles)
% hObject    handle to edit1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of edit1 as text
%        str2double(get(hObject,'String')) returns contents of edit1 as a double


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



function Xcin_Callback(hObject, eventdata, handles)
% hObject    handle to Xcin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Xcin as text
%        str2double(get(hObject,'String')) returns contents of Xcin as a double
updateAxes1

% --- Executes during object creation, after setting all properties.
function Xcin_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Xcin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function Ycin_Callback(hObject, eventdata, handles)
% hObject    handle to Ycin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of Ycin as text
%        str2double(get(hObject,'String')) returns contents of Ycin as a double
updateAxes1

% --- Executes during object creation, after setting all properties.
function Ycin_CreateFcn(hObject, eventdata, handles)
% hObject    handle to Ycin (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function dX_Callback(hObject, eventdata, handles)
% hObject    handle to dX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of dX as text
%        str2double(get(hObject,'String')) returns contents of dX as a double
updateAxes1

% --- Executes during object creation, after setting all properties.
function dX_CreateFcn(hObject, eventdata, handles)
% hObject    handle to dX (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function dY_Callback(hObject, eventdata, handles)
% hObject    handle to dY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of dY as text
%        str2double(get(hObject,'String')) returns contents of dY as a double
updateAxes1

% --- Executes during object creation, after setting all properties.
function dY_CreateFcn(hObject, eventdata, handles)
% hObject    handle to dY (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

% --- Executes on button press in camerasettings.
function camerasettings_Callback(hObject, eventdata, handles)
% hObject    handle to camerasettings (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
camsettings

% --- Executes on button press in savesettings.
function savesettings_Callback(hObject, eventdata, handles)
% hObject    handle to savesettings (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
autosave

% --- Executes on button press in fit.
function fit_Callback(hObject, eventdata, handles)
% hObject    handle to fit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
autoguessflag=getappdata(0,'autoguessflag');
setfitflag=getappdata(0,'setfitflag');
imagestack=getappdata(0,'imagestack');
ODimage=getappdata(0,'ODimage');
hax2=getappdata(0,'hax2');
hax5=getappdata(0,'hax5');
xc=str2double(get(handles.Xcin,'String'));
yc=str2double(get(handles.Ycin,'String'));
dx=str2double(get(handles.dX,'String'));
dy=str2double(get(handles.dY,'String'));
if isempty(imagestack) == 0
    if setfitflag == 0
        fitsettings
    else
        fitmodel=getappdata(0,'fitmodel');
        if fitmodel ==1
            fitframeno=get(handles.showframe,'value');
            if autoguessflag == 0
                load('savedinig1D.mat')
            else
                saveinig1D=autoguess(ODimage,imagestack,fitframeno,xc,yc,dx,dy);
            end
            [fittracex fittracey tracex tracey fitparx fitpary]...
                =fitgaussian1D(ODimage,imagestack,saveinig1D,fitframeno,xc,yc,dx,dy);
            axes(hax2)
            plot(fittracex,'r','LineWidth',2)
            hold on
            plot(tracex,'LineWidth',2)
            hold off
            set(hax2,'Xlim',[1 size(imagestack(round(yc-((dy-1)/2)):...
                round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno),2)])
            set(handles.showaxes2,'Value',1)
            
            axes(hax5)
            plot(fittracey,'r','LineWidth',2)
            hold on
            plot(tracey,'LineWidth',2)
            hold off
            set(hax5,'Xlim',[1 size(imagestack(round(yc-((dy-1)/2))...
                :round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno),1)])
            set(handles.showaxes5,'Value',2)
            
            % henry modified 
            fitdata={fitparx.fitval,fitpary.fitval; fitparx.inival,fitpary.inival}';
            setappdata(0,'fitdata',fitdata)
            % end henry modification
            
            hMainGui=getappdata(0,'hMainGui');
            showaxes2=findobj(hMainGui,'Tag','showaxes2');
            set(showaxes2,'String',{'fit_tracex';'fit_tracey'})
            showaxes5=findobj(hMainGui,'Tag','showaxes5');
            set(showaxes5,'String',{'fit_tracex';'fit_tracey'})
            
            handles.fitdata1=tracex;
            handles.fitdata2=tracey;
            handles.fitresult1=fittracex;
            handles.fitresult2=fittracey;
            handles.fitpars=[fitparx fitpary];
            guidata(hObject,handles)
            
            saveinig1D.nx=fitparx(1).fitval;
            saveinig1D.wx=fitparx(2).fitval;
            saveinig1D.xc=fitparx(3).fitval;
            saveinig1D.bg=(fitparx(4).fitval+fitpary(4).fitval)/2;
            saveinig1D.ny=fitpary(1).fitval;
            saveinig1D.wy=fitpary(2).fitval;
            saveinig1D.yc=fitpary(3).fitval;
            save('sk','saveinig1D')
        elseif fitmodel ==2
        elseif fitmodel ==3
        elseif fitmodel ==4
        elseif fitmodel ==5
        elseif fitmodel ==6
        end
    end
else
    set(handles.mesg,'String','There is no data!!')
end

% --- Executes on button press in fitsettings.
function fitsettings_Callback(hObject, eventdata, handles)
% hObject    handle to fitsettings (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
fitsettings

% --- Executes on button press in quit.
function quit_Callback(hObject, eventdata, handles)
% hObject    handle to quit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
CloseCamera(handles)
close SKHpixelfly


function CloseCamera(handles)
error_code = pfSTOP_CAMERA(handles.board_handle);
if error_code ~= 0
     error('....quit_Callback: pfSTOP_CAMERA error!')
end
error_code = pfCLOSEBOARD(handles.board_handle);
if error_code ~= 0
    error('....disconnected error!');
end
if (libisloaded('PCO_PF_SDK'))
 unloadlibrary('PCO_PF_SDK');
end
if (libisloaded('PCO_CNV_SDK'))
  calllib('PCO_CNV_SDK','DELETE_COLORLUT_EX',handles.colorlutptr);
  unloadlibrary('PCO_CNV_SDK');
end
clear all

function updateAxes1
hax1=getappdata(0,'hax1');
hMainGui=getappdata(0,'hMainGui');
h=findobj(hMainGui,'Tag','showframe');
hxcin=findobj(hMainGui,'Tag','Xcin');
hycin=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');
frameno=round(get(h,'Value'));
xc=str2double(get(hxcin,'String'));
yc=str2double(get(hycin,'String'));
dx=str2double(get(hdx,'String'));
dy=str2double(get(hdy,'String'));
imagestack=getappdata(0,'imagestack');
ODimage=getappdata(0,'ODimage');
hcmax=findobj(hMainGui,'Tag','colorbar_max');
cmaxstr=get(hcmax,'String');
cmaxval = str2num(cmaxstr);
%isstr(cmaxstr)
hcmin=findobj(hMainGui,'Tag','colorbar_min');
cminstr=get(hcmin,'String');
cminval = str2num(cminstr);
%isstr(cminstr)

%my_sz_my_my = size(imagestack);
%fprintf('sz_sz:%d\n', numel(my_sz_my_my));
%fprintf('frameno:%d sz1:%d sz2:%d\n', frameno, my_sz_my_my(1), my_sz_my_my(2));

if frameno == 1
    imageshow=ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)));
else
    imageshow=imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),frameno-1);
end
axes(hax1)
imagesc(imageshow)
axis image
hax1bar=colorbar;
colormap(jet)
impixelinfo(hax1)
%Clim=get(hax1,'CLim');
set(hax1,'CLim',[cminval cmaxval])
hMainGui=getappdata(0,'hMainGui');
%set(hcmax,'String',num2str(1));
%set(hcmax,'String',num2str(Clim(2)));
%set(hcmin,'String',num2str(0));
%set(hcmin,'String',num2str(Clim(1)));


% --- Executes on selection change in showframe.
function showframe_Callback(hObject, eventdata, handles)
% hObject    handle to showframe (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
mode_index=getappdata(0,'mode_index');
if mode_index == 1 || mode_index == 5
    updateAxes1
    hax1=getappdata(0,'hax1');
    Clim=get(hax1,'CLim');
    hMainGui=getappdata(0,'hMainGui');
    h=findobj(hMainGui,'Tag','colorbar_max');
    set(h,'String',num2str(Clim(2)));
    h=findobj(hMainGui,'Tag','colorbar_min');
    set(h,'String',num2str(Clim(1)));
else
end


% --- Executes during object creation, after setting all properties.
function showframe_CreateFcn(hObject, eventdata, handles)
% hObject    handle to showframe (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

function update_popupmenu1
hMainGui=getappdata(0,'hMainGui');
num_of_images=getappdata(0,'num_of_images');
frame=1:num_of_images;
h=findobj(hMainGui,'Tag','showframe');
set(h,'String',num2str(frame'));



function colorbar_min_Callback(hObject, eventdata, handles)
% hObject    handle to colorbar_min (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of colorbar_min as text
%        str2double(get(hObject,'String')) returns contents of colorbar_min as a double
colormin=str2double(get(hObject,'String'));
hax1=getappdata(0,'hax1');
Clim_old=get(hax1,'CLim');
Clim=[colormin Clim_old(2)];
set(hax1,'CLim',Clim)


% --- Executes during object creation, after setting all properties.
function colorbar_min_CreateFcn(hObject, eventdata, handles)
% hObject    handle to colorbar_min (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end



function colorbar_max_Callback(hObject, eventdata, handles)
% hObject    handle to colorbar_max (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of colorbar_max as text
%        str2double(get(hObject,'String')) returns contents of colorbar_max as a double
colormax=str2double(get(hObject,'String'));
hax1=getappdata(0,'hax1');
Clim_old=get(hax1,'CLim');
Clim=[Clim_old(1) colormax];
set(hax1,'CLim',Clim)

% --- Executes during object creation, after setting all properties.
function colorbar_max_CreateFcn(hObject, eventdata, handles)
% hObject    handle to colorbar_max (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in saveimg.
function saveimg_Callback(hObject, eventdata, handles)
% hObject    handle to saveimg (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
savefolderdir=getappdata(0,'savefolderdir');
savefolderdir2=getappdata(0,'savefolderdir2');
%savedate=getappdata(0,'savedate');
%saveno=getappdata(0,'saveno');
imagestack = getappdata(0,'imagestack');
savfilename=strcat(savefolderdir,'\','image.mat');
uisave('imagestack',savfilename)

% --- Executes on button press in pushbutton12.
function pushbutton12_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton12 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
image_width=getappdata(0,'image_width');
image_height=getappdata(0,'image_height');
hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

set(hxc,'String',num2str((double(image_width)+1)/2));
set(hyc,'String',num2str((double(image_height)+1)/2));
set(hdx,'String',num2str(double(image_width)));
set(hdy,'String',num2str(double(image_height)));

hax1=getappdata(0,'hax1');
hMainGui=getappdata(0,'hMainGui');
h=findobj(hMainGui,'Tag','showframe');
frameno=round(get(h,'Value'));
imagestack=getappdata(0,'imagestack');
imageshow=imagestack(:,:,frameno);
axes(hax1)
image(imageshow,'CDataMapping','scaled')
axis image
hax1bar=colorbar;


% --- Executes on selection change in showaxes2.
function showaxes2_Callback(hObject, eventdata, handles)
% hObject    handle to showaxes2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns showaxes2 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from showaxes2
hax2=getappdata(0,'hax2');
imagestack=getappdata(0,'imagestack');
fitmodel=getappdata(0,'fitmodel');
selectval=get(hObject,'Value');
fitframeno=1;
axes(hax2)
if fitmodel == 1
    if selectval == 1
        plot(handles.fitresult1,'r','LineWidth',2)
        hold on
        plot(handles.fitdata1,'--')
        hold off
        set(hax2,'Xlim',[1 size(imagestack(:,:,fitframeno),2)])
        hidden off
    elseif selectval == 2
        plot(handles.fitresult2,'r','LineWidth',2)
        hold on
        plot(handles.fitdata2,'--')
        hold off
        set(hax2,'Xlim',[1 size(imagestack(:,:,fitframeno),1)])
        hidden off
    end
elseif fitmodel == 2
elseif fitmodel == 3
elseif fitmodel == 4
elseif fitmodel == 5
elseif fitmodel == 6
end
    

% --- Executes on selection change in showaxes5.
function showaxes5_Callback(hObject, eventdata, handles)
% hObject    handle to showaxes5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns showaxes5 contents as cell array
%        contents{get(hObject,'Value')} returns selected item from showaxes5
hax5=getappdata(0,'hax5');
imagestack=getappdata(0,'imagestack');
fitmodel=getappdata(0,'fitmodel');
selectval=get(hObject,'Value');
fitframeno=1;
axes(hax5)
if fitmodel == 1
    if selectval == 1
        plot(handles.fitresult1,'r')
        hold on
        plot(handles.fitdata1)
        hold off
        set(hax5,'Xlim',[1 size(imagestack(:,:,fitframeno),2)])
    elseif selectval == 2
        plot(handles.fitresult2,'r')
        hold on
        plot(handles.fitdata2)
        hold off
        set(hax5,'Xlim',[1 size(imagestack(:,:,fitframeno),1)])        
    end
elseif fitmodel == 2
elseif fitmodel == 3
elseif fitmodel == 4
elseif fitmodel == 5
elseif fitmodel == 6
end

% --- Executes during object creation, after setting all properties.
function showaxes2_CreateFcn(hObject, eventdata, handles)
% hObject    handle to showaxes2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes during object creation, after setting all properties.
function showaxes5_CreateFcn(hObject, eventdata, handles)
% hObject    handle to showaxes5 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in autofit.
function autofit_Callback(hObject, eventdata, handles)
% hObject    handle to autofit (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of autofit
autofitflag = get(hObject,'Value');
setappdata(0,'autofitflag',autofitflag)
if autofitflag == 1
    fitsettings
end


% --- Executes on button press in autoacq.
function autoacq_Callback(hObject, eventdata, handles)
% hObject    handle to autoacq (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of autoacq
autoacqflag = get(hObject,'Value');
setappdata(0,'autoacqflag',autoacqflag);

% --------------------------------------------------------------------
function uitoggletool6_OnCallback(hObject, eventdata, handles)
% hObject    handle to uitoggletool6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
w = 0;
hax1=getappdata(0,'hax1');
hax2=getappdata(0,'hax2');
hax5=getappdata(0,'hax5');
imagestack=getappdata(0,'imagestack');
ODimage=getappdata(0,'ODimage');
xlimit=get(hax1,'Xlim');
ylimit=get(hax1,'Ylim');
l1=line([600 600],[1 1024],'Visible','off');
l2=line([1 1024],[600 600],'Visible','off');
set(handles.showframe,'Enable','off')
showframeval=get(handles.showframe,'Value');
showframestr=get(handles.showframe,'String');
frameno=round(str2double(showframestr(showframeval)));
 while w == 0
     w = waitforbuttonpress;
     if w == 1 
         set(hObject,'State','off')
         set(handles.showframe,'Enable','on')
     else
         a=get(gca,'CurrentPoint');
         if isempty(a)
             a=[0,0];
         end
         point=round(a(1,1:2));
         if point(1) >= xlimit(1) && point(1) <= xlimit(2) && point(2) >= ylimit(1) && point(2) <= ylimit(2)
             set(l1,'XData',[point(1) point(1)],'YData',[0 3000],'Visible','on');
             set(l2,'XData',[0 3000],'YData',[point(2) point(2)],'Visible','on');

            if strcmp(showframestr(showframeval),'ODimage')
                axes(hax2)
                plot(1:length(ODimage(:,point(1))),ODimage(:,point(1)))
                set(handles.showaxes2,'String','ytrace')
                set(hax2,'Xlim',ylimit)
                axes(hax5)
                plot(1:length(ODimage(point(2),:)),ODimage(point(2),:))
                set(handles.showaxes5,'String','xtrace')
                set(hax5,'Xlim',xlimit)
            else
                axes(hax2)
                plot(1:length(imagestack(:,point(1),frameno)),...
                    imagestack(:,point(1),frameno))
                set(handles.showaxes2,'String','ytrace')
                set(hax2,'Xlim',ylimit)
                axes(hax5)
                plot(1:length(imagestack(point(2),:,frameno)),...
                    imagestack(point(2),:,frameno))
                set(handles.showaxes5,'String','xtrace')
                set(hax5,'Xlim',xlimit)
            end
         end
     end
 end
delete(l1)
delete(l2)
set(gcf,'CurrentAxes',hax1);
% while w == 0
%     [X Y]=SKginput(1);
%     hax1=getappdata(0,'hax1');
%     get(hax1)
%     %annotation('line',[0.5 0.5],[0 1])
%     if isempty(X)
%         w = 1;
%         set(hObject,'State','off')
%     end
% end
%create another figure has the same size
%if w == 1
%    set(hObject,'State','off')
%end

% --------------------------------------------------------------------
function uitoggletool6_ClickedCallback(hObject, eventdata, handles)
% hObject    handle to uitoggletool6 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
%lineh=findobj(hax1,'Type','line');
%delete(lineh)


% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

delete(hObject);


% --- Executes on button press in pushbutton13.
function pushbutton13_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton13 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)



function imgnum_Callback(hObject, eventdata, handles)
% hObject    handle to imgnum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
saveno = get(hObject,'String');
setappdata(0,'saveno',saveno);
% Hints: get(hObject,'String') returns contents of imgnum as text
%        str2double(get(hObject,'String')) returns contents of imgnum as a double


% --- Executes during object creation, after setting all properties.
function imgnum_CreateFcn(hObject, eventdata, handles)
% hObject    handle to imgnum (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
set(hObject,'String','0');
setappdata(0,'saveno','0');
% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on selection change in imgtype.
function imgtype_Callback(hObject, eventdata, handles)
% hObject    handle to imgtype (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
imgtype = get(hObject,'Value');
setappdata(0,'imgtype',imgtype);
% Hints: contents = cellstr(get(hObject,'String')) returns imgtype contents as cell array
%        contents{get(hObject,'Value')} returns selected item from imgtype


% --- Executes during object creation, after setting all properties.
function imgtype_CreateFcn(hObject, eventdata, handles)
% hObject    handle to imgtype (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called
setappdata(0,'imgtype',1);
% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end


% --- Executes on button press in OTOP.
function OTOP_Callback(hObject, eventdata, handles)
% hObject    handle to OTOP (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

set(hxc,'String',num2str(950));
set(hyc,'String',num2str(750));
set(hdx,'String',num2str(500));
set(hdy,'String',num2str(500));

updateAxes1


% --- Executes on button press in BEC.
function BEC_Callback(hObject, eventdata, handles)
% hObject    handle to BEC (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

set(hxc,'String',num2str(950));
set(hyc,'String',num2str(813));
set(hdx,'String',num2str(50));
set(hdy,'String',num2str(50));

updateAxes1


% --- Executes on button press in LiIS.
function LiIS_Callback(hObject, eventdata, handles)
% hObject    handle to LiIS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

set(hxc,'String',num2str(950));
set(hyc,'String',num2str(248));
set(hdx,'String',num2str(70));
set(hdy,'String',num2str(20));

updateAxes1


% --- Executes on button press in FieldCal.
function FieldCal_Callback(hObject, eventdata, handles)
% hObject    handle to FieldCal (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
hMainGui=getappdata(0,'hMainGui');
hxc=findobj(hMainGui,'Tag','Xcin');
hyc=findobj(hMainGui,'Tag','Ycin');
hdx=findobj(hMainGui,'Tag','dX');
hdy=findobj(hMainGui,'Tag','dY');

set(hxc,'String',num2str(950));
set(hyc,'String',num2str(248));
set(hdx,'String',num2str(150));
set(hdy,'String',num2str(20));

updateAxes1


function vals = fitdata_conversion(fitdata, image_type)
fitdata = [fitdata{:,1}];
vals = cell(1, 4);
pix = 7.72; % in microns
if image_type == 1
    lambda = 852; % in nm
elseif image_type == 2
    lambda = 671;
end

vals{1} = 1e6*(pix^2)/(3.*(lambda^2)/(2*pi))*sqrt(2*pi)*fitdata(1)*fitdata(2);
vals{2} = 1e6*(pix^2)/(3.*(lambda^2)/(2*pi))*sqrt(2*pi)*fitdata(5)*fitdata(6);
vals{3} = pix*fitdata(2);
vals{4} = pix*fitdata(6);

for i = 1:4
    if vals{i} > 1e6
        vals{i} = sprintf('%.3gM', vals{i}/1e6);
    elseif vals{i} > 1e3
        vals{i} = sprintf('%.3gk', vals{i}/1e3);
    else
        vals{i} = sprintf('%.3g', vals{i});
    end
end


% --- Executes during object creation, after setting all properties.
function figure1_CreateFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called


% --- Executes on button press in cleartbl.
function cleartbl_Callback(hObject, eventdata, handles)
% hObject    handle to cleartbl (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
set(handles.fitdisplay,'Data',cell(4, 5));
