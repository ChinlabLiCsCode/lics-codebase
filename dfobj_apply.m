function outimgs = dfobj_apply(imgs, dfobj)

% copied from cvpdefringe

outimgs = (dfobj.fulleigvecs') * (dfobj.fulleigvecs * (dfobj.maskmat * imgs(:)));
outimgs = real(reshape(out_image,size(imgs)));