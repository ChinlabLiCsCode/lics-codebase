function scan = proc_scan(params, shots, dfinfo, varargin)


%% build a shots cell if not supplied 
if ~iscell(shots)
    shots = {params.date, shots};
end
shotnums = shots{2};
shotdate = shots{1};

%% handle varargin

% initialize default values 
xvalname = '';
figname = sprintf('scan %d-%d-%d %c%c shots %d-%d', shotdate(1), shotdate(2), ...
    shotdate(3), params.cam, params.atom, shotnums(1), shotnums(end));
bginfo = params.bginfo;
macrocalc = {};
debug = params.debug;
xvals = shotnums(1, :);

% process varargin
for setting = 1:2:length(varargin)
    switch varargin{setting}
        case 'xvalname'
            xvalname = varargin{setting + 1};
        case 'figname'
            figname = varargin{setting + 1};
        case 'bginfo' 
            bginfo = varargin{setting + 1};
        case 'macrocalc' 
            macrocalc = varargin{setting + 1};
        case 'debug'
            debug = varargin{setting + 1};
        case 'xvals'
            xvals = varargin{setting + 1};
        otherwise
            error('Invalid input: %s', varargin{setting});
    end
end

% save all inputs to a struct
inputs = struct();
inputs.shots = shots;
inputs.params = params;
inputs.xvals = xvals;
inputs.dfinfo = dfinfo;
inputs.bginfo = bginfo;
inputs.figname = figname;
inputs.xvalname = xvalname;
inputs.macrocalc = macrocalc;
inputs.debug = debug;

% get image sizes
view = params.view;
mask = params.mask;
viewx = view(4) - view(3) + 1;
viewy = view(2) - view(1) + 1;
maskx = mask(4) - mask(3) + 1;
masky = mask(2) - mask(1) + 1;

%% figure out how the user supplied bginfo.
if debug
    disp('Loading bg');
end
% bgcase tells us about the method
% bg is the actual background we will subtract
if ischar(bginfo)
    switch bginfo
        case 'none'
            % Case 1: "none" - Do no bg subtraction (V images).
            bgcase = 1;
            Abg = zeros(1, viewx, viewy);
            Lbg = Abg;
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
    Abg = bg(:, :, :, 1);
    Lbg = bg(:, :, :, 2);
else
    error('Invalid bginfo input');
end

%% figure out how the user supplied dfinfo.
if debug
    disp('Loading df');
end
% dfcase tells us about the method
% L is the light frames 
if ischar(dfinfo)
    switch dfinfo
        case 'none'
            % Case 1: "none" - Do no defringing.
            dfcase = 1;
            ndf = 0;
        case 'self'
            % Case 2: "self" - Defringe using only images from dataset.
            dfcase = 2;
            ndf = 0;
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
    ndf = size(Lload, 1);
else
    error('Invalid dfinfo input');
end



%% initialize all the image variables and arrays 

% get the number of shots
nshots = numel(shotnums);
[nreps, nxvals] = size(shotnums);

% number of frames in each raw image
if params.cam == 'H'
    nF = 3; % number of frames
else
    nF = 2;
end

% create blank image arrays 
raw = NaN(nshots, viewx, viewy, nF); % raw images
L = NaN(nshots + ndf, viewx, viewy); % light images
A = NaN(nshots, viewx, viewy); % atom images
Aprime = NaN(nshots, viewx, viewy); % ideal light for atom images
ND = NaN(nshots, viewx, viewy); % number density images 
if dfcase == 3
    L(1:ndf, :, :) = Lload; % insert preloaded light frames
end
if bgcase == 2
    bg = NaN(nshots, sz(1), sz(2)); % background frames
end



%% MAIN LOOP %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
loadind = 1;
procind = 1;

while procind <= nshots
    
    % this block of while loops continues to load images until you reach 
    % one that doesn't exist 
    loading = true;
    while loading
        if debug
            fprintf('Loading shot %d of %d\r', loadind, nshots);
        end
        fexists = false;
        while ~fexists
            try 
                raw = load_img(shots, params, loadind);
                fexists = true;
            catch 
                pause(0.5);
                loading = false;
            end
        end
        if debug
            fprintf('Shot %d of %d loaded\r', loadind, nshots);
        end
        % load frames into stack
        A(loadind, :, :) = raw(:, :, :, 1); % atom frames
        L(loadind + ndf, :, :) = raw(:, :, :, 2); % light frames
        if bgcase == 2
            bg(loadind, :, :) = raw(:, :, :, 3); % bg frame
        end

        % increment load index
        loadind = loadind + 1;

        % stop if we've loaded everything
        if loadind > nshots
            loading = false;
        end
        
    end


    % create background set 
    if bgcase == 2 % use background from current shots 
        Abg = mean(bg(1:loadin, :, :), 1);
        Lbg = Abg;
    end

    % subtract background 
    A(procind:loadind-1, :, :) = A(procind:loadind-1, :, :) - Abg;
    L(ndf + (procind:loadind-1), :, :) = ...
        L(ndf + (procind:loadind-1), :, :) - Lbg;

    % create defringe set
    dfobj = cvpcreatedefringeset(L(1:(loadind-1 + ndf), :, :), ...
        params.mask, params.pcanum); 

    % defringe and calculate images 
    for ind = procind:loadind-1
        Aprime(ind, :, :) = cvpdefringe(A(ind, :, :), dfobj);
        ND(ind, :, :) = nd_calc(A(ind, :, :), Aprime(ind, :, :), params);
        
    end

    % perform fits 
    for ind = procind:loadind-1
        if ind == 1
            fd = scan_fit1Dflex(squeeze(ND(ind, :, :)), params);
        else
            fd = scan_fit1Dflex(squeeze(ND(ind, :, :)), params, fd);
        end
    end

    
    % update plots
    if procind == 1
        % Initialize the plot
        fig = figure('Name', figname, 'NumberTitle', 'off',...
            'Units', 'normalized', 'OuterPosition', [0 0 1 1],...
            'Theme', 'light');
        sgtitle(fig, figname, 'FontSize', 35);
    end
    fig = scan_figupdate(fig, params, xvals, fd, ND, xvalname,...
        loadind-1, nreps, nxvals);

    procind = loadind;

end %%%% end of main loop %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% save the figure 
smart_fig_export(fig, figname);

% save the data
save([figname, '.mat'], 'inputs', 'ND', 'fd');

scan.ND = ND;
scan.fd = fd;
scan.inputs = inputs;

end 

%%%% end of function %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

