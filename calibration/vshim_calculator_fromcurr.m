function vshim = vshim_calculator_fromcurr(abf, vshim_curr, uwave_curr)

fprintf('a_bf = %.1f a_0\n', abf);

fun_abf = @(b) aLiCs(b, 'a') - abf;
if abf > 0
    B = fzero(fun_abf, [880, 892.647]);
else
    B = fzero(fun_abf, [892.649, 900]);
end
fprintf('B = %.3f G\n', B);

uwave = breit_rabi(B,4,1,133)-breit_rabi(B,3,-1,133);
fprintf('uwave = %.3f MHz\n', uwave);

freq_to_shim = 1/0.41/2.5;
vshim = vshim_curr + (uwave - uwave_curr)*freq_to_shim;
fprintf('vshim = %.3f\n\n', vshim);

end