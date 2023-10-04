function scan = proc_scan(shots, params, xvals, dfinfo, bginfo, figname, xvalname)


%% handle varargsin

% don't plot x axis name if none supplied
if nargin < 7
    xvalname = '';
end

% make up a name if none supplied
if nargin < 6
    if isstruct(shots)
        s = sprintf('%d-%d', shots.shots(1), shots.shots(end));
        d = sprintf('%d%d%d', shots.date(1), shots.date(2), shots.date(3));
    else
        s = sprintf('%d-%d', shots(1), shots(end));
        d = sprintf('%d%d%d', params.date(1), params.date(2), params.date(3));
    end
    figname = strcat(d, '_', params.cam, params.atom, '_', s);
end

% use params bginfo if none supplied
if nargin < 5
    bginfo = params.bginfo;
end

% use params dfinfo if none supplied
if nargin < 4
    dfinfo = params.dfinfo;
end

% use shots as xvals if none supplied
if nargin < 3
    if isstruct(shots)
        xvals = shots.shots;
    else
        xvals = shots;
    end
end

% save all inputs to a struct
inputs = struct('shots', shots, 'params', params, 'xvals', xvals, ...
    'dfinfo', dfinfo, 'bginfo', bginfo, 'figname', figname, 'xvalname', xvalname);


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
elseif isstruct(bginfo) && isfield(bginfo, 'shots') && isfield(bginfo, 'date')
    % Case 3: Shots struct - Use a struct containing shots and date information.
    bgcase = 3;
    bg = mean(load_img(bginfo, params), 1);
else
    error('Invalid bginfo input');
end

% distinguish between H and V images 
if bgcase == 3
    if params.cam == 'H'
        Abg = bg(:, :, :, 2);
        Lbg = bg(:, :, :, 3);
    else
        Abg = bg(:, :, :, 1);
        Lbg = bg(:, :, :, 2);
    end
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

view = params.view;
mask = params.mask;

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
if params.cam == 'H'
    nF = 3; % number of frames
else
    nF = 2;
end

raw = NaN(nA, sz(1), sz(2), nF); % raw images
A = NaN(nA, sz(1), sz(2)); % atom frames
% cA = NaN(nA, sz(1), sz(2)); % atom frames with background subtracted
% dA = NaN(nA, sz(1), sz(2)); % mean subtracted atom frames
% Aprime = NaN(nA, sz(1), sz(2)); % defringed ideal light pattern for atom frames
dAprime = NaN(nA, sz(1), sz(2)); % mean subtracted defringed ideal light pattern for atom frames
OD = NaN(nA, sz(1), sz(2)); % optical density images
L = NaN(nL, sz(1), sz(2)); % light frames
% cL = NaN(nL, sz(1), sz(2)); % light frames with background subtracted
% dL = NaN(nL, sz(1), sz(2)); % mean subtracted light frames
if dfcase == 3
    L(1:ndf, :, :) = loadL; % insert preloaded light frames
end
if bgcase == 2
    bg = NaN(nA, sz(1), sz(2)); % background frames
end



%% MAIN LOOP %%
for ind = 1:nA

fprintf('Loading shot %d of %d\r', ind, nA);
% wait till file exists
fexists = false;
while ~fexists 
    try 
        raw = load_img(shots, params, ind);
        fexists = true;
    catch 
        pause(0.5);
    end
end
fprintf('Shot %d of %d loaded\r', ind, nA);

A(ind, :, :) = raw(:, :, :, 1); % atom frames
L(ind + ndf, :, :) = raw(:, :, :, 2);
if bgcase == 2
    bg(ind, :, :) = raw(:, :, :, 3);
    Abg = mean(bg(1:ind, :, :), 1);
    Lbg = Abg;
end


% analyze the images
cA = A - Abg;
cL = L - Lbg;
Lavg = mean(cL(1:ind, :, :), 1);
dA = cA - Lavg;
dL = cL - Lavg;
dfobj = dfobj_create(dL(1:ind, :, :), params.mask, params.pcanum);
dAprime(1:ind, :, :) = dfobj_apply(dA(1:ind, :, :), dfobj);
Aprime = dAprime + Lavg;
% OD = od_calc(cA, Aprime, params);
OD = od_calc(cA + Lavg, Lavg, params);

% perform fits
if ind == 1
    fd = fit1Dflex(squeeze(OD(ind, :, :)), params);
else
    fd = fit1Dflex(squeeze(OD(ind, :, :)), params, fd);
end

% update plots
if ind == 1
    h = scanfig_init(params, figname);
end
h = scanfig_update(h, params, xvals, OD, fd, ind, xvalname);


end % end of main loop


% save the figure 
savefig(h.fig, strcat(figname, '.fig'));

% save the data
save(strcat('scan', figname, '.mat'), 'inputs', 'OD', 'fd');

scan.OD = OD;
scan.fd = fd;
scan.inputs = inputs;

end % end of function

