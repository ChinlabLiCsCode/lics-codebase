%% GUI to use on the V imaging computer to autosave Andor camera images and read them on the analysis computer.
% The logic will be similar to the old solistomat code but more convenient.
% Changes can be made if the pixel fly controlling PCI card is moved from
% the old imaging computer to the new one. Right now, it is configured for full-frame read out, but it may need to be changed when
% we switch over to fast kinetics mode. 20190702
% -Krutik

function andor_img_viewer_v8
%% parameters %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

umperpix = 0.78; % calibration of pixel size
Isat_cs = 355; % calibration 2023-09-01 5 microsecond
Isat_li = 125;   % calibration 2023-03-21 5 microsecond
sigma_cs = (3*(852e-3)^2./(2*pi)); % sigma in um^2
sigma_li = (3*(671e-3)^2./(2*pi)); % sigma in um^2
aa = load('m25DkCount'); 
Dk_Bkg140 = aa.avg_bkg';
aa = load('m25DkCount180'); 
Dk_Bkg180 = aa.avg_bkg'; 
%Dk_Bkg = zeros(1024, 1024);

% Fast Kinetics Parameters
sub_area_width = 1024;
sub_area_height = 140; % this might change depending on mode! add a button! 

% Imaging order
csfirst = false; % this might change depending on the mode! add a button!

% Default view
csimgview = [300, 500, 45, 90, -0.1, 11];
liimgview = [150, 700, 20, 110, -0.1, 2];
csimgROI = [320, 480, 55, 70];
liimgROI = [250, 600, 40, 90];

%% Initialize %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Open a figure
f = figure('Position',[460,100,1280,800],'Name','Andor Image Viewer');

% Instantiate axes
lia  = axes(f, 'Units','Pixels','Position',[70,650,630,100]);
liax = axes(f, 'Units','Pixels','Position',[70,450,300,150]);
liay = axes(f, 'Units','Pixels','Position',[430,450,270,150]);

csa  = axes(f, 'Units','Pixels','Position',[70,250,630,100]);
csax = axes(f, 'Units','Pixels','Position',[70,50,300,150]);
csay = axes(f, 'Units','Pixels','Position',[430,50,270,150]);

% Initialize a bunch of variables so they have global scope
Li_OD = [];
Cs_OD = [];
Cs_No_Atoms = []; 
Cs_Atoms = [];
Li_No_Atoms = []; 
Li_Atoms = [];

liimgselectval = 1;
% lifitselectval = 3;
liPlotData = [];
csimgselectval = 2;
csPlotData = [];
% csfitselectval = 2;
img = [];
imgfile = 'C:\Data\andorimage.tif';
imgstcknum = 1;
imagestack = [];
localdirfmt = 'C:\\Data\\%1$4.4i\\%2$2.2i\\%1$4.4i%2$2.2i%3$2.2i';
remotedirfmt = '\\\\LiCs_NAS\\Data_Backup\\V_Images\\Data\\%1$4.4i\\%2$2.2i\\%1$4.4i%2$2.2i%3$2.2i';
filefmt = '\\%1$4.4i%2$2.2i%3$2.2i_%4$i.mat';
aslabelfmt = 'Saved as %1$4.4i%2$2.2i%3$2.2i_%4$i.mat';
asbutton_state = false;
logfit_flag = true;
dofitsbutton_state = false;
fitdata = struct();

%% Make the Li and Cs input fields %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Top image
% Choose which of the images in the imagestack to view, or the OD.
liimglbl = uicontrol(f,'Style','text','String','Img type:');
liimglbl.Position = [740 750 55 15];
liimgselector = uicontrol(f,'Style','popupmenu');
liimgselector.String = {'Li OD', 'Cs OD', 'Li Atoms', 'Cs Atoms',...
    'No Li Atoms', 'No Cs Atoms'};
liimgselector.Position = [740 720 100 20];
liimgselector.Callback = @updatePlots;
% color bar lower and upper range boxes
licbarl = uicontrol(f,'Style','edit');
licbarl.String = liimgview(5);
licbarl.Position = [740 690 40 26];
licbarl.Callback = @updatePlots;
licbaru = uicontrol(f,'Style','edit');
licbaru.String = liimgview(6);
licbaru.Position = [790 690 40 26];
licbaru.Callback = @updatePlots;
liclbl = uicontrol(f,'Style','text','String','C:');
liclbl.Position = [720 690 15 15];

% Li View section
liviewfieldlbl = uicontrol(f,'Style','text','String','View:',...
    'HorizontalAlignment','left');
liviewfieldlbl.Position = [740 660 100 15];
% Li View x lower and upper range boxes
liviewfieldxl = uicontrol(f,'Style','edit');
liviewfieldxl.String = liimgview(1);
liviewfieldxl.Position = [740 630 40 26];
liviewfieldxl.Callback = @updatePlots;
liviewfieldxu = uicontrol(f,'Style','edit');
liviewfieldxu.String = liimgview(2);
liviewfieldxu.Position = [790 630 40 26];
liviewfieldxu.Callback = @updatePlots;
liviewxlbl = uicontrol(f,'Style','text','String','X:');
liviewxlbl.Position = [720 630 15 15];
% View y lower and upper range boxes
liviewfieldyl = uicontrol(f,'Style','edit');
liviewfieldyl.String = liimgview(3);
liviewfieldyl.Position = [740 600 40 26];
liviewfieldyl.Callback = @updatePlots;
liviewfieldyu = uicontrol(f,'Style','edit');
liviewfieldyu.String = liimgview(4);
liviewfieldyu.Position = [790 600 40 26];
liviewfieldyu.Callback = @updatePlots;
liviewylbl = uicontrol(f,'Style','text','String','Y:');
liviewylbl.Position = [720 600 15 15];

% Li ROI section
liROIfieldlbl = uicontrol(f,'Style','text','String','ROI:',...
    'HorizontalAlignment','left');
liROIfieldlbl.Position = [740 570 100 15];
% ROI x lower and upper range boxes
liROIfieldxl = uicontrol(f,'Style','edit');
liROIfieldxl.String = liimgROI(1);
liROIfieldxl.Position = [740 540 40 26];
liROIfieldxl.Callback = @updatePlots;
liROIfieldxu = uicontrol(f,'Style','edit');
liROIfieldxu.String = liimgROI(2);
liROIfieldxu.Position = [790 540 40 26];
liROIfieldxu.Callback = @updatePlots;
lixlbl = uicontrol(f,'Style','text','String','X:');
lixlbl.Position = [720 540 15 15];
% ROI y lower and upper range boxes
liROIfieldyl = uicontrol(f,'Style','edit');
liROIfieldyl.String = liimgROI(3);
liROIfieldyl.Position = [740 510 40 26];
liROIfieldyl.Callback = @updatePlots;
liROIfieldyu = uicontrol(f,'Style','edit');
liROIfieldyu.String = liimgROI(4);
liROIfieldyu.Position = [790 510 40 26];
liROIfieldyu.Callback = @updatePlots;
liylbl = uicontrol(f,'Style','text','String','Y:');
liylbl.Position = [720 510 15 15];
% Li ROI lock button
liROIlockbox = uicontrol(f,'Style','togglebutton','String', 'Lock?');
liROIlockbox.Position = [740 480 50 15];
liROIlockbox.Callback = @updatePlots;

% Bottom image
% Choose which of the images in the imagestack to view, or the OD.
csimglbl = uicontrol(f,'Style','text','String','Img type:');
csimglbl.Position = [740 350 55 15];
csimgselector = uicontrol(f,'Style','popupmenu');
csimgselector.String = {'Li OD', 'Cs OD', 'Li Atoms', 'Cs Atoms',...
    'No Li Atoms', 'No Cs Atoms'};
csimgselector.Position = [740 320 100 20 ];
csimgselector.Callback=@updatePlots;
csimgselector.Value = 2;
% color bar lower and upper range boxes
cscbarl = uicontrol(f,'Style','edit');
cscbarl.String = csimgview(5);
cscbarl.Position = [740 290 40 26];
cscbarl.Callback = @updatePlots;
cscbaru = uicontrol(f,'Style','edit');
cscbaru.String = csimgview(6);
cscbaru.Position = [790 290 40 26];
cscbaru.Callback = @updatePlots;
csclbl = uicontrol(f,'Style','text','String','C:');
csclbl.Position = [720 290 15 15];

% Cs View section
csviewfieldlbl = uicontrol(f,'Style','text','String','View:',...
    'HorizontalAlignment','left');
csviewfieldlbl.Position = [740 260 100 15];
% Cs View x lower and upper range boxes
csviewfieldxl = uicontrol(f,'Style','edit');
csviewfieldxl.String = csimgview(1);
csviewfieldxl.Position = [740 230 40 26];
csviewfieldxl.Callback = @updatePlots;
csviewfieldxu = uicontrol(f,'Style','edit');
csviewfieldxu.String = csimgview(2);
csviewfieldxu.Position = [790 230 40 26];
csviewfieldxu.Callback = @updatePlots;
csviewxlbl = uicontrol(f,'Style','text','String','X:');
csviewxlbl.Position = [720 230 15 15];
% y lower and upper range boxes
csviewfieldyl = uicontrol(f,'Style','edit');
csviewfieldyl.String = csimgview(3);
csviewfieldyl.Position = [740 200 40 26];
csviewfieldyl.Callback = @updatePlots;
csviewfieldyu = uicontrol(f,'Style','edit');
csviewfieldyu.String = csimgview(4);
csviewfieldyu.Position = [790 200 40 26];
csviewfieldyu.Callback = @updatePlots;
csviewylbl = uicontrol(f,'Style','text','String','Y:');
csviewylbl.Position = [720 200 15 15];
% Cs View lock button
csviewlockbox = uicontrol(f,'Style','togglebutton','String', 'Lock?', 'Value', false);
csviewlockbox.Position = [740 170 50 15];
csviewlockbox.Callback = @updatePlots;

% Cs ROI section
csROIfieldlbl = uicontrol(f,'Style','text','String','ROI:',...
    'HorizontalAlignment','left');
csROIfieldlbl.Position = [740 140 100 15];
% Cs ROI x lower and upper range boxes
csROIfieldxl = uicontrol(f,'Style','edit');
csROIfieldxl.String = csimgROI(1);
csROIfieldxl.Position = [740 110 40 26];
csROIfieldxl.Callback = @updatePlots;
csROIfieldxu = uicontrol(f,'Style','edit');
csROIfieldxu.String = csimgROI(2);
csROIfieldxu.Position = [790 110 40 26];
csROIfieldxu.Callback = @updatePlots;
csROIxlbl = uicontrol(f,'Style','text','String','X:');
csROIxlbl.Position = [720 110 15 15];
% y lower and upper range boxes
csROIfieldyl = uicontrol(f,'Style','edit');
csROIfieldyl.String = csimgROI(3);
csROIfieldyl.Position = [740 80 40 26];
csROIfieldyl.Callback = @updatePlots;
csROIfieldyu = uicontrol(f,'Style','edit');
csROIfieldyu.String = csimgROI(4);
csROIfieldyu.Position = [790 80 40 26];
csROIfieldyu.Callback = @updatePlots;
csROIylbl = uicontrol(f,'Style','text','String','Y:');
csROIylbl.Position = [720 80 15 15];
% Cs ROI lock button
csROIlockbox = uicontrol(f,'Style','togglebutton','String', 'Lock?', 'Value', false);
csROIlockbox.Position = [740 50 50 15];
csROIlockbox.Callback = @updatePlots;

%% General column %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Path label
dirlbl = uicontrol(f,'Style','text','String','Loaded image...');
dirlbl.Position = [860 740 400 15];
dirlbl.HorizontalAlignment = 'left';
dirlbl.String = imgfile;

% Make a button to load an imagestack for viewing by browsing to it
loadButton = uicontrol(f,'Style','togglebutton','String','Load Image');
loadButton.Position = [860 700 80 26];
loadButton.Callback = @loadButtonHit;

% Specify location of the Andor .tif file that is being written to to load
% and save as matlab files
filepathbutton = uicontrol(f,'Style','togglebutton','String','Choose .tif');
filepathbutton.Position = [860 670 80 26 ];
filepathbutton.Callback = @filepathEnter;

% Toggle acquiring new data on or off
acquirebutton = uicontrol(f,'Style','togglebutton','String','Acquire');
acquirebutton.Position = [950 700 80 26 ];
acquirebutton.Callback = @acquirebuttonhit;

% Toggle autosave on or off.
asbutton = uicontrol(f,'Style','togglebutton','String','Autosave');
asbutton.Position = [950 670 80 26];
asbutton.Callback = @asbuttonhit;

% Toggle units from px to um
unitbutton = uicontrol(f,'Style','togglebutton','String','px/um');
unitbutton.Position = [1040 700 80 26 ];
unitbutton.Callback = @updatePlots;

% Update view from params
paramsbutton = uicontrol(f,'Style','togglebutton','String','Params ->');
paramsbutton.Position = [1040 670 80 26 ];
paramsbutton.Callback = @paramsbuttonhit;

% Toggle doing fits
dofitsbutton = uicontrol(f,'Style','togglebutton','String','Do fits');
dofitsbutton.Position = [1130 700 80 26 ];
dofitsbutton.Callback = @dofitsbuttonhit;

% Toggle imaging order
csfirstbutton = uicontrol(f,'Style','togglebutton','String','Cs first?');
csfirstbutton.Position = [1130 670 50 26 ];
csfirstbutton.Callback = @csfirstbuttonhit;

% Toggle image height
windowheightbutton = uicontrol(f,'Style','togglebutton','String','180 px?');
windowheightbutton.Position = [1190 670 50 26 ];
windowheightbutton.Callback = @windowheightbuttonhit;

% Specify image number to save to
asnumber = uicontrol(f,'Style','edit');
asnumber.Position = [860 630 40 26];
asnumber.Callback = @asnumberenter;

% Autosave path label
aspathlbl = uicontrol(f,'Style','text','String','Saved as...');
aspathlbl.Position = [860 610 400 15];
aspathlbl.HorizontalAlignment = 'left';

% Display for view and mask
liparamsviewlbl = uicontrol(f,'Style','text','String','li_params.view = ');
liparamsviewlbl.Position = [860 570 190 15];
liparamsviewlbl.HorizontalAlignment = 'left';
liparamsview = uicontrol(f,'Style','edit');
liparamsview.Position = [860 540 190 25];

liparamsmasklbl = uicontrol(f,'Style','text','String','li_params.mask = ');
liparamsmasklbl.Position = [1060 570 190 15];
liparamsmasklbl.HorizontalAlignment = 'left';
liparamsmask = uicontrol(f,'Style','edit');
liparamsmask.Position = [1060 540 190 25];

csparamsviewlbl = uicontrol(f,'Style','text','String','cs_params.view = ');
csparamsviewlbl.Position = [860 520 190 15];
csparamsviewlbl.HorizontalAlignment = 'left';
csparamsview = uicontrol(f,'Style','edit');
csparamsview.Position = [860 490 190 25];

csparamsmasklbl = uicontrol(f,'Style','text','String','cs_params.mask = ');
csparamsmasklbl.Position = [1060 520 190 15];
csparamsmasklbl.HorizontalAlignment = 'left';
csparamsmask = uicontrol(f,'Style','edit');
csparamsmask.Position = [1060 490 190 25];


% Display for fit results
fittbllbl = uicontrol(f,'Style','text','String','Fit Results: ');
fittbllbl.Position = [860 460 150 15];
fittbllbl.HorizontalAlignment = 'left';
fittbl = uitable(f);
fittbl.Position = [860 20 400 435];
fittbl.ColumnName = ["#","nxLi", "nyLi", "wxLi", "wyLi", "nxCs", "nyCs", "wxCs", "wyCs"];
w = 45;
fittbl.ColumnWidth = {35,w,w,w,w,w,w,w,w};
fittbl.RowName = [];
fittbl.Data = {};


%% All of the function definitions for button presses/text fields %%%%%%%%%

function updatePlots(src, event)

    % View and ROI "lock" button logic
    if get(csviewlockbox,'Value')
        set(csviewfieldxl,'enable','off',...
            'String',get(liviewfieldxl,'String'));
        set(csviewfieldxu,'enable','off',...
            'String',get(liviewfieldxu,'String'));
        set(csviewfieldyl,'enable','off',...
            'String',get(liviewfieldyl,'String'));
        set(csviewfieldyu,'enable','off',...
            'String',get(liviewfieldyu,'String'));
    else
        set(csviewfieldxl,'enable','on');
        set(csviewfieldxu,'enable','on');
        set(csviewfieldyl,'enable','on');
        set(csviewfieldyu,'enable','on');
    end
    if get(liROIlockbox,'Value')
        set(liROIfieldxl,'enable','off',...
            'String',get(liviewfieldxl,'String'));
        set(liROIfieldxu,'enable','off',...
            'String',get(liviewfieldxu,'String'));
        set(liROIfieldyl,'enable','off',...
            'String',get(liviewfieldyl,'String'));
        set(liROIfieldyu,'enable','off',...
            'String',get(liviewfieldyu,'String'));
    else
        set(liROIfieldxl,'enable','on');
        set(liROIfieldxu,'enable','on');
        set(liROIfieldyl,'enable','on');
        set(liROIfieldyu,'enable','on');
    end
    if get(csROIlockbox,'Value')
        set(csROIfieldxl,'enable','off',...
            'String',get(liROIfieldxl,'String'));
        set(csROIfieldxu,'enable','off',...
            'String',get(liROIfieldxu,'String'));
        set(csROIfieldyl,'enable','off',...
            'String',get(liROIfieldyl,'String'));
        set(csROIfieldyu,'enable','off',...
            'String',get(liROIfieldyu,'String'));
    else
        set(csROIfieldxl,'enable','on');
        set(csROIfieldxu,'enable','on');
        set(csROIfieldyl,'enable','on');
        set(csROIfieldyu,'enable','on');
    end
    
    
    % extract view and ROI from boxes
    liviewfieldxl.String = max(str2num(liviewfieldxl.String), 1);
    liviewfieldxu.String = min(str2num(liviewfieldxu.String), sub_area_width);
    liviewfieldyl.String = max(str2num(liviewfieldyl.String), 1);
    liviewfieldyu.String = min(str2num(liviewfieldyu.String), sub_area_height);
    if ~(str2num(liviewfieldxl.String) < str2num(liviewfieldxu.String))
        liviewfieldxl.String = 1;
        liviewfieldxu.String = sub_area_width;
    end
    if ~(str2num(liviewfieldyl.String) < str2num(liviewfieldyu.String))
        liviewfieldyl.String = 1;
        liviewfieldyu.String = sub_area_height;
    end
    liimgview = [str2num(liviewfieldxl.String), str2num(liviewfieldxu.String),...
        str2num(liviewfieldyl.String), str2num(liviewfieldyu.String),...
        str2num(licbarl.String), str2num(licbaru.String)];
    
    liROIfieldxl.String = max(str2num(liviewfieldxl.String), str2num(liROIfieldxl.String));
    liROIfieldxu.String = min(str2num(liviewfieldxu.String), str2num(liROIfieldxu.String));
    liROIfieldyl.String = max(str2num(liviewfieldyl.String), str2num(liROIfieldyl.String));
    liROIfieldyu.String = min(str2num(liviewfieldyu.String), str2num(liROIfieldyu.String));
    if ~((str2num(liviewfieldxl.String) <= str2num(liROIfieldxl.String)) && ...
        (str2num(liROIfieldxl.String) < str2num(liROIfieldxu.String)) && ...
        (str2num(liROIfieldxu.String) <= str2num(liviewfieldxu.String)))
        liROIfieldxl.String = liviewfieldxl.String;
        liROIfieldxu.String = liviewfieldxu.String;
    end
    if ~((str2num(liviewfieldyl.String) <= str2num(liROIfieldyl.String)) && ...
        (str2num(liROIfieldyl.String) < str2num(liROIfieldyu.String)) && ...
        (str2num(liROIfieldyu.String) <= str2num(liviewfieldyu.String)))
        liROIfieldyl.String = liviewfieldyl.String;
        liROIfieldyu.String = liviewfieldyu.String;
    end
    liimgROI = [str2num(liROIfieldxl.String), str2num(liROIfieldxu.String),...
        str2num(liROIfieldyl.String), str2num(liROIfieldyu.String)];
    
    csviewfieldxl.String = max(str2num(csviewfieldxl.String), 1);
    csviewfieldxu.String = min(str2num(csviewfieldxu.String), sub_area_width);
    csviewfieldyl.String = max(str2num(csviewfieldyl.String), 1);
    csviewfieldyu.String = min(str2num(csviewfieldyu.String), sub_area_height);
    if ~(str2num(csviewfieldxl.String) < str2num(csviewfieldxu.String))
        csviewfieldxl.String = 1;
        csviewfieldxu.String = sub_area_width;
    end
    if ~(str2num(csviewfieldyl.String) < str2num(csviewfieldyu.String))
        csviewfieldyl.String = 1;
        csviewfieldyu.String = sub_area_height;
    end
    csimgview = [str2num(csviewfieldxl.String), str2num(csviewfieldxu.String),...
        str2num(csviewfieldyl.String), str2num(csviewfieldyu.String),...
        str2num(cscbarl.String), str2num(cscbaru.String)];
    
    csROIfieldxl.String = max(str2num(csviewfieldxl.String), str2num(csROIfieldxl.String));
    csROIfieldxu.String = min(str2num(csviewfieldxu.String), str2num(csROIfieldxu.String));
    csROIfieldyl.String = max(str2num(csviewfieldyl.String), str2num(csROIfieldyl.String));
    csROIfieldyu.String = min(str2num(csviewfieldyu.String), str2num(csROIfieldyu.String));
    if ~((str2num(csviewfieldxl.String) <= str2num(csROIfieldxl.String)) && ...
        (str2num(csROIfieldxl.String) < str2num(csROIfieldxu.String)) && ...
        (str2num(csROIfieldxu.String) <= str2num(csviewfieldxu.String)))
        csROIfieldxl.String = csviewfieldxl.String;
        csROIfieldxu.String = csviewfieldxu.String;
    end
    if ~((str2num(csviewfieldyl.String) <= str2num(csROIfieldyl.String)) && ...
        (str2num(csROIfieldyl.String) < str2num(csROIfieldyu.String)) && ...
        (str2num(csROIfieldyu.String) <= str2num(csviewfieldyu.String)))
        csROIfieldyl.String = csviewfieldyl.String;
        csROIfieldyu.String = csviewfieldyu.String;
    end
    csimgROI = [str2num(csROIfieldxl.String), str2num(csROIfieldxu.String),...
        str2num(csROIfieldyl.String), str2num(csROIfieldyu.String)];
   
    
    % get the right data for plot
    liimgselectval = liimgselector.Value;
    if liimgselectval == 1
        liPlotData = Li_OD;
    elseif liimgselectval == 2
        liPlotData = Cs_OD;
    elseif liimgselectval == 3
        liPlotData = Li_Atoms;
    elseif liimgselectval == 4
        liPlotData = Cs_Atoms;
    elseif liimgselectval == 5
        liPlotData = Li_No_Atoms;
    elseif liimgselectval == 6
        liPlotData = Cs_No_Atoms;
    end
    
    csimgselectval = csimgselector.Value;
    if csimgselectval == 1
        csPlotData = Li_OD;
    elseif csimgselectval == 2
        csPlotData = Cs_OD;
    elseif csimgselectval == 3
        csPlotData = Li_Atoms;
    elseif csimgselectval == 4
        csPlotData = Cs_Atoms;
    elseif csimgselectval == 5
        csPlotData = Li_No_Atoms;
    elseif csimgselectval == 6
        csPlotData = Cs_No_Atoms;
    end
    
    % set scale factor
    if unitbutton.Value 
        scale = umperpix;
    else 
        scale = 1;
    end

    % perform all integrations
    lixtrc = trapz(liPlotData(liimgROI(3):liimgROI(4),...
        liimgview(1):liimgview(2)),1);
    liytrc = trapz(liPlotData(liimgview(3):liimgview(4),...
        liimgROI(1):liimgROI(2)),2);
    csxtrc = trapz(csPlotData(csimgROI(3):csimgROI(4),...
        csimgview(1):csimgview(2)),1);
    csytrc = trapz(csPlotData(csimgview(3):csimgview(4),...
        csimgROI(1):csimgROI(2)),2);

    % perform fits  
    if dofitsbutton_state
        [lixfit, ~, lixnum, lixsigma] = gaussianfit(lixtrc, sigma_li);
        [liyfit, ~, liynum, liysigma] = gaussianfit(liytrc, sigma_li);
        [csxfit, ~, csxnum, csxsigma] = gaussianfit(csxtrc, sigma_cs);
        [csyfit, ~, csynum, csysigma] = gaussianfit(csytrc, sigma_cs);
    end

    % make plots for Li
    % image
    imagesc(lia, scale.*(liimgview(1):liimgview(2)),...
        scale.*(liimgview(3):liimgview(4)),...
        liPlotData(liimgview(3):liimgview(4), liimgview(1):liimgview(2)),...
        [liimgview(5) liimgview(6)]);
    hold(lia,'on');
    rectangle(lia, 'edgecolor', [1 0 0],...
        'position', scale.*[liimgROI(1), liimgROI(3), liimgROI(2)-liimgROI(1),...
        liimgROI(4)-liimgROI(3)]);
    if unitbutton.Value
        xlabel(lia, 'x (um)');
        ylabel(lia, 'y (um)');
    else
        xlabel(lia, 'x (pix)');
        ylabel(lia, 'y (pix)');
    end
    colorbar(lia);
    axis(lia,'image');
    hold(lia,'off');
    % x plot
    plot(liax, scale.*(liimgview(1):liimgview(2)), lixtrc, 'LineWidth', 1);
    hold(liax,'on');
%     plot(liax, scale.*(liimgview(1):liimgview(2)), lixguess, 'k:', 'LineWidth', 1);
    if dofitsbutton_state
        plot(liax, scale.*(liimgview(1):liimgview(2)), lixfit, 'r', 'LineWidth', 1);
    end
    l = ylim(liax);
    rectangle(liax, 'edgecolor', [1 0 0],...
        'position', [scale*liimgROI(1), l(1), scale*(liimgROI(2)-liimgROI(1)), l(2)-l(1)]);
    if unitbutton.Value
        xlabel(liax, 'x (um)');
    else
        xlabel(liax, 'x (pix)');
    end
    ylabel(liax,'Integrated OD');
    xlim(liax, scale.*[liimgview(1), liimgview(2)]);
    hold(liax,'off');
    % y plot
    plot(liay, scale.*(liimgview(3):liimgview(4)), liytrc, 'LineWidth', 1);
    hold(liay,'on');
%     plot(liay, scale.*(liimgview(3):liimgview(4)), liyguess, 'k:', 'LineWidth', 1);
    if dofitsbutton_state
        plot(liay, scale.*(liimgview(3):liimgview(4)), liyfit, 'r', 'LineWidth', 1);
    end
    l = ylim(liay);
    rectangle(liay, 'edgecolor', [1 0 0],...
        'position', [scale*liimgROI(3), l(1), scale*(liimgROI(4)-liimgROI(3)), l(2)-l(1)]);
    if unitbutton.Value
        xlabel(liay, 'y (um)');
    else
        xlabel(liay, 'y (pix)');
    end
    ylabel(liay,'Integrated OD');
    xlim(liay, scale.*[liimgview(3), liimgview(4)]);
    hold(liay,'off');
    
    % make plots for Cs
    % image
    imagesc(csa, scale.*(csimgview(1):csimgview(2)),...
        scale.*(csimgview(3):csimgview(4)),...
        csPlotData(csimgview(3):csimgview(4), csimgview(1):csimgview(2)),...
        [csimgview(5) csimgview(6)]);
    hold(csa,'on');
    rectangle(csa, 'edgecolor', [1 0 0],...
        'position', scale.*[csimgROI(1), csimgROI(3), csimgROI(2)-csimgROI(1),...
        csimgROI(4)-csimgROI(3)]);
    if unitbutton.Value
        xlabel(csa, 'x (um)');
        ylabel(csa, 'y (um)');
    else
        xlabel(csa, 'x (pix)');
        ylabel(csa, 'y (pix)');
    end
    colorbar(csa);
    axis(csa,'image');
    hold(csa,'off');
    % x plot
    plot(csax, scale.*(csimgview(1):csimgview(2)), csxtrc, 'LineWidth', 1);
    hold(csax,'on');
%     plot(csax, scale.*(csimgview(1):csimgview(2)), csxguess, 'k:', 'LineWidth', 1);
    if dofitsbutton_state
        plot(csax, scale.*(csimgview(1):csimgview(2)), csxfit, 'r', 'LineWidth', 1);
    end
    l = ylim(csax);
    rectangle(csax, 'edgecolor', [1 0 0],...
        'position', [scale*csimgROI(1), l(1), scale*(csimgROI(2)-csimgROI(1)), l(2)-l(1)]);
    if unitbutton.Value
        xlabel(csax, 'x (um)');
    else
        xlabel(csax, 'x (pix)');
    end
    ylabel(csax,'Integrated OD');
    xlim(csax, scale.*[csimgview(1), csimgview(2)]);
    hold(csax,'off');
    % y plot
    plot(csay, scale*(csimgview(3):csimgview(4)), csytrc, 'LineWidth', 1);
    hold(csay,'on');
%     plot(csay, scale.*(csimgview(3):csimgview(4)), csyguess, 'k:', 'LineWidth', 1);
    if dofitsbutton_state
        plot(csay, scale.*(csimgview(3):csimgview(4)), csyfit, 'r', 'LineWidth', 1);
    end
    l = ylim(csay);
    rectangle(csay, 'edgecolor', [1 0 0],...
        'position', [scale*csimgROI(3), l(1), scale*(csimgROI(4)-csimgROI(3)), l(2)-l(1)]);
    if unitbutton.Value
        xlabel(csay, 'y (um)');
    else
        xlabel(csay, 'y (pix)');
    end
    ylabel(csay,'Integrated OD');
    xlim(csay, scale.*[csimgview(3), csimgview(4)]);
    hold(csay,'off');
    
    
    % update text in info box
    liviewtext = sprintf('[%d %d %d %d]',...
        liimgview(3), liimgview(4), 1+sub_area_width-liimgview(2),...
        1+sub_area_width-liimgview(1));
    liROItext = sprintf('[%d %d %d %d]',...
        liimgROI(3)-liimgview(3)+1, liimgROI(4)-liimgview(3)+1,...
        liimgview(2)-liimgROI(2)+1, liimgview(2)-liimgROI(1)+1);
    csviewtext = sprintf('[%d %d %d %d]',...
        csimgview(3), csimgview(4), 1+sub_area_width-csimgview(2),...
        1+sub_area_width-csimgview(1));
    csROItext = sprintf('[%d %d %d %d]',...
        csimgROI(3)-csimgview(3)+1, csimgROI(4)-csimgview(3)+1,...
        csimgview(2)-csimgROI(2)+1, csimgview(2)-csimgROI(1)+1);
    liparamsview.String = liviewtext;
    liparamsmask.String = liROItext;
    csparamsview.String = csviewtext;
    csparamsmask.String = csROItext;

    % update fit results box
    if (logfit_flag && asbutton_state && dofitsbutton_state)
        d = fittbl.Data;
        d = cat(1, d, {num2str(imgstcknum, '%d'),...
            num2str(lixnum, '%.1e'), num2str(liynum, '%.1e'),...
            num2str(lixsigma, '%.1e'), num2str(liysigma, '%.1e'),...
            num2str(csxnum, '%.1e'), num2str(csynum, '%.1e'),...
            num2str(csxsigma, '%.1e'), num2str(csysigma, '%.1e')});
        fittbl.Data = d;

        % update save fit object
        fitdata.lixnum = lixnum;
        fitdata.liynum = liynum;
        fitdata.csxnum = csxnum;
        fitdata.csynum = csynum;
        fitdata.lixsigma = lixsigma;
        fitdata.liysigma = liysigma;
        fitdata.csxsigma = csxsigma;
        fitdata.csysigma = csysigma;

        logfit_flag = false;
    end
    
end

function asbuttonhit(src, event)
    asbutton_state = get(src,'Value');
end

function dofitsbuttonhit(src, event)
    dofitsbutton_state = get(src,'Value');
    updatePlots(src, event);
end

function csfirstbuttonhit(src, event)
    csfirst = get(src,'Value');
end

function windowheightbuttonhit(src, event)
    state = get(src,'Value');
    if state
        sub_area_height = 180;
    else
        sub_area_height = 140;
    end
end

function asnumberenter(src, event)
    imgstcknum = str2num(get(src,'String'));
end

function acquirebuttonhit(src,event)
    % This function listens to changes in the Andor .tif file and
    % accordingly reads them in, organizes them into imagestacks, and
    % saves them as .mat files.
    % img num is the number within an image stack, totimg num is the
    % total number of frames, and imstcknum is counting img stacks.
    
    acquirebutton_state = get(src,'Value');
    
    if acquirebutton_state==1
        disp('Acquiring');
    end
    
    while acquirebutton_state==1
        acquirebutton_state = get(src,'Value');
        if isfile(imgfile)

            pause(1);
            %load fast kinetics mode series here, hard coded to 5
            %images. Don't increment.
            img = zeros(sub_area_height, sub_area_width, 5);
            imagestack = zeros(sub_area_width, sub_area_height, 5);
            img(:,:,1) = imread(imgfile,1);
            img(:,:,2) = imread(imgfile,2);
            img(:,:,3) = imread(imgfile,3);
            img(:,:,4) = imread(imgfile,4);
            img(:,:,5) = imread(imgfile,5);

            %intended order: li atoms, cs atoms, li no atoms, cs no
            %atoms, electronic bg. we arent using electronic bg anymore

            % presaved background subtraction
            if sub_area_height == 140
                bg = Dk_Bkg140;
            elseif sub_area_height == 180
                bg = Dk_Bkg180;
            else
                error("Invalid sub_area_height");
            end
            
            im1 = img(:,:,1)-bg(3*sub_area_height+1:4*sub_area_height,:);
            im2 = img(:,:,2)-bg(2*sub_area_height+1:3*sub_area_height,:);
            im3 = img(:,:,3)-bg(sub_area_height+1:2*sub_area_height,:);
            im4 = img(:,:,4)-bg(1:sub_area_height,:);
            
            if csfirst
                Cs_Atoms = im1;
                Li_Atoms = im2;
                Cs_No_Atoms = im3;
                Li_No_Atoms = im4;
            else
                Cs_Atoms = im2;
                Li_Atoms = im1;
                Cs_No_Atoms = im4;
                Li_No_Atoms = im3;
            end
            
            size(imagestack)
            size(Li_Atoms)
            imagestack(:,:,1) = rot90(Li_Atoms);
            imagestack(:,:,2) = rot90(Cs_Atoms);
            imagestack(:,:,3) = rot90(Li_No_Atoms);
            imagestack(:,:,4) = rot90(Cs_No_Atoms);

            ratio_cs = Cs_No_Atoms./Cs_Atoms;
            ratio_cs(ratio_cs<0)=1; %get rid of infinities

            ratio_li = Li_No_Atoms./Li_Atoms;
            ratio_li(ratio_li<0)=1; %get rid of infinities
            Cs_OD = log(ratio_cs)+(Cs_No_Atoms-Cs_Atoms)./Isat_cs;
            Li_OD = log(ratio_li)+(Li_No_Atoms-Li_Atoms)./Isat_li;

            % Update plots
            logfit_flag = true;
            updatePlots(src, event);

            % Check and delete
            delete(imgfile);

            % Save image
            if asbutton_state==1
                % get date in such a way as to roll over the date at 4 am
                % instead of midnight
                myclock = round(datevec(datetime("now", "TimeZone","-09:00")));
                
                localdir = sprintf(localdirfmt, myclock(1), myclock(2), myclock(3), imgstcknum);
                if ~isfolder(localdir)
                    mkdir(localdir);
                end
                
                remotedir = sprintf(remotedirfmt, myclock(1), myclock(2), myclock(3), imgstcknum);
                if ~isfolder(remotedir)
                    mkdir(remotedir);
                end
                
                file = sprintf(filefmt, myclock(1), myclock(2), myclock(3), imgstcknum);
                save(strcat(localdir, file), 'imagestack', 'fitdata');
                save(strcat(remotedir, file), 'imagestack', 'fitdata');

                aspathlbl.String = sprintf(aslabelfmt, myclock(1), myclock(2), myclock(3), imgstcknum);
                imgstcknum = imgstcknum + 1;
                asnumber.String = imgstcknum;
            end
        else % if the file hasn't been updated  
            pause(0.5);
        end
    end
    disp('Stopped Acquiring');
end

function filepathEnter(src,event)
    [filename, pathname] = uigetfile('*.tif','File Selector');
    %filename = filename(1:8); %ignore if Andor appends _1,_2. etc.
    imgfile = strcat(pathname,filename);
    %imgfile = strcat(pathname,filename,'.tif');
    dirlbl.String = imgfile;
    disp(filename);
end

function loadButtonHit(src,event)

    [filename, pathname] = uigetfile('File Selector');
    imgfile = strcat(pathname,filename);
    dirlbl.String = strcat(imgfile,',',num2str(imgstcknum));
    a = load(imgfile,'imagestack');
    imagestack = a.imagestack;

    Li_Atoms = rot90(imagestack(:,:,1), 3);
    Cs_Atoms = rot90(imagestack(:,:,2), 3);
    Li_No_Atoms = rot90(imagestack(:,:,3), 3);
    Cs_No_Atoms = rot90(imagestack(:,:,4), 3);
    
    ratio_cs = Cs_No_Atoms./Cs_Atoms;
    ratio_cs(ratio_cs<0)=1; %get rid of infinities
    
    ratio_li = Li_No_Atoms./Li_Atoms;
    ratio_li(ratio_li<0)=1; %get rid of infinities
    Cs_OD = log(ratio_cs)+(Cs_No_Atoms-Cs_Atoms)./Isat_cs;
    Li_OD = log(ratio_li)+(Li_No_Atoms-Li_Atoms)./Isat_li;
    
    % Update plots
    updatePlots(src, event);
    
end

function paramsbuttonhit(src,event)
    % update text in info box
    liviewtext = cellfun(@str2num, regexp(liparamsview.String(2:end-1), ' ', 'split'));
    liROItext = cellfun(@str2num, regexp(liparamsmask.String(2:end-1), ' ', 'split'));
    liimgview(3) = liviewtext(1);
    liimgview(4) = liviewtext(2);
    liimgview(2) = 1+sub_area_width-liviewtext(3);
    liimgview(1) = 1+sub_area_width-liviewtext(4);
    liimgROI(3) = liROItext(1)+liimgview(3)-1;
    liimgROI(4) = liROItext(2)+liimgview(3)-1;
    liimgROI(2) = liimgview(2)-liROItext(3)+1;
    liimgROI(1) = liimgview(2)-liROItext(4)+1;

    csviewtext = cellfun(@str2num, regexp(csparamsview.String(2:end-1), ' ', 'split'));
    csROItext = cellfun(@str2num, regexp(csparamsmask.String(2:end-1), ' ', 'split'));
    csimgview(3) = csviewtext(1);
    csimgview(4) = csviewtext(2);
    csimgview(2) = 1+sub_area_width-csviewtext(3);
    csimgview(1) = 1+sub_area_width-csviewtext(4);
    csimgROI(3) = csROItext(1)+csimgview(3)-1;
    csimgROI(4) = csROItext(2)+csimgview(3)-1;
    csimgROI(2) = csimgview(2)-csROItext(3)+1;
    csimgROI(1) = csimgview(2)-csROItext(4)+1;

    liviewfieldxl.String = liimgview(1);
    liviewfieldxu.String = liimgview(2);
    liviewfieldyl.String = liimgview(3);
    liviewfieldyu.String = liimgview(4);
    liROIfieldxl.String = liimgROI(1);
    liROIfieldxu.String = liimgROI(2);
    liROIfieldyl.String = liimgROI(3);
    liROIfieldyu.String = liimgROI(4);

    csviewfieldxl.String = csimgview(1);
    csviewfieldxu.String = csimgview(2);
    csviewfieldyl.String = csimgview(3);
    csviewfieldyu.String = csimgview(4);
    csROIfieldxl.String = csimgROI(1);
    csROIfieldxu.String = csimgROI(2);
    csROIfieldyl.String = csimgROI(3);
    csROIfieldyu.String = csimgROI(4);

    paramsbutton.Value = false;
    updatePlots(src,event);
end


function [fit, guess, n, sigma] = gaussianfit(ydata, crosssec)
    xdata = 1:length(ydata);
    if size(ydata,1) > 1
        ydata = ydata';
    end
    ydata(~isfinite(ydata)) = 0;
    bgguess = min(ydata);
    ampguess = max(ydata)-min(ydata);
    meanguess = max(xdata)/2;
    sigmaguess = max(xdata)/6;
%     weight = (ydata - bgguess)';
%     meanguess = sum(xdata * weight)./sum(weight);
%     sigmaguess = sqrt(sum(((xdata-meanguess).^2) * weight)./sum(weight));
    fun = @(c, x) c(1).*exp(-(x-c(2)).^2./(2*c(3)^2)) + c(4);
    paramguess = [ampguess, meanguess, sigmaguess, bgguess];
    guess = fun(paramguess, xdata);
    LB = [0, -Inf, 0, min(ydata)];
    UB = [Inf, Inf, Inf, max(ydata)];
    opt = optimoptions('lsqcurvefit','Display','off');
    params = lsqcurvefit(fun, paramguess, xdata, ydata, LB, UB, opt);
    fit = fun(params, xdata);
    n = params(1)*params(3)*sqrt(2*pi)*umperpix^2/crosssec; % fitted atom number
    sigma = params(3)*umperpix; % gaussian sigma in um
    
end


end
