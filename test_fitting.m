
x = 1:200;
trace = exp(-x.^2./200);
mask = [20  180];


% configure independent variable
if size(trace, 1) == 1
    trace = trace';
end
x = (1:length(trace))';
low = mask(1);
high = mask(2);

% fit type 
ft = fittype(@(amp, sigma, x0, x) ...
    gauss1D(amp, sigma, x0, x));

% initial guesses and bounds
p0 = [max(trace(low:high)), (high - low)/10, (low + high)/2];
plb = [0, 0, low];
pub = [2.*max(trace(low:high)), high-low, high];

% perform fit
fo = fit(x, trace, ft, ...
    StartPoint=p0, Lower=plb, Upper=pub);

% get trace
fit_trace = fo(x);

% get coeffs and calculate physical quantities
coeffs = coeffvalues(fo);


% calculate fit parameters




function f = gauss1D(amp, sigma, x0, x)
    f = amp * exp(-(x-x0).^2/2/(sigma^2));
end
