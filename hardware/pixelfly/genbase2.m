function [newbase_hole,newbase,coef,newbgimg]=genbase2(bgimg,rawimage,mask)

num_img=size(bgimg,3);
newbase_hole=bgimg;
newbase=bgimg;
newbgimg=zeros(size(bgimg));
coef=zeros(1,num_img);
for i = 1 : num_img
    if i == 1
        newbase_hole(:,:,1)=(bgimg(:,:,1).*mask)/sqrt(sum(sum(bgimg(:,:,1).^2.*mask)));
        newbase(:,:,1)=(bgimg(:,:,1))/sqrt(sum(sum(bgimg(:,:,1).^2)));
        coef(1)=sum(sum(rawimage.*newbase_hole(:,:,1)))/sum(sum(newbase_hole(:,:,1).^2));
        newbgimg(:,:,1)=coef(1)*newbase(:,:,1);
    else
        for j = 1 : i-1
            newbase_hole(:,:,i)=newbase_hole(:,:,i).*mask-sum(sum(bgimg(:,:,i).*newbase_hole(:,:,j)))*newbase_hole(:,:,j);
            newbase(:,:,i)=newbase(:,:,i)-sum(sum(bgimg(:,:,i).*newbase(:,:,j)))*newbase(:,:,j);
        end
        newbase_hole(:,:,i)=newbase_hole(:,:,i)/sqrt(sum(sum(newbase_hole(:,:,i).^2)));
        newbase(:,:,i)=newbase(:,:,i)/sqrt(sum(sum(newbase(:,:,i).^2)));
        coef(i)=sum(sum(rawimage.*newbase_hole(:,:,i)))/sum(sum(newbase_hole(:,:,i).^2));
        newbgimg(:,:,i)=coef(i)*newbase(:,:,i);
    end
    
end
newbgimg=sum(newbgimg,3);