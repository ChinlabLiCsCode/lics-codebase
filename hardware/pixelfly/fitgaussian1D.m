function [fittracex fittracey tracex tracey fitparx fitpary] = fitgaussian1D...
    (ODimage,imagestack,saveinig1D,fitframeno,xc,yc,dx,dy)
if fitframeno == 1
    tracex=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),1);
    tracey=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),2);
else
    tracex=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),1);
    tracey=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),2);
end
tracey=tracey';
p(1)=saveinig1D.nx;
p(2)=saveinig1D.wx;
p(3)=saveinig1D.xc;
q(1)=saveinig1D.ny;
q(2)=saveinig1D.wy;
q(3)=saveinig1D.yc;
p(4)=saveinig1D.bg;
q(4)=p(4);

options = optimset('TolX',1e-8);


[pfit pfval pexitflag]=fminsearch(@(v) fitg1D(v,tracex),p,options);
[qfit qfval qexitflag]=fminsearch(@(v) fitg1D(v,tracey),q,options);

x=1:length(tracex);
y=1:length(tracey);
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


function f = fitg1D(v,u)
x=1:length(u);
g1D=v(1)*exp(-(x-v(3)).^2/2/(v(2)^2))+v(4);
f=sum((u-g1D).^2);
% figure(3)
% plot(x,u)
% hold on
% plot(x,g1D,'r--')
% hold off

