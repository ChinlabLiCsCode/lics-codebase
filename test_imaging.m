params = struct();
params.date = [2022 12 16];
params.view = [1, 100, 1, 1000];
params.cam = 'V';
params.atom = 'C';
shots = 71:80;
im = image_load(shots, params);