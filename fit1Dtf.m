%% Fit function for Thomas-Fermi (TF) condensate
% Parabola

function [fittracex fittracey tracex tracey fitparx fitpary] = fittf1D...
    (ODimage,imagestack,saveinig1D,fitframeno,xc,yc,dx,dy,mask,process_args)

if nargin < 10
    process_args = struct();
end

if nargin<9 || isempty(mask)
    if fitframeno == 1
        tracex=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),1);
        tracey=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),2);
    else
        tracex=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),1);
        tracey=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),2);
    end
else
    if fitframeno == 1
        tracex=sum(ODimage(round(yc-((dy-1)/2)+mask(3)):round(yc-((dy-1)/2)+mask(4)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),1);
        tracey=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)+mask(1)):round(xc-((dx-1)/2)+mask(2))),2);
    else
        tracex=sum(imagestack(round(yc-((dy-1)/2)+mask(3)):round(yc-((dy-1)/2)+mask(4)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),1);
        tracey=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)+mask(1)):round(xc-((dx-1)/2)+mask(2)),fitframeno+1),2);
    end
end

tracey=tracey';

p(1)=saveinig1D.nx;
p(2)=saveinig1D.wx;
p(3)=saveinig1D.xc;
p(4)=saveinig1D.nx;
p(5)=saveinig1D.wx;
q(1)=saveinig1D.ny;
q(2)=saveinig1D.wy;
q(3)=saveinig1D.yc;
q(4)=saveinig1D.ny;
q(5)=saveinig1D.wy;
p(6)=saveinig1D.bg;
q(6)=p(4);

p(1) = max(tracex(mask(1):mask(2)));
p(2) = (mask(2)-mask(1))/10;
p(3) = (mask(1)+mask(2))/2;
p(4) = max(tracex(mask(1):mask(2)))/4;
p(5) = (mask(2)-mask(1))/5;
p(6) = mean(tracex([1:(mask(1)-1) (mask(2)+1):numel(tracex)]));

q(1) = max(tracey(mask(3):mask(4)));
q(2) = (mask(4)-mask(3))/10;
q(3) = (mask(3)+mask(4))/2;
q(4) = max(tracey(mask(3):mask(4)))/4;
q(5) = (mask(4)-mask(3))/5;
q(6) = mean(tracey([1:(mask(3)-1) (mask(4)+1):numel(tracey)]));

options = optimset('TolX',1e-8,'Display','off');

x=1:length(tracex);
y=1:length(tracey);

% plb = [0 0 max(x)*0.4 1.25*min(tracex)-0.25*max(tracex)];
% qlb = [0 0 max(y)*0.4 1.25*min(tracey)-0.25*max(tracey)];
%plb = [0 0 0 0 0 1.25*min(tracex)-0.25*max(tracex)];
%qlb = [0 0 0 0 0 1.25*min(tracey)-0.25*max(tracey)];
plb = [0 0 0 0 0 -Inf];
qlb = [0 0 0 0 0 -Inf];

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
%pub = [1.25*(max(tracex)-min(tracex)) max(x) Inf max(tracex)-min(tracex) max(x) mean(tracex)];
%qub = [1.25*(max(tracey)-min(tracey)) max(y) Inf max(tracey)-min(tracey) max(y) mean(tracey)];
pub = [Inf Inf Inf Inf Inf Inf];
qub = [Inf Inf Inf Inf Inf Inf];

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

pfit = lsqcurvefit(@tf1D,p,x,tracex,plb,pub,options);
qfit = lsqcurvefit(@tf1D,q,y,tracey,qlb,qub,options);
%[pfit pfval pexitflag]=fminsearch(@(v) fitg1D(v,tracex),p,options);
%[qfit qfval qexitflag]=fminsearch(@(v) fitg1D(v,tracey),q,options);

if pfit(2)>pfit(5)
    temp = pfit(2);
    pfit(2) = pfit(5);
    pfit(5) = temp;
    
    temp = pfit(1);
    pfit(1) = pfit(4);
    pfit(4) = temp;
end

if qfit(2)>qfit(5)
    temp = qfit(2);
    qfit(2) = qfit(5);
    qfit(5) = temp;
    
    temp = qfit(1);
    qfit(1) = qfit(4);
    qfit(4) = temp;
end

fittracex=tf1D(pfit,x);
fittracey=tf1D(qfit,y);
fitparx.name='nx';
fitparx.fitval=pfit(1);
fitparx.inival=p(1);
fitparx(2).name='wx';
fitparx(2).fitval=pfit(2);
fitparx(2).inival=p(2);
fitparx(3).name='xc';
fitparx(3).fitval=pfit(3);
fitparx(3).inival=p(3);
fitparx(4).name='nx2';
fitparx(4).fitval=pfit(4);
fitparx(4).inival=p(4);
fitparx(5).name='wx2';
fitparx(5).fitval=pfit(5);
fitparx(5).inival=p(5);
fitparx(6).name='bgx';
fitparx(6).fitval=pfit(6);
fitparx(6).inival=p(6);

fitpary.name='ny';
fitpary.fitval=qfit(1);
fitpary.inival=q(1);
fitpary(2).name='wy';
fitpary(2).fitval=qfit(2);
fitpary(2).inival=q(2);
fitpary(3).name='yc';
fitpary(3).fitval=qfit(3);
fitpary(3).inival=q(3);
fitpary(4).name='ny2';
fitpary(4).fitval=qfit(4);
fitpary(4).inival=q(4);
fitpary(5).name='wy2';
fitpary(5).fitval=qfit(5);
fitpary(5).inival=q(5);
fitpary(6).name='bgy';
fitpary(6).fitval=qfit(6);
fitpary(6).inival=q(6);




%TF fit (KP)
function f = tf1D(v,x)
%sort for zeros to truncate parabola (~max function in TF)
arg = 1-((x-v(3))/v(2)).^2;
arg(arg<0)=0;
%return function
f = v(1).*(arg).^(3/2);



