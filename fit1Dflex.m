function fd = fit1Dflex(ND, params, fd)


% extract fittype args
ft = params.fittype;
if iscell(ft)
    xft = ft{1};
    yft = ft{2};
else
    xft = ft;
    yft = ft;
end

% integrate traces over mask
mask = params.mask;
xtrace = sum(ND(mask(3):mask(4), :), 1);
ytrace = sum(ND(:, mask(1):mask(2)), 2);
ytrace = ytrace';

% perform fits 
x = fit1D(xtrace, xft, mask(1:2), params);
y = fit1D(ytrace, yft, mask(3:4), params);

% calculate total flourescence for image
n_count = sum(sum(ND(mask(3):mask(4), mask(1):mask(2))));

% output
if nargin < 3
    % create fd struct
    fd = struct();
    fd.ND = ND;
    fd.n_count = n_count;
    fd.x = x;
    fd.y = y;
else
    % append to fd if you've already 
    fd(end+1).ND = ND;
    fd(end).n_count = n_count;

    % extract the x and y fields 
    flds = fieldnames(fd);
    xflds = fields(startsWith(flds, 'x_'));
    yflds = fields(startsWith(flds, 'y_'));
    for i = 1:length(xflds)
        fd(end).(xflds{i}) = x.(xflds{i}(3:end));
    end
    for i = 1:length(yflds)
        fd(end).(yflds{i}) = y.(yflds{i}(3:end));
    end
end

end

% function to perform fitting 
function dout = fit1D(trace, ftype, mask, params)
    x = zeros(size(trace));
    x(:) = 1:length(trace);
    low = mask(1);
    high = mask(2);

    switch ftype
        case 'gauss'
            pfun = @gauss1Dp0;
            fun = @gauss1D;
            dfun = @gauss1Dcalcs;

        case 'dbl'
            pfun = @dbl1Dp0;
            fun = @dbl1D;
            dfun = @dbl1Dcalcs;

        case 'tf'
            pfun = @tf1Dp0;
            fun = @tf1D;
            dfun = @tf1Dcalcs;
    end

    % initial guess
    [p, pub, plb] = pfun(trace, low, high);
    p(p < plb) = plb(p < plb);
    p(p > pub) = pub(p > pub);

    options = optimset('TolX', 1e-8, 'Display', 'off');
    pars = lsqcurvefit(fun, p, x, trace, plb, pub, options);
    fit_trace = fun(pars, x);

    % calculate fit parameters
    dout = dfun(pars, params);
    dout.fit_trace = fit_trace;
    dout.trace = trace;

end




%% fit functions, parameters, and calculations

% single gaussian
function f = gauss1D(v,x)
    f = v(1) * exp(-(x-v(3)).^2/2/(v(2)^2))+v(4);
end

function [p, pub, plb] = gauss1Dp0(trace, low, high)
    p(1) = max(trace(low:high));
    p(2) = (high - low)/10;
    p(3) = (low + high)/2;
    p(4) = mean(trace([1:(low-1) (high+1):numel(trace)]));

    plb = [0 0 0 1.25*min(trace)-0.25*max(trace)];
    pub = [1.25*(max(trace)-min(trace)) numel(trace) Inf mean(trace)];
end

function f = gauss1Dcalcs(p, params)
    f = struct('f_amp', p(1),...
                'f_sigma', p(2),...
                'f_pos', p(3),...
                'f_bg', p(4));
    f.fwhm = 2*sqrt(2*log(2)) * f.f_sigma * params.pixel;
    f.sigma = f.f_sigma * params.pixel;
    f.nfit = sqrt(2*pi)*f.f_amp*abs(f.f_sigma);
    f.center = f.f_pos * params.pixel;
end

% double gaussian
function f = dbl1D(v,x)
    f = v(1)*exp(-(x-(v(3)+v(4)/2)).^2/2/(v(2)^2))/2+v(1)*exp(-(x-(v(3)-v(4)/2)).^2/2/(v(2)^2))/2+v(5);
end

function [p, pub, plb] = dbl1Dp0(trace, low, high)
    p(1) = max(trace(low:high));
    p(2) = (high - low)/10;
    p(3) = (low + high)/2;
    p(4) = (high - low)/4;
    p(5) = mean(trace([1:(low-1) (high+1):numel(trace)]));

    plb = [0 0 0 0 1.25*min(trace)-0.25*max(trace)];
    pub = [2.5*(max(trace)-min(trace)) numel(trace) Inf numel(trace) mean(trace)];
end

function f = dbl1Dcalcs(p, params)
    f = struct('f_amp', p(1),...
                'f_sigma', p(2),...
                'f_pos', p(3),...
                'f_sep', p(4),...   
                'f_bg', p(5));
    f.fwhm_um = 2*sqrt(2*log(2)) * f.f_sigma * params.pixel;
    f.sigma_um = f.f_sigma * params.pixel;
    f.nfit = 2 * sqrt(2*pi)*f.f_amp*abs(f.f_sigma);
    f.center_um = f.f_pos * params.pixel;
    f.sep_um = f.f_sep * params.pixel;
end

% thomas-fermi BEC profile
function f = tf1D(v,x)
    arg = 1 - ((x - v(3))/v(2)).^2;
    arg(arg < 0) = 0;
    f = v(4) + v(1).*(arg).^2;
end

function [p, pub, plb] = tf1Dp0(trace, low, high)
    [p, pub, plb] = gauss1Dp0(trace, low, high);
end

function f = tf1Dcalcs(p, params)
    f = struct('f_amp', p(1),...
                'f_rtf', p(2),...
                'f_pos', p(3),...
                'f_bg', p(4));
    f.rtf_um = f.f_rtf * params.pixel;
    f.nfit = f.f_amp*f.f_rtf*16/15;
    f.center_um = f.f_pos * params.pixel;
end