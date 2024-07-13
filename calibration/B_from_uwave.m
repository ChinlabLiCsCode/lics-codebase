function B = B_from_uwave(uwave)


fun_uwave = @(b) breit_rabi(b,4,1,133)-breit_rabi(b,3,-1,133) - uwave;
B = fzero(fun_uwave, 892);

end