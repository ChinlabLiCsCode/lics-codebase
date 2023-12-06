function results = bimodal_fit_2x1d(params, img, varargin)

% initialize default inputs
crop = 'mask';
c0x = 'guess';
c0y = 'guess';

% process varargin
for setting = 1:2:length(varargin)
    switch varargin{setting}
        case 'crop'
            crop = varargin{setting + 1};
        case 'c0x'
            c0x = varargin{setting + 1};
        case 'c0y'
            c0y = varargin{setting + 1};
    end
end

% if given an image stack, average first
img = squeeze(img);
while ndims(img) > 2
    img = squeeze(mean(img, 1));
end

pix = params.pixel;

% define crop window properly
if ~isnumeric(crop)
    switch crop 
        case 'mask'
            crop = params.mask;
        case 'none'
            [Y, X] = size(img);
            crop = [1, X, 1, Y];
        % in the third case, you can directly pass a 4-element array
    end
end

% crop the supplied image
img = img(crop(3):crop(4), crop(1):crop(2));
[Y, X] = size(img);

xtrc = trapz(img, 1)';
ytrc = trapz(img, 2);
xpix = (1:X)' - X/2;
ypix = (1:Y)' - Y/2;

disp(size(xtrc))
disp(size(xpix));
% define fit type
ftbm = fittype(@(x0, aTF, aG, rTF, rG, x)...
    fit1dbm(x0, aTF, aG, rTF, rG, x));

%% X fit 
% set upper bounds, lower bounds, and starting point for fit params
c0x = [0, max(xtrc), 0.1, 50, 100];
lbx = [-100, 0, 0, 0, 0];
ubx = [100, Inf, Inf, 300, 300];

% do fit
fox = fit(xpix, xtrc, ftbm, Start=c0x, Lower=lbx, Upper=ubx);

% get traces 
xtrace_bm = fox(xpix);
xtrace_tf = fit1dtf(fox.x0, fox.aTF, fox.rTF, xpix);
xtrace_gauss = fit1dgauss(fox.x0, fox.aG, fox.rG, xpix);


% get out useful parameters and error bounds from those fits 
fvx = coeffvalues(fox); % values
ul = confint(fox); % 95% confidence intervals 
fvx_se = (ul(2, :) - ul(1, :))/4; % 1 sigma error
      
% get condensate number
n0x = fox.aTF * fox.rTF * 16/15;
% get condensate number error by combining errors in quadrature
n0x_se = n0x * sqrt(...
    (fvx_se(2)/fvx(2))^2 + (fvx_se(4)/fvx(4))^2);



figure(Units='normalized', Position=[0.25, 0.25, 0.5, 0.5]);
tiledlayout(1, 2);

nexttile;
hold on;
plot(xpix, xtrc, 'o');



results = struct('n0x', n0x, 'n0x_se', n0x_se, 'fox', fox);

end

% 1d bimodal fit
function f = fit1dbm(x0, aTF, aG, rTF, rG, x)
arg = 1 - ((x - x0) ./ rTF).^2;
arg(arg < 0) = 0;
h = aTF .* arg.^2;
g = aG .* exp(-((x - x0).^2)/(2 * rG.^2));
f = h + g;
end

% 1d tf profile
function h = fit1dtf(x0, aTF, rTF, x)
arg = 1 - ((x - x0) ./ rTF).^2;
arg(arg < 0) = 0;
h = aTF .* arg.^2;
end

% 1d gaussian profile
function g = fit1dgauss(x0, aG, rG, x)
g = aG .* exp(-((x - x0).^2)/(2 * rG.^2));
end
