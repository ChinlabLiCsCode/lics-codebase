paramsVC = struct();
paramsVC.date = [2023 09 19];
paramsVC.view = [1, 100, 1, 1000];
paramsVC.cam = 'V';
paramsVC.atom = 'C';
shotsV = 347:376;
im = img_load(shotsV, paramsVC);

figure();
imagesc(squeeze(im(1, :, :, 1)));
axis image;

paramsVL = paramsVC;
paramsVL.atom = 'L';
im = img_load(shotsV, paramsVL);

figure();
imagesc(squeeze(im(1, :, :, 1)));
axis image;

