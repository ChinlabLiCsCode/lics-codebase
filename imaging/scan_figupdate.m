function [fig, data] = scan_figupdate(fig, data, ind, nreps, nxvals)
data
xvals = data.xvals;
xvalname = data.xvalname;
macrocalc = data.macrocalc;

% extract fittype args
ft = data.params.fittype;
if iscell(ft)
    x_fit_type = ft{1};
    y_fit_type = ft{2};
else
    x_fit_type = ft;
    y_fit_type = ft;
end

% transpose xvals if need be 
if size(xvals, 1) == 1
    xvals = xvals';
end

% initialize a cell array to store the results of macrocalcs
res = cell(1, length(macrocalc)/2);

view = data.params.view;
mask = data.params.mask;
viewy = view(2) - view(1) + 1;
viewx = view(4) - view(3) + 1;

figure(fig);
% update the OD image axis 
subplot(3, 3, 1:2, 'replace');
imagesc(1:viewx, 1:viewy, squeeze(data.ND(ind, :, :)));
axis image;
hold on;
boxy = mask([1, 1, 2, 2, 1]);
boxx = mask([3, 4, 4, 3, 3]);
plot(boxx, boxy, 'r-', 'LineWidth', 1);
% set(gca, 'YDir', 'normal');
xlabel('x position [pixels]');
ylabel('y position [pixels]');
cb = colorbar();
ylabel(cb, 'atoms/pixel');
title('number density');


% update the n_count axis
subplot(3, 3, 3, 'replace');
fld = 'n_count';
y = data.(fld);
lbl = 'n\_count [atoms]';
update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
res = macrocalcplot(fld, macrocalc, xvals, y, res);

% update the directional axes
for r = 1:2
    % get type of fitting and mask 
    if r == 1
        mask = data.params.mask(3:4);
        fit_type = x_fit_type;
        name = 'x';
    else
        mask = data.params.mask(1:2);
        fit_type = y_fit_type;
        name = 'y';
    end

    % figure out right number of subplots
    if strcmp(fit_type, 'dbl')
        nplt = 5;
    else
        nplt = 4;
    end

    % update the trace axis 
    subplot(3, nplt, r*nplt + 1, 'replace');
    update_trace(data, ind, mask, name);

    % update the fitted number axis
    subplot(3, nplt, r*nplt + 2, 'replace');
    fld = [name, '_nfit'];
    y = data.(fld);
    lbl = [name, '\_nfit [atoms]'];
    update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
    res = macrocalcplot(fld, macrocalc, xvals, y, res);

    % update the center position axis
    subplot(3, nplt, r*nplt + 3, 'replace');
    fld = [name, '_center'];
    y = 1e6 .* data.(fld);
    lbl = [name, '\_center [µm]'];
    update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
    res = macrocalcplot(fld, macrocalc, xvals, y, res);

    % update more specific axes 
    if strcmp(fit_type, 'gauss') || strcmp(fit_type, 'dbl')
        % sigma
        subplot(3, nplt, r*nplt + 4, 'replace');
        fld = [name, '_sigma'];
        y = 1e6 .* data.(fld);
        lbl = [name, '\_sigma [µm]'];
        update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
        res = macrocalcplot(fld, macrocalc, xvals, y, res);
    end
    if strcmp(fit_type, 'dbl')
        % sep
        subplot(3, nplt, r*nplt + 5, 'replace');
        fld = [name, '_sep'];
        y = 1e6 .* data.(fld);
        lbl = [name, '\_sep [µm]'];
        update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
        res = macrocalcplot(fld, macrocalc, xvals, y, res);
    end
    if strcmp(fit_type, 'tf')
        % rtf
        subplot(3, nplt, r*nplt + 4, 'replace');
        fld = [name, '_rTF'];
        y = 1e6 .* data.(fld);
        lbl = [name, '\_rTF [µm]'];
        update_ax(xvals, y, xvalname, lbl, ind, nreps, nxvals);
        res = macrocalcplot(fld, macrocalc, xvals, y, res);
    end
    
end

% store calculation results
calcresults = cell(1, length(res) * 3);
for a = 1:length(res)
    calcresults{3*a - 2} = macrocalc{2*a - 1};
    calcresults{3*a - 1} = macrocalc{2*a};
    calcresults{3*a} = res{a};
end

data.calcs = calcresults;

end


%%%% function to update trace axes %%%%%%%%%%%%%%%%%%%
function update_trace(data, ind, mask, name)

    trace = data.([name, '_trace']);
    trace = trace(ind, :);
    fit_trace = data.([name, '_fit_trace']);
    fit_trace = fit_trace(ind, :);

    co = colororder();

    hold on;
    plot(trace, '-', 'LineWidth', 2.5, 'Color', co(1, :));
    plot(fit_trace, '-', 'LineWidth', 2, 'Color', co(5, :));
    ylimits = ylim();
    rectangle('Position', ...
        [mask(1), ylimits(1), mask(2)-mask(1), ylimits(2)-ylimits(1)], ...
        'EdgeColor', 'r', 'LineWidth', 1);
    ylim(ylimits);
    xlim([0, length(trace)]);
    xlabel([name, ' position [pix]']);
    ylabel('1D density [atoms/pix]');
    title([name, '\_trace']);
    
end



%%%% function to update axes with fit parameters %%%%%%%%%%%%%%%%%%%
function update_ax(xvals, yvals, xvalname, sftitle, ind, nreps, nxvals)

    yarr = NaN([nxvals, nreps]);
    yarr(1:ind) = yvals(1:ind);
    yarr = yarr';
    y_mean = mean(yarr, 1, 'omitmissing');
    y_err = std(yarr, [], 1, 'omitmissing');
    y_mean(isnan(y_mean)) = 0;
    
    co = colororder();
    blue = co(1, :);
    optsErrorbar = {'Marker', 'none', 'LineWidth', 1,...
        'CapSize', 2, 'LineStyle', 'none', 'Color', blue};
    optsScatterO = {'Marker', 'o', 'LineWidth', 1, 'MarkerFaceColor', blue, ...
        'MarkerEdgeColor', blue, 'MarkerFaceAlpha', 0.3};
    optsScatterX = {'Marker', 'x', 'LineWidth', 1, 'MarkerFaceColor', blue, ...
        'MarkerEdgeColor', blue};


    hold on;
    if ind == nreps * nxvals
        errorbar(xvals, y_mean, y_err, optsErrorbar{:});
        scatter(xvals, y_mean, 64, optsScatterO{:})
    else 
        modind = mod(ind, nxvals);  % scan isnt done yet 
        ia = 1:modind;
        ib = modind+1 : nxvals;
        errorbar(xvals, y_mean, y_err, optsErrorbar{:});
        scatter(xvals(ia), y_mean(ia), 64, optsScatterO{:});
        scatter(xvals(ib), y_mean(ib), 64, optsScatterX{:});
    end
    xlabel(xvalname);
    p = (max(xvals) - min(xvals)) / (2 * nxvals);
    xlim([min(xvals) - p, max(xvals) + p]);
    title(sftitle);
    
end


%%%% function to do macrocalcs %%%%%%%%%%%%%%%%%%%
function res = macrocalcplot(currparam, macrocalc, x, y, res)

calcpars = {macrocalc{1:2:end}};
calcfuncs = {macrocalc{2:2:end}};

for i = 1:length(calcpars)
if strcmp(currparam, calcpars{i})
switch calcfuncs{i}
    case 'mean'
        % calculation
        m = mean(y);
        se = std(y) ./ sqrt(length(y));
    
        % plot
        xl = xlim();
        plot(xl, [m, m], 'r');
        xlim(xl);

        % save result
        res{i} = [m, se];
    case 'peak'
        while length(x) < length(y)
            x = [x; x];
        end
        x = x(1:length(y));

        % perform skew normal fit
        ft = fittype(@(x0, amp, sigma, skew, bg, x) ...
            skewgauss(x0, amp, sigma, skew, bg, x));
        sp = [mean(x), max(y), std(x)/4, 0, 0];
        fo = fit(x, y, ft, StartPoint=sp);
        
        % find peak
        [bestx, maxy] = fminbnd(@(x) -fo(x), min(x), max(x));
        
        % plot
        finex = linspace(min(x), max(x), 100);
        plot(finex, fo(finex), 'r');
        yl = ylim();
        plot([bestx, bestx], yl, ':r');
        ylim(yl);

        % save result
        res{i} = [bestx, maxy];

end
end
end

end

%%%% just a lil fit function for peak finding %%%%%%%%%%%%%%%%
function y = skewgauss(x0, amp, sigma, skew, bg, x)
x = (x - x0) ./ sigma;
a = exp(-x.^2 / 2);
b = 1 + erf(skew * x / 2);
y = bg + 2 * amp * a .* b;
end