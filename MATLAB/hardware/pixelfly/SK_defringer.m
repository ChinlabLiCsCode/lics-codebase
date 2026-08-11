function [ODimage_defringed, defbgImg] = SK_defringer(Image_to_defring,bgimgstack,rect2)

mask = ones(size(bgimgstack(:,:,1))); 
mask(rect2(2):rect2(2)+rect2(4)-1,rect2(1):rect2(1)+rect2(3)-1) = 0;
%[~,~,~,defbgImg] = genbase2(real(log(bgimgstack)),real(log(Image_to_defring)),mask);
[~,~,~,defbgImg] = genbase2(bgimgstack,Image_to_defring,mask);

%figure
%subplot(2,2,1);imagesc(real(log(Image_to_defring)))
%subplot(2,2,2);imagesc()

ODimage_defringed = real(log(defbgImg./Image_to_defring));
%ODimage_defringed(~isfinite(ODimage_defringed)) = 0;
