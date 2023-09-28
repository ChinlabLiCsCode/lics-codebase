function OD = proc_scan(shots, params, xvals, dfinfo, bginfo)

% 
% scannnnnnnn
%   
% INPUTS
%   shots:      1D or 2D array of shot numbers (uses params.date), 
%               or a shots struct (shots + date)
%   params:     params struct, should have the following fields:
%               - date: [yyyy mm dd]
%               - cam: 'H' or 'V'
%               - atom: 'C' or 'L'
%               - view: [xmin xmax ymin ymax]
%               - mask: [xmin xmax ymin ymax]
%               - wavelength: wavelength of imaging light (m)
%               - pix: pixel size (m)
%               - I_sat: saturation intensity in counts per pixel
%               - alpha: correction factor for OD calculation, should 
%               take the form [c b a] for the 0th, 0th, 1st, and 2nd order terms
%               - 'plot_init': function to 

%   dfinfo:     can be one of the following options:
%               1) 'none'
%               2) 'self'
%               3) 1D array of shots (uses params.date)
%                   or shots struct (shots + date)
%   bginfo:     can be one of the following options:
%               1) 'none'
%               2) 'self'
%               3) 1D array of shots (uses params.date)
%                   or shots struct (shots + date)
%               4) 3D array (basically a preaveraged image) 
% 
%   cancelled params: 
%               - 'dfmethod': 
%                   - 'od' (previous method, defringes the OD image)
%                   - 'raw' (defringes both the light and shadow images)
%                   - 'avg' (defringes the shadow image and uses an average 
%                       light image from the df set. Also uses an average 
%                       bg if bg mode is 'self'.)
            
%% handle varargsin



%% perform some checks on the inputs

view = params.view;
mask = params.mask;


%% figure out how the user supplied bginfo.

% bgcase tells us about the method
% bg is the actual background we will subtract

if ischar(bginfo)
    switch bginfo
        case 'none'
            % Case 1: "none" - Do no bg subtraction (V images).
            bgcase = 1;
        case 'self'
            % Case 2: "self" - Use the background frame (H images).
            bgcase = 2;
        otherwise
            error('Invalid bginfo input');
    end
elseif isnumeric(bginfo) && size(bginfo, 1) == 1
    % Case 3: 1D array of shots - Use a 1D array of shots data.
    bgcase = 3;
    bg = squeeze(mean(load_img(bginfo, params), 1));
elseif isstruct(bginfo) && isfield(bginfo, 'shots') && isfield(bginfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    bgcase = 3;
    bg = squeeze(mean(load_img(bginfo, params), 1));
elseif isnumeric(bginfo) && ndims(bginfo) == 3
    % Case 3: 3D array - Preaveraged image.
    bgcase = 3;
    bg = bginfo;
else
    error('Invalid bginfo input');
end

% distinguish between H and V images 
if bgcase == 3
    if cam == 'H'
        Abg = bg(:, :, 3);
        Lbg = bg(:, :, 1);
    else
        Abg = bg(:, :, 1);
        Lbg = bg(:, :, 2);
end

%% figure out how the user supplied dfinfo.

% dfcase tells us about the method
% L is the actual light frames we will use

if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringeing.
            dfcase = 1;
            ndf = 0;
        case 'self'
            % Case 2: "self" - Use just the light images from the 
            dfcase = 2;
            ndf = 0;
        otherwise
            error('Invalid dfinfo input');
    end
elseif isnumeric(dfinfo) && size(dfinfo, 1) == 1
    % Case 3: 1D array of shots - Use a 1D array of shots data.
    dfcase = 3;
    loadL = load_img(dfinfo, params);
    loadL = loadL(:, :, :, 2);
    ndf = size(loadL, 1);
elseif isstruct(dfinfo) && isfield(dfinfo, 'shots') && isfield(dfinfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    dfcase = 3;
    loadL = load_img(dfinfo, params);
    loadL = loadL(:, :, :, 2);
    ndf = size(loadL, 1);
else
    error('Invalid dfinfo input');
end


%% initialize all the image variables and arrays 

% get the number of shots
if isstruct(shots)
    nA = numel(shots.shots);
else
    nA = numel(shots);
end

% number of light images
nL = nA + ndf;

% size of the images
sz = [view(4) - view(3) + 1, view(2) - view(1) + 1]; % size of the images

% number of frames in each raw image
if cam == 'H'
    nF = 3; % number of frames
else
    nF = 2;
end

raw = NaN(nA, sz(1), sz(2), nF); % raw images
A = NaN(nA, sz(1), sz(2)); % atom frames
dA = NaN(nA, sz(1), sz(2)); % mean subtracted atom frames
Aprime = NaN(nA, sz(1), sz(2)); % defringed ideal light pattern for atom frames
dAprime = NaN(nA, sz(1), sz(2)); % mean subtracted defringed ideal light pattern for atom frames
OD = NaN(nA, sz(1), sz(2)); % optical density images
L = NaN(nL, sz(1), sz(2)); % light frames
dL = NaN(nL, sz(1), sz(2)); % mean subtracted light frames
if dfcase == 3
    L(1:ndf, :, :) = loadL; % insert preloaded light frames
end
if bgcase == 2
    bg = NaN(nA, sz(1), sz(2)); % background frames
end


% % initialize figure and outputs 
% switch fittype 
%     case 'gauss'
%         fig = figure("Position", [100 100 1000 800]);
%         axim = subplot(2, 4, [1 2]);
%         title(axim, 'OD');
%         axxtrc = subplot(2, 4, 3);
%         xlabel(axxtrc, 'x (px)');
%         ylabel(axxtrc, 'OD');
%         title(axxtrc, 'x trace');
%         axytrc = subplot(2, 4, 4);
%         xlabel(axytrc, 'y (px)');
%         ylabel(axytrc, 'OD');
%         title(axytrc, 'y trace');
%         axnx = subplot(2, 4, 5);
%         xlabel(axnx, xvallbl);
%         ylabel(axnx, 'number (x)');
%         title(axnx, 'number (x)');
%         axny = subplot(2, 4, 6);
%         title(axny, 'number (y)');
%         xlabel(axny, xvallbl);
%         ylabel(axny, 'number (y)');
%         axwx = subplot(2, 4, 7);
%         xlabel(axwx, xvallbl);
%         ylabel(axwx, 'width (x)');
%         title(axwx, 'width (x)');
%         axwy = subplot(2, 4, 8);
%         xlabel(axwy, xvallbl);
%         ylabel(axwy, 'width (y)');
%         title(axwy, 'width (y)');
% end


for ind = 1:nA

fprintf('Awaiting shot %d of %d\r', ind, nA);
% wait till file exists
fexists = 0;
while ~fexists 
    try 
        im = load_img(shots, params, ind);
        fexists = 1;
    catch 
        pause(0.5);
    end
end
fprintf('Shot %d of %d loaded\r', ind, nA);

A(ind, :, :) = im(:, :, 1);
L(ind + ndf, :, :) = im(:, :, 2);
if bgcase == 2
    bg(ind, :, :) = im(:, :, 3);
    Abg = squeeze(mean(bg(1:ind, :, :), 1));
    Lbg = Abg;
end
Lavg = squeeze(mean(L(1:ind, :, :), 1));
for i = 1:ind
    dA(i) = A(i) - Lavg;
end
for i = 1:(ind + ndf)
    dL(i) = L(i) - Lavg;
end
dfobj = dfobj_create(dL(1:ind, :, :), params.mask, params.pcanum);
dAprime(1:ind, :, :) = dfobj_apply(dA(1:ind, :, :), dfobj);
for i = 1:ind
    Aprime(i) = dAprime(i) + Lavg;
end

OD(1:ind, :, :) = od_calc(A(1:ind, :, :), Aprime(1:ind, :, :), params);

imagesc(OD(ind, :, :));
axis image;


end % end of loop


end % end of function

