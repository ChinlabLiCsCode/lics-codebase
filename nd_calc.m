function nd = nd_calc(A, Aprime, params)
% nd = nd_calc(A, Aprime, params)
%
% Calculates the number density from the absorption image A and the
% reference image Aprime.  The parameters are stored in params. The
% output is in units of atoms per pixel. The calculation is based on
% the method described in the paper "Quantitative absorption imaging: 
% The role of incoherent multiple scattering in the saturating regime"
% but includes a quadratic term which comes from our empirical 
% observations. The quadratic term is only used if the third element
% of params.alpha is non-zero.
%   
% INPUTS
%   A: absorption image
%   Aprime: reference image
%   params: structure containing the imaging parameters
%      params.I_sat: saturation intensity in units of counts per pixel
%      params.alpha: vector of three parameters used to calculate the
%                    optical density
%      params.pixel: pixel size in meters
%      params.wavelength: imaging wavelength in meters
%
% OUTPUTS
%   nd: number density in units of atoms per pixel
%

% T is the transmission fraction
T = A./Aprime;
% logT is the log of the transmission fraction
lT = log(T);
% sc is the saturation parameter
sc = Aprime./params.I_sat;

% extract the imaging parameters from params
a0 = params.alpha(1);
a1 = params.alpha(2);
a2 = params.alpha(3);

% calculate the optical density
if a2 == 0
    % if a2 is zero, then we can use this easier version
    od = (sc - sc.*T - a0.*lT)./(1 + a1.*lT);
else
    % otherwise, we have to use the quadratic formula
    od = (-1 - a1.*lT + sqrt(-4.*a2.*lT.*(sc.*(T - 1) + a0.*lT) ...
        + (1 + a1.*lT).^2)) ./ (2.*a2.*lT);
end

% convert from OD to pixel density 
nd = params.pixel^2/(3*params.wavelength^2/(2*pi)) .* od;

% set any non-finite values to zero
nd(~isfinite(nd)) = 0;

% set any complex values to be real
nd = real(nd);
