function dfobj = dfobj_create(dfimgs, mask, pcanum)

if ndims(dfimgs) > 3
    error('Too many dims');
end

if nargin < 4
    debug = false;
end

sz = size(dfimgs);
pcanum = min([pcanum, sz(3)]);
mask_x = zeros(sz(1:2));
mask_y = mask_x;
mask_x(mask(3):mask(4),:) = 1;
mask_y(:,mask(1):mask(2)) = 1;
mask = mask_x.*mask_y;
mask = ~mask;

% full_size = orig_size(2)*orig_size(3);
% imagestack = reshape(imagestack,[orig_size(1) full_size]);
% big_sparse = spdiags(mask(:), 0, full_size, full_size);
% cov_matrix = (imagestack)*big_sparse*(imagestack');

npix = sz(1)*sz(2); % number of pixels per image
mask = reshape(mask, [npix, 1]); % reshape mask to be column vec
maskmat = spdiags(mask, 0, npix, npix);
fullvecs = reshape(dfimgs, [npix sz(3)]); % reshape image to be column vecs (R_i in the paper)
covmat = fullvecs' * maskmat * fullvecs;
[V,D] = eig(covmat); % find eigensystem
[eigvals, order] = sort(diag(D), 'descend'); % sort eigenvals
eigvecs = V(:, order(1:pcanum)); % get first pcanum of eigvecs (v_i in the paper)
eigvals = eigvals(1:pcanum); % get first pcanum of eigvals
eigvecs = eigvecs * diag(1./sqrt(eigvals)); % maybe this is some kind of normalization? 
dfvecs = (eigvecs') * (fullvecs'); % probably like P_j in the paper? 
% dfvecs has dims [pcanum, npix]

% dfvecs = diag(1./diag(dfvecs * (dfvecs'))) * dfvecs;

eigvecims = reshape(dfvecs', [sz(1), sz(2), pcanum]);

dfobj = struct('dfmat', dfvecs' * dfvecs * maskmat, ...
    'maskmat', maskmat, 'dfvecs', dfvecs, 'eigvecims', eigvecims);
