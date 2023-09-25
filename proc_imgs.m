function imgs = proc_imgs(shots, params, dfinfo, bginfo)

% 
% Returns defringed images from a set of shots.
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
%               take the form [a b c] for the 0th, 0th, 1st, and 2nd order terms
%               - 'fit_fun': a function 
%               - 'fit_params_names'
%               - 'plot_params'
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
           

%% enable user to pass bginfo and dfinfo in params
if nargin < 4
    bginfo = params.bginfo;
end
if nargin < 3
    dfinfo = params.dfinfo;
end



%% figure out how the user supplied bginfo.
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
    B = squeeze(mean(img_load(bginfo, params), 1));
elseif isstruct(bginfo) && isfield(bginfo, 'shots') && isfield(bginfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    bgcase = 3;
    B = squeeze(mean(img_load(bginfo, params), 1));
elseif isnumeric(bginfo) && ndims(bginfo) == 3
    % Case 3: 3D array - Preaveraged image.
    bgcase = 3;
    B = bginfo;
else
    error('Invalid bginfo input');
end


%% figure out how the user supplied dfinfo.
if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringeing.
            dfcase = 1;
        case 'self'
            % Case 2: "self" - Use the light images from the shots to
            % defringe.
            dfcase = 2;
        otherwise
            error('Invalid dfinfo input');
    end
elseif isnumeric(dfinfo) && size(dfinfo, 1) == 1
    % Case 3: 1D array of shots - Use a 1D array of shots data.
    dfcase = 3;
elseif isstruct(dfinfo) && isfield(dfinfo, 'shots') && isfield(dfinfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    dfcase = 3;
else
    error('Invalid dfinfo input');
end


%% load images 

% load shots
raw = img_load(shots, params);

A = raw(:, :, :, 1); % atom frames
L = raw(:, :, :, 2); % light frames

if bgcase == 2 % use background frames from the images 
    B = squeeze(mean(raw(:, :, :, 3), 1)); % background frames
end

switch dfcase
    case 2 % use light frames as df set
        df = L; 
    case 3 % use light frames + external loaded df set 
        df = img_load(dfinfo, params);
        if bgcase == 2 % additionally, use individual backround shots
            dfbg = squeeze(mean((1, df(:, :, :, 3), raw(:, :, :, 3)); % get background from images and df set 
        end
        df = cat(1, df(:, :, :, 2), raw(:, :, :, 2)); 
end

n = size(A, 1); % image set length
m = size(df, 1); % df set length

%% subtract electronic background

% image set 
for i = 1:n
    switch bgcase
        case 2 % subtract off the background from each image
            A(i) = A(i) - B(i);
            L(i) = L(i) - B(i);
        case 3 % subtract off the appropriate preaveraged image
            A(i) = A(i) - B(:, :, 1);
            L(i) = L(i) - B(:, :, 2);
    end
end

% df set 
for i = 1:m
    switch bgcase
        case 2 % subtract off the background from each image
            df(i) = df(i) - dfbg(i);
        case 3 % subtract off the appropriate preaveraged image
            df(i) = df(i) - B(:, :, 2);
    end
end


%% perform defringing 

meanlight = squeeze(mean(df, ))

