function imagestack = load_img(shots, params)
% 
% Loads and returns an image or set of images
% 'shots' can be an integer or an n-d array of integers.
% 'shots' can also be a struct that includes a date as well as shots.
% 'in_params' must have a date (3 element array), view (4 element array),
% cam (either 'H' or 'V), and atom (either 'C' or 'L').
% Returned imagestack has dimensions [numel(shots), view(3)-view(4),
% view(1)-view(2), x]. If the cam is 'H', we return the atoms, no atoms, 
% and background frames (so x=3). If the cam is 'V',
% then depending on the value of atom we either return the frames 1 and 3
% (for Li) or 2 and 4 (for Cs), so x=2. If you want to reshape the
% imagestack to match the shots shape, then do it yourself.
% 

%%%%%% add something to copy over the data if we request it in params %%%%%


% relevant parts of params
view = params.view;
cam = params.cam;
atom = params.atom;

% allow shots to include a date
if isstruct(shots)
    date = shots.date;
    shots = shots.shots;
else
    date = params.date;
end

% flatten shots array
n = numel(shots);
fshots = reshape(shots, [n, 1]);

% set file template
if cam == 'H'
    file_template = '//LiCs_NAS/Data_Backup/Data/%1$04d%2$02d%3$02d/%1$04d%2$02d%3$02d_%4$d.mat';
elseif cam == 'V'
    file_template = '//LiCs_NAS/Data_Backup/V_Images/Data/%1$04d/%2$02d/%1$04d%2$02d%3$02d/%1$04d%2$02d%3$02d_%4$d.mat';
else
    error('Invalid params.cam value')
end

% ensure valid atom setting
if not(or(atom == 'C', atom == 'L')) 
    error('Invalid params.atom value')
end

% load the first shot to get image size
fname = sprintf(file_template, date(1), date(2), date(3), fshots(1));
vars = load(fname, 'imagestack');
sz = size(vars.imagestack);

% initialize full imagestack
imagestack = zeros(n, sz(1), sz(2), sz(3));
imagestack(1, :, :, :) = vars.imagestack;

% load the full image stack
if n > 1
    for a=2:n
        fname = sprintf(file_template, date(1), date(2), date(3), fshots(a));
        vars = load(fname, 'imagestack');
        imagestack(a, :, :, :) = vars.imagestack;
    end
end

% only return the relevant parts of the image stack
imagestack = imagestack(:, view(3):view(4), view(1):view(2), :);
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