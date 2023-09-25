function images = imag_clean(shots, dfshots, bgshots, params)

% load the image set (can be an N-D array or a struct with array plus
% date)
images = image_load(shots, params);

% load the background set (can be a 1D array of shots, a struct with array plus
% date, a 2D array of exactly what you want subtracted off, or false)
% In the first two cases, we average together the background images first.
% If false, 
if isstruct(bgshots)
    bgimages = image_load(bgshots, params);
    bg = squeeze(mean(bgimages, 1));
elseif min(size(bgshots)) == 1
    bgimages = image_load(bgshots, params);
    bg = squeeze(mean(bgimages, 1));
elseif max(size(bgshots)) > 1
    bg = bgshots;
elseif ~bgshots
    bg = 
end

% load the df set (can be 1D array, a struct with array plus
% date, or false, in which case the image set will be used as the df set.)
if isstruct(dfshots)
    dfimages = image_load(dfshots, params);
elseif max(size(dfshots)) > 1
    dfimages = image_load(dfshots, params);
elseif ~dfshots
    dfimages = images;
end


% subtract background from the df set and the image set
dfimages = dfimages - bg;
images = images - bg;

% use the df set to create a dfobject
dfset = df_vecs()

% apply the dfobject to the image set to get defringed absorption images


% calculate atom density from absorption profile


