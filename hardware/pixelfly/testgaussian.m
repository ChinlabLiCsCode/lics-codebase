%A small routine to create a 2D gaussian for test the fitting routine inthe
%camera program
sizex=1392;
sizey=1024;
[X Y]=meshgrid(1:sizex,1:sizey);

fakedata=zeros(sizey,sizex,3);
xc=500;
yc=300;
wx=50;
wy=40;
n=300;
X1=X-xc;
Y1=Y-yc;

for i = 1 :3
bg=rand(sizey,sizex)*200+500;
gdata=n*exp(-(X1.^2/2/wx^2)-(Y1.^2/2/wy^2))+bg;
fakedata(:,:,i)=gdata;
end
    