function results = bimodal_fit_2x1d(params, img, varargin)

% initialize default inputs
crop = 'mask';
% c0x = 'guess';
% c0y = 'guess';

% process varargin
for setting = 1:2:length(varargin)
    switch varargin{setting}
        case 'crop'
            crop = varargin{setting + 1};
        % case 'c0x'
        %     c0x = varargin{setting + 1};
        % case 'c0y'
        %     c0y = varargin{setting + 1};
    end
end

% if given an image stack, average first
img = squeeze(img);
while ndims(img) > 2
    img = squeeze(mean(img, 1));
end



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

% rescale and make trace axes 
pix = 1e6*params.pixel;
xtrc = trapz(img, 1)' ./ pix; % units of atoms/um
ytrc = trapz(img, 2) ./ pix; % units of atoms/um
xum = pix .* (1:X)'; % units of um
yum = pix .* (1:Y)'; % units of um

% subtract off center of mass 
xcom = sum(xtrc .* xum) ./ sum(xtrc)
ycom = sum(ytrc .* yum) ./ sum(ytrc);
xum = xum - xcom;
yum = yum - ycom;

% make finer xaxis for fits 
xum_fine = linspace(min(xum), max(xum), 1000);
yum_fine = linspace(min(yum), max(yum), 1000);


% define fit types
ftbm = fittype(@(x0, aTF, aG, rTF, rG, x)...
    fit1dbm(x0, aTF, aG, rTF, rG, x));
fttf = fittype(@(x0, aTF, rTF, x)...
    fit1dtf(x0, aTF, rTF, x));

%% X fit

% do a pure thomas-fermi fit first
sp = [0, max(xtrc), std(xum)/4];
lb = [-100, 1, 0.5];
ub = [100, 2*max(xtrc), 300];

tffitx = fit(xum, xtrc, fttf, Start=sp, Lower=lb, Upper=ub);
tffvalsx = coeffvalues(tffitx); % values
ul = confint(tffitx) % 95% confidence intervals 
tffsex = (ul(2, :) - ul(1, :))/4; % 1 sigma error

% set upper bounds, lower bounds, and starting point for fit params
sp = [0, 0.9*max(xtrc), 0.1*max(xtrc), std(xum)/4, std(xum)];
lbx = [-100, 1, 1, 0.5, 0.5];
ubx = [100, Inf, Inf, 300, 300];

% do fit
fox = fit(xum, xtrc, ftbm, Start=sp, Lower=lbx, Upper=ubx);

% get out useful parameters and error bounds from those fits 
fvx = coeffvalues(fox) % values
ul = confint(fox) % 95% confidence intervals 
fvx_se = (ul(2, :) - ul(1, :))/4; % 1 sigma error
disp(fvx_se);

% if gaussian part is impossible to fit, do just a tf fit


% get traces 
xtrc_bm = fox(xum_fine);
xtrc_tf = fit1dtf(fox.x0, fox.aTF, fox.rTF, xum_fine);
xtrc_gauss = fit1dgauss(fox.x0, fox.aG, fox.rG, xum_fine);



      
% get condensate number
n0x = fox.aTF * fox.rTF * 16/15;
% get condensate number error by combining errors in quadrature
n0x_se = n0x * sqrt(...
    (fvx_se(2)/fvx(2))^2 + (fvx_se(4)/fvx(4))^2);

% plot result
figure(Units='normalized', Position=[0.25, 0.25, 0.7, 0.5]);
plot_defaults;
tiledlayout(1, 2);

nexttile;
hold on;
plot(xum_fine, xtrc_bm, '-', Color='k', LineWidth=1.5);
plot(xum_fine, xtrc_tf, '--', Color=green);
plot(xum_fine, xtrc_gauss, '--', Color=purple);
scatter(xum, xtrc, 64, 'o', MarkerEdgeColor=blue, ...
    MarkerFaceColor=blue, MarkerFaceAlpha=0.3);
xlabel('Position [µm]');
ylabel('Density [atoms/µm]');
legend({'bimodal fit', 'Thomas-Fermi part', 'gaussian part', 'data'});
xlim([min(xum), max(xum)]);

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
