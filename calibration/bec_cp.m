%BEC chemical potential (all SI)
%https://arxiv.org/pdf/cond-mat/9806038.pdf
%http://users.physik.fu-berlin.de/~pelster/Vorlesungen/WS1213/stringari1.pdf
%Usage:bec_cp(fx,fy,fz,N,a,outflag)
%


function out = bec_cp(fx,fy,fz,N,a,outflag)

wx = 2*pi*fx; wy = 2*pi*fy; wz = 2*pi*fz;
w = (wx.*wy.*wz)^(1/3);
make_constants;

aho = sqrt(hbar./(mCs.*w));
mu=((hbar.*w)./2).*((15.*N.*a.*a_0)/(aho)).^(2/5);
muT = mu./k_B;

gint = 4.*pi.*hbar.^2.*a.*a_0./mCs;
Rx = sqrt(2.*mu./(mCs.*wx^2)); Ry = sqrt(2.*mu./(mCs*wy^2)); Rz = sqrt(2.*mu./(mCs.*wz^2));
%transition temperature
TC = 0.94.*(hbar.*w./k_B).*N.^(1/3);

dTC0=(-0.73.*((wx+wy+w)./3)./w).*N.^(-1/3);
dTCint=(-1.33.*a.*a_0./aho).*N.^(1/6);

crit_a = 0.575.*aho./N./a_0; %spherical symmetry crit a

%Healing length
xi = (8.*pi.*(mu/gint).*a.*a_0).^(-1/2);
cs = sqrt(mu/mCs);

%Thermal deBroglie wavelength & peak phase space density
lamdaDB = sqrt((2*pi*hbar^2)/(mCs*k_B*muT));
phaseDensity = lamdaDB^3*(mu./gint);



%%
out.oscillatorLength = aho;
out.chemPotential = muT;
out.peakDensity = mu./gint;
out.rtf = [Rx Ry Rz];
out.centeralHealingLength = xi;
out.Tc = TC;
out.c = cs;
out.lamdaT = lamdaDB;
out.phaseDensity = phaseDensity;
%%
if outflag==1
    disp(['Oscillator_Length: ', num2str(aho*1e6), ' microns']);
    disp(['Chem. Potential: ', num2str(muT*1e9), ' nK']);
    disp(['Peak Density: ', num2str(mu./gint) ]);
    disp(['TF Radii: (', num2str(Rx),',',num2str(Ry),',',num2str(Rz),')']);
    disp(['Central healing length: ', num2str(1e6.*xi), ' microns']);
    disp(['Critical Temperature ', num2str(1e9.*TC), ' nK' ]);
    disp(['TC correction (%) : ', num2str(dTCint+dTC0)]);
    disp(['Critical a (Spherical) : ', num2str(crit_a)]);
    disp(['Sound speed : ', num2str(cs.*1e3), 'mm per second']);
    disp(['WRONG? deBroglie wavelength : ', num2str(lamdaDB*10^6), 'microns']);
    disp(['WRONG? phase space density: ', num2str(phaseDensity)]);
    %disp(['TC correction finite size (%) : ', num2str(dTC0)]);
    %disp(['TC correction interactions (%) : ', num2str(dTCint)]);
end
end