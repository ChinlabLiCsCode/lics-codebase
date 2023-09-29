function pars = fit1Dgauss(OD, params, fitdat)

% OD should be a matrix

mask = params.mask;
tracex = sum(OD(mask(3):mask(4), :), 1);
tracey = sum(OD(:, mask(1):mask(2)), 2);

p(1) = max(tracex(mask(1):mask(2)));
p(2) = (mask(2)-mask(1))/10;
p(3) = (mask(1)+mask(2))/2;
p(4) = mean(tracex([1:(mask(1)-1) (mask(2)+1):numel(tracex)]));

q(1) = max(tracey(mask(3):mask(4)));
q(2) = (mask(4)-mask(3))/10;
q(3) = (mask(3)+mask(4))/2;
q(4) = mean(tracey([1:(mask(3)-1) (mask(4)+1):numel(tracey)]));

x=1:length(tracex);
y=1:length(tracey);

plb = [0 0 0 1.25*min(tracex)-0.25*max(tracex)];
qlb = [0 0 0 1.25*min(tracey)-0.25*max(tracey)];

pub = [1.25*(max(tracex)-min(tracex)) max(x) Inf mean(tracex)];
qub = [1.25*(max(tracey)-min(tracey)) max(y) Inf mean(tracey)];

p(p < plb) = plb(p < plb);
p(p > pub) = pub(p > pub);
q(q < qlb) = qlb(q < qlb);
q(q > qub) = qub(q > qub);

pfit = lsqcurvefit(@g1D,p,x,tracex,plb,pub,options);
qfit = lsqcurvefit(@g1D,q,y,tracey,qlb,qub,options);

fittracex=pfit(1)*exp(-(x-pfit(3)).^2/2/(pfit(2)^2))+pfit(4);
fittracey=qfit(1)*exp(-(y-qfit(3)).^2/2/qfit(2)^2)+qfit(4);

pars = cell(1, length(fitdat.cols));
for i = 1:length(fitdat.cols)
    switch fitdat.cols{i}
        case 'tracex'
            pars{i} = tracex;
        case 'tracey'
            pars{i} = tracey;
        case 'fittracex'
            pars{i} = fittracex;
        case 'fittracey'
            pars{i} = fittracey;
        case 'nx'
            pars{i} = pfit(1);
        case 'wx'
            pars{i} = pfit(2);
        case 'xc'
            pars{i} = pfit(3);
        case 'bgx'
            pars{i} = pfit(4);
        case 'ny'
            pars{i} = qfit(1);
        case 'wy'
            pars{i} = qfit(2);
        case 'yc'
            pars{i} = qfit(3);
        case 'bgy'
            pars{i} = qfit(4);
    end
end







function f = g1D(v,x)
f = v(1)*exp(-(x-v(3)).^2/2/(v(2)^2))+v(4);

