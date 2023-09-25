function od = od_calc(A, Aprime, params)

T = A./Aprime;
sc = Aprime./params.I_sat;

c = params.alpha(1);
b = params.alpha(2);
a = params.alpha(3);

if a == 0
    od = (-c.*log(T) + sc.*(1 - T))./(1 + b.*log(T));
else
    od = (-(1 + b.*log(T))...
        + sqrt((1 + b.*log(T)).^2 - 4.*a.*log(T).*(c.*log(T) - sc.*(1 - T)))...
        ) ./ (2.*a.*log(T));
end