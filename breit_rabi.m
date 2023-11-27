function out_energy = breit_rabi(field,m_f,branch,atom_type)

%pre-programmed for 40K and 6Li and 133Cs

h = 6.62606957E-34;
u_B_si = 9.27400915E-24;

% in MHz/G
u_B = u_B_si*1E-4*1E-6/h;
out_energy = u_B*field;

if atom_type == 6 % lithium
	g_J = 2.0023010;
	g_I = -0.0004476540;
	a_HF = 152.1368407;
	I = 1;
elseif atom_type == 133 % cesium
	g_J = 2.00254032;
	g_I = -0.00039885395;
	a_HF = 2298.1579425;
	I = 7/2;
else % potassium
	g_J = 2.00229421;
	g_I = 0.000176490;
	a_HF = -285.7308;
	I = 4;
end

x = (g_J-g_I)*u_B/(a_HF*(I+1/2))*field;

temp1 = a_HF*(I+1/2)/2;
temp2 = 1 + 4*m_f*x/(2*I+1)+x.^2;

branch = branch*ones(size(x));
if m_f == -(I+1/2)*sign(a_HF)
	funny_sign = x*sign(a_HF) > 1;
	branch(funny_sign) = branch(funny_sign)*-1;
end

out_energy = -a_HF/4+g_I*u_B*m_f*field+temp1*branch.*sqrt(temp2);

