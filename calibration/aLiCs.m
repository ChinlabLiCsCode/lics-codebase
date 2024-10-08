function a = aLiCs(B,species)
% aLiCs - returns the Li-Cs scattering length at a given magnetic field B, for Li atoms in 
% the state given by species. 
% B is the magnetic field in Gauss.
% a is the scattering length in Bohr radii.
% Here the data use the resonance positions found in Jacob's Nature paper, I believe. 
if species == 'a'
%            a = -29.4.*(1 - (-58.21)./(B - 842.829) - (-4.55)./(B - 892.6475));
        a = -29.4.*(1 - (-58.21)./(B - 842.829) - (-4.55)./(B - 892.648));
elseif species == 'b' 
%            a = -29.6.*(1 - (-0.37)./(B - 816.113) - (-57.45)./(B - 888.5769) - (-4.22)./(B - 943.033));
        a = -29.6.*(1 - (-0.37)./(B - 816.113) - (-57.45)./(B - 888.577) - (-4.22)./(B - 943.033));
end
end