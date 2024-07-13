function fig = imgstack_viewer(ims, figname, inax)


    
if nargin < 3
    fig = figure;
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
    A = size(ims, 1);
    stk = cell(A, 1);
    for a = 1:size(ims, 1)
        stk{a} = squeeze(ims(a, :, :));
    end
    imagesc(imtile(stk, 'BorderSize', 5));
    axis image;
    colorbar();
elseif ndims(ims) == 4
    [X, Y, A, B] = size(ims, [3, 4]);
    rims = reshape(ims, [X, Y, A*B]);
    stk = cell(A*B, 1);
    for a = 1:(A*B)
        stk{a} = squeeze(rims(a, :, :));
    end
    imagesc(imtile(stk, 'BorderSize', 5));
    axis image;
    colorbar();
end
