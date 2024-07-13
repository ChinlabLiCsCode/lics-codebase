function sabf = aLiCs_ci(abf, fielderr, invflag)
% sabf = aLiCs_ci(abf, fielderr, invflag)
% Calculate the confidence interval on the LiCs scattering length abf given the field error fielderr.
% If invflag is true, then abf and sabf will be interpreted as 1/abf and 1/sabf.

if nargin < 3
    invflag = false;
end

if invflag
    abf = 1 ./ abf;
end

bs = zeros(size(abf));
for i = 1:length(abf)
    if abf(i) >= 0
        bs(i) = fzero(@(b) aLiCs(b,'a')-abf(i), [890,892.647]);
    else
        bs(i) = fzero(@(b) aLiCs(b,'a')-abf(i), [892.649, 895]);
    end
end

lb = aLiCs(bs - fielderr, 'a');
ub = aLiCs(bs + fielderr, 'a');

if invflag
    sl = abs(1./lb - 1./abf);
    su = abs(1./ub - 1./abf);
else
    sl = abs(lb - abf);
    su = abs(ub - abf);
end

sabf = [sl; su];

    
end