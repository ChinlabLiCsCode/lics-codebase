function outimgs = dfobj_apply(imgs, dfobj)

sz = size(imgs);
outimgs = NaN(sz);
for i = 1:sz(1)
    t = imgs(i, :);
    t = (dfobj.fulleigvecs')*(dfobj.fulleigvecs*(dfobj.maskmat*t'));
    outimgs(i, :, :) = real(reshape(t, sz([2 3])));
end
