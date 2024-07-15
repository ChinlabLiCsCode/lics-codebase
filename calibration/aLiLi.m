function a = aLiLi(B, species)
% aLiLi - returns the Li Li scattering lengths at field B between the
% species given in species ('ab', 'ac', or 'bc'). Values from Table 2 in 
% "Precise Characterization of $^{6}\mathrm{Li}$ Feshbach Resonances Using 
% Trap-Sideband-Resolved RF Spectroscopy of Weakly Bound Molecules" by
% Zurn, et. al. PRL 110 13 135301 (2013).

if strcmp(species, 'ab')
    abg = -1582;
    delta = -262.3;
    B0 = 832.18;
elseif strcmp(species, 'ac')
    abg = -1770;
    delta = -166.6;
    B0 = 689.68;
elseif strcmp(species, 'bc')
    abg = -1490;
    delta = -222.3;
    B0 = 809.76;
else
    error('invalid species argument')
end

a = abg .* (1 - delta ./ (B - B0));