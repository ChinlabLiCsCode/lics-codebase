% Li cloud sizes/T_F
%https://journals.aps.org/rmp/pdf/10.1103/RevModPhys.80.1215
function out = fermi_cp(fx,fy,fz,N,liflag,outflag)
make_constants;
if liflag==0
    mLi = 40.*amu;
end
wx=2.*pi.*fx; wy=2.*pi.*fy; wz=2.*pi.*fz;
who = (wx.*wy.*wz).^(1/3);
EF = (6*N)^(1/3).*hbar.*who;
TF = EF/k_B;
kf = sqrt(2.*mLi.*EF./hbar.^2);
Rx = sqrt(2.*EF./(mLi.*(wx).^2));
Ry = sqrt(2.*EF./(mLi.*(wy).^2));
Rz = sqrt(2.*EF./(mLi.*(wz).^2));
vf = sqrt(2.*EF/mLi);
%peak density
npeak = (8./(pi.^2)).*N./(Rx.*Ry.*Rz);

out.TF = TF;
out.kF = kf;
out.rTF = [Rx Ry Rz];
out.peakDensity = npeak;
out.vf = vf;

if outflag==1
    disp(['Fermi Temperature: ', num2str(TF.*1e9), 'nK']); 
    disp(['Fermi momentum', num2str(kf)]);
    disp(['1/Fermi momentum ',num2str(1/kf)]);
    disp(['TF Radii: (', num2str(Rx),',',num2str(Ry),',',num2str(Rz), ')']);
    disp(['Peak Density:',num2str(npeak)]);
    disp(['Fermi Velocity: ', num2str(vf.*1e3), ' mm per second']);
end
end