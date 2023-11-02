function shots = genshots(vals, start, reps)

nvals = length(vals);

shots = start:(start + nvals - 1);
if nargin > 2
    shots = shots + (nvals .* (0:reps-1))';
end

end