function fitoutput = fit1Dgauss(OD, params)


tracex = sum(OD,1);
tracey = sum(OD,2);

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

% plb = [0 0 max(x)*0.4 1.25*min(tracex)-0.25*max(tracex)];
% qlb = [0 0 max(y)*0.4 1.25*min(tracey)-0.25*max(tracey)];
plb = [0 0 0 1.25*min(tracex)-0.25*max(tracex)];
qlb = [0 0 0 1.25*min(tracey)-0.25*max(tracey)];

if isfield(process_args,'xlb')
    plb = max(plb,process_args.xlb);
%     plb = process_args.xlb;
end

if isfield(process_args,'ylb')
    qlb = max(qlb,process_args.ylb);
%     qlb = process_args.ylb;
end

% pub = [1.25*(max(tracex)-min(tracex)) max(x)/8 max(x)*0.6 mean(tracex)];
% qub = [1.25*(max(tracey)-min(tracey)) max(y)/8 max(y)*0.6 mean(tracey)];
pub = [1.25*(max(tracex)-min(tracex)) max(x) Inf mean(tracex)];
qub = [1.25*(max(tracey)-min(tracey)) max(y) Inf mean(tracey)];

if isfield(process_args,'xub')
    pub = min(pub,process_args.xub);
%     pub = process_args.xub;
end

if isfield(process_args,'yub')
    qub = min(qub,process_args.yub);
%     qub = process_args.yub;
end

p(p < plb) = plb(p < plb);
p(p > pub) = pub(p > pub);
q(q < qlb) = qlb(q < qlb);
q(q > qub) = qub(q > qub);

if any(isnan(p)) || any(isnan(q))
    
end

pfit = lsqcurvefit(@g1D,p,x,tracex,plb,pub,options);
qfit = lsqcurvefit(@g1D,q,y,tracey,qlb,qub,options);


fittracex=pfit(1)*exp(-(x-pfit(3)).^2/2/(pfit(2)^2))+pfit(4);
fittracey=qfit(1)*exp(-(y-qfit(3)).^2/2/qfit(2)^2)+qfit(4);
fitparx.name='nx';
fitparx.fitval=pfit(1);
fitparx.inival=p(1);
fitparx(2).name='wx';
fitparx(2).fitval=pfit(2);
fitparx(2).inival=p(2);
fitparx(3).name='xc';
fitparx(3).fitval=pfit(3);
fitparx(3).inival=p(3);
fitparx(4).name='bgx';
fitparx(4).fitval=pfit(4);
fitparx(4).inival=p(4);

fitpary.name='ny';
fitpary.fitval=qfit(1);
fitpary.inival=q(1);
fitpary(2).name='wy';
fitpary(2).fitval=qfit(2);
fitpary(2).inival=q(2);
fitpary(3).name='yc';
fitpary(3).fitval=qfit(3);
fitpary(3).inival=q(3);
fitpary(4).name='bgy';
fitpary(4).fitval=qfit(4);
fitpary(4).inival=q(4);




function f = g1D(v,x)
f = v(1)*exp(-(x-v(3)).^2/2/(v(2)^2))+v(4);

