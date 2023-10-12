function fig = imgstack_viewer(ims, figname)

figure;
hold on;
if nargin > 1
    sgtitle(figname);
end

if ndims(ims) == 2
    imagesc(ims);
    axis image;
    colorbar();
elseif ndims(ims) == 3
    imagesc(imtile(ims, 'BorderSize', 5));
    axis image;
    colorbar();
elseif ndims(ims) == 4
    for i = 1:size(ims, 4)
        subplot(1, size(ims, 4), i);
        imagesc(imtile(ims(:, :, :, i), 'BorderSize', 5));
        axis image;
        colorbar();
    end
end
