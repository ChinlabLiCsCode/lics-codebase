k_B = 1.380649e-23;
hbar = 1.054572e-34; %reduced plank's constant
h = hbar * 2*pi; % planck length
amu = 1.660539040e-27; % 1 amu in kg
c = 299792458;
u_B = 927.400968e-26;
a_0 = 5.29177e-11; % bohr radius in m
q_e = 1.60217663e-19; % electron charge
muB = 9.27401007e-24; % bohr magneton in SI 
mu0 = 1.2566370614e-6; 
epsilon0 = 8.8541878176e-12;

%%% from makeconstants.m
% qe = 1.602e-19;
% amu = 1.660539040e-27;
% a0 = 5.29177e-11;
% muB = 9.274e-24;
% mLi = 6.*amu; %mass of lithium (kg)
% mCs = 133.*amu; %mass of Cesium (kg)
% hbar = 1.054572e-34; %reduced plank's constant
% h = hbar.*2.*pi;
% kb = 1.38064852e-23; %2020-04-21
% sigmali = 2.15e-13;
% lambdaLi = 671e-9;
% pixsize = 8.2e-6;
%%%

mLi = 6.*amu;   % mass of lithium (kg)
mCs = 133.*amu; % mass of Cesium (kg)

sigmali = 2.15e-13;
lambdaLi = 671e-9;

GammaD1Li = 2*pi * 5.8724e6;
GammaD2Li = 2*pi * 5.8724e6;

OmegaD1Li = 2*pi*446.789634*10^12;
OmegaD2Li = 2*pi*446.799677*10^12;

GammaD2Cs = 2*pi*5.234*10^6; 
OmegaD2Cs = 2*pi*351.72571850*10^12;

GammaD1Cs = 2*pi*4.575*10^6;
OmegaD1Cs = 2*pi*335.116048807*10^12;
