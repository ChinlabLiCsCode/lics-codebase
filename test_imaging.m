
clear;
close all;
clc;
build_params;

params = paramsCV_IS;
params.debug = true;

% bginfo = {[2023 09 29], 5:64};
% dfinfo = {[2023 09 29], 98:199};
% shots = {[2023 09 29], 198:217};
bginfo = 'none';
dfinfo = {[2023 10 13], 5:105};
shots = {[2023 10 13], 110:130};
    

od = proc_imgs(shots, params, dfinfo, bginfo);


%% test for figure production

clear;
close all;
clc;
day = [2023 10 17];
build_params;

scanfig_init(paramsCV_IS, 'test');


%% defringing test
clear;
clc;
close all;

nx = 100;
ny = 100;
lambda = 10;

x = 1:nx;
y = 1:ny;

[X, Y] = meshgrid(x, y);
mask = [25, 75, 25, 75];

im1 = 10 .* ones([nx, ny]);
im2 = 2 .* im1;
im3 = im1 + 2.*sin((X + Y)/lambda);
im4 = im1 + 3.*cos((X + Y)/lambda);
im5 = 1.5*im1 + 4.*sin((X + Y)/lambda);


L = cat(1, im1, im2, im3, im4, im5);
L = cat(1, L, L, L, L);
L = L + randn(size(L));
imgstack_viewer(L, 'L');
dfobj = dfobj_create(L, mask, Inf);
imgstack_viewer(dfobj.eigvecims, 'eigvecs');


A = im1 + 5.*sin((X + Y)/lambda + 1);
Lavg = mean(L, 3);
Aprime1 = dfobj_apply(A, dfobj);
Aprime2 = Lavg + dfobj_apply(A-Lavg, dfobj);
imgstack_viewer(A, 'A');
imgstack_viewer(Aprime1, 'Aprime1');
imgstack_viewer(A-Aprime1, 'A-Aprime1');
imgstack_viewer(Aprime2, 'Aprime2');
imgstack_viewer(A-Aprime2, 'A-Aprime2');