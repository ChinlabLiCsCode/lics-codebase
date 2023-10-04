function h = scanfig_update(h, params, xvals, OD, fd, ind, xvalname)

% update the OD image axis 
axes(h.OD);
imagesc(squeeze(OD(ind, :, :))');
axis image;
hold on;
boxx = params.mask([3, 4, 4, 3, 3]);
boxy = params.mask([1, 1, 2, 2, 1]);
plot(boxx, boxy, 'r-', 'LineWidth', 1);
colorbar();
hold off;

% update the n_count axis
h.n_count = update_ax(h.n_count, fd.n_count, xvals, ind, xvalname, 'n count');

% update the fit axes
for a = ['x', 'y']
    fld = fields(h.(a));
    for i = 1:length(fld)
        if strcmp(fld{i}, 'trace')
            if a == 'x'
                m = params.mask(1:2);
            else
                m = params.mask(3:4);
            end
            h.(a).(fld{i}) = update_trace(h.(a).(fld{i}), fd.(a), ind, m, a);
        else
            h.(a).(fld{i}) = update_ax(h.(a).(fld{i}), fd.(a).(fld{i}), ...
                xvals, ind, xvalname, fld{i}); 
        end
    end
end

end


function ax = update_trace(ax, fdr, ind, mask, axname)
    axes(ax);
    
    trace = fdr.trace(ind, :);
    fit_trace = fdr.fit_trace(ind, :);

    plot(trace, '-', 'Color', 'b', 'LineWidth', 1);
    hold on;
    plot(fit_trace, '-', 'Color', 'g', 'LineWidth', 1);
    ylimits = ylim();
    rectangle('Position', [mask(1) ylimits(1) mask(2) ylimits(2)-ylimits(1)], 'EdgeColor', 'r', 'LineWidth', 1);
    ylim(ylimits);
    xlabel([axname, ' position']);
    ylabel('integrated od');
    hold off;
    
end

function ax = update_ax(ax, dat, xvals, ind, xvalname, fldname)
    axes(ax);
    nx = length(xvals);
    i = mod(ind, nx);
    optsA = {'MarkerSize', 5, 'LineWidth', 1, 'Color', 'b'};
    optsB = {'MarkerSize', 3, 'LineWidth', 1, 'Color', [0.5 0.5 1]};

    if ind < nx
        plot(xvals(1:i), dat(1:i), 'o', optsA{:});
        hold on;
        ylimits = ylim();
        plot(xvals(i+1:end), ylimits(1) + zeros(1, nx - i), 'x', optsA{:});
        ylim(ylimits);
    else
        x = NaN(nx, ceil(ind/nx));
        d = NaN(nx, ceil(ind/nx));
        plot(x, d, 'o', optsB{:});
        d(1:ind) = dat;
        avg = mean(d, 2, 'omitmissing');
        err = std(d, 0, 2, 'omitmissing');
        errorbar(xvals(1:i), avg(1:i), err(1:i), 'o', optsA{:});
        hold on;
        ylimits = ylim();
        errorbar(xvals(i+1:end), avg(i+1:end), err(i+1:end), 'x', optsA{:});
        ylim(ylimits);
    end
    xlabel(xvalname)
    ylabel(fldname)
    hold off;
end