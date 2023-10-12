
clear;
close all;
clc;
day = [2023 10 02];
build_params;

params = paramsCV_IS;
params.pcanum = 50;
params.dfmethod = 'odavg';
params.debug = true;

bginfo = {[2023 09 29], 5:64};
dfinfo = {[2023 09 29], 98:199};
shots = {[2023 09 29], 198:217};


od = proc_imgs(shots, params, dfinfo, bginfo);