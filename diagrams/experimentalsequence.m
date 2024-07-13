clear;
close all;
clc;

dmdcolor = [0.6350 0.0780 0.1840];
imagingcolor = [0 0.4470 0.7410];
fieldcontrolcolor = [0.4940 0.1840 0.5560];
fieldcolor = [0.4660 0.6740 0.1880];

times = -6:0.005:13;
zeroarr = zeros(1, length(times));
dmd = 2 + (times < 0);
imaging = and(times > 12, times < 12.2);
fieldcontrol = 6.5 + 0.5.*(times > -5);
field = 5 - 0.5.*min(zeroarr+1, exp(-(times+5)/2));


f = figure('Position',[100,100,300,200]);
hold on;
plot(times, dmd, 'Color', dmdcolor, 'LineWidth', 1);
plot(times, imaging, 'Color', imagingcolor, 'LineWidth', 1);
plot(times, field, '--', 'Color', fieldcolor, 'LineWidth', 1);
plot(times, fieldcontrol, 'Color', fieldcontrolcolor, 'LineWidth', 1);

fill([times, fliplr(times)], [dmd, zeroarr+2],dmdcolor, ...
    'LineStyle','none','FaceAlpha',0.2);
fill([times, fliplr(times)], [imaging, zeroarr],imagingcolor, ...
    'LineStyle','none','FaceAlpha',0.2);
fill([times, fliplr(times)], [field, zeroarr+4],fieldcolor, ...
    'LineStyle','none','FaceAlpha',0.2);
fill([times, fliplr(times)], [fieldcontrol, zeroarr+6],fieldcontrolcolor, ...
    'LineStyle','none','FaceAlpha',0.2);

% text(5,0.25,'Imaging','Color',imagingcolor, ...
%     'HorizontalAlignment','center','VerticalAlignment','baseline');
% text(5,2.25,'DMD','Color',dmdcolor, ...
%     'HorizontalAlignment','center','VerticalAlignment','baseline');
% text(2.5,4.25,'Magnetic Field','Color',fieldcolor, ...
%     'HorizontalAlignment','center','VerticalAlignment','baseline');
% text(5,4.25,'Field Control','Color',fieldcontrolcolor, ...
%     'HorizontalAlignment','center','VerticalAlignment','baseline');

xlim([-6, 13]);
ylim([-1, 8]);
xticks([-5, 0, 12]);
yticks([0, 2, 4, 6]);
box('on');
yticklabels({"Imaging", "DMD Potential Strength", "Magnetic Field", "Magnetic Field Control"});
xticklabels({"-5", "0", "\fontname{Times}\itt"});
ax = gca;
% ax.YAxis.Visible = 'off';
ax.LineWidth = 1;
xlabel('Time (ms)');

smart_fig_export(gcf, 'timingsequence');
