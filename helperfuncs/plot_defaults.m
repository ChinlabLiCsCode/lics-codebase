set(groot, 'defaultLineLineWidth', 1);
set(groot, 'defaultErrorBarLineWidth', 1);
set(groot, 'defaultErrorBarCapSize', 1);
set(groot, 'defaultScatterMarkerFaceAlpha', 0.2);
set(groot, 'defaultScatterLineWidth', 1);
set(groot, 'defaultAxesLineWidth', 1);
set(groot, 'defaultAxesBox', true);
set(groot, 'defaultAxesFontSize', 12);

cs_cbar = cubehelix(256, -0.25, 0, 2, 1.1, [0,0.95], [0,0.95]);
li_cbar = cubehelix(256, 1, 0, 2, 1.1, [0,0.95], [0,0.95]);

% cs_blue = "#0072BD";
% li_red = "#A2142F";
li_red = li_cbar(128,:);
cs_blue = cs_cbar(128,:);

co = [...        
    0    0.4470    0.7410
    0.8500    0.3250    0.0980
    0.9290    0.6940    0.1250
    0.4940    0.1840    0.5560
    0.4660    0.6740    0.1880
    0.3010    0.7450    0.9330
    0.6350    0.0780    0.1840
    1.0000    0.2700    0.2270
    0.3960    0.5090    0.9920
    0.3000    0.3000    0.3000
         0    0.6390    0.6390
    0.7960    0.5170    0.3640
    0.8000    0.0000    0.8000];
blue = co(1, :);
orange = co(2, :);
yellow = co(3, :);
purple = co(4, :);
green = co(5, :);
lightblue = co(6, :);
maroon = co(7, :);
red = co(8, :);
lavender = co(9, :);
gray = co(10, :);
teal = co(11, :);
brown = co(12, :);
magenta = co(13, :);
black = [0 0 0];
white = [1 1 1];
