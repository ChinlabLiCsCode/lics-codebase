function out_image = defringe(in_image,defringeset)
% function out_image = cvpdefringe(in_image,defringeset)
%
% This function removes the fringes from the image in_image using the
% defringeset structure.  The defringeset structure is created by the
% function cvpcreatedefringeset. The function returns the defringed image out_image.
%
% Originally written by Colin Parker
% Modified very slightly by Henry in November 2023
% Sorry that this code isn't commented properly...Colin didn't leave a lot 
% of comments in his code

out_image = (defringeset.out_vecs')*(defringeset.out_vecs*(defringeset.sp_mask*in_image(:)));
out_image = real(reshape(out_image,size(in_image)));

