%% Cs Fitting and Thermometry
% The purpose of this code is to think about how to do some smarter
% fittting now that we have BEC, before working it into the processing
% scripts on the LiCs computers. 
% "Making and Probing" good ref. for this

%c0 is initial fit guess
%img specifies the image
%tof -> time of flight. Specify as array, with first number time spent at
%high field and second number total tof (typically [10e-3 25e-3]


function outStruct = CsTOF(img,tof,fignum,c0x)
make_constants;
img = squeeze(img);
imslcx = trapz(img,1);
imslcy = trapz(img,2);
x = 1:length(imslcx);
y = 1:length(imslcy);
%Fit
opts = optimset('Display','off'); %suppress output. Undo this if you are troubleshooting.

%c0x = [7 1 50 0.0 10 0];
%reasonable y guess
c0y = c0x;
c0y(1) = 400;
c0y(3) =55;
c0y(2) = 10;
c0y(4) = 0;
%c0y(1) = c0x(1);
%c0y(3) = 10; c0y(2) = 5; c0y(5) = c0y(2)*10;
%c0y(4)=0;
LB = [0 0 0 0 0 -Inf]; UB = [Inf Inf Inf Inf Inf Inf];
%kill thermal part?
%UB = [Inf Inf Inf 0 Inf Inf];

LBtf = [0 0 0 -Inf];
UBtf = [Inf Inf Inf Inf];
fit1dtffuncCall = @(c,x) fit1dtf(c,x);
fit1dbmfuncCall = @(c,x) fit1dbm(c,x);
fit1dgaussfuncCall = @(c,x) fit1dgauss(c,x);


%tic

%[ccy,~,resy,~,~,~,jacoby] = lsqcurvefit(fit1dbmfuncCall,c0y,y(:),imslcy,LB,UB,opts);
% Force y-fits to be TF
[ccy,~,resy,~,~,~,jacoby] = lsqcurvefit(fit1dtffuncCall,[c0y(1) c0y(2) c0y(3) 0],y(:),imslcy,LBtf,UBtf,opts);
[ccx,~,resx,~,~,~,jacobx] = lsqcurvefit(fit1dbmfuncCall,c0x,x,imslcx,LB,UB,opts);
%force gaussian fit x
%[ccx,~,resx,~,~,~,jacobx] = lsqcurvefit(fit1dgaussfuncCall,[c0x(4)  c0x(3) c0x(3) 0],x,imslcx,LB,UB,opts);

%toc
% fit error
sex = nlstandarderror(jacobx,resx);
sey = nlstandarderror(jacoby,resy);

%disp(['ccx: ', num2str(ccx)]);
%disp(['ccy: ', num2str(ccy)]);


fitx = fit1dbm(ccx,x); %fity = fit1dbm(ccy,y);
guessx = fit1dbm(c0x,x);
%guessx = fit1dgauss([c0x(4) c0x(6) c0x(3) 0],x);
%fitx = fit1dgauss(ccx,x);
%guessy = fit1dbm(c0y,y);
%fitx = fit1dbmg(ccx,x); 
%fity = fit1dbmg(ccy,y);
%guessx = fit1dbmg(c0x,x);
fity = fit1dtf(ccy,y);
guessy = fit1dtf(c0y,y);

%Our fit results are in terms of pixels, which is sensible. Now, we
%would like to turn them into real quantities.

%Condensate fraction and real number of atoms
%constants
lambda = 852e-9; sigma = (3*lambda^2./(2*pi)); %pixsize = 8.2e-6;
%pixsize = 0.8e-6;
pixsize = 0.78e-6;

xplt = pixsize.*x.*1e6;
yplt = pixsize.*y.*1e6;

% size(ccx)


%disp(['Condensate Fraction x/y: ' , num2str(Fcx),' / ', num2str(Fcy)]);

%Plot Residuals?
%{
figure
subplot(2,1,1)
plot(1:size(resx'),resx','r*');
xlabel('x (pix)')
ylabel('Residual')
title('Residuals')
subplot(2,1,2)
plot(1:size(resy),resy,'b*');
xlabel('y (pix)')
ylabel('Residual')
%}

if fignum > 0
    figure(fignum);
end

if ~(fignum == 0)

    hold on;
    plot(xplt,guessx,'k--'); hold on;
    plot(xplt,fit1dtf([ccx(1) ccx(2) ccx(3) 0],x),'b--');
    
    plot(xplt, ccx(6)+fit1dth([ccx(4) ccx(3) ccx(5)],x),'r--');
      
    plot(xplt,fitx,'k-','LineWidth',2);
    
    plot(xplt,imslcx,'ko');
    xlabel('x (\mu m)')
    ylabel('Summed n\sigma')
    text(0.55,0.95,['R_{TF,x} = ' num2str(ccx(2).*pixsize*1e6) '(' num2str(sex(2).*pixsize*1e6) ') \mum'],'Units','Normalized');
    ax1=gca;
    
    
    
    if fignum > 0
        axes('Position',[.15 .7 .25 .25])
        box on;
        imagesc(img); axis image;
        set(gca,'XTickLabel',[]);
        set(gca,'YTickLabel',[]);
    end
    hold off;
    %{
    figure
    plot(yplt,fit1dtf([ccy(1) ccy(2) ccy(3) 0],y),'b--');
    hold on;
    plot(yplt,guessy,'k--'); hold on;

    %plot(yplt, fit1dth([ccy(4) ccy(3) ccy(5)],y),'r--');
    hold on;   
    plot(yplt,fity,'k-','LineWidth',2);
    hold on;
    plot(yplt,imslcy,'ko');
    xlabel('y (\mu m)')
    ylabel('OD')
    %title('Bose-Einstein Condensation')
    axes('Position',[.7 .7 .18 .18])
    box on
    imagesc(img); axis image;
    set(gca,'XTickLabel',[]);
    set(gca,'YTickLabel',[]);
    %}
end
%Define outputs!
%function [imslcx,fitx,xplt,yplt,img,ccx,ccy,Fcx,Fcy]=CsTOF(img,tof)

%t-fact from Jacob's thermometry code
%[~,tfact] = full_thermometry(ccx(5).*pixsize,tof,[]);
outStruct.tx = (pixsize.*ccx(5)).^2.*(133.*amu).*(2.*pi.*6.65).^2./k_B;
%outStruct.tx = (pixsize.*ccx(3)).^2.*(133.*amu).*(2.*pi.*6.65).^2./k_B

%return
%Ntotx = (pixsize).^2.*trapz(fitx - ccx(6))./sigma;
Ntotx = (pixsize).^2.*trapz(fitx)./sigma;

%Ntoty = (pixsize).^2.*trapz(fity - ccy(6))./sigma;
Ntoty = (pixsize).^2.*trapz(fity - ccy(4))./sigma;

%Ncx = (pixsize).^2.*trapz(fit1dtf([ccx(1) ccx(2) ccx(3) ccx(6)],x) - ccx(6))./sigma;
Ncx = (pixsize).^2.*trapz(fit1dtf([ccx(1) ccx(2) ccx(3) 0],x))./sigma;

%Ncy = (pixsize).^2.*trapz(fit1dtf([ccy(1) ccy(2) ccy(3)],y) - ccy(6))./sigma;
Ncy = (pixsize).^2.*trapz(fit1dtf([ccy(1) ccy(2) ccy(3) ccy(4)],y) - ccy(4))./sigma;

Fcx = Ncx/Ntotx;
Fcy = Ncy/Ntoty;
N0x = Fcx.*Ntotx;
N0y = Fcy.*Ntoty;

outStruct.N = trapz(trapz(img)).*pixsize.^2./sigma;
outStruct.imslcx = imslcx;outStruct.imslcy = imslcy;
outStruct.fitx = fitx; outStruct.fity = fity;
outStruct.xplt = xplt; outStruct.yplt = yplt;
outStruct.img = img; 
outStruct.ccx = ccx; outStruct.ccy = ccy;
outStruct.Fcy = Fcy; outStruct.Fcx = Fcx;
outStruct.ty = 0; outStruct.sty = 0;
outStruct.stx = (pixsize.*sex(5)).*2.*(pixsize.*ccx(5)).*(133.*amu).*(2.*pi.*6.65).^2./k_B;
%outStruct.tx = full_thermometry(ccx(5).*pixsize,tof,[],1);
%outStruct.ty = full_thermometry(ccy(5).*pixsize,tof);
%outStruct.ty = tfact.*(ccy(5).*pixsize).^2;
%outStruct.sty = tfact.*2.*(ccy(5).*pixsize).*sey(5).*pixsize;
outStruct.nx = Ntotx; outStruct.ny = Ntoty;
outStruct.n0x = N0x; outStruct.n0y = N0y;
outStruct.sex = sex; outStruct.sey = sey;
outStruct.Ntotx = Ntotx; outStruct.Ntoty = Ntoty;
%outStruct.n0xc = (3.*pi./8).*(ccx(1).*ccx(2).*pixsize.^2)./sigma;
%outStruct.sn0xc = ((3.*pi./8).*(pixsize.^2)./sigma).*sqrt((ccx(1).*sex(2)).^2 + (ccx(2).*sex(1)).^2);

outStruct.n0xc = (16/15).*(ccx(1).*ccx(2).*pixsize.^2)./sigma;
outStruct.sn0xc = ((16/15).*(pixsize.^2)./sigma).*sqrt((ccx(1).*sex(2)).^2 + (ccx(2).*sex(1)).^2);

outStruct.sFcx = outStruct.sn0xc./outStruct.Ntotx;

outStruct.cwx = ccx(2).*pixsize; outStruct.cwy = ccy(2).*pixsize;
outStruct.scwx = sex(2).*pixsize; outStruct.scwy = sey(2).*pixsize;

if ~(fignum == 0)
    %adding text to plot
    text(ax1,0.55,0.9,['n0x = ' num2str(outStruct.n0xc) '(' num2str(outStruct.sn0xc) ')'],'Units','Normalized');
    text(ax1,0.55,0.85,['Tx = ' num2str(outStruct.tx*1e9) '(' num2str(outStruct.stx*1e9) ') nK'],'Units','Normalized');
end
end

function g = fit1dth(c,x)
g = c(1).*exp(-((x-c(2)).^2)./(2*c(3).^2));
end

function f = fit1dtf(c,x)
%Calculate inverted parabola
arg = 1-((x-c(3))/c(2)).^2;
ind = find(arg<0);
arg(ind) = 0;
f = c(1).*(arg).^(2)+c(4);
%Set negative entires to zero for TF distribution, using indices to do fast
end

function f = fit1dbm(c,x)
arg = 1-((x-c(3))/c(2)).^2;
arg(arg<0)=0;
h = c(1).*(arg).^(2);
%Set negative entires to zero for TF distribution, using indices to do so fast
g = c(4).*exp(-((x-c(3)).^2)/(2*c(5).^2));
f = h+g+c(6);
end
    
function f = fit1dbmg(c,x)
%arg = 1-((x-c(3))/c(2)).^2;
%arg(arg<0)=0;
h = c(1).*exp(-((x-c(3)).^2)./(2*c(2).^2));
%h = c(1).*(arg).^(2);
%Set negative entiraes to zero for TF distribution, using indices to do so fast
g = c(4).*exp(-((x-c(3)).^2)/(2*c(5).^2));
f = h+g+c(6);
end

function f = fit1dpl(c,x)
argpl = exp(-(x - c(2)).^2./(2*(c(3).^2)));
f = c(1).*PolyLog(2,argpl)./PolyLog(2,1);
end
function g = fit1dgauss(c,x)

g = c(1).*exp(-((x-c(2)).^2)./(2*c(3).^2))+c(4);
end


    