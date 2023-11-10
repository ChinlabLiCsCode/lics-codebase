function out_struct = cvpcreatedefringeset(imagestack, mask, pca_number)

% originally written by Colin Parker
% modified by Henry in November 2023


imagestack = real(imagestack);
imagestack(~isfinite(imagestack)) = 0;
orig_size = size(imagestack);
imagestack(end+1,:,:) = ones(orig_size(2:3));
orig_size = size(imagestack);

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
imagestack = reshape(imagestack,[orig_size(1) full_size]);
big_sparse = spdiags(mask(:), 0, full_size, full_size);
cov_matrix = (imagestack)*big_sparse*(imagestack');
[V, D] = eig(cov_matrix);
[sortD, sort_order] = sort(diag(D),'descend');
sortV = V(:,sort_order(1:pca_number));
sortD = sortD(1:pca_number);
sortV = sortV*diag(1./sqrt(sortD));

out_struct.out_vecs = (sortV')*imagestack;
out_struct.sp_mask = big_sparse;

