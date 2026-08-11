function out_info = sound_fit_dual(paramsC, paramsL, shots, dfset, times, varargin)
% out_info = sound_fit_dual(paramsC, paramsL, shots, dfset, times, varargin)
%
%


%% handle inputs

abf = NaN;
linum = NaN;
sound = true; 
mask = paramsC.mask;
savefig = true;
fittimes = 1:length(times);
fitxrng = 70;
imgsin = false;


% process varargin
for setting = 1:2:length(varargin)
    switch varargin{setting}
        case 'abf'
            abf = varargin{setting + 1};
        case 'linum'
            linum = varargin{setting + 1};
        case 'sound'
            sound = varargin{setting + 1};
        case 'mask' 
            mask = varargin{setting + 1};
        case 'fitxrng'
            fitxrng = varargin{setting + 1};
        case 'savefig' 
            savefig = varargin{setting + 1};
        case 'fittimes'
            fittimes = varargin{setting + 1};
        case 'imgsin'
            imgsin = varargin{setting + 1};
        otherwise
            error('Invalid input: %s', varargin{setting});
    end
end

if imgsin
    imgsC = imgsin{1};
    imgsL = imgsin{2};
else 
    imgsC = proc_imgs(paramsC, shots, dfset);
    imgsL = proc_imgs(paramsL, shots, dfset);
end


% name string for output figures
namestr = sprintf('Sound propagation aBF=%d linum=%.2f', ...
    round(abf, 2-floor(log10(abs(abf)))), linum);

% start saving inputs to output structure
out_info = struct();
out_info.mask = mask;
out_info.pixforsoundfit = fitxrng;
out_info.shots = shots;
out_info.times = times;
out_info.paramsC = paramsC;
out_info.paramsL = paramsL;
out_info.imgsC = imgsC;
out_info.imgsL = imgsL;
out_info.abf = abf;
out_info.linum = linum;
out_info.namestr = namestr;
out_info.sound = sound;


%% begin processing 
% crop Cs images
imgsC = imgsC(:, :, mask(1):mask(2), mask(3):mask(4));

% get total atoms nums 
ncountC = mean(sum(imgsC, [3, 4]), 1);
ncountCse = std(sum(imgsC, [3, 4]), [], 1);
ncountL = mean(sum(imgsL, [3, 4]), 1);
ncountLse = std(sum(imgsL, [3, 4]), [], 1);

% compute expected bare sound speed
[v0, ~, ~] = v0nB_from_NB(ncountC(1));
v0se = v0 * (1/5) * ncountCse / ncountC; % 1/5 factor comes from power 

% average over multiple images
imgsCavg = squeeze(mean(imgsC, 1));
imgsLavg = squeeze(mean(imgsL, 1));

% integrate along y axis 
n1d = squeeze(trapz(imgsCavg, 2));

% get dimensions
[nT, nY, nX] = size(imgsCavg);
xpix = ((1:nX)') - nX/2;
ypix = (1:nY)';

% get pixel size
pix = paramsC.pixel;

% initialize loop variables
n1dnobg = n1d; % background subtracted density 
n1dnobgnorm = n1d; % background subtracted and normalized
n1dbg = n1d; % the fit result
n1dbgscale = zeros(nT, 1); % the scale factor for normalizing 
n0 = zeros(nT, 1); % condensate number
sn0 = zeros(nT, 1);

%% do a bimodal fit and subtract it to remove background 

% define fit type
ftbm = fittype(@(x0, aTF, aG, rTF, rG, bg, x)...
    fit1dbmbg(x0, aTF, aG, rTF, rG, bg, x));

% set upper bounds, lower bounds, and starting point for fit params
sp = [0, 1, 0.1, 50, 100, 0];
lb = [-100, 0, 0, 0, 0, -10];
ub = [100, Inf, Inf, 300, 300, 10];

for t=1:nT

    % set start point amplitude based on data scale 
    sp(2) = max(n1d(t, :));
    sp(3) = max(n1d(t, :)) / 10;
    
    % do fit
    fobm = fit(xpix, n1d(t, :)', ...
        ftbm, Start=sp, Lower=lb, Upper=ub);

    % save background subtracted density 
    n1dbg(t, :) = fobm(xpix)';
    n1dnobg(t, :) = n1d(t, :) - n1dbg(t, :);
    n1dbgscale(t) = max(abs(n1dnobg(t, :)));

    % get out useful parameters and error bounds from those fits 
    fvbm = coeffvalues(fobm); % values
    ul = confint(fobm); % 95% confidence intervals 
    fvbm_err = (ul(2, :) - ul(1, :))/4; % 1 sigma error
          
    % get condensate number. have to rescale by max(n1d)
    n0(t) = fvbm(2) * fvbm(4) * 16/15;

    % get condensate number error by combining errors in quadrature
    sn0(t) = n0(t) * sqrt(...
        (fvbm_err(2)/fvbm(2))^2 + (fvbm_err(4)/fvbm(4))^2);
    
end


% do a 2d surface fit to the normalized background-less profile
xpixfit = (1:fitxrng)' + round((nX - fitxrng) / 2);
xpixfitax = xpixfit - mean(xpixfit);
n1dforfit = n1dnobg(fittimes, xpixfit);

timesfit = times(fittimes);


% make x and t grid 
[X, T] = meshgrid(xpixfitax, timesfit);


%% FIRST we do the normal sound fit 

% set upper bounds, lower bounds, and starting point for fit params
% order is: [amp, x0, sigma, v, b, gamma]
sp = [min(min(n1dnobg)), 0, 3, 0.75, 0.1, 0.1];
lb = [-300, -100, 0.1, 0, 0, 0];
ub = [0, 100, 10, 1.5, 10, 10];

% define weights to make later values more important
weights = repmat(abs(1./n1dbgscale(fittimes)), [1, fitxrng]);

% define fit type
ft2d = fittype(@(amp, x0, sigma, v, b, gamma, x, t)...
    fit2dvarsound(amp, x0, sigma, v, b, gamma, x, t),...
    independent=["x", "t"]);

% do fit
[fo2d, gof2d] = fit([X(:), T(:)], n1dforfit(:), ...
    ft2d, Start=sp, Lower=lb, Upper=ub, weights=weights(:));
rsquared2d = gof2d.adjrsquare;

%% SECOND we do the single dip fit for comparison 

% set upper bounds, lower bounds, and starting point for fit params
% order is: [amp, x0, sigma, b, gamma]
sp = [min(min(n1dnobg)), 0, 3, 0.1, 0.1];
lb = [-300, -100, 0.1, 0, 0];
ub = [0, 100, 10, 10, 10];

% define weights to make later values more important
weights = repmat(abs(1./n1dbgscale), [1, fitxrng]);

% define fit type
ft2dns = fittype(@(amp, x0, sigma, b, gamma, x, t)...
    fit2dnosound(amp, x0, sigma, b, gamma, x, t),...
    independent=["x", "t"]);

% do fit
[fo2dns, gof2dns] = fit([X(:), T(:)], n1dforfit(:), ...
    ft2dns, Start=sp, Lower=lb, Upper=ub, weights=weights(:));
rsquared2dns = gof2dns.adjrsquare;

%% processing after 2d fits

% evaluate fits
[X, T] = meshgrid(xpix, times);
feval2d = reshape(fo2d([X(:), T(:)]), size(n1d));
feval2dns = reshape(fo2dns([X(:), T(:)]), size(n1d));

% rebuild full distribution 
n1dfit = n1dbg + feval2d;
n1dfitns = n1dbg + feval2dns;

% get parameters out from fit 
fv2d = coeffvalues(fo2d); % values
ul = confint(fo2d); % 95% confidence intervals 
fv2d_err = (ul(2, :) - ul(1, :))/4; % 1 sigma error

c = 1e6 * pix * fv2d(4);
sc = 1e6 * pix * fv2d_err(4);
gamma = fv2d(6);
sgamma = fv2d_err(6);


% load variables into output object
out_info.c = c;
out_info.sc = sc;
out_info.c0 = v0;
out_info.sc0 = v0se;
out_info.coverc0 = c / v0;
out_info.scoverc0 = (c / v0) * sqrt((sc/c)^2 + (v0se/v0)^2);
out_info.gamma = gamma;
out_info.sgamma = sgamma;
out_info.n0 = n0;
out_info.sn0 = sn0;
out_info.ncountC = ncountC;
out_info.ncountCse = ncountCse;
out_info.ncountL = ncountL;
out_info.ncountLse = ncountLse;
out_info.rsquared_sound = rsquared2d;
out_info.rsquared_nosound = rsquared2dns;
out_info.soundbyrsquared = rsquared2d > rsquared2dns;

fprintf('c = %.2f (%.2f)\n', c, sc);
fprintf('r^2 (sound) = %.3f\n', rsquared2d);
fprintf('r^2 (no sound) = %.3f\n\n', rsquared2dns);

%% plotting section

if savefig

% initialize diagnostic figure
plot_defaults;
figure(Units='normalized', OuterPosition=[0 0 1 1]);
tiledlayout(6, 3, TileSpacing='compact');
sgtitle(namestr, FontSize=30);

% show a single raw image (Cs)
nexttile(3);
imagesc(xpix, ypix, squeeze(imgsCavg(1, :, :)));
axis image;
xlabel('x position [pix]');
ylabel('y position [pix]');
title('t = 0 Cs image (cropped)');
cb = colorbar();
ylabel(cb, 'atoms/pix^2');
colormap(gca, cs_cbar);

% show a single raw image (Li)
nexttile(6);
imagesc(squeeze(imgsLavg(1, :, :)));
axis image;
xlabel('x position [pix]');
ylabel('y position [pix]');
title('t = 0 Li image');
cb = colorbar();
ylabel(cb, 'atoms/pix^2');
colormap(gca, li_cbar);


% show numbers over time
ebaropts = {'CapSize', 2, 'LineWidth', 1, 'LineStyle', 'none', ...
    'Marker', 'o', 'MarkerSize', 6};
nexttile(9, [2, 1]);
hold on;
errorbar(times, ncountC, ncountCse, ebaropts{:}, ...
    'Color', blue, 'MarkerFaceColor', lighter(blue));
errorbar(times, ncountL, ncountLse, ebaropts{:}, ...
    'Color', red, 'MarkerFaceColor', lighter(red));
xlabel('time [ms]');
ylabel('number');
title('numbers vs. time');
xlim([-0.5, max(times)+0.5]);
legend({"Cs [count]", "Li [count]"});
% ylim([0, max(n0) * 1.5]);


%% plots of full n1d

% show n1d 
nexttile(1, [1, 2]);
imagesc(xpix, times, n1d);
set(gca, 'YDir', 'normal');
% xlabel('x position [pix]');
ylabel('time [ms]');
title('1D density evolution');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
l = clim();

% show n1dfit plot
nexttile(4, [1, 2]);
imagesc(xpix, times, n1dfit);
set(gca, 'YDir', 'normal');
% xlabel('x position [pix]');
ylabel('time [ms]');
title('fitted with sound');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
clim(l);

% show n1dfit no sound plot
nexttile(7, [1, 2]);
imagesc(xpix, times, n1dfitns);
set(gca, 'YDir', 'normal');
% xlabel('x position [pix]');
ylabel('time [ms]');
title('fitted no sound');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
clim(l);



%% plots of n1d no background 

% show n1dnobg
nexttile(10, [1, 2]);
imagesc(xpix, times, n1dnobg);
set(gca, 'YDir', 'normal');
% xlabel('x position [pix]');
ylabel('time [ms]');
title('background subtracted 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
colormap(gca, brewermap(256, 'PuBu'));
l = clim();

% a few lines to help with boxes to demonstrate fit region
xl = xlim();
yl = ylim();
xft = xpix([xpixfit(1), xpixfit(end)]);
yft = [min(times)-1, max(times)+1];

% show sound fit 
nexttile(13, [1, 2]);
imagesc(xpix, times, feval2d);
hold on;
plot([xft(1), xft(1)], [yft(1), yft(2)], 'r-');
plot([xft(2), xft(2)], [yft(1), yft(2)], 'r-');
set(gca, 'YDir', 'normal');
% xlabel('x position [pix]');
ylabel('time [ms]');
title(sprintf('fitted with sound (r^2 = %.2f)', rsquared2d));
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
colormap(gca, brewermap(256, 'PuBu'));
clim(l);
xlim(xl);
ylim(yl);

% show no sound fit 
nexttile(16, [1, 2]);
imagesc(xpix, times, feval2dns);
hold on;
plot([xft(1), xft(1)], [yft(1), yft(2)], 'r-');
plot([xft(2), xft(2)], [yft(1), yft(2)], 'r-');
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title(sprintf('fitted no sound (r^2 = %.2f)', rsquared2dns));
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');
colormap(gca, brewermap(256, 'PuBu'));
clim(l);
xlim(xl);
ylim(yl);

end

% save figure is savefig = 2
if savefig == 2
    smart_fig_export(gcf, namestr);
end

end


% 1d bimodal fit
function f = fit1dbmbg(x0, aTF, aG, rTF, rG, bg, x)
arg = 1 - ((x - x0) ./ rTF).^2;
arg(arg < 0) = 0;
h = aTF .* arg.^2;
g = aG .* exp(-((x - x0).^2)/(2 * rG.^2));
f = h + g + bg;
end


% 2d sound speed fit with variable sound speed and gamma
function f = fit2dvarsound(amp, x0, sigma, v, b, gamma, x, t)
% p = v.*t + 0.5 * dvdt .* t.^2;
p = v.*t;
f = amp .* exp(-gamma .* t) .*( ...
    exp(-(x - x0 - p).^2 ./ (2 * (sigma + b.*t).^2)) ...
    + exp(-(x - x0 + p).^2 ./ (2 * (sigma + b.*t).^2)));
end

% 2d dip fit with no sound propagation
function f = fit2dnosound(amp, x0, sigma, b, gamma, x, t)
f = amp .* exp(-gamma .* t) .*( ...
    exp(-(x - x0).^2 ./ (2 * (sigma + b.*t).^2)) ...
    + exp(-(x - x0).^2 ./ (2 * (sigma + b.*t).^2)));
end

% calculate v0 and nB_peak
function [v0, nB_peak, muB] = v0nB_from_NB(NB)
make_constants_expanded;
muB = 15 / (16 * pi * sqrt(2));
muB = muB * NB * gBB * omegaBx * omegaBy * omegaBz;
muB = (muB * mB^(3/2))^(2/5);
nB_peak = muB/gBB;
c0 = sqrt(gBB * nB_peak / mB);
v0 = c0 * sqrt((1 - 1/4) / 2);
end

