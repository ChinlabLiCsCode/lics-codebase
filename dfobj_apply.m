function outimgs = dfobj_apply(imgs, dfobj)

sz = size(imgs);
npix = sz(1) * sz(2);
if length(sz) < 3
    sz(3) = 1;
end

flt = reshape(imgs, [npix, sz(3)]);
outflt = dfobj.dfmat * flt;
outimgs = reshape(outflt, sz);

