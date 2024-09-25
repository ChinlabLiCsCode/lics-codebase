clear; close all; clc;

today = [2024 09 23];
load_params(today, true);
vdfset = 26:28;
%%
close all;
vals = 0.53 : 0.003 : 0.58;
shots = genshots(vals, 64, 3);
scan = proc_scan(paramsCV_IS, shots, vdfset, 'xvals', vals, ...
    'xvalname', 'int lock val', 'figname', 'intlockscan01', ...
    'debug', true, 'macrocalc', {'n_count', 'peak'});
scan.n_count

%%
figure();
imagesc(squeeze(scan.ND(3, 2, :, :)))