function [saveinig1D] = autoguess(ODimage,imagestack,fitframeno,xc,yc,dx,dy)
if fitframeno == 1
    tracex=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),1);
    tracey=sum(ODimage(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2))),2);
else
    tracex=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),1);
    tracey=sum(imagestack(round(yc-((dy-1)/2)):round(yc+((dy-1)/2)),round(xc-((dx-1)/2)):round(xc+((dx-1)/2)),fitframeno+1),2);
end
tracey=tracey';
secsizex=20;
xsize=size(tracex,2);
x=1:xsize;
if xsize > secsizex
    n=floor(xsize/secsizex);
    xsect=zeros(1,n);
    for i = 1 : n
        xsect(i)=sum(tracex(1+(i-1)*secsizex:i*secsizex))/secsizex;
    end
    bgx=min(xsect);
    saveinig1D.nx=max(xsect)-min(xsect);
    saveinig1D.wx=sum((tracex-bgx)>saveinig1D.nx*exp(-0.5))/2;
else
    bgx=0;
    saveinig1D.nx=max(tracex);
    saveinig1D.wx=sum((tracex-bgx)>saveinig1D.nx*exp(-0.5))/2;
end
saveinig1D.xc=sum(x.*(tracex-bgx))/sum(tracex-bgx);

secsizey=20;
ysize=size(tracey,2);
y=1:ysize;
if ysize > secsizey
    n=floor(ysize/secsizey);
    ysect=zeros(1,n);
    for i = 1 : n
        ysect(i)=sum(tracey(1+(i-1)*secsizey:i*secsizey))/secsizey;
    end
    bgy=min(ysect);
    saveinig1D.ny=max(ysect)-min(ysect);
    saveinig1D.wy=sum((tracey-bgy) > saveinig1D.ny*exp(-0.5))/2;
else
    bgy=0;
    saveinig1D.ny=max(tracey);
    saveinig1D.wy=sum((tracey-bgy) > saveinig1D.ny*exp(-0.5))/2;
end
saveinig1D.yc=sum(y.*(tracey-bgy)) / sum(tracey-bgy);

saveinig1D.bg=0.5*(bgx+bgy);