function vshim = vshim_calculator_fromcal(abf, fieldcal)

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

fun_vshim = @(v) field_from_comp_z(-0.85, 3.85, v, fieldcal) - B;
vshim = fzero(fun_vshim, 5);
fprintf('vshim = %.3f\n\n', vshim);

end

function bz = field_from_comp_z(a, b, c, d)
b = field_from_comp(a, b, c, d);
bz = b(1);
end