% bimodal profile
function y = fitfun_bimodal(c, x)
% 
% parameters: 
%   1: center
%   2: tf amp
%   3: tf radius
%   4: gaussian amp
%   5: gaussian sigma
%   6: background
%

tf = 1 - ((x - c(1))/c(3)).^2;
tf(tf < 0) = 0;
gauss = c(4).*exp((-(x - c(1)).^2) ./ (2*c(5)^2));
y = c(6) + c(2).*(tf).^2 + gauss;

end