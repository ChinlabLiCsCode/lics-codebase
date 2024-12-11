clear;
close all;
clc;

plot_defaults;

xi = 800;
xf = 980;
yi = -600;
yf = 600;
co = colororder();

Ca = co(1, :);
Cb = co(2, :);
Cc = co(3, :);
Ccs = co(4, :);
Cab = co(5, :);
Cac = co(6, :);
Cbc = co(7, :);

bvals = xi:0.05:xf;

a = aLiCs(bvals, 'a');
b = aLiCs(bvals, 'b');
c = aLiCs_molscat(bvals, 'c');
cs = aCsCs(bvals);

a(abs(a)>2*yf) = NaN;
b(abs(b)>2*yf) = NaN;
c(abs(c)>2*yf) = NaN;
cs(abs(cs)>2*yf) = NaN;



fig = figure('Position', [0, 0, 1300, 800]);
% tiledlayout(3, 1, 'TileSpacing','tight');

%%% lics figure
specialvals = [816.1, 843.4, 889.0,  892.65, 943.4];
specialvalcolors = [Cb; Ca; Cb; Ca; Cb];

ax1 = subplot(3, 1, 1);
hold on;
box("on");
plot(bvals, a, 'LineWidth', 1.5, 'Color', Ca);
plot(bvals, b, 'LineWidth', 1.5, 'Color', Cb);
plot(bvals, c, 'LineWidth', 1.5, 'Color', Cc);
xlim([xi, xf]);
ylim([yi, yf]);
for ii = 1:length(specialvals)
    plot(specialvals(ii)+[0 0], [yi, yf], '--', 'LineWidth', 1, 'Color', specialvalcolors(ii, :));
end
% set(gca, 'XTickLabels', []);
yticks(-500:250:500)
ylabel("Scattering length [a_0]");
% xlabel("Magnetic field [G]");
legend({'Li_a-Cs', 'Li_b-Cs', 'Li_c-Cs'})
grid on;


ax1top = axes('Position', get(ax1, 'Position'),'Color', 'none');
set(ax1top, 'XAxisLocation', 'top','YAxisLocation','Right');
box(ax1top, 'off');
set(ax1top, 'XLim', get(ax1, 'XLim'),'YLim', get(ax1, 'YLim'));
set(ax1top, 'XTick', specialvals, 'YTick', []);
xtickangle(ax1top, 60);



%%% cs cs figure
specialvals = [820, 880.65];
specialvalcolors = [Ccs; Ccs];

ax2 = subplot(3, 1, 2);
hold on;
box("on");
plot(bvals, cs, 'LineWidth', 1.5, 'Color', Ccs);
xlim([xi, xf]);
ylim([yi, yf]);
for ii = 1:length(specialvals)
    plot(specialvals(ii)+[0 0], [yi, yf], '--', 'LineWidth', 1, 'Color', specialvalcolors(ii, :));
end
% set(gca, 'XTickLabels', []);
yticks(-500:250:500)
ylabel("Scattering length [a_0]");
% xlabel("Magnetic field [G]");
legend({'Cs-Cs'})
grid on;


ax2top = axes('Position', get(gca, 'Position'),'Color', 'none');
set(ax2top, 'XAxisLocation', 'top','YAxisLocation','Right');
box(ax2top, 'off');
set(ax2top, 'XLim', get(ax2, 'XLim'),'YLim', get(ax2, 'YLim'));
set(ax2top, 'XTick', specialvals, 'YTick', []);
xtickangle(ax2top, 60);



%%% li li figure
yi = -2e4;
yf = 2e4;
ab = aLiLi(bvals, 'ab');
ac = aLiLi(bvals, 'ac');
bc = aLiLi(bvals, 'bc');

ab(abs(ab)>2*yf) = NaN;
ac(abs(ac)>2*yf) = NaN;
bc(abs(bc)>2*yf) = NaN;

specialvals = [809.76, 832.18];
specialvalcolors = [Cbc; Cab];

ax3 = subplot(3, 1, 3);
hold on;
box("on");
plot(bvals, ab, 'LineWidth', 1.5, 'Color', Cab);
plot(bvals, ac, 'LineWidth', 1.5, 'Color', Cac);
plot(bvals, bc, 'LineWidth', 1.5, 'Color', Cbc);
xlim([xi, xf]);
ylim([yi, yf]);
for ii = 1:length(specialvals)
    plot(specialvals(ii)+[0 0], [yi, yf], '--', 'LineWidth', 1, 'Color', specialvalcolors(ii, :));
end
% set(gca, 'XTickLabels', []);
yticks(yi:(yf-yi)/4:yf)
ylabel("Scattering length [a_0]");
xlabel("Magnetic field [G]");
legend({'Li_a-Li_b', 'Li_a-Li_c', 'Li_b-Li_c'})
grid on;


ax3top = axes('Position', get(gca, 'Position'),'Color', 'none');
set(ax3top, 'XAxisLocation', 'top','YAxisLocation','Right');
box(ax3top, 'off');
set(ax3top, 'XLim', get(ax3, 'XLim'),'YLim', get(ax3, 'YLim'));
set(ax3top, 'XTick', specialvals, 'YTick', []);
xtickangle(ax3top, 60);


smart_fig_export(fig, 'feshbachfig');