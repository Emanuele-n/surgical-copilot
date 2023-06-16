clear all;
clc

% Define symbolic variables
% Unknowns vincular reactions and inputs
syms xc xs xh Fp P 'real';

% Geometry and material properties
syms Rc Rs Rh Ec Es Eh sIc Is Ih Ic Ac As Ah  'real'
syms hc 'real'

%% Solve symbolic system of equations
% Consider tube and hollow channel as parallel beams (same formulation as
%parallel springs) MODIFY WITH NEW FORMULATION
% M = [- 1/(Es*As + Eh*Ah) - 1/(Ec*Ac), - 1/(Es*As + Eh*Ah) - 1/(Ec*Ac);
%     -(2*Rh+2*Rs-hc)/(Es*Is + Eh*Ih) + 1/(Ec*Ic), + hc*(1/(Es*Is + Eh*Ih) - 1/(Ec*Ic));];
% 
% Y = [-Fp*(Es*As + Eh*Ah); -Fp*(2*Rh+Rs-hc)/(Es*Is + Eh*Ih);];
% 
% disp("##### Two systems problem results #####")
% N = [M, Y];
% disp('rank(M):')
% disp(rank(M))
% disp('rank(N):')
% disp(rank(N))
% 
% solution = simplify(subs(linsolve(M, Y)));
% disp(solution)
% 
% Ts = solution(1);
% Th = solution(2);
% 
% % Results
% epsilon = (Ts+Th)/(Ec*Ac);
% epsilon = simplify(subs(epsilon));
% vpa(epsilon)
% 
% kc = Rc*(Ts-Th)/(Ec*Ac);
% kc = simplify(subs(kc));
% vpa(kc)

%% Substitute Data 
% V: Verified data
% X: To be checked
% Initial length
L = 5*1e-3; % [m] V

% Initial curvature
k_0 = 0; % [1/m] V

% Outer radii
Rc = 0.4*1e-3; % [m] V
Rs = 0.15*1e-3; % [m] X
Rh = 0.15*1e-3; % [m] V

% Inner radii
Rci = 0.3*1e-3; % [m] X
Rsi = 0.075*1e-3; % [m] X
Rhi = 0.075*1e-3; % [m] X

% Area
Ac = pi*(Rc^2 - Rci^2); % External coil
As = pi*(Rs^2 - Rsi^2); % Silicon tube (now considered as hollow cylinder 0.3mm OD, better to consired half-hollow cylinder 0.6 mm OD)
Ah = pi*(Rh^2 - Rhi^2); % Hollow channel
Ap = pi*(Rsi^2);        % Water inside silicon tube (same discussion as silicon tube)
Ash = As + Ah;
Acsh = Ac + Ash;

% Young's modulus
Es = 1.648e6;
% 0.001	0.05 GPa (https://www.azom.com/properties.aspx?ArticleID=920)
% 1.648 MPa; % Cong paper
% 0.387 MPa (A Structural Optimisation Method for a Soft Pneumatic Actuator)  
% 2.69 3.57 3.84 4.51 4.27 MPa (https://www.researchgate.net/publication/314012355_Preparation_and_characterization_of_silicone_rubber_with_high_modulus_via_tension_spring-type_crosslinking)
% Young's modulus from spring constant
% k = F/dL ;  E*A/L = F/dL  -> E = k*L/A
spring_c = 0.035; % [N/m] % Cong paper
Ec = spring_c*L/Ac; % [Pa]
spring_h = 0.035; % [N/m]
Eh = spring_h*L/As; % [Pa]

% Moment of inertia
% Height of the centroid of every section
yc = Rc;
ys = Rc + Rs;
yh = Rh + Rc - Rci;

% Compute equivalent area (silicon as reference material)
Asn = As*Es/Es;
Ahn = Ah*Eh/Es;
Acn = Ac*Ec/Es;
Acshn = Asn + Ahn + Acn;

% Neutral axis
y_bar_area = (ys*As + yh*Ahn + yc*Acn)/(As + Ahn + Acn);
y_bar_parallel = (ys*Es*As + yh*Eh*Ah + yc*Ec*Ac)/(Es*As + Eh*Ah + Ec*Ac);
y_bar = y_bar_parallel;
%y_bar = Rc;

% Distances from centroid to neutral axis (take absolute value)
dc = abs(yc - y_bar);
ds = abs(ys - y_bar);
dh = abs(yh - y_bar);

% pi*(do^4 - di^4)/64 + Ad^4
Ic = pi*(Rc^4 - Rci^4)/4 + Ac*dc^2; 
Is = pi*(Rs^4 - Rsi^4)/4 + As*ds^2 ; % Consider full since there is water inside? (approximation)
Ih = pi*(Rh^4 - Rhi^4)/4 + Ah*dh^2 ;
Ish = Is + Ih; 
Icsh = Ic + Ish;  

% Inputs
P = P*1e6; % [Pa] -> [MPa]
Fp = P*Ap; % [N]

% epsilon = simplify(subs(epsilon));
% L_p = (epsilon + L)*1e3; %[m] -> [mm]
% disp("L_p = ")
% vpa(L_p) %0.111067
% 
% kc = simplify(subs(kc));
% k_p = (kc + k_0)*1e-3; %[1/m] -> [1/mm]
% disp("k_p = ")
% vpa(k_p) % 0.038811


%% Simplest case (consider the structure as a whole)
%Input moment from pressure
hp = Rc + Rs; % [m] (center of the silicon tube)
e = hp - y_bar; % [m] (center of the silicon tube - neutral axis)
M = Fp * e; % [Nm]

disp("##### One system problem results #####")
disp("AXIAL ELONGATION (target coef: 0.111067)")
epsilon_area = Fp / (Es*Acshn); % with area transformation
epsilon_parallel = Fp / (Es*As + Ec*Ac + Eh*Ah); % parallel springs
epsilon_area = simplify(epsilon_area);
epsilon_parallel = simplify(epsilon_parallel);
%fprintf('Transformed cross-section method:\nepsilon = %s\n',char(vpa(epsilon_area))) % 0.111067
fprintf('\nParallel spring method: \nepsilon = %s\n',char(vpa(epsilon_parallel))) % 0.111067

disp(" ")
disp("CURVATURE (target coef: 0.038811)")
k_parallel = M / (Es*Is + Ec*Ic + Eh*Ih)*1e-3;
k_parallel = simplify(k_parallel);
fprintf('\nParallel spring method: \nk = %s\n',char(vpa(k_parallel))) % 0.038811

%% Considerd three bodies separately
% % Define M and Y matrices
% M = [1/(Es*As), 1/(Ec*Ac)+1/(Es*As), 1/(Ec*Ac);
%     -1/(Es*As)-1/(Eh*Ah), -1/(Es*As), 1/(Eh*Ah);
%     -1/(Eh*Ah), 1/(Ec*Ac), 1/(Ec*Ac)+1/(Eh*Ah);
%     0, Rc/(Ec*Ic)+2*Rs/(Es*Is), -Rc/(Ec*Ic);
%     0, -2*Rs/(Es*Is), -2*Rh/(Eh*Ih);
%     0, Rc/(Ec*Ic), -Rc/(Ec*Ic)-2*Rh/(Eh*Ih);
% 
% ];
% 
% X = [xc; xs; xh];
% Y = [Fp/(Es*As), -Fp/(Es*As), 0, Rs*Fp/(Es*Is), -Rs*Fp/(Es*Is), 0]';
% 
% N = [M, Y];
% disp(M)
% disp(N)
% 
% % Rouchè-Capelli:
% % Unique solution if and only if rank(M) = rank(N) 
% % Infinite solutions if rank(M) < rank(N)
% % No solutions if rank(M) > rank(N)
% 
% disp('rank(M):')
% disp(rank(M))
% disp('rank(N):')
% disp(rank(N))
% 
% 
% % Solve the system of linear equations for X
% solution = simplify(subs(linsolve(M, Y)));
% disp(solution)
% 
% % Elongation only
% M = M((1:3),:);
% Y = Y(1:3);
% N = [M, Y];
% disp(M)
% disp(N)
% 

% 
% 
% % Solve the system of linear equations for X
% solution = simplify(subs(linsolve(M, Y)));
% disp(solution)