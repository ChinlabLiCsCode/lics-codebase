function nd = nd_calc(A, Aprime, params)

T = A./Aprime;
lT = log(T);
sc = Aprime./params.I_sat;


a0 = params.alpha(1);
a1 = params.alpha(2);
a2 = params.alpha(3);

if a2 == 0
    od = (sc - sc.*T - a0.*lT)./(1 + a1.*lT);
else
    od = (-1 - a1.*lT + sqrt(-4.*a2.*lT.*(sc.*(T - 1) + a0.*lT) ...
        + (1 + a1.*lT).^2)) ./ (2.*a2.*lT);
end

% convert from OD to pixel density 
nd = params.pixel^2/(3*params.wavelength^2/(2*pi)) .* od;
nd(~isfinite(nd)) = 0;
