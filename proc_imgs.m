function ND = proc_imgs(params, shots, dfinfo, varargin)
% PROC_IMGS Loads and defringes a set of images.
% 
%   ND = PROC_IMGS(params, shots, dfinfo) loads and defringes a set of
%   images. The images are loaded from the shots array, which is a cell
%   array with the date as the first element and the shot numbers as the
%   second element. The defringing is performed using the defringing
%   information in dfinfo, which can be 'none', 'self', or an array of
%   shots. The defringing information is loaded from the same date as the
%   shots array, or from a different date if specified as a cell. 
%   PROC_IMGS returns the atom number density ND, which is a 3D array with
%   the first dimension corresponding to the shots array and the second and
%   third dimensions corresponding to the x and y dimensions of the images.
% 
%   ND = PROC_IMGS(params, shots, dfinfo, 'bginfo', bginfo) specifies the
%   background subtraction information bginfo. bginfo can be 'none', 'self',
%   or an array of shots. The background subtraction information is loaded
%   from the same date as the shots array, or from a different date if
%   specified as a cell.
%
%   ND = PROC_IMGS(params, shots, dfinfo, 'debug', debug) specifies whether
%   to display debug images. debug can be true or false.
%
% INPUTS:
%   params: structure with fields
%       date: date of the shots
%       camera: camera number
%       odmethod: method of calculating optical depth
%       mask: mask to apply to images
%       pcanum: number of principal components to use for defringing
%       bginfo: background subtraction information
%       dfinfo: defringing information
%       debug: whether to display debug images
%   shots: array of shots, or cell with date and shots
%   dfinfo: defringing information
%   varargin: optional inputs
%       'bginfo': background subtraction information
%       'debug': whether to display debug images
%

           
%% build a shots cell if not supplied 
if ~iscell(shots)
    shots = {params.date, shots};
end
shotnums = shots{2};

%% handle varargin

% initialize default values 
bginfo = params.bginfo;
debug = params.debug;

% process varargin
for setting = 1:2:length(varargin)
    switch varargin{setting}
        case 'bginfo' 
            bginfo = varargin{setting + 1};
        case 'debug'
            debug = varargin{setting + 1};
        otherwise
            error('Invalid input: %s', varargin{setting});
    end
end

%% enable user to pass dfinfo in params
if nargin < 3
    dfinfo = params.dfinfo;
end

%% figure out how the user supplied bginfo.
if debug
    disp('loading bg');
end
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
elseif isnumeric(bginfo) || iscell(bginfo)
    % Case 3: array of shots, assuming today, or cell with date and shots
    bgcase = 3;
    bg = mean(load_img(bginfo, params), 1);
else
    error('Invalid bginfo input');
end

%% figure out how the user supplied dfinfo.
if debug
    disp('loading df');
end
% dfcase tells us about the method
% L is the light frames 
if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringing.
            dfcase = 1;
        case 'self'
            % Case 2: "self" - Defringe using only images from dataset.
            dfcase = 2;
        otherwise
            error('Invalid dfinfo input');
    end
elseif isnumeric(dfinfo) || iscell(dfinfo)
    % Case 3: array of shots, assuming today, or cell with date and shots
    dfcase = 3;
    dfload = load_img(dfinfo, params);
    switch bgcase
        case 1 
            Lload = dfload(:, :, :, 2);
        case 2
            Lload = dfload(:, :, :, 2) - dfload(:, :, :, 3);
        case 3
            Lload = dfload(:, :, :, 2) - bg(:, :, :, 2);
    end
else
    error('Invalid dfinfo input');
end


%% load images 
if debug
    disp('loading imgs');
end

% load full image stack 
raw = load_img(shots, params);

% atom frames
A = raw(:, :, :, 1); 
% light frames 
L = raw(:, :, :, 2);

% subtract background 
if bgcase == 2
    % subtract background frame by frame from loaded shots
    A = A - raw(:, :, :, 3);
    L = L - raw(:, :, :, 3);
elseif bgcase == 3
    % subtract preaveraged background
    A = A - bg(:, :, :, 1);
    L = L - bg(:, :, :, 2);
end

if debug
    imgstack_viewer(A, 'A (ebg subtracted)');
    imgstack_viewer(L, 'L (ebg subtracted)');
end


%% perform defringing and od calculation

% combine Lload and L if necessary
if dfcase == 3
    L = cat(1, Lload, L);
end

% create defringeset object
dfobj = new_cvpcreatedefringeset(L, params.mask, params.pcanum);

% perform defringing
Aprime = A; % initialize Aprime
for a = 1:size(A, 1)
    % Aprime is the ideal light frame corresponding to A
    Aprime(a, :, :) = new_cvpdefringe(A(a, :, :), dfobj);
end

% calculate atom number density
ND = nd_calc(A, Aprime, params);

if debug
    imgstack_viewer(Aprime, 'Aprime');
    imgstack_viewer(ND, 'ND');
end

% reshape output if input was more than 1d
if ndims(shotnums) > 1
    szA = size(ND);
    szB = size(shotnums);
    ND = reshape(ND, [szB(1), szB(2), szA(2), szA(3)]);
end

end

