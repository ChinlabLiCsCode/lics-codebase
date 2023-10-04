function h = scanfig_init(params, figname)

% extract fittype args
ft = params.fittype;
if iscell(ft)
    xft = ft{1};
    yft = ft{2};
else
    xft = ft;
    yft = ft;
end

% Initialize the plot
h = struct();
% disp(figname)
h.fig = figure('Name', figname, 'NumberTitle', 'off', 'Units', 'normalized', 'OuterPosition', [0 0 1 1]);


% OD axis 
h.OD = subplot(3, 4, 1:3);
axis(h.OD, "image");
colorbar(h.OD);

% total flour axis
h.n_count = subplot(3, 4, 4);

% 1D fit axes
h.x = makerow(xft, 1);
h.y = makerow(yft, 2);

end


function hr = makerow(fittype, ind)
% Make a row of plots for a given fittype
hr = struct();
switch fittype
    case 'gauss'
        n = 4;
        hr.sigma_um = subplot(3, n, ind*n + 4);
        
    case 'dbl'
        n = 5;
        hr.sigma_um = subplot(3, n, ind*n + 4);
        hr.sep_um = subplot(3, n, ind*n + 5);

    case 'tf'
        n = 4;
        hr.rtf_um = subplot(3, n, ind*n + 4);
end

% we do these plots for everything
hr.trace = subplot(3, n, ind*n + 1);
hr.nfit = subplot(3, n, ind*n + 2);
hr.center_um = subplot(3, n, ind*n + 3);

end