function dfobj = dfobj_create(dfimgs, mask, pcanum)


sz = size(dfimgs);
pcanum = min([pcanum, sz(1)]);
mask_x = zeros(sz(2:3));
mask_y = mask_x;
mask_x(mask(3):mask(4),:) = 1;
mask_y(:,mask(1):mask(2)) = 1;
mask = mask_x.*mask_y;
mask = ~mask;

npix = sz(2)*sz(3); % number of pixels per image
mask = reshape(mask, [npix, 1]); % reshape mask to be column vec
maskmat = spdiags(mask, 0, npix, npix);
fullvecs = reshape(dfimgs, [sz(1) npix]); % reshape image to be column vecs (R_i in the paper)
edgevecs = fullvecs(:, mask); % reshape edge pixels to be column vecs (u_i in the paper)
covmat = edgevecs * edgevecs'; % make covariance matrix (S in the paper)
[V,D] = eig(covmat); % find eigensystem
[eigvals, order] = sort(diag(D),'descend'); % sort eigenvals
eigvecs = V(:, order(1:pcanum)); % get first pcanum of eigvecs (v_i in the paper)
eigvals = eigvals(1:pcanum); % get first pcanum of eigvals
eigvecs = eigvecs * diag(1./sqrt(eigvals)); % maybe this is some kind of normalization? 
fulleigvecs = (eigvecs') * fullvecs; % probably like P_j in the paper? 

dfobj = struct('maskmat', maskmat, 'fulleigvecs', fulleigvecs);
