function fig = imgstack_viewer(imgstack)

sz = size(imgstack);
d = numel(sz);

figure();
if d == 2
    imagesc(imgstack);
elseif d == 3
    figure();
    imagesc(reshape(imgstack, [sz(1)*sz(2), sz(3)]));
else 
    error('too many dims!')
end

axis image;
colorbar();