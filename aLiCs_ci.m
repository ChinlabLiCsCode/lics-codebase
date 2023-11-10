function [sl, su] = aLiCs_ci(abf, fielderr, invflag)

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

disp(bs)
lb = aLiCs(bs - fielderr, 'a');
ub = aLiCs(bs + fielderr, 'a');
disp(lb)
disp(ub)

if invflag
    sl = abs(1./lb - 1./abf);
    su = abs(1./ub - 1./abf);
else
    sl = abs(lb - abf);
    su = abs(ub - abf);
end
disp(sl)
disp(su)
    
end