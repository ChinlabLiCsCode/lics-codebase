function h = scanfig_init(params, xvals, figname, xvalname)

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
h.fig = figure('Name', figname, 'NumberTitle', 'off', 'Units', 'normalized', 'OuterPosition', [0 0 1 1]);


% OD axis 
h.OD = subplot(3, 4, 1:3);
axis(h.OD, "image");
colorbar(h.OD);

% total flour axis
h.n_count = subplot(3, 4, 4);
xlabel(h.n_count, xvalname);
ylabel(h.n_count, "Counted atoms");

% 1D fit axes
h.x = makerow(xft, 1, xvalname);
h.y = makerow(yft, 2, xvalname);

end


function hr = makerow(fittype, ind, xvalname)
% Make a row of plots for a given fittype
hr = struct();
switch fittype
    case 'gauss'
        n = 4;
        hr.sigma_um = subplot(3, n, ind*n + 4);
        xlabel(hr.sigma_um, xvalname);
        ylabel(hr.sigma_um, "Fitted sigma (um)");
        
    case 'dbl'
        n = 5;
        hr.sigma_um = subplot(3, n, ind*n + 4);
        xlabel(hr.sigma_um, xvalname);
        ylabel(hr.sigma_um, "Fitted sigma (um)");

        hr.sep_um = subplot(3, n, ind*n + 5);
        xlabel(hr.sep_um, xvalname);
        ylabel(hr.sep_um, "Fitted separation (um)");

    case 'tf'
        n = 4;
        hr.rtf_um = subplot(3, n, ind*n + 4);
        xlabel(hr.rtf_um, xvalname);
        ylabel(hr.rtf_um, "Fitted rtf (um)");
end

% we do these plots for everything
hr.trace = subplot(3, n, ind*n + 1);
xlabel(hr.trace, "Position (pix)");
ylabel(hr.trace, "Integrated OD");

hr.nfit = subplot(3, n, ind*n + 2);
xlabel(hr.nfit, xvalname);
ylabel(hr.nfit, "Fitted atom number");

hr.center_um = subplot(3, n, ind*n + 3);
xlabel(hr.center_um, xvalname);
ylabel(hr.center_um, "Fitted center (um)");

end