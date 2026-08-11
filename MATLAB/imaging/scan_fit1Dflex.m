function data = scan_fit1Dflex(data, index, nshots)
% scan_fit1Dflex: fits 1D traces of an image to a specified fit type.
% Takes in a data structure and an index to the image to be analyzed.
% Returns a data structure with the fit results appended to it.
% 
% Usage: data = scan_fit1Dflex(data, index)
% 
% Arguments:
% data: data structure containing the fields:
%   .ND: 2D array of the image data
%   .params: structure containing the fields:
%       .fittype: cell array of fit types for x and y traces
%       .mask: 1x4 array of the mask for the image
%       .pixel: scalar of the pixel size
% index: index of the image to be analyzed
% nshots: number of total shots in this scan
% 
% Returns:
% data: original data structure with the fields (updated or added 
% after the first time):
%   .n_count: scalar of the total fluorescence in the image
%   .x_foo: various fit results for the x trace
%   .y_foo: various fit results for the y trace
% 

% extract fittype args
ft = data.params.fittype;
if iscell(ft)
    x_fit_type = ft{1};
    y_fit_type = ft{2};
else
    x_fit_type = ft;
    y_fit_type = ft;
end

% integrate traces over mask
mask = data.params.mask;
ND = squeeze(data.ND(index, :, :));
x_trace = sum(ND(mask(1):mask(2), :), 1);
y_trace = sum(ND(:, mask(3):mask(4)), 2);
x_trace = x_trace';

% perform fits 
xdata = fit1D(x_trace, x_fit_type, mask(3:4), data.params);
ydata = fit1D(y_trace, y_fit_type, mask(1:2), data.params);

% calculate total flourescence for image
n_count = sum(sum(ND(mask(1):mask(2), mask(3):mask(4))));

% output
if index == 1
    % create n_count entry if it's the first time
    data.n_count = NaN(nshots, 1);
end

% store fit results into the data structure
data.n_count(index) = n_count;

% store axis specific information into the data structure
for r = 1:2
    if r == 1
        ds = xdata;
        name = 'x';
    else
        ds = ydata;
        name = 'y';
    end
    flds = fields(ds);
    for f = 1:length(flds)
        fld = sprintf('%c_%s', name, flds{f});
        l = length(ds.(flds{f}));
        if index == 1
            % create the field if it's the first time
            data.(fld) = NaN(nshots, l);
        end
        data.(fld)(index, :) = ds.(flds{f});
    end
end


end
%%%% end main function %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%% function to perform fitting %%%%%%%%%%%%%%%%%%%%%%%
function data = fit1D(trace, fit_type, mask, params)

% configure independent variable
if size(trace, 1) == 1
    trace = trace';
end
x = (1:length(trace))';
low = mask(1);
high = mask(2);

% initialize data object
data = struct();

switch fit_type 
case 'gauss'
    % fit type 
    ft = fittype(@(amp, sigma, x0, x) ...
        gauss1D(amp, sigma, x0, x));
    
    % initial guesses and bounds
    p0 = [max(trace(low:high)), (high - low)/10, (low + high)/2];
    plb = [0, 0, low];
    pub = [Inf, high-low, high];
    
    % perform fit
    fo = fit(x, trace, ft, ...
        StartPoint=p0, Lower=plb, Upper=pub);
    
    % get trace
    fit_trace = fo(x);
    
    % calculate physical quantities
    data.sigma = fo.sigma * params.pixel;
    data.nfit = sqrt(2*pi) * fo.amp * abs(fo.sigma);
    data.center = fo.x0 * params.pixel;

case 'dbl'
    % fit type 
    ft = fittype(@(amp, sigma, x0, sep, x) ...
        dblgauss1D(amp, sigma, x0, sep, x));
    
    % initial guesses and bounds
    p0 = [max(trace(low:high)), (high - low)/10, (low + high)/2, (low + high)/2];
    plb = [0, 0, low, 0];
    pub = [Inf, high-low, high, high-low];
    
    % perform fit
    fo = fit(x, trace, ft, ...
        StartPoint=p0, Lower=plb, Upper=pub);
    
    % get trace
    fit_trace = fo(x);
    
    % calculate physical quantities
    data.sigma = fo.sigma * params.pixel;
    data.nfit = 2 * sqrt(2*pi) * fo.amp * abs(fo.sigma);
    data.center = fo.x0 * params.pixel;
    data.sep = fo.sep * params.pixel;

case 'tf'
    % fit type 
    ft = fittype(@(amp, rTF, x0, x) ...
        tf1D(amp, rTF, x0, x));
    
    % initial guesses and bounds
    p0 = [max(trace(low:high)), (high - low)/10, (low + high)/2];
    plb = [0, 0, low];
    pub = [Inf, high-low, high];
    % perform fit
    fo = fit(x, trace, ft, ...
        StartPoint=p0, Lower=plb, Upper=pub);
    
    % get trace
    fit_trace = fo(x);
    
    % calculate physical quantities
    data.rTF = fo.rTF * params.pixel;
    data.nfit = fo.amp * fo.rTF * 16/15;
    data.center = fo.x0 * params.pixel;
        
end

data.trace = trace;
data.fit_trace = fit_trace;

end
%%%% end of fitting function %%%%%%%%%%%%%%%%%%%%%%%%%%%%%



%% fit functions, parameters, and calculations

%%%% single gaussian %%%%
function f = gauss1D(amp, sigma, x0, x)
    f = amp * exp(-(x-x0).^2/(2 * sigma^2));
end

%%%% double gaussian %%%%
function f = dblgauss1D(amp, sigma, x0, sep, x)
    f = amp * (...
        exp(-(x - x0 - sep/2).^2/(2 * sigma^2)) + ...
        exp(-(x - x0 + sep/2).^2/(2 * sigma^2)));
end

%%%% thomas-fermi %%%%
function f = tf1D(amp, rTF, x0, x)
    arg = 1 - ((x - x0)/rTF).^2;
    arg(arg < 0) = 0;
    f = amp .* (arg).^2;
end