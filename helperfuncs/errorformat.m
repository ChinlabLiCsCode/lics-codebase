function str = errorformat(val, err)
% makes a smart error format out of a val and error combo

if nargin < 2
    err = std(val, [], "all");
    val = mean(val, "all");
end

decval = - floor(log10(abs(val)));
decerr = - floor(log10(abs(err)));

if decval <= decerr 
    % normal case 
    val = round(val, decerr);
    err = round(err, decerr);
    if decerr < 0
        str = sprintf('%g(%g)', val, err);
    else
        fmt = sprintf('%%.%df(%%g)', decerr);
        str = sprintf(fmt, val, err*10^decerr);
    end
else
    % error exceeds value 
    if isfinite(decval)
        val = round(val, decval);
    end
    if isfinite(decerr)
        err = round(err, decerr);
        str = sprintf('%g +- %g', val, err);
    else
        str = sprintf('%g +- ?', val);
    end
end
