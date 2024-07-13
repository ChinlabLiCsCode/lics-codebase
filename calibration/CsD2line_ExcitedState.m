%This code is tend for calculate the energy splitting of Cesium D2 line excited
%state in a magnetic field, for both F=2,3,4,5. The Hamiltonian is
%block-diagonalized in different m_F states(Total angular momentum is
%conserved in this process). m_F=5,-5: uncoupled states; m_F=4,-4:
%Breit-Rabi Formula applies; The rest states requies diagonalizing the
%matrix numerically.

figure
hold on;

Bmax= 900;
Bstep= 10;

B=0:Bstep:Bmax;
E=zeros(32,length(B));
count=0;
for B=0:Bstep:Bmax            %Unit in G
    count=count+1;
%Matrix of States
M=[  5   4   4    3   3   3    2    2   2   2    1    1   1    1    0    0    0    0   -1   -1   -1   -1   -2   -2   -2   -2   -3   -3   -3   -4   -4   -5;     %m_F
   3.5 3.5 2.5  3.5 2.5 1.5  3.5  2.5 1.5 0.5  2.5  1.5 0.5 -0.5  1.5  0.5 -0.5 -1.5  0.5 -0.5 -1.5 -2.5 -0.5 -1.5 -2.5 -3.5 -1.5 -2.5 -3.5 -2.5 -3.5 -3.5;     %m_I
   1.5 0.5 1.5 -0.5 0.5 1.5 -1.5 -0.5 0.5 1.5 -1.5 -0.5 0.5  1.5 -1.5 -0.5  0.5  1.5 -1.5 -0.5  0.5  1.5 -1.5 -0.5  0.5  1.5 -1.5 -0.5  0.5 -1.5 -0.5 -1.5];    %m_J 
H=zeros(32,32);    % Hamiltonian
I=7/2;
J=3/2;
S=1/2;
u_B=1.399624624;      %MHz*h/G  Bohr Magneton
A_hfs=50.275;         %MHz*h   Magnetic Dipole Constant for 6P3/2
B_hfs=-0.53;          %MHz*h    
g_s=2.0023193043737;  %Electron spin Lande-g factor
g_L=0.99999587;       %Electron orbital Lande-g factor
g_I=-0.00039885395;   %Nuclar Lande-g factor
g_J=1.3340;           %2P3/2 Lande-g factor


%diag 
for i=1:32
    H(i,i)=u_B*B*(g_J*M(3,i)+g_I*M(2,i)) + A_hfs*M(2,i)*M(3,i)  + (B_hfs/((2*I^2-I)*(2*J^2-J)))*(  -0.5*(I+I^2)*(J+J^2) + 0.75*M(3,i)*M(2,i) + 1.5*M(3,i)^2*M(2,i)^2 + 0.75*( (J+M(3,i))*(J-M(3,i)+1)*(I-M(2,i))*(I+M(2,i)+1)+(I+M(2,i))*(I-M(2,i)+1)*(J-M(3,i))*(J+M(3,i)+1)) );                                       
end
for ii=1:31
    if M(1,ii)==M(1,ii+1)
        H(ii,ii+1)=( 0.5*A_hfs +( B_hfs/((2*I^2-I)*(2*J^2-J)) )*(3/8 + 1.5*M(2,ii)*M(3,ii)) )*sqrt( (J-M(3,ii))*(J+M(3,ii)+1)*(I+M(2,ii))*(I-M(2,ii)+1) );
        H(ii+1,ii)= H(ii,ii+1);
    end
end
for j=1:30
    if M(1,j)==M(1,j+2)
        H(j,j+2)=(3*B_hfs/(8*(2*I^2-I)*(2*J^2-J) ))*sqrt( (J+M(3,j)+2)*(J+M(3,j)+1)*(J-M(3,j))*(J-M(3,j)-1)*(I+M(2,j))*(I-M(2,j)+1)*(I+M(2,j)-1)*(I-M(2,j)+2) );
        H(j+2,j)=H(j,j+2);
%         H(j+2,j)=(3*B_hfs/(8*(2*I^2-I)*(2*J^2-J) ))*sqrt( (J+M(3,j)+2)*(J+M(3,j)+1)*(J-M(3,j))*(J-M(3,j)-1)*(I+M(2,j))*(I-M(2,j)+1)*(I+M(2,j)-1)*(I-M(2,j)+2) );
    end
end

E(:,count)=eig(H);
end

B=0:Bstep:Bmax;

for i=1:32
    plot(B,E(i,1:length(B)));
end
ylabel('HyperFine Splitting (MHz)');
xlabel('Magnetic Field (G)');
title('Cesium 6^2P_{3/2} Level Hyperfine Structure in Magnetic Field');








