today = [2023 10 17];

gaussfig = {...
    {3, {'nd', 1:2}, {'n_count', 3}}, ...
    {5, {'x_trace', 1:2}, {'x_nfit', 3}, {'x_sigma', 4}, {'x_center', 5}}, ...
    {5, {'y_trace', 1:2}, {'y_nfit', 3}, {'y_sigma', 4}, {'y_center', 5}}, ...
    };
tffig = {...
    {3, {'nd', 1:2}, {'n_count', 3}}, ...
    {5, {'x_trace', 1:2}, {'x_nfit', 3}, {'x_rtf', 4}, {'x_center', 5}}, ...
    {5, {'y_trace', 1:2}, {'y_nfit', 3}, {'y_rtf', 4}, {'y_center', 5}}, ...
    };
fieldcalfig = {...
    {3, {'nd', 1:2}, {'n_count', 3}}, ...
    {5, {'x_trace', 1:2}, {'x_nfit', 3}, {'x_sigma', 4}, {'x_center', 5}}, ...
    {6, {'y_trace', 1:2}, {'y_nfit', 3}, {'y_sigma', 4}, {'y_center', 5}, {'y_fit', 6}}, ...
    };

% cs h params
paramsCH_IS = struct( ...
    'atom', 'C', ...
    'cam', 'H', ...
    'wavelength', 852.347e-9, ...
    'pixel', 7.72e-6, ...
    'I_sat', Inf, ...
    'alpha', [1 0 0], ...
    'view', [820 1060 215 275], ...
    'mask', [105 175 5 45], ...
    'fittype', 'gauss', ...
    'date', today, ...
    'pcanum', 50, ...
    'debug', false, ...
    'dfmethod', 'norm');
paramsCH_IS.pltinfo = gaussfig;

paramsCH_RSC = paramsCH_IS;
paramsCH_RSC.view = [600 1200 400 1000];
paramsCH_RSC.mask = [40 560 40 560];

paramsCH_BEC = paramsCH_IS;
paramsCH_BEC.view = [900 1000 770 870];
paramsCH_BEC.mask = [20 80 20 80];

paramsCH_B = paramsCH_IS;
paramsCH_B.view = [825 1075 200 300];
paramsCH_B.mask = [5 245 20 80];
paramsCH_B.fittype = {'dbl', 'gauss'};

paramsCH_MOT = paramsCH_IS;
paramsCH_MOT.view = [300 1000 400 1000];
paramsCH_MOT.mask = [60 140 60 140];


% li h params
paramsLH_IS = paramsCH_IS;
paramsLH_IS.atom = 'L';
paramsLH_IS.wavelength = 670.977e-9;
paramsLH_IS.view = [910 1010 200 300];
paramsLH_IS.mask = [20 80 20 80];

paramsLH_MOT = paramsLH_IS;
paramsLH_IS.view = [770 1170 50 450];
paramsLH_IS.mask = [20 380 20 380];


% cs v params
paramsCV_IS = struct( ...
    'atom', 'C', ...
    'cam', 'V',...
    'wavelength', paramsCH_IS.wavelength, ...
    'pixel', 0.78e-6, ...
    'I_sat', 125, ...
    'alpha', [1.23 0.19 0.0051], ...
    'view', [1 70 325 875], ...
    'mask', [11 50 51 451], ...
    'fittype', 'gauss', ...
    'date', today, ...
    'pcanum', 50, ...
    'debug', false, ...
    'dfmethod', 'norm');
paramsCV_IS.pltinfo = tffig;

% li v params
paramsLV_IS = struct( ...
    'atom', 'L', ...
    'cam', 'V', ...
    'wavelength', paramsLH_IS.wavelength, ...
    'pixel', paramsCV_IS.pixel, ...
    'I_sat', 125, ...
    'alpha', [1 0 0], ...
    'view', [1 70 325 875], ...
    'mask', [11 50 51 451], ...
    'fittype', 'gauss', ...
    'date', today, ...
    'pcanum', 50, ...
    'debug', false, ...
    'dfmethod', 'norm');
paramsLV_IS.pltinfo = gaussfig;
