function imagestack = load_img(shots, params, ind)


% relevant parts of params
view = params.view;
cam = params.cam;
atom = params.atom;

% allow shots to include a date
if iscell(shots)
    date = shots{1};
    shots = shots{2};
else
    date = params.date;
end

if nargin == 3
    % if we are given an index, then we only want to load one shot
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