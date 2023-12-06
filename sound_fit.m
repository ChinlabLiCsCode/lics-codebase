function out_info = soundplot_2023(params, shots, df_set, times, abf, ...
    mask, imgsin, fittimes, savefig)
% this version does a 2-d surface fit
% rewritten almost from scratch by Henry in November 2023 to remove dead
% weight

if nargin < 9
    savefig = false;
end

% fittimes are for if you want to only fit to a certain time range
if nargin < 8
    fittimes = 1:length(times);
end

% allow user to pass the preloaded images
if nargin < 7
    imgs = proc_imgs(params, shots, df_set);
else
    if imgsin
        imgs = imgsin;
    else 
        imgs = proc_imgs(params, shots, df_set);
    end
end


% allow user to pass their own mask for cropping
if nargin < 6
    mask = params.mask;
end


% name string for output figures
namestr = sprintf('Sound propagation aBF = %d a0', round(abf, 2-floor(log10(abs(abf)))));

% start saving inputs to output structure
out_info = struct();
out_info.mask = mask;
out_info.shots = shots;
out_info.times = times;
out_info.params = params;
out_info.imgs = imgs;
out_info.abf = abf;
out_info.namestr = namestr;


% average over multiple images
sz = size(imgs);
if length(sz) == 4
    imgsavg = squeeze(mean(imgs,1));
elseif length(sz) == 3
    imgsavg = imgs;
end

% crop image
imgsavgc = imgsavg(:, mask(1):mask(2), mask(3):mask(4));

% integrate along y axis 
n1d = squeeze(trapz(imgsavgc, 3));
norm1d = n1d ./ max(n1d, [], 2);

% get dimensions
[nT, nX, nY] = size(imgsavgc);
xpix = ((1:nX)') - nX/2;
ypix = (1:nY)';

% get pixel size
pix = params.pixel;

% initialize loop variables
n1dnobg = norm1d; % background subtracted density 
n1dbg = norm1d; % the fit result
n0 = zeros(nT, 1); % condensate number
sn0 = zeros(nT, 1);

for t=1:nT

    % do a fit1dbmbg fit and subtract it to remove background 

    % define fit type
    ftbm = fittype(@(x0, aTF, aG, rTF, rG, bg, x)...
        fit1dbmbg(x0, aTF, aG, rTF, rG, bg, x));
    % set upper bounds, lower bounds, and starting point for fit params
    sp = [0, 1, 0.1, 50, 100, 0];
    lb = [-100, 0, 0, 0, 0, -10];
    ub = [100, Inf, Inf, 300, 300, 10];
    % do fit
    fobm = fit(xpix, norm1d(t, :)', ...
        ftbm, Start=sp, Lower=lb, Upper=ub);
    % save background subtracted density 
    n1dnobg(t, :) = norm1d(t, :) - fobm(xpix)';
    n1dbg(t, :) = fobm(xpix)';

    % get out useful parameters and error bounds from those fits 
    fvbm = coeffvalues(fobm); % values
    ul = confint(fobm); % 95% confidence intervals 
    fvbm_err = (ul(2, :) - ul(1, :))/4; % 1 sigma error
          
    % get condensate number. have to rescale by max(n1d)
    n0(t) = max(max(n1d)) * fvbm(2) * fvbm(4) * 16/15;
    % get condensate number error by combining errors in quadrature
    sn0(t) = n0(t) * sqrt(...
        (fvbm_err(2)/fvbm(2))^2 + (fvbm_err(4)/fvbm(4))^2);
    
end


% do a 2d surface fit to the background-less profile
% make x and t grid 
[X, T] = meshgrid(xpix, times);
% define fit type
ft2d = fittype(@(amp, gamma, x0, sigma, v, b, bg, x, t)...
    fit2dpert(amp, gamma, x0, sigma, v, b, bg, x, t),...
    independent=["x", "t"]);
% set upper bounds, lower bounds, and starting point for fit params
sp = [-0.5, 0.1, 0, 3, 1, 0, 0];
lb = [-10, 0, -100, 0, 0, 0, -10];
ub = [0, 10, 100, 10, 20, 10];
% do fit
fo2d = fit([X(:), T(:)], n1dnobg(:), ...
    ft2d, Start=sp, Lower=lb, Upper=ub);
% evaluate fit
feval2d = reshape(fo2d([X(:), T(:)]), size(n1d));

% rebuild full distribution 
norm1dfit = n1dbg + feval2d;
n1dfit = norm1dfit .* max(n1d, [], 2);

% get parameters out from fit 
fv2d = coeffvalues(fo2d); % values
ul = confint(fo2d); % 95% confidence intervals 
fv2d_err = (ul(2, :) - ul(1, :))/4; % 1 sigma error

c = 1e6 * pix * fv2d(5);
sc = 1e6 * pix * fv2d_err(5);
gamma = fv2d(2);
sgamma = fv2d_err(2);


% load variables into output object
out_info.c = c;
out_info.sc = sc;
out_info.gamma = gamma;
out_info.sgamma = sgamma;
out_info.n0 = n0;
out_info.sn0 = sn0;


% plotting section

% initialize diagnostic figure
plot_defaults;
figure(Units='normalized', OuterPosition=[0 0 1 1]);
tiledlayout(3, 3, TileSpacing='compact');
sgtitle(namestr, FontSize=30);

% show a single raw image 
nexttile([1, 2]);
imagesc(xpix, ypix, squeeze(imgsavgc(1, :, :))');
axis image;
xlabel('x position [pix]');
ylabel('y position [pix]');
title('cropped t = 0 raw image');
cb = colorbar();
ylabel(cb, 'atoms/pix^2');
colormap(gca, cs_cbar);

% show condensate fraction over time
ebaropts = {'CapSize', 0, 'LineWidth', 1, 'LineStyle', 'none', ...
    'Marker', 'o', 'MarkerSize', 6};
co = colororder();
nexttile;
errorbar(times, n0, sn0, ebaropts{:}, ...
    'Color', co(1, :), 'MarkerFaceColor', lighter(co(1, :)));
xlabel('time [ms]');
ylabel('number');
title('condensate number from fits');
xlim([-0.5, max(times)+0.5]);
ylim([0, max(n0) * 1.5]);


% show n1d 
nexttile;
imagesc(xpix, times, n1d);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('1D density evolution');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');

% show n1dprime
nexttile;
imagesc(xpix, times, norm1d);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('normalized 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [a.u.]');

% show n1dnobg
nexttile;
imagesc(xpix, times, n1dnobg);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('background subtracted 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [a.u.]');
colormap(gca, brewermap(256, 'PuBu'));
l = clim();


% plot result of fit
% show reconstruction of full distribution 
% show n1dfit plot
nexttile;
imagesc(xpix, times, n1dfit);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('fitted 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [atoms/pix]');

% show n1dprime
nexttile;
imagesc(xpix, times, norm1dfit);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('fitted normalized 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [a.u.]');

% background subtracted
nexttile;
imagesc(xpix, times, feval2d);
set(gca, 'YDir', 'normal');
xlabel('x position [pix]');
ylabel('time [ms]');
title('fitted background subtracted 1D density evolution');
cb = colorbar();
ylabel(cb, 'density [a.u.]');
colormap(gca, brewermap(256, 'PuBu'));
clim(l);

if savefig
    smart_fig_export(gcf, namestr);
end

end







% 1d bimodal fit
function f = fit1dbmbg(x0, aTF, aG, rTF, rG, bg, x)
arg = 1 - ((x - x0) ./ rTF).^2;
arg(arg < 0) = 0;
h = aTF .* arg.^2;
%Set negative entires to zero for TF distribution, using indices to do so fast
%symmetric perturbation
g = aG .* exp(-((x - x0).^2)/(2 * rG.^2));
f = h + g + bg;

end

% 2d perturbation fit
function f = fit2dpert(amp, gamma, x0, sigma, v, b, bg, x, t)
f = bg + amp .* exp(-gamma .* t) .*( ...
    exp(-(x - x0 - v.*t).^2 ./ (2 * (sigma + b.*t).^2)) ...
    + exp(-(x - x0 + v.*t).^2 ./ (2 * (sigma + b.*t).^2)));
end


