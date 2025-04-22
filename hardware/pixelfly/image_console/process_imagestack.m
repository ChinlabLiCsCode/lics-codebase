function [fit_params od_image] = process_imagestack(imagestack, lambda, pixel_sz)

pixel = 8.4E-6;
lambda = 671E-9;

if size(imagestack,4) == 0
    img_shadow = zeros(size(imagestack,1),size(imagestack,2),size(imagestack,3));
    img_light = zeros(size(img_shadow));
elseif size(imagestack,4) == 1
    img_shadow = double(imagestack(:,:,:,1));
    img_light = zeros(size(img_shadow));
elseif size(imagestack,4) == 2
    img_shadow = double(imagestack(:,:,:,1));
    img_light = double(imagestack(:,:,:,2));
else
    if size(imagestack,4) == 3
        img_shadow = double(imagestack(:,:,:,1));
        img_light = double(imagestack(:,:,:,2));
        img_bg_shadow = mean(double(imagestack(:,:,:,3)),1);
        img_bg_light = img_bg_shadow;
    else
        img_shadow = double(imagestack(:,:,:,1));
        img_light = double(imagestack(:,:,:,2));
        img_bg_shadow = mean(double(imagestack(:,:,:,3)),1);
        img_bg_light = mean(double(imagestack(:,:,:,4)),1);
    end
    for a = 1:size(img_shadow,1)
        img_shadow(a,:,:) = img_shadow(a,:,:) - img_bg_shadow;
        img_light(a,:,:) = img_light(a,:,:) - img_bg_light;
    end
end

img_shadow = real(log(img_shadow));
img_shadow(~isfinite(img_shadow)) = 0;
img_light = real(log(img_light));
img_light(~isfinite(img_light)) = 0;
img_shadow_avg = squeeze(mean(img_shadow,1));
img_light_avg = squeeze(mean(img_light,1));

%Gaussian smoothing
%h=fspecial('gaussian',35,12);
%img_light=imfilter(img_light,h);
%img_shadow=imfilter(img_shadow,h);

od_image=img_light_avg-img_shadow_avg;

num_shots = size(img_light,1);
short_dims = size(img_light_avg);
if num_shots > 5
    long_dim = numel(img_light_avg);
    
    
    for a = 1:num_shots
        img_light(a,:,:) = squeeze(img_light(a,:,:)) - img_light_avg;
    end
    img_light = reshape(img_light,[num_shots long_dim]);
    
    cov = img_light*img_light';
    [best_eigs, ~] = eigs(cov,[],4);
    
    e_big1 = reshape((best_eigs(:,1)')*img_light,short_dims);
    e_big2 = reshape((best_eigs(:,2)')*img_light,short_dims);
    e_big3 = reshape((best_eigs(:,3)')*img_light,short_dims);
    e_big4 = reshape((best_eigs(:,4)')*img_light,short_dims);
    
    % find lightest pixel (95th percentile)
    bright = prctile(img_light_avg(:),95);
    good_pixels = img_light_avg > bright/10;
    
    od_image = od_image - e_big1*sum(od_image(good_pixels).*e_big1(good_pixels))/sum(e_big1(good_pixels).^2);
    od_image = od_image - e_big2*sum(od_image(good_pixels).*e_big2(good_pixels))/sum(e_big2(good_pixels).^2);
    od_image = od_image - e_big3*sum(od_image(good_pixels).*e_big3(good_pixels))/sum(e_big3(good_pixels).^2);
    od_image = od_image - e_big4*sum(od_image(good_pixels).*e_big4(good_pixels))/sum(e_big4(good_pixels).^2);
end

od_image(~isfinite(od_image)) = 0;

yc = (short_dims(1)+1)/2;
dy = short_dims(1);
xc = (short_dims(2)+1)/2;
dx = short_dims(2);

fit_params.init_guesses = autoguess(od_image,[],1,xc,yc,dx,dy);
[fit_params.fittracex fit_params.fittracey fit_params.tracex fit_params.tracey fit_params.fitparx fit_params.fitpary]...
                =fitgaussian1D(od_image,[],fit_params.init_guesses,1,xc,yc,dx,dy);

fit_params.xdist = pixel*(1:length(fit_params.fittracex));
fit_params.ydist = pixel*(1:length(fit_params.fittracey));

fit_params.sensible_output(1) = num_shots;
fit_params.sensible_output(2) = pixel^2/(3*lambda^2/(2*pi))*sqrt(2*pi)*fit_params.fitparx(1).fitval*fit_params.fitparx(2).fitval;
fit_params.sensible_output(3) = pixel^2/(3*lambda^2/(2*pi))*sqrt(2*pi)*fit_params.fitpary(1).fitval*fit_params.fitpary(2).fitval;
fit_params.sensible_output(4) = pixel*fit_params.fitparx(2).fitval;
fit_params.sensible_output(5) = pixel*fit_params.fitpary(2).fitval;