function [cv, ci] = fit_object_parse(fo)

cv = coeffvalues(fo);
ci = confint(fo);
ci = (ci(2, :) - ci(1, :))/4;

end