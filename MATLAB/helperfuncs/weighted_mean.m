function [avg, err] = weighted_mean(vals, errs)

w = 1./errs.^2;
w(isnan(w)) = 0;
avg = sum(vals .* w) / sum(w);
err = 1./sqrt(sum(w));