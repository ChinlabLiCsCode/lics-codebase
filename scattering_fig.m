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

bvals = xi:0.05:xf;

a = aLiCs(bvals, 'a');
b = aLiCs(bvals, 'b');
c = aCsCs(bvals);

a(abs(a)>2*yf) = NaN;
b(abs(b)>2*yf) = NaN;
c(abs(c)>2*yf) = NaN;

specialvals = [816.1, 843.4, 880.65, 889.0,  892.65, 943.4];
specialvalcolors = [Cb; Ca; Cc; Cb; Ca; Cb];

fig = figure('Position', [100, 100, 900, 300]);
ax1 = axes(fig, "OuterPosition", [0, 0, 1, 0.9]);
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
xlabel("Magnetic field [G]");
legend({'Li_a-Cs', 'Li_b-Cs', 'Cs-Cs'})
grid on;


ax2 = axes('Position', get(gca, 'Position'),'Color', 'none');
set(ax2, 'XAxisLocation', 'top','YAxisLocation','Right');
box(ax2, 'off');
set(ax2, 'XLim', get(ax1, 'XLim'),'YLim', get(ax1, 'YLim'));
set(ax2, 'XTick', specialvals, 'YTick', []);
xtickangle(ax2, 60);



smart_fig_export(fig, 'feshbachfig');