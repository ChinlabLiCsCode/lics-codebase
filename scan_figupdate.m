function fig = scan_figupdate(fig, params, xvals, fd, ND, xvalname,...
    ind, nreps, nxvals)

% extract fittype args
ft = params.fittype;
if iscell(ft)
    x_fit_type = ft{1};
    y_fit_type = ft{2};
else
    x_fit_type = ft;
    y_fit_type = ft;
end

view = params.view;
mask = params.mask;
viewx = view(4) - view(3) + 1;
viewy = view(2) - view(1) + 1;

figure(fig);
% update the OD image axis 
subplot(3, 3, 1:2, 'replace');
imagesc(1:viewx, 1:viewy, squeeze(ND(ind, :, :))');
axis image;
hold on;
boxx = mask([3, 4, 4, 3, 3]);
boxy = mask([1, 1, 2, 2, 1]);
plot(boxx, boxy, 'r-', 'LineWidth', 1);
% set(gca, 'YDir', 'normal');
xlabel('x position [pixels]');
ylabel('y position [pixels]');
cb = colorbar();
ylabel(cb, 'atoms/pixel');
title('number density');
hold off;

% update the n_count axis
subplot(3, 3, 3, 'replace');
update_ax(xvals, horzcat(fd.n_count), xvalname, 'integrated number', ...
    'n\_count', ind, nreps, nxvals);

% update the directional axes
for r = 1:2
    % get type of fitting and mask 
    if r == 1
        mask = params.mask(1:2);
        fit_type = x_fit_type;
        name = 'x';
    else
        mask = params.mask(3:4);
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
    update_trace(fd, ind, mask, name);

    % update the fitted number axis
    subplot(3, nplt, r*nplt + 2, 'replace');
    update_ax(xvals, horzcat(fd.([name, '_nfit'])), xvalname, ...
        [name, ' fitted number'], [name, '\_nfit'], ind, nreps, nxvals);

    % update the center position axis
    subplot(3, nplt, r*nplt + 3, 'replace');
    update_ax(xvals, 1e6.*horzcat(fd.([name, '_center'])), xvalname, ...
        [name, ' position [µm]'], [name, '\_center'], ind, nreps, nxvals);

    % update more specific axes 
    if strcmp(fit_type, 'gauss') || strcmp(fit_type, 'dbl')
        % sigma
        subplot(3, nplt, r*nplt + 4, 'replace');
        update_ax(xvals, 1e6.*horzcat(fd.([name, '_sigma'])), xvalname, ...
            [name, ' sigma [µm]'], [name, '\_sigma'], ind, nreps, nxvals);
    end
    if strcmp(fit_type, 'dbl')
        % sep
        subplot(3, nplt, r*nplt + 5, 'replace');
        update_ax(xvals, 1e6.*horzcat(fd.([name, '_sep'])), xvalname, ...
            [name, ' separation [µm]'], [name, '\_sep'], ind, nreps, nxvals);
    end
    if strcmp(fit_type, 'tf')
        % rtf
        subplot(3, nplt, r*nplt + 4, 'replace');
        update_ax(xvals, 1e6.*horzcat(fd.([name, '_rTF'])), xvalname, ...
            [name, ' r_{TF} [µm]'], [name, '\_rTF'], ind, nreps, nxvals);
    end


    
end

end


%%%% function to update trace axes %%%%%%%%%%%%%%%%%%%
function update_trace(fd, ind, mask, name)

    trace = vertcat(fd(ind).([name, '_trace']));
    fit_trace = vertcat(fd(ind).([name, '_fit_trace']));

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
    hold off;
    
end



%%%% function to update axes with fit parameters %%%%%%%%%%%%%%%%%%%
function update_ax(xvals, yvals, xvalname, yvalname, sftitle, ind, nreps, nxvals)

    yarr = NaN([nxvals, nreps]);
    yarr(1:ind) = yvals(1:ind);
    yarr = yarr';
    y_mean = mean(yarr, 1, 'omitmissing');
    y_err = std(yarr, [], 1, 'omitmissing');
    y_mean(isnan(y_mean)) = 0;
    
    co = colororder();
    optsA = {'MarkerSize', 8, 'Marker', 'o', 'LineWidth', 1,...
        'CapSize', 0, 'LineStyle', 'none', ...
        'Color', co(1,:), 'MarkerFaceColor', lighter(co(1, :))};
    optsB = {'MarkerSize', 8, 'Marker', 'x', 'LineWidth', 1,...
        'CapSize', 0, 'LineStyle', 'none', ...
        'Color', co(1,:), 'MarkerFaceColor', lighter(co(1, :))};


    hold on;
    if ind == nreps * nxvals
        errorbar(xvals, y_mean, y_err, optsA{:});
    else 
        modind = mod(ind, nxvals);  % scan isnt done yet 
        ia = 1:modind;
        ib = modind+1 : nxvals;
        errorbar(xvals(ia), y_mean(ia), y_err(ia), optsA{:});
        errorbar(xvals(ib), y_mean(ib), y_err(ib), optsB{:});
    end
    xlabel(xvalname);
    ylabel(yvalname);
    p = (max(xvals) - min(xvals)) / (2 * nxvals);
    xlim([min(xvals) - p, max(xvals) + p]);
    title(sftitle);
    hold off;
    
end