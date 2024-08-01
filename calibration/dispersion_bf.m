%theory from: [2]
%[1] L. Viverit and S. Giorgini, Phys. Rev. A 66, 063604(2002).
%[2] https://journals.aps.org/pra/abstract/10.1103/PhysRevA.103.L021301

%% perturbation prediction[1]
% clear;clc;close all;
% kIn = 0.4e6; aBFin = -2000; NF = 20e3; aBBin = 270; NB = 30e3; plotFlag = 0;
function out = dispersion_bf(kIn,aBFin,NF,aBBin, NB, plotFlag)
%here we setup a typilcal BEC in DFG
%-------------------------parms input--------------------------------------
make_constants;
becProp = bec_cp(6.53, 114, 152, NB, aBBin, 0);
%%
cMeanDensity = 0.5; %non-uniform density correction!
nB = becProp.peakDensity*cMeanDensity;
%%
fermiProp = fermi_cp(33,400,400, NF, 1,0);
nF = fermiProp.peakDensity;
kF = (6*pi^2*nF)^(1/3); %1/kF=3.3e-7; lamda_F=2micron->we can reach kF!
ksz = size(kIn,2);
mF = mLi;
mB = mCs;
%% input unit conversion
aBF = aBFin*a_0;
aBB = aBBin*a_0;
k = kIn./kF;
%-------------------------parms input--------------------------------------
vF = kF*hbar/mF;
E_F = kF^2/(2*mF);
omega = zeros(1,ksz);
gamma  =zeros(1,ksz);
omega2 = zeros(1,ksz);
gamma2  =zeros(1,ksz);
omega3 = zeros(1,ksz);
gamma3  =zeros(1,ksz);
%%
gBF = aBF*2*pi*(1/mF+1/mB); %in unit of hbar^2
gBB = aBB*4*pi/mB;
geff = gBB - 1.5*nF*gBF^2/E_F;
aeff = geff/gBB*aBB;

for i = 1:ksz
q = k(i)*kF + 1e-4;
Ek = q^2/(2*mB);
syms w
eqnLeft = w;
u1 = w./(q*vF)+q/(2*kF);
u2 = w./(q*vF)-q/(2*kF);
RePol = -mF*kF/(4*pi^2)*( 1 + ( (1-u1.^2).*log(abs((1+u1)/(1-u1))) ...
    - (1-u2.^2).*log(abs((1+u2)/(1-u2)))        )*kF*0.5/q );
ImPol = -mF*kF^2/(8*q*pi)*( (1-u2^2)*heaviside(1-u2^2) - (1-u1^2)*heaviside(1-u1^2)  );
eqnRight = hbar*real(sqrt(    Ek^2 + 2*Ek*nB*(gBB+gBF^2*(RePol + 1i*ImPol))          ));
eqnRight2 = hbar*real(sqrt(   Ek^2 + 2*Ek*nB*gBB ));
eqnRight3 = hbar*real(sqrt(   Ek^2 + 2*Ek*nB*geff ));
% fplot([eqnLeft eqnRight])
% title([texlabel(eqnLeft) ' = ' texlabel(eqnRight)])
S1 = vpasolve(eqnLeft == eqnRight, w);
S2 = vpasolve(eqnLeft == eqnRight2, w);
S3 = vpasolve(eqnLeft == eqnRight3, w);
omega(1,i) = double(S1)./(hbar*E_F);
omega2(1,i) = double(S2)./(hbar*E_F);
omega3(1,i) = double(S3)./(hbar*E_F);
w1 = omega(1,i)*(hbar*E_F);
u10 = w1./(q*vF)+q/(2*kF);
u20 = w1./(q*vF)-q/(2*kF);
RePol0 = -mF*kF/(4*pi^2)*( 1 + ( (1-u10.^2).*log(abs((1+u10)/(1-u10))) ...
    - (1-u20.^2).*log(abs((1+u20)/(1-u20)))        )*kF*0.5/q );
ImPol0 = -mF*kF^2/(8*q*pi)*( (1-u20^2)*heaviside(1-u20^2) - (1-u10^2)*heaviside(1-u10^2)  );
eqnRight0 = -hbar*sqrt(    Ek^2 + 2*Ek*nB*(gBB+gBF^2*(RePol0 + 1i*ImPol0))          );
gamma(1,i) = imag(eqnRight0)./(hbar*E_F);
gamma2(1,i) = imag(   hbar*sqrt(Ek^2 + 2*Ek*nB*gBB )./(hbar*E_F)    );
gamma3(1,i) = imag(   hbar*sqrt(Ek^2 + 2*Ek*nB*geff )./(hbar*E_F)    );
end
%% conversion and output
%note E_F is in unit of 1/hbar^2
c1 =  E_F*hbar; % conversion factor of omega

out.omega = omega(1,:)*c1;
out.omega_bare = omega2(1,:)*c1;
out.omega_eff  = omega3(1,:)*c1;

out.gamma = gamma(1,:)*c1;
out.gamma_bare = gamma2(1,:)*c1;
out.gamma_eff  = gamma3(1,:)*c1;

out.nB = nB;
out.aeff = aeff./a_0;

%% plot and saving
kplot = kIn*1e-6;


if plotFlag

P1 = figure; 
set(P1,'position',[300,200,1000,400])
subplot(1,3,1);
hold on;
plot(kplot, 1e-3*omega(1,:)*c1, 'r-');
plot(kplot, 1e-3*omega2(1,:)*c1,'b-');
title('Dispersion Relation');
xlabel('k [2\pi/µm]');
ylabel('\omega [2\pi kHz]')
legend(['aBF=' num2str(aBF/a_0,'%.0f')],'bare Cs','Location','Northwest');
box on;
H=gca;
H.LineWidth=1.5; %change to the desired value     

subplot(1,3,2);
hold on;
plot(kplot,1e-3*gamma(1,:)*c1,'r--');
title('Damping');
xlabel('k [2\pi/µm]');
ylabel('\gamma [2\pi kHz]')
box on;
H=gca;
H.LineWidth=1.5; %change to the desired value     


subplot(1,3,3);hold on;
plot(kplot, 1e-3*c1*(omega2(1,:)-omega(1,:))./omega2(1,:),'r-');
title('Deviation caused by Fermion');
ylabel('\omega [2\pi kHz]')
xlabel('k [2\pi/µm]');
box on;
H=gca;
H.LineWidth=1.5; %change to the desired value    


saveStr = ['BF_dispersion_aBF=' num2str(aBF/a_0,'%.0f') 'aBB=' num2str(aBB/a_0,'%.0f') ];
saveas(P1,saveStr,'fig');
saveas(P1,saveStr,'png');
end



% end
