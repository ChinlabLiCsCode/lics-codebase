function [x, y] = filled_errorbar(x, y, yerr)
% FILLED_ERRORBAR(x, y, yerr) generates the x and y vectors for a filled
% error bar plot. x is a vector of x values, y is a vector of y values, and
% yerr is a vector of error values. The function returns the x and y
% vectors for a filled error bar plot.
    
[x, inds] = sort(x(:));
x = [x; flipud(x)];

y = y(inds);
yerr = yerr(inds);

y = [y(:); flipud(y(:))];
yerr = [yerr(:); -flipud(yerr(:))];
y = y + yerr;

end