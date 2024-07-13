clear; close all; clc;

today = [2023 12 04];
build_params;
plot_defaults;


%% field calibration 
clc; close all; 
Bdfset = 53:55;
Bshots = 56:59;
Bscan = proc_scan(paramsCH_B, Bshots, Bdfset);
Bvals = field_cal(horzcat(Bscan.fd.x_sep), 11447.750);
B = mean(Bvals);
Bse = std(Bvals);
fprintf('B = %.3f (%d)\n\n', B, round(1e3 * Bse));


%% dual health check
clc; close all;
vdfset = 66:68;
shots = 69:73;
cshealthcheck = proc_scan(paramsCV_IS, shots, vdfset, 'macrocalc', {'x_nfit', 'mean', 'x_rTF', 'mean'});




%% save params and workspace

save(sprintf('workspace_%04d%02d%02d.mat', today(1), today(2), today(3)));
save_params(today);

%% check if params worked 
clear; close all; clc;
today = [2023 12 05];
load_params([2023 12 05], [2023 12 07]);

%% test peak finding 
plot_defaults;
x = (-5:5)';
y = exp(-x.^2 /6) + randn(size(x))/8;

% perform skew normal fit
ft = fittype(@(x0, amp, sigma, skew, bg, x) ...
    skewgauss(x0, amp, sigma, skew, bg, x));
sp = [mean(x), max(y), std(x)/4, 0, 0];
fo = fit(x, y, ft, StartPoint=sp);

% find peak
[bestx, maxy] = fminbnd(@(x) -fo(x), min(x), max(x));


figure();
hold on;
scatter(x, y, LineWidth=1);
finex = linspace(min(x), max(x), 100);
plot(finex, fo(finex));
yl = ylim();
plot([bestx, bestx], yl, 'r');
ylim(yl);




function y = skewgauss(x0, amp, sigma, skew, bg, x)
x = (x - x0) ./ sigma;
a = exp(-x.^2 / 2);
b = 1 + erf(skew * x / 2);
y = bg + 2 * amp * a .* b;
end