function [imgs, fitvals] = proc_scan(shots, params, xvals, dfinfo, bginfo)

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
            


%% enable user to pass bginfo and dfinfo in params, and 
if nargin < 5
    bginfo = params.bginfo;
end
if nargin < 4
    dfinfo = params.dfinfo;
end
if nargin < 3
    xvals = shots;
end


%% perform validation on various params
% TODO: add validation for params struct


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



%% figure out how the user supplied dfinfo.

% dfcase tells us about the method
% L is the actual light frames we will use

if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringeing.
            dfcase = 1;
        case 'self'
            % Case 2: "self" - Use just the light images from the 
            dfcase = 2;
        otherwise
            error('Invalid dfinfo input');
    end
elseif isnumeric(dfinfo) && size(dfinfo, 1) == 1
    % Case 3: 1D array of shots - Use a 1D array of shots data.
    dfcase = 3;
    L = load_img(dfinfo, params);
    L = L(:, :, :, 2);
elseif isstruct(dfinfo) && isfield(dfinfo, 'shots') && isfield(dfinfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    dfcase = 3;
    L = load_img(dfinfo, params);
    L = L(:, :, :, 2);
else
    error('Invalid dfinfo input');
end


%% initialize arrays 

% initialize shots arrays 
sz = [params.view(4) - params.view(3) + 1, params.view(2) - params.view(1) + 1];
if cam == 'H'
    raw = zeros(numel(shots), sz(1), sz(2), 3);
else
    raw = zeros(numel(shots), sz(1), sz(2), 2);
end
A = raw(:, :, :, 1); % atom frames
dA = A; % background subtracted atom frames
Aprime = A; % defringed atom frames

% initialize light arrays
switch dfcase
    case 1 % none
        L = 0;
    case 2 % self
        L = raw(:, :, :, 2); % light frames
    case 3 % self + extra
        L = cat(1, L, raw(:, :, :, 2));
end
dL = L; % background subtracted light frames
Lavg = squeeze(mean(L, 1)); % average light image

% initialize background array
if bgcase == 2 % use background frames from the images 
    bg = raw(:, :, :, 3); % background frames
end

% get lengths 
n = size(A, 1); % atom set length
m = size(L, 1); % light set length
l = m - n; % number of extra light frames


% initialize figure

