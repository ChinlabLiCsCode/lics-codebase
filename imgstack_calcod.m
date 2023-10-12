function od = imgstack_calcod(A, L, bg, dfcase, bgcase, params)

%% subtract electronic background

if bgcase == 2
    A = A - bg;
    L = L - bg;
    
% atom set 
A = A - Abg;
% light set 
L = L - Lbg;

if debug 
    imgstack_viewer(A, 'A (after subtracting Abg)');
    imgstack_viewer(L, 'L (after subtracting Lbg)');
end

%% calculate mean light image and subtract from light and atom images

Lavg = mean(L, 3);

% atom set
dA = A - Lavg;
% light set
dL = L - Lavg;

if debug 
    imgstack_viewer(Lavg, 'Lavg');
    imgstack_viewer(dA, 'dA');
    imgstack_viewer(dL, 'dL');
end


%% perform defringing

dfobj = dfobj_create(dL, params.mask, params.pcanum);
dAprime = dfobj_apply(dA, dfobj);
Aprime = Lavg + dAprime;
if debug
    imgstack_viewer(dfobj.eigvecims, 'dfobj.eigvecims');
    imgstack_viewer(dA, 'dA')
    imgstack_viewer(dAprime, 'dAprime')
    imgstack_viewer(dAprime, 'Aprime')
end

%% calculate OD 

od = od_calc(A, Aprime, params);

if debug
    imgstack_viewer(od, 'OD');
end