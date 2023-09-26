paramsVC = struct();
paramsVC.date = [2023 09 19];
paramsVC.view = [1, 100, 1, 1000];
paramsVC.cam = 'V';
paramsVC.atom = 'C';
shotsV = 347:376;
im = load_img(shotsV, paramsVC);

figure();
imagesc(squeeze(im(1, :, :, 1)));
axis image;

paramsVL = paramsVC;
paramsVL.atom = 'L';
im = load_img(shotsV, paramsVL);

figure();
imagesc(squeeze(im(1, :, :, 1)));
axis image;

