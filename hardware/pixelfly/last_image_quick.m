make_constants;
if ~exist('my_clock')
    my_clock = clock();
end
while true
    if ~exist('image_type')
        image_type = 1;
    end
    if ~exist('img_num')
        img_num = 0;
    end
    [img_num out_stats] = last_image(img_num, my_clock, image_type);
    if image_type == 1 || image_type == 2
        %pixel_size = 8.2E-6;
        pixel_size = 7.64e-6;
    else
        pixel_size = 2.47E-6;
    end
    if image_type == 1 || image_type == 3
        mass = 133;
    else
        mass = 6;
    end
    if ~isempty(out_stats)
        wx = pixel_size*out_stats(2);
        wy = pixel_size*out_stats(6);
        Tx = NaN;
        Ty = NaN;
        if ~exist('w0x')
            my_w0x = 0;
        else
            my_w0x = w0x;
        end
        if ~exist('w0y')
            my_w0y = 0;
        else
            my_w0y = w0y;
        end
        if exist('tof')
            Tx = mass*amu/k_B*(wx^2-my_w0x^2)/tof^2;
            Ty = mass*amu/k_B*(wy^2-my_w0y^2)/tof^2;
        end
        clear my_w0x;
        clear my_w0y;
        if exist('optim_power')
            fprintf('%d:\tnx/ny:%.02e/%.02e\twx/wy:%.02e/%.02e\tOx/Oy:%.02e/%.02e\n',img_num-1,out_stats(end-1),out_stats(end),wx,wy,out_stats(end-1)/Tx^optim_power,out_stats(end)/Ty^optim_power);
        else
            fprintf('%d:\tnx/ny:%.02e/%.02e\twx/wy:%.02e/%.02e\tTx/Ty:%.02e/%.02e\n',img_num-1,out_stats(end-1),out_stats(end),wx,wy,Tx,Ty);
        end
        running_stats(img_num,:) = out_stats;
    end
    pause(1);
end