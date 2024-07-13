function scan = proc_scan(params, shots, dfinfo, varargin)
% proc_scan(params, shots, dfinfo, varargin)
%
% This function processes a scan of images. It loads the images, subtracts
% the background, defringes the images, calculates the number density, and
% fits the number density. It then plots the results. Plotting is live, so
% you can watch the plots update as the images are taken.
%
% INPUTS
%   params - struct containing the parameters for the scan. Needs the 
%       following fields:
%       cam - 'H' or 'V'
%       atom - 'Rb' or 'K'
%       date - date of the scan, in the format [yyyy, mm, dd]
%       view - [ymin, ymax, xmin, xmax] of the view window
%       mask - [ymin, ymax, xmin, xmax] of the mask window
%       pcanum - number of principal components to use for defringing
%       bginfo - how to get the background. Can be 'none', 'self', or an
%           array of shots. If 'none', no background subtraction is done.
%           If 'self', the background is taken from the same shots as the
%           data. If an array of shots, the background is taken from those
%           shots.
%   shots - array of shots to process. Can be an array of shot numbers, or
%       a cell array with the date and shot numbers. If the date is not
%       supplied, it is assumed to be the same as params.date.
%   dfinfo - how to get the defringing data. Can be 'none', 'self', or an
%       array of shots. If 'none', no defringing is done. If 'self', the
%       defringing is done using only the shots in the scan. If an array of
%       shots, the defringing is done using those shots.
%   varargin - optional inputs. Can be any of the following:
%       'xvalname' - name of the x value. If supplied, the x value is
%           plotted on the x axis instead of the shot number.
%       'figname' - name of the figure. If supplied, the figure is saved
%           with this name.
%       'bginfo' - how to get the background. Overrides the bginfo in
%           params.
%       'macrocalc' - cell array of macroscopic calculation parameters. If
%           supplied, the macroscopic calculation is done and plotted.
%       'debug' - if true, prints out debug statements.
%       'xvals' - array of x values. If supplied, the x values are plotted
%           on the x axis instead of the shot number.
%
% OUTPUTS
%   scan - struct containing the following fields:
%       ND - number density images
%       fd - fit data. Contains the following fields:.....
%       inputs - struct containing the inputs to the function



%% build a shots cell if not supplied 
if ~iscell(shots)
    shots = {params.date, shots};
end
shotnums = shots{2};
shotdate = shots{1};

%% handle varargin

% initialize default values 
xvalname = '';
figname = sprintf('scan %04d-%02d-%02d %c%c shots %d-%d', shotdate(1), shotdate(2), ...
    shotdate(3), params.cam, params.atom, shotnums(1), shotnums(end));
bginfo = params.bginfo;
macrocalc = {};
debug = params.debug;
xvals = shotnums(1, :);
savefig = true;

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
        case 'savefig'
            savefig = varargin{setting + 1};
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
            Abg = zeros(1, viewy, viewx);
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
raw = NaN(nshots, viewy, viewx, nF); % raw images
L = NaN(nshots + ndf, viewy, viewx); % light images
A = NaN(nshots, viewy, viewx); % atom images
Aprime = NaN(nshots, viewy, viewx); % ideal light for atom images
ND = NaN(nshots, viewy, viewx); % number density images 
if dfcase == 3
    L(1:ndf, :, :) = Lload; % insert preloaded light frames
end
if bgcase == 2
    bg = NaN(nshots, viewy, viewx); % background frames
end



%% MAIN LOOP %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
loadind = 1;
procind = 1;



while procind <= nshots
    havenewdata = false;
    loading = true;
    while loading
        if debug
            fprintf('Loading shot %d of %d\r', loadind, nshots);
        end
        try
            raw = load_img(shots, params, loadind);
            % load frames into stack
            A(loadind, :, :) = raw(:, :, :, 1); % atom frames
            L(loadind + ndf, :, :) = raw(:, :, :, 2); % light frames
            if bgcase == 2
                bg(loadind, :, :) = raw(:, :, :, 3); % bg frame
            end

            % increment load index
            loadind = loadind + 1;

            % register having loaded something
            havenewdata = true;

            % stop if we've loaded everything
            if loadind > nshots
                loading = false;
            end
        catch
            if havenewdata
                loading = false;
            else
                pause(0.5);
            end

        end
    end

    % create background set 
    if bgcase == 2 % use background from current shots 
        Abg = mean(bg(1:loadind-1, :, :), 1);
        Lbg = Abg;
    end

    % subtract background 
    A(procind:loadind-1, :, :) = A(procind:loadind-1, :, :) - Abg;
    L(ndf + (procind:loadind-1), :, :) = ...
        L(ndf + (procind:loadind-1), :, :) - Lbg;

    % create defringe set
    dfobj = defringeset_create(L(1:(loadind-1 + ndf), :, :), ...
        params.mask, params.pcanum); 

    % defringe and calculate images 
    for ind = procind:loadind-1
        Aprime(ind, :, :) = defringe(A(ind, :, :), dfobj);
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
        plot_defaults;
        fig = figure('Name', figname, 'NumberTitle', 'off',...
            'Units', 'normalized', 'OuterPosition', [0 0 1 1],...
            'Theme', 'light');
        sgtitle(fig, figname, 'FontSize', 35);
    end
    [fig, calcs] = scan_figupdate(fig, params, xvals, fd, ND, xvalname,...
        loadind-1, nreps, nxvals, macrocalc);
    procind = loadind;

end %%%% end of main loop %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% report results
for i = 1:(length(calcs)/3)
    fld = calcs{3*i - 2};
    type = calcs{3*i - 1};
    val = calcs{3*i};
    fprintf('%s of %s = %.6f (%.6f)\n\n', type, fld, val(1), val(2));
end 

% save the figure 
if savefig
    smart_fig_export(fig, figname);
end

% save the data
save([figname, '.mat'], 'inputs', 'ND', 'fd', 'calcs');

% return object 
scan.ND = ND;
scan.fd = fd;
scan.inputs = inputs;
scan.calcs = calcs;



%%%% end of function %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

