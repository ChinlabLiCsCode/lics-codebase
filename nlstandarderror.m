%nlstandarderror.m
%Calculates the Standard Error of Mean for fitting parameters given the
%Jacobian and residuals of the fit. Assumes a Jacobian of the form given by
%lsqcurvefit.
%INPUTS:
%jacob: Jacobian matrix
%res: Residuals of the fit
%deg (OPTIONAL): Number of degrees of freedom. The default is to calculate
%the number of degrees of freedom from the size of the Jacobian.

function se = nlstandarderror(jacob,res,deg)

if nargin<3 || isempty(deg)
    sz = size(jacob);
    deg = max(sz)-min(sz);
end

[~,R] = qr(jacob,0);
Rinv = R\eye(size(R));
diag_info = sum(Rinv.*Rinv,2);

rmse = norm(res)/sqrt(deg);
se = sqrt(diag_info)*rmse;
se = se';