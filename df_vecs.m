function [df_vecs, df_mask] = df_vecs(imagestack, params)
% 
% Loads and returns an image or set of images
% 'shots' can be an integer or an n-d array of integers.
% 'in_params' must have a date (3 element array), view (4 element array),
% cam (either 'H' or 'V), and atom (either 'C' or 'L').
% Returned imagestack has dimensions [numel(shots), view(3)-view(4),
% view(1)-view(2), x]. If the cam is 'H', we return the atoms, no atoms, 
% and background frames (so x=3). If the cam is 'V',
% then depending on the value of atom we either return the frames 1 and 3
% (for Li) or 2 and 4 (for Cs), so x=2. If you want to reshape the
% imagestack to match the shots shape, then do it yourself.
% 

imagestack = squeeze(imagestack(:,:,:,shot_number(1))-imagestack(:,:,:,shot_number(2)));
imagestack = real(log(imagestack));
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