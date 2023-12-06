function [fitvals, fiterrs, ToverTF, N, Nc] = fermi_fit_2d(dat, guess, params, fignum, convert_units)
    % performs 2d fit of non-interacting fermions according to 
    % [Ketterle, Zwierlein (2008) - Making, probing, understanding ultracold
    % Fermi gases], eq. 65 and following
    % inputs: 
    %   dat: 2d array dat (e.g. average results of df_view_image_fk())
    %   guess: amplitude, q, x0, Rx, y0, Ry, background
    %        lengths in [mu m] if convert_units (default) else in [pix]
    %   params: normally li_params_fk, needs .pixel and .wavelength
    %   fignum: number of figure to plot, also determines name for saving
    %   convert_units: lengths are [mu m] if 1 (default), else [pix]
    % returns:
    %   fitvals, fiterrs: same as 'guess', fiterrs is std error of fit
    %       returns lengths in micro meters if convert_units == 1
    %   ToverTF: temperature in units of Fermi temperature
    %   N: total number of imaged atoms
    
    [L, H] = size(dat);
    x_Li = (1:L); % 1d grids in [pix]
    y_Li = (1:H); 
    
    px = params.pixel*1e6;  % conversion from pix to microns
    clims = [min(min(dat)), max(max(dat))];  % limits for color scales
    
    if nargin < 5
        convert_units = 1;
    end
    if convert_units
        guess([3 4 5 6]) = guess([3 4 5 6])/px;
    end
    
    figure(fignum);
    subplot(3,1,1);
    imagesc(x_Li*px, y_Li*px, dat', clims);
    title("data"); ylabel("y / \mum");
    colorbar();

    % set up 2d grid in [pix]
    [Xin, Yin] = meshgrid(x_Li, y_Li);  
    XY(:, :, 1) = Xin;
    XY(:, :, 2) = Yin;

    subplot(3,1,2);

    lb = [0 -Inf 0 0 0 0 -Inf]; % z > -.9 for fermi_fit
    ub = [Inf 9 Inf Inf Inf Inf Inf];  % z < 3.5 for fermi_fit
    [fitvals,~,res,~,~,~,jacob] = lsqcurvefit(@fermi_fit_Ketterle, guess, XY, dat', lb, ub);
    fermi_fit = fermi_fit_Ketterle(fitvals, XY);
    fermi_fit = abs(fermi_fit);
    imagesc(x_Li*px, y_Li*px, fermi_fit, clims);
    fiterrs = nlstandarderror(jacob,res);
    colorbar();
    
    ToTF = get_ToverTF(exp(fitvals(2)));
    u = get_ToverTF(exp(fitvals(2) + fiterrs(2))) - ToTF;
    l = get_ToverTF(exp(fitvals(2) - fiterrs(2))) - ToTF;
    e = max(abs([l, u]));
    
    title(sprintf("fit, T/T_F = %.4f \\pm %.4f", ToTF, e)); 
    ylabel("y / \mum");

    subplot(3,1,3);
    % imagesc(x_Li, y_Li, li_V_scan04imgsavgc' - fermi_fit_Ketterle(fitvals, XY));
    % colorbar();
    % title("data - fit");
    plot(x_Li*px, sum(dat,2));
    hold on;
    plot(x_Li*px, sum(fermi_fit_Ketterle(fitvals, XY),1));
    xlabel("x / \mum");
    ylabel("col dens (a.u.)");
    hold off
    ylim([min(sum(dat,2)), max(sum(dat,2))]);
    
    savefig(sprintf("fermi_2dfit_%d", fignum));
    saveas(gcf, sprintf("fermi_2dfit_%d.png", fignum));

    if nargout > 2
        ToverTF = ToTF;
        if nargout > 3
            N = get_N(fitvals, params); % fitvals in [pix]!!
            if nargout > 4
                Nc = count_pixels(dat, params);
            end
        end
    end
    

    if convert_units
        % convert radii and center positions to microns
        fitvals([3 4 5 6]) = fitvals([3 4 5 6])*px;
        fiterrs([3 4 5 6]) = fiterrs([3 4 5 6])*px^2;
    end
end

function y = fermi_fit_Ketterle(c, XYin)
    X = XYin(:, :, 1);   % meshgrid
    Y = XYin(:, :, 2);
    
    amplitude = c(1);
    q = c(2);  % q = beta mu, log of fugacity
    x0 = c(3);
    Rx = c(4);
    y0 = c(5); 
    Ry = c(6);
    bg = c(7);
    
    arg = exp(q -((X-x0).^2 ./ Rx^2 + (Y-y0).^2./Ry^2) .* f(exp(q)));
    % fprintf("min %.2f, max %.2f\n", min(arg(:)), max(arg(:)));
    y = amplitude .* polylog_num(2, -arg) ./ polylog(2, -exp(q)) + bg;
    
end

function y = f(x)
    y = (1+x) ./ x .* log(1+x);
end

function ToverTF = get_ToverTF(z)
    ToverTF = (-6 .* polylog(3, -z)).^(-1/3);
end

function N = get_N(fitres, params)
    n0 = fitres(1);
    q = fitres(2);  % q = beta mu, log of fugacity
    Rx = fitres(4); % in [pix]
    Ry = fitres(6); % in [pix]
    bg = fitres(7);

    A = params.pixel^2/(3*params.wavelength^2/(2*pi)); % (pixel area)/sigma0
    temp = polylog(3, -exp(q))/polylog(2, -exp(q))*polylog(0, -exp(q))/polylog(1, -exp(q));
    N = A * pi * (n0-bg) * Rx * Ry * temp;
        
end


function N = count_pixels(data, params)
    A = params.pixel^2/(3*params.wavelength^2/(2*pi));
    N = sum(sum(data)) * A;
end