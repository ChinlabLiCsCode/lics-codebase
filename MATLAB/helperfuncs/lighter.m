function c1 = lighter(c0, degree)
if nargin < 2
    degree = 3;
end
c1 = 1 - (1 - c0)./degree;
end