function fd = scan_fit1Dflex(ND, params, fd)

% extract fittype args
ft = params.fittype;
if iscell(ft)
    x_fit_type = ft{1};
    y_fit_type = ft{2};
else
    x_fit_type = ft;
    y_fit_type = ft;
end

% integrate traces over mask
mask = params.mask;
x_trace = sum(ND(mask(3):mask(4), :), 1);
y_trace = sum(ND(:, mask(1):mask(2)), 2);
x_trace = x_trace';

% perform fits 
xdata = fit1D(x_trace, x_fit_type, mask(1:2), params);
ydata = fit1D(y_trace, y_fit_type, mask(3:4), params);

% calculate total flourescence for image
n_count = sum(sum(ND(mask(3):mask(4), mask(1):mask(2))));

% output
if nargin < 3
    % create fd struct
    fd = struct();
    fd.n_count = n_count;
else
    % append to fd if you've already 
    fd(end+1).n_count = n_count;
end

% store axis specific information into the data structure
for d = ['x', 'y']
    eval(sprintf('data = %cdata;', d));
    flds = fields(data);
    for f = 1:length(flds)
        fd(end).(sprintf('%c_%s', d, flds{f})) = data.(flds{f});
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
    pub = [2.*max(trace(low:high)), high-low, high];
    
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
    pub = [2.*max(trace(low:high)), high-low, high, high-low];
    
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
    pub = [2.*max(trace(low:high)), high-low, high];
    
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
data.fit_object = fo;
data.fit_type = fittype;

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