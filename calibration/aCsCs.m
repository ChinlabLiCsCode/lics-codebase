function a = aCsCs(B)
% aCsCs - returns the scattering length of two Cs atoms in the |3, 3> state.
% B is the magnetic field in Gauss.
% a is the scattering length in Bohr radii.
% The data is from Berninger et. al. "Feshbach resonances, weakly bound molecular states, 
% and coupled-channel potentials for cesium at high magnetic fields" Phys. Rev. A 87, 032517 (2013)
% Here we store it in Cs_a_vs_B.txt. Then this functiona basically just interpolates the data.



a = zeros(1,length(B));
%B = round(B*10)/10;

fid = fopen('Cs_a_vs_B.txt');
Cs_a_vs_B = fscanf(fid, '%f %f',[2 inf]);
fclose(fid);

%apparently I have to add this because of legacy behavior of interp1 in MATLAB I
%guess.
[Cs_a_vs_B_u,ind] = unique(Cs_a_vs_B(1,:)); 

for i = 1 : length(B)
    if B(i) > 0 && B(i) < 1200;
        a(i) = interp1(Cs_a_vs_B_u,Cs_a_vs_B(2,ind),B(i),'spline');
        
        %[x y] = find(Cs_a_vs_B(1,:) == B(i));
        %a(i) = Cs_a_vs_B(2,y);
    else
        a(i) = NaN;
     
    end
end