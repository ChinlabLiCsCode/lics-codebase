
clear;
close all;
clc;
day = [2023 10 02];
build_params;

bginfo = struct('date', [2023 09 29], 'shots', 68:97);
dfinfo = struct('date', [2023 09 29], 'shots', 98:199);
shots = struct('date', [2023 09 29], 'shots', 198:217);

proc_scan(shots, paramsCV_IS, shots.shots, dfinfo, bginfo, 'test', 'shot')


