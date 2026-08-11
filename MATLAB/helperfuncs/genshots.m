function shots = genshots(vals, start, reps, varargin)

nvals = length(vals);

% allow supplying a date
if mod(length(varargin), 2) == 1
    date = varargin{end};
else
    date = false;
end

% find out how many extra blocks of start/reps we have
nblocks = floor(length(varargin)/2);

% populate array 
startarr(1) = start;
reparr(1) = reps;
for a = 1:nblocks
    startarr(a+1) = varargin{2*a - 1};
    reparr(a+1) = varargin{2*a};
end

% create shot array
shotnums = [];
for a = 1:length(startarr)
    start = startarr(a);
    reps = reparr(a);

    shots = start:(start + nvals - 1);
    shots = shots + (nvals .* (0:reps-1))';

    shotnums = [shotnums; shots];
end

shotnums

if date
    shots = {date, shotnums};
else
    shots = shotnums;
end

end