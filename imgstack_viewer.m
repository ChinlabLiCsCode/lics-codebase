function fig = imgstack_viewer(ims, figname, inax)

if nargin < 3
    figure;
else
    axes(inax);
end

hold on;
title(figname);

if ndims(ims) == 2
    imagesc(ims);
    axis image;
    colorbar();
elseif ndims(ims) == 3
    imagesc(imtile(ims, 'BorderSize', 5));
    axis image;
    colorbar();
elseif ndims(ims) == 4
    sz = size(ims);
    rims = reshape(ims, [sz(1), sz(2), sz(3) * sz(4)]);
    imagesc(imtile(rims, 'BorderSize', 5));
    axis image;
    colorbar();
end
