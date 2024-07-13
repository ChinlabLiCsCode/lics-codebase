function B = B_from_uwave(uwave)
% B_from_uwave - returns the magnetic field that corresponds to a given 
% microwave frequency between Cs in |3, 3> and |4, 4>.

fun_uwave = @(b) breit_rabi(b,4,1,133)-breit_rabi(b,3,-1,133) - uwave;
B = fzero(fun_uwave, 892);

end