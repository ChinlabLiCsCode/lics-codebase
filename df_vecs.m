function [df_vecs, df_mask] = df_vecs(images, params)
% 
% Inputs: images is an n by m by 2
% 

images = squeeze(images(:,:,:,shot_number(1))-images(:,:,:,shot_number(2)));
images = real(log(images));
images(~isfinite(images)) = 0;
orig_size = size(images);
images(end+1,:,:) = ones(orig_size(2:3));
orig_size = size(images);

if pca_number > orig_size(1)
    pca_number = orig_size(1);
end

if size(mask,1) < 2
    mask_x = zeros(orig_size(2:3));
    mask_y = mask_x;
    mask_x(mask(3):mask(4),:) = 1;
    mask_y(:,mask(1):mask(2)) = 1;
    mask = mask_x.*mask_y;
    mask = ~mask;
end

full_size = orig_size(2)*orig_size(3);
images = reshape(images,[orig_size(1) full_size]);
big_sparse = spdiags(mask(:), 0, full_size, full_size);
cov_matrix = (images)*big_sparse*(images');
[V, D] = eig(cov_matrix);
[sortD, sort_order] = sort(diag(D),'descend');
sortV = V(:,sort_order(1:pca_number));
sortD = sortD(1:pca_number);
sortV = sortV*diag(1./sqrt(sortD));

out_struct.out_vecs = (sortV')*images;
out_struct.sp_mask = big_sparse;