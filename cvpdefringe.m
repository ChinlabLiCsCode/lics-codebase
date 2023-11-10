function out_image = cvpdefringe(in_image,defringeset)

out_image = (defringeset.out_vecs')*(defringeset.out_vecs*(defringeset.sp_mask*in_image(:)));
out_image = real(reshape(out_image,size(in_image)));
%figure
%imagesc(squeeze(out_image));
