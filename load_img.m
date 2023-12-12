function imagestack = load_img(shots, params, ind)
% LOAD_IMG Load image stack from a given set of shots
%
%   imagestack = LOAD_IMG(shots, params) loads the image stack for the
%   given set of shots. The shots can be given as a vector or a cell array
%   of vectors. The params struct should contain the following fields:
%       params.view - the view of the image stack to load
%       params.cam - the camera to load
%       params.atom - the atom type to load
%       params.date - the date of the shots
%
%   imagestack = LOAD_IMG(shots, params, ind) loads only the shot at index
%   ind from the given set of shots.
%
%   See also: LOCALPATH, which defines the file template for loading the
%   image stack.
% 
%  INPUTS:
%   shots:  [vector] or [cell array] of vectors of shots to load. If a cell
%           array is given, the first element should be the date of the
%           shots, and the second element should be the vector of shots. 
%           Otherwise, the date is taken from params.date.
%   params: [struct] containing the fields view, cam, atom, and date:
%           params.view - [vector] of the form [xmin, xmax, ymin, ymax]
%           params.cam - [char] either 'V' or 'H'
%           params.atom - [char] either 'L' or 'C'
%           params.date - [vector] of the form [year, month, day]
%   ind:    [scalar] index of the shot to load. If ind is given, then only
%           the shot at index ind is loaded. Otherwise, all shots are
%           loaded.
%
%  OUTPUTS:
%   imagestack: [array] image stack of the given shots. The first dimension
%               is the shot number, the second and third dimensions are the
%               x and y dimensions of the image, and the fourth dimension
%               is the frame index (atoms, light, background). If the input 
%               shots array was 2d, it gets flattened before loading. So the 
%               output imagestack will be 4d regardless of whether shots is 
%               1d or 2d.
%


% relevant parts of params
view = params.view;
cam = params.cam;
atom = params.atom;
transpose = params.transpose;

% allow shots to include a date
if iscell(shots)
    date = shots{1};
    shots = shots{2};
else
    date = params.date;
end

if nargin == 3
    % if we are given an index, then we only want to load one shot
    shots = shots'; % realized this flip was necessary because proc scan was getting very messed up.
    shots = shots(ind);
end

% flatten shots array
n = numel(shots);
fshots = reshape(shots, [n, 1]);

% set file template
file_template = localpath(cam);

% load the first shot to get image size
fname = sprintf(file_template, date(1), date(2), date(3), fshots(1));
vars = load(fname, 'imagestack');
sz = size(vars.imagestack);

% initialize full imagestack
imagestack = zeros(n, sz(1), sz(2), sz(3));
imagestack(1, :, :, :) = vars.imagestack;

% load the full image stack
if n > 1
    for a = 2:n
        fname = sprintf(file_template, date(1), date(2), date(3), fshots(a));
        vars = load(fname, 'imagestack');
        imagestack(a, :, :, :) = vars.imagestack;
    end
end

% do transpose if necessary
if transpose
    imagestack = permute(imagestack, [1, 3, 2, 4]);
end

% only return the relevant parts of the image stack

imagestack = imagestack(:, view(1):view(2), view(3):view(4), :);
if cam == 'V'
    if atom == 'L'
        imagestack = imagestack(:, :, :, [1, 3]);
    elseif atom == 'C'
        imagestack = imagestack(:, :, :, [2, 4]);
    else
        error('Invalid params.atom input');
    end
elseif cam == 'H'
    % reverse the order of the imagestack to be consistent with the
    % convention from fk imaging, that is, 1. atoms 2. light 3. background
    imagestack = imagestack(:, :, :, [2, 3, 1]);
else
    error('Invalid params.cam input');
end 

end