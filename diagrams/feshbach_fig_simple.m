clear;
close all;
clc;

plot_defaults;

xi = 878;
xf = 898;
yi = -600;
yf = 600;
co = colororder();

Ca = co(2, :);
Cb = co(2, :);
Cc = co(3, :);
Ccs = co(1, :);
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



fig = figure('Position', [0, 0, 400, 220]);
% tiledlayout(3, 1, 'TileSpacing','tight');

%%% lics figure
specialvals = [880.65, 892.65];
specialvalcolors = [Ccs; Ca];

hold on;
box("on");
plot(bvals, a, 'LineWidth', 1.5, 'Color', Ca);
plot(bvals, cs, 'LineWidth', 1.5, 'Color', Ccs);
xlim([xi, xf]);
ylim([yi, yf]);
for ii = 1:length(specialvals)
    xline(specialvals(ii), '--', 'LineWidth', 1, 'Color', specialvalcolors(ii, :));
end
% set(gca, 'XTickLabels', []);
yticks(-500:250:500)
ylabel("scattering length (a_0)");
xlabel("magnetic field (G)");
% legend({'Li_a-Cs', 'Li_b-Cs'}, 'location', 'northwest')
text(882, 70, 'Cs-Cs scattering length a_{BB}', ...
    'Color', Ccs, 'Rotation', 11, 'HorizontalAlignment', 'left', ...
    'VerticalAlignment', 'bottom', 'fontsize', 11)
text(882, -80, 'Li-Cs scattering length a_{BF}', ...
    'Color', Ca, 'Rotation', 0, 'HorizontalAlignment', 'left', ...
    'VerticalAlignment', 'top', 'fontsize', 11)
% grid on;
yline(0, 'k-')
ax1 = gca;
fontsize(gcf, 12, "points")

% ax1top = axes('Position', get(ax1, 'Position'),'Color', 'none');
% set(ax1top, 'XAxisLocation', 'top','YAxisLocation','Right');
% box(ax1top, 'off');
% set(ax1top, 'XLim', get(ax1, 'XLim'),'YLim', get(ax1, 'YLim'));
% set(ax1top, 'XTick', specialvals, 'YTick', []);
% xtickangle(ax1top, 0);
% ax1top.FontSize = 11;
title(ax1, 'LiCs Scattering Lengths')

smart_fig_export(fig, 'feshbachfig_simple');