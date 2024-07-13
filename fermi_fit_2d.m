function [fitvals, fiterrs, ToverTF, N, Nc] = fermi_fit_2d(img, params, varargin)
% performs 2d fit of non-interacting fermions according to 
% [Ketterle, Zwierlein (2008) - Making, probing, understanding ultracold
% Fermi gases], eq. 65 and following
% inputs: 
%   dat: 2d array dat (e.g. average results of df_view_image_fk())
%   guess: amplitude, q, x0, Rx, y0, Ry, background
%        lengths in [mu m] if convert_units (default) else in [pix]
%   params: normally li_params_fk, needs .pixel and .wavelength
%   convert_units: lengths are [mu m] if 1 (default), else [pix]
% returns:
%   fitvals, fiterrs: same as 'guess', fiterrs is std error of fit
%       returns lengths in micro meters if convert_units == 1
%   ToverTF: temperature in units of Fermi temperature
%   N: total number of imaged atoms

while ndims(img) > 2
    img = squeeze(mean(img, 1));
end
[nY, nX] = size(img);
yvals = (1:nY)'; % 1d grids in [pix]
xvals = (1:nX)'; 

pix = params.pixel*1e6;  % conversion from pix to microns
xvals = xvals;
yvals = yvals;
img = img;

clims = [min(min(img)), max(max(img))];  % limits for color scales

figure();
subplot(3,1,1);
imagesc(xvals, yvals, img, clims);
title("data"); 
ylabel("y [pix]");
colorbar();

% set up 2d grid in [pix]
[Xgrid, Ygrid] = meshgrid(xvals, yvals);  

subplot(3,1,2);

% prep fit parameters
ft = fittype(@(amp, q, x0, Rx, y0, Ry, bg, X, Y) ...
    fermi_fit_Ketterle(amp, q, x0, Rx, y0, Ry, bg, X, Y),...
    independent=["X", "Y"]);
sp = [max(img(:)), 6, mean(xvals), mean(xvals), mean(yvals), mean(yvals), 0];
lb = [0 -Inf 0 0 0 0 -Inf]; % z > -.9 for fermi_fit
ub = [Inf 9 Inf Inf Inf Inf Inf];  % z < 3.5 for fermi_fit

% do fit
fo = fit([Xgrid(:), Ygrid(:)], img(:), ft, ...
    Start=sp, Lower=lb, Upper=ub);
% evaluate fit
fermi_fit = reshape(fo([Xgrid(:), Ygrid(:)]), size(img));
fermi_fit = abs(fermi_fit);

% extract quantities 
fitvals = coeffvalues(fo);
fiterrs = confint(fo);
fiterrs = (fiterrs(2, :) - fiterrs(1, :)) / 4;
ToTF = get_ToverTF(exp(fitvals(2)));
u = get_ToverTF(exp(fitvals(2) + fiterrs(2))) - ToTF;
l = get_ToverTF(exp(fitvals(2) - fiterrs(2))) - ToTF;
e = max(abs([l, u]));

% plot fit
imagesc(xvals, yvals, fermi_fit, clims);
colorbar();
title(sprintf("fit, T/T_F = %.4f \\pm %.4f", ToTF, e)); 
ylabel("y [pix]");

subplot(3,1,3);
plot(xvals, sum(img, 1));
hold on;
plot(xvals, sum(fermi_fit, 1));
xlabel("x [pix]");
ylabel("density [atoms/pix]");
hold off
% ylim([min(sum(img,2)), max(sum(img,2))]);

savefig(sprintf("fermi_2dfit"));
saveas(gcf, sprintf("fermi_2dfit.png"));

if nargout > 2
    ToverTF = ToTF;
    if nargout > 3
        N = get_N(fitvals, params); % fitvals in [pix]!!
        if nargout > 4
            Nc = count_pixels(img, params);
        end
    end
end


end

function y = fermi_fit_Ketterle(amp, q, x0, Rx, y0, Ry, bg, X, Y)
    arg = exp(q -((X-x0).^2 ./ Rx^2 + (Y-y0).^2./Ry^2) .* f(exp(q)));
    % fprintf("min %.2f, max %.2f\n", min(arg(:)), max(arg(:)));
    y = amp .* polylog_num(2, -arg) ./ polylog(2, -exp(q)) + bg;
    
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

    % A = params.pixel^2/(3*params.wavelength^2/(2*pi)); % (pixel area)/sigma0
    A = 1; % pretty sure this factor is already accounted for now.
    temp = polylog(3, -exp(q))/polylog(2, -exp(q))*polylog(0, -exp(q))/polylog(1, -exp(q));
    N = A * pi * (n0-bg) * Rx * Ry * temp;
        
end


function N = count_pixels(data, params)
    % A = params.pixel^2/(3*params.wavelength^2/(2*pi));
    A = 1;
    N = sum(sum(data)) * A;
end