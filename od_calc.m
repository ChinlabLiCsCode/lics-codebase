function od = od_calc(A, Aprime, params)

T = A./Aprime;
lT = log(T);
sc = Aprime./params.I_sat;


a0 = params.alpha(1);
a1 = params.alpha(2);
a2 = params.alpha(3);

if a2 == 0
    % od = (-a0.*log(T) + sc.*(1 - T))./(1 + a1.*log(T));
    od = (sc - sc.*T - a0.*lT)./(1 + a1.*lT);
else
    % od = (-(1 + a1.*log(T))...
    %     + sqrt((1 + a1.*log(T)).^2 - 4.*a2.*log(T).*(a0.*log(T) - sc.*(1 - T)))...
    %     ) ./ (2.*a2.*log(T));
    od = (-1 - a1.*lT + sqrt(-4.*a2.*lT.*(sc.*(T - 1) + a0.*lT) ...
        + (1 + a1.*lT).^2)) ./ (2.*a2.*lT);


end

od(~isfinite(od)) = 0;
