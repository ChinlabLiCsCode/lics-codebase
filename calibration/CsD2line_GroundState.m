%This code is tend for calculate the energy splitting of Cesium ground
%state in a magnetic field, for both F=3 and F=4. This situation is easily
%characterized by Breit-Rabi formula.
%Constants
I=7/2;
J=1/2;
L=0;
S=1/2;
u_Bohr=1.399624624;             %MHz*h/G
A_hfs=2298.1579425;             %MHz*h
g_s=2.0023193043737;            %Electron spin Lande-g factor
g_L=0.99999587;                 %Electron orbital Lande-g factor
g_I=-0.00039885395;             %Nuclar Lande-g factor

B=0:10:900;
figure
hold on;

%Plot the m_F=-3-->3 states by Breit Rabi Formula, the m_F=-4,+4 are not
%free from m_J coupling
for m_F=-3:1:3
    for m_J=-1/2:1:1/2
        plot( B, ZeemanHyper(B,m_F,m_J),'linewidth',1);
    end
end
plot( B, ZeemanHyper(B, 4, 1/2),'linewidth',1);
plot( B, ZeemanHyper(B,-4,-1/2),'linewidth',1);

ylabel('HyperFine Splitting (MHz)');
xlabel('Magnetic Field (G)');
title('Cesium 6^2S_{1/2} Level Hyperfine Structure in Magnetic Field');  %x^{\chi}_{\alpha}^{2}(3)  
ylim([-8000 6000]);

vpa(ZeemanHyper(892,3,-1/2),8)-vpa(ZeemanHyper(892,3,-1/2),8)

function deltaE=ZeemanHyper(B,m_F,m_J)   %Output unit: MHz    Magnetic field unit: G
%Constants
I=7/2;
J=1/2;
L=0;
S=1/2;
u_Bohr=1.399624624;             % MHz*h/G
A_hfs=2298.1579425;             % MHz*h
g_s=2.0023193043737;            % Electron spin Lande-g factor
g_L=0.99999587;                 % Electron orbital Lande-g factor
g_I=-0.00039885395;             % Nuclear Lande-g factor

E_hfs=A_hfs*(I+1/2);  % Energy Level Shift of Hyperfine Structure
g_J=0.5*g_L*(J^2+J-S^2-S-L^2-L)/(J^2+J)+0.5*g_s*(J^2+J+S^2+S-L^2-L)/(J^2+J);
x=B*(g_J-g_I)*u_Bohr/E_hfs;
if abs(m_F)<4
    deltaE= -A_hfs/4 + g_I*u_Bohr*m_F*B + m_J*E_hfs*sqrt(1+x.^2+4*m_F*x/(2*I+1));
else
    deltaE= A_hfs*7/4 + g_I*u_Bohr*m_F*B + g_J*u_Bohr*m_J*B;
end
end


