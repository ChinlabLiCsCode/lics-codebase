function a = aLiCs_molscat(B, species)
% aLiCs_molscat - returns scattering length a from molscat calculations 
% stored in file LiCs_a_cs_B.txt

% B = 850;
% species = 'a';
a = zeros(1,length(B));

M = readmatrix('LiCs_a_vs_B.txt');
Bload = M(:, 1);
if species == 'a'
    aload = M(:, 2);
elseif species == 'b'
    aload = M(:, 3);
elseif species == 'c'
    aload = M(:, 4);
else 
    error("invalid species");
end


for i = 1 : length(B)
    if B(i) >= Bload(1) && B(i) <= Bload(end)
        a(i) = interp1(Bload, aload, B(i), 'spline');
    else
        a(i) = NaN;
    end
end