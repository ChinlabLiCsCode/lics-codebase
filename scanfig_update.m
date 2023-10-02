function h = scanfig_update(h, params, xvals, OD, fd, ind)

% update the OD image axis 
axes(h.OD);
imagesc(OD);
axis image;
hold on;
rectangle('Position', params.mask, 'EdgeColor', 'r', 'LineWidth', 1);
hold off;

% update the n_count axis
h.n_count = update_ax(h.n_count, fd.n_count, xvals, ind);

% update the trace axes
h.x.trace = update_trace(h.x.trace, fd.x.trace, ind, params.mask(3, 4));
h.y.trace = update_trace(h.y.trace, fd.y.trace, ind, params.mask(1, 2));

% update the fit axes
fld = fields(h.x);
for i = 2:length(fld)
    h.x.(fld{i}) = update_ax(h.x.(fld{i}), fd.x.(fld{i}), xvals, ind);
end
fld = fields(h.y);
for i = 2:length(fld)
    h.y.(fld{i}) = update_ax(h.y.(fld{i}), fd.y.(fld{i}), xvals, ind);
end

end



function ax = update_trace(ax, fdr, ind, mask)
    axes(ax);
    
    trace = fdr.trace(ind, :);
    trace_fit = fdr.trace_fit(ind, :);

    plot(trace, '-', 'Color', 'b', 'LineWidth', 1);
    hold on;
    plot(trace_fit, '-', 'Color', 'g', 'LineWidth', 1);
    ylimits = ylim();
    rectangle('Position', [mask(1) ylimits(1) mask(2) ylimits(2)], 'EdgeColor', 'r', 'LineWidth', 1);
    ylim(ylimigs);
    hold off;
    
end

function ax = update_ax(ax, dat, xvals, ind)
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
        hold off;
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
        hold off;
    end

end