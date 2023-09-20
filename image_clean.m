function images = imageset_clean(shots, dfshots, bgshots, params)

% load the image set (can be an N-D array or a struct with array plus
% date)
images = image_load(shots, params);

% load the background set (can be a 1D array of shots, a struct with array plus
% date, or a 2D array of exactly what you want subtracted off.)
if isstruct(bgshots)
    bgimgs = image_load(bgshots, params);
    bg = squeeze(mean(bgims, 1));
elseif min(size(bgshots)) == 1
    bgbgims = image_load(bgshots, params);
    bg = squeeze(mean(bgims, 1));
else
    bg = bgshots;
end

% load the df set (can be 1D array, a struct with array plus
% date, or false, in which case the image set will be used as the df set.)
if isstruct(dfshots)
    dfimgs = image_load(dfshots, params);
elseif max(size(dfshots)) > 1
    dfimgs = image_load(dfshots, params);
elseif ~dfshots
    dfimgs = images;
end



% average the background set and subtract from the df set and the image set


% use the df set to create a dfobject


% apply the dfobject to the image set to get defringed absorption images


% calculate atom density from absorption profile


