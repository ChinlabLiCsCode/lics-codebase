function out_info = macro_scan(params, shots, in_x, dfshots)


%Keep track of images to plot later
% allimgs = [];

% out_info.x = in_x;
% out_info.n = zeros(1,size(in_x,2));
% out_info.nx = zeros(1,size(in_x,2));
% out_info.ny = zeros(1,size(in_x,2));
% out_info.tx = zeros(1,size(in_x,2));
% out_info.ty = zeros(1,size(in_x,2));
% out_info.px = zeros(1,size(in_x,2));
% out_info.py = zeros(1,size(in_x,2));
% out_info.wx = zeros(1,size(in_x,2));
% out_info.wy = zeros(1,size(in_x,2));

%Do you have any extra outputs compared to single Gauss fit?
% if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
%     out_info.sep = zeros(1,size(in_x,2));
% end
% if isfield(params,'bimodal') && strcmp(params.fit_fun,'bimodal')
%     out_info.cf = zeros(1,size(in_x,2));
% end

% if nargin<4 || isempty(fig_num)
%     fig_num = figure;
% end

% if ~isfield(params,'num_avg') || (isfield(params,'avg_type') && strcmp(params.avg_type,'all'))
%     num_avg = 1;
% else
%     num_avg = params.num_avg;
% end
% total_fits = ceil(size(shots,1)/num_avg);
% info_sz = size(shots);
% info_sz(1) = total_fits;

% out_info.ns = zeros(info_sz);
% out_info.nxs = zeros(info_sz);
% out_info.nys = zeros(info_sz);
% out_info.txs = zeros(info_sz);
% out_info.tys = zeros(info_sz);
% out_info.pxs = zeros(info_sz);
% out_info.pys = zeros(info_sz);
% out_info.wxs = zeros(info_sz);
% out_info.wys = zeros(info_sz);
% if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
%     out_info.seps = zeros(info_sz);
% end
% if isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
%     out_info.cfs = zeros(info_sz); 
% end
% 
% out_info.sn = NaN*zeros(1,size(in_x,2));
% out_info.snx = NaN*zeros(1,size(in_x,2));
% out_info.sny = NaN*zeros(1,size(in_x,2));
% out_info.stx = NaN*zeros(1,size(in_x,2));
% out_info.sty = NaN*zeros(1,size(in_x,2));
% out_info.spx = NaN*zeros(1,size(in_x,2));
% out_info.spy = NaN*zeros(1,size(in_x,2));
% out_info.swx = NaN*zeros(1,size(in_x,2));
% out_info.swy = NaN*zeros(1,size(in_x,2));

% Initialize outputs here

% if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
%     out_info.ssep = NaN*zeros(1,size(in_x,2));
% end
% if isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
%     out_info.scf =  NaN*zeros(1,size(in_x,2)); 
% end

% if ~isfield(params,'date')
%     params.date = 'today';
% end
% if isstr(params.date) %#ok<DISSTR,*REMFF1>
%     if strcmp(params.date,'today')
%         exp_date = clock();
%     else
%         error('invalid date');
%     end
% else
%     exp_date = params.date;
% end

% if ~isfield(params,'shot_set')
%     shot_set = 1;
% else
%     shot_set = params.shot_set;
% end

% in_tfact = params.tfact;
% in_lambda = params.wavelength;
% in_pixel = params.pixel;
% if isfield(params,'w0x')
%     w0x = params.w0x;
% else
%     w0x = 0;
% end
% if isfield(params,'w0y')
%     w0y = params.w0y;
% else
%     w0y = 0;
% end




% file_name = sprintf(file_template,exp_date(1),exp_date(2),exp_date(3),shots(1,1));
% vars = load(file_name,'imagestack');
% if isfield(params,'angle')
%     in_angle = params.angle;
%     imagestack_rot = imrotate(vars.imagestack,params.angle);
%     %if isfield(in_params,'view')
%     %    in_view = in_params.view;
% 
%         image_light_rot = imagestack_rot(:,:,3);
%         image_dark_rot = imagestack_rot(:,:,2);
%         odimage_rot = log(double(image_light_rot))-log(double(image_dark_rot));
%         odimage_rot(~isfinite(odimage_rot)) = 0;
%         figure(fig_num)
%         imagesc(odimage_rot)
%         %in_view = input('Please enter the view.\n');
% 
%         %in_params.view = in_view; %KP fix
%         in_view = params.view;
%         %if isfield(in_params,'maskg')
%         %    imagesc(odimage_rot(in_view(3):in_view(4),in_view(1):in_view(2)))
%         %    in_params.maskg = input('Please enter the mask.\n');
%         %end
% 
%     imagestack_sz = size(imagestack_rot(in_view(3):in_view(4),in_view(1):in_view(2),:));
% else
%     in_view = params.view;
%     imagestack_sz = size(vars.imagestack(in_view(3):in_view(4),in_view(1):in_view(2),:));
% end

% if nargin < 5 || isempty(dfshots)
% end

done = false;
acquiring = true;
num_complete = 0;
% if nargin < 5 || isempty(dfshots)
%     bgstack = zeros([numel(shots) imagestack_sz(1:2)]);
%     num_df = 0;
% else
dfshots = unique(dfshots);
num_df = numel(dfshots);
% bgstack = zeros([numel(shots)+num_df imagestack_sz(1:2)]);
% old_set_bad = true;
% if evalin('base','~isempty(who(''ZZZ_DF_SHOTS''))') && evalin('base','~isempty(who(''ZZZ_DATE''))') && isequal(evalin('base','ZZZ_DATE(1:3)'),exp_date(1:3))
%     if isequal(evalin('base','ZZZ_DF_SHOTS'),dfshots) && isequal(evalin('base','ZZZ_OLD_PARAMS.view'),params.view) && isequal(evalin('base','ZZZ_OLD_PARAMS.maskg'),params.maskg)
%         old_set_bad = false;
%     end
% end
% if old_set_bad
%     imagestack_single = zeros(imagestack_sz,'uint16');
%     for a = 1:num_df
%         file_name = sprintf(file_template,exp_date(1),exp_date(2),exp_date(3),dfshots(a));
%         vars = load(file_name,'imagestack');
%         if isfield(params,'angle')
%             imagestack_rot = imrotate(vars.imagestack,in_angle);
%             imagestack_single(:,:,:) = imagestack_rot(in_view(3):in_view(4),in_view(1):in_view(2),:);
%         else
%             imagestack_single(:,:,:) = vars.imagestack(in_view(3):in_view(4),in_view(1):in_view(2),:);
%         end
%         bgstack(a,:,:) = squeeze(imagestack_single(:,:,2*shot_set+1)-imagestack_single(:,:,1));
%     end
%     assignin('base','ZZZ_DF_SHOTS',dfshots);
%     assignin('base','ZZZ_DF_STACK',bgstack(1:num_df,:,:));
% else
%     bgstack(1:num_df,:,:) = evalin('base','ZZZ_DF_STACK');
%     disp('Note: reloading defringe set');
% end
% end
% old_params_bad = true;
% if evalin('base','~isempty(who(''ZZZ_OLD_PARAMS''))') && evalin('base','~isempty(who(''ZZZ_DATE''))') && isequal(evalin('base','ZZZ_DATE(1:3)'),exp_date(1:3))
%     if isequal(evalin('base','ZZZ_OLD_PARAMS.view'),params.view) && isequal(evalin('base','ZZZ_OLD_PARAMS.maskg'),params.maskg)
%         old_params_bad = false;
%     end
% end
% is_filled = zeros(1,numel(shots));
% fgstack = zeros([numel(shots) imagestack_sz(1:2)]);
% if ~old_params_bad
%     temp_filled = evalin('base','ZZZ_DONE_SHOTS');
%     is_filled(1:numel(temp_filled)) = temp_filled;
%     is_filled = is_filled(1:numel(shots));
%     old_fg_size = evalin('base','size(ZZZ_FG_STACK)');
%     old_bg_size = evalin('base','size(ZZZ_BG_STACK)');
%     bgstack((num_df+1):(num_df+old_bg_size(1)),:,:) = evalin('base','ZZZ_BG_STACK');
%     fgstack(1:old_fg_size(1),:,:) = evalin('base','ZZZ_FG_STACK');
%     fprintf('Note: loaded %d old shots\n',old_fg_size(1));
% end

while ~done
    worst = size(shots,1);
    for a = 1:size(shots,2)
        imagestack = zeros([size(shots,1) imagestack_sz],'uint16');
        no_load = true;
        bad_load = false;
        plotted = false;
        b = 0;
        while no_load && b <= num_complete
            try
                if acquiring
                    b_max = size(shots,1);
                else
                    b_max = num_complete;
                end
                for b = 1:b_max
                    shot_index = (b-1)*size(shots,2)+a;
                    if shot_index > numel(is_filled) || is_filled(shot_index) ~= shots(b,a) + 1
                        file_name = sprintf(file_template,exp_date(1),exp_date(2),exp_date(3),shots(b,a));
                        vars = load(file_name,'imagestack');
                        if isfield(params,'angle')
                            imagestack_rot = imrotate(vars.imagestack,in_angle);
                            imagestack(b,:,:,:) = imagestack_rot(in_view(3):in_view(4),in_view(1):in_view(2),:);
                        else
                            imagestack(b,:,:,:) = vars.imagestack(in_view(3):in_view(4),in_view(1):in_view(2),:);
                        end
                        bgstack(shot_index + num_df,:,:) = squeeze(imagestack(b,:,:,2*shot_set+1)-imagestack(b,:,:,1));
                        fgstack(shot_index,:,:) = squeeze(imagestack(b,:,:,2*shot_set)-imagestack(b,:,:,1));
                        is_filled(shot_index) = shots(b,a)+1;
                        assignin('base','ZZZ_DONE_SHOTS',is_filled(1:shot_index));
                        assignin('base','ZZZ_FG_STACK',fgstack(1:shot_index,:,:));
                        assignin('base','ZZZ_BG_STACK',bgstack((1+num_df):(shot_index+num_df),:,:));
                        assignin('base','ZZZ_DATE',exp_date);
                        assignin('base','ZZZ_OLD_PARAMS',params);
                    else
%                         fprintf('reloading from stack shot %d place %d\n',in_ranges(b,a),shot_index);
                        imagestack(b,:,:,2*shot_set) = fgstack((b-1)*size(shots,2)+a,:,:);
                        imagestack(b,:,:,2*shot_set+1) = bgstack((b-1)*size(shots,2)+a+num_df,:,:);
                        imagestack(b,:,:,1) = 0;
                    end
                end
                no_load = false;
            catch err %#ok<NASGU>
                no_load = true;
                if acquiring
                    bad_load = true;
                end
                b = b - 1;
            end
            if bad_load
                if ~plotted
                    plotted = true;
                    out_info.so_far = a - 1;
                    if exist('my_img','var')
                        out_info.img = my_img;
                    end
                    if exist('my_sum_img','var')
                        out_info.sum_img = my_sum_img;
                    end
                    if exist('fit_params','var')
                        out_info.tracex = fit_params.tracex;
                        out_info.tracey = fit_params.tracey;
                        out_info.fittracex = fit_params.fittracex;
                        out_info.fittracey = fit_params.fittracey;
                        if isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
                            out_info.xclfittracex = fit_params.xclfittracex;
                            out_info.xclfittracey = fit_params.xclfittracey;
                        end
                    end
                    params.plot_handles = plot_lifetime_process_multi(out_info,params,fig_num);
                else
                    pause(1);
                end
            end
        end
        if b < worst
            worst = b;
        end
        if ~acquiring
            if a == 1
                df_set = cvpcreatedefringeset(bgstack(1:(num_complete*size(shots,2)+num_df),:,:),[],params.maskg,Inf);
            end
            num_now = num_complete;
        else
            %df_set = cvpcreatedefringeset(bgstack(1:((num_complete)*size(in_ranges,2)+a+num_df),:,:),[],in_params.maskg,Inf);
            df_set = cvpcreatedefringeset(bgstack(1:((num_complete)*size(shots,2)+a+num_df),:,:),[],params.maskg,Inf);

            num_now = worst;
        end
        
        if ~isfield(params,'process_args')
            params.process_args = struct();
        end
        if isfield(params,'avg_type') && strcmp(params.avg_type,'all') && num_now > 2
            num_fits = num_now;
            %How many sensible outputs?
            if ~isfield(params,'fit_fun') || strcmp(params.fit_fun,'gauss')
                all_fits = zeros(num_now,10);
                tempfits = zeros(num_now+1,10);
            elseif strcmp(params.fit_fun,'dbl')
                all_fits = zeros(num_now,11);
                tempfits = zeros(num_now+1,11);
            elseif strcmp(params.fit_fun,'xcl')
                all_fits = zeros(num_now,16);
                tempfits = zeros(num_now+1,16);
            elseif strcmp(params.fit_fun,'bimodal')
                all_fits = zeros(num_now,11);
                tempfits = zeros(num_now+1,11);   
            elseif strcmp(params.fit_fun,'tf')
                all_fits = zeros(num_now,10);
                tempfits = zeros(num_now+1,10);     
            end
            for b = 1:num_now
                if ~isfield(params,'fit_fun')
                    fit_params = process_imagestack(imagestack([1:b-1 b+1:num_now],:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,[],shot_set);
                else
                    fit_params = process_imagestack(imagestack([1:b-1 b+1:num_now],:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,params.fit_fun,shot_set);
                end
                tempfits(b,:) = fit_params.sensible_output;
                if ~isfield(params,'fit_fun')
                    [~,my_img] = process_imagestack(imagestack(b,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,[],shot_set);
                else
                    [~,my_img] = process_imagestack(imagestack(b,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,params.fit_fun,shot_set);
                end
                
                allimgs = cat(3,allimgs,my_img);
                %size(allimgs)
                
            end
            if ~isfield(params,'fit_fun')
                [fit_params, my_sum_img] = process_imagestack(imagestack(1:num_now,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,[],shot_set);
            else
                [fit_params, my_sum_img] = process_imagestack(imagestack(1:num_now,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,params.fit_fun,shot_set);
            end
%             fit_params = process_imagestack(imagestack(1:num_now,:,:,:),in_lambda,in_pixel,df_set,in_params.maskg,in_params.process_args);
            tempfits(end,:) = fit_params.sensible_output;
            for b = 1:num_now
                all_fits(b,:) = num_now*tempfits(end,:)-(num_now-1)*tempfits(b,:);            
            end
        else
            %How many sensible outputs?
            num_fits = ceil(num_now/num_avg);
            if ~isfield(params,'fit_fun') || strcmp(params.fit_fun,'gauss')
                all_fits = zeros(num_fits,10);
            elseif strcmp(params.fit_fun,'dbl')
                all_fits = zeros(num_fits,11);
            elseif strcmp(params.fit_fun,'bimodal')
                all_fits = zeros(num_fits,11);    
            elseif strcmp(params.fit_fun,'tf')
                all_fits = zeros(num_fits,10);      
            else
                all_fits = zeros(num_fits,16);
            end
            for b = 1:num_fits
                ss = 1+num_avg*(b-1);
                fs = min(num_now,b*num_avg);
                if ~isfield(params,'fit_fun')
                    [fit_params,my_img] = process_imagestack(imagestack(ss:fs,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,[],shot_set);
                else
                    [fit_params,my_img] = process_imagestack(imagestack(ss:fs,:,:,:),in_lambda,in_pixel,df_set,params.maskg,params.process_args,params.fit_fun,shot_set);
                end
                all_fits(b,:) = fit_params.sensible_output;
            end
        end
        
        good_vals = true(size(all_fits,1),1);
        for b = 1:num_fits
%             width_t = all_fits(b,5);
%             if ((abs(all_fits(b,2) - all_fits(b,10)) > 3000 && abs(all_fits(b,2)/all_fits(b,10)) > 3) || (abs(all_fits(b,3) - all_fits(b,10)) > 3000 && abs(all_fits(b,3)/all_fits(b,10)) > 3)) || (all_fits(b,10) < 1e4)
%                 good_vals(b) = false;
%             end
        end
        all_fits_r = all_fits(good_vals,:);
        
        out_info.n(a) = mean(all_fits(:,10));
        out_info.nx(a) = mean(all_fits_r(:,2));
        out_info.ny(a) = mean(all_fits_r(:,3));
        out_info.tx(a) = in_tfact*((mean(all_fits_r(:,4)))^2-w0x^2);
        out_info.ty(a) = in_tfact*((mean(all_fits_r(:,5)))^2-w0y^2);
        out_info.px(a) = mean(all_fits_r(:,8));
        out_info.py(a) = mean(all_fits_r(:,9));
        out_info.wx(a) = mean(all_fits_r(:,4));
        out_info.wy(a) = mean(all_fits_r(:,5));
        %Do you have any additional outputs compared to normal Gauss fit?
        %Deal with them below.
        if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
            out_info.sep(a) = mean(all_fits_r(:,11));
        elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
            out_info.cf(a) = mean(all_fits_r(:,11));
        elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
            out_info.xclnx(a) = mean(all_fits_r(:,11));
            out_info.xclny(a) = mean(all_fits_r(:,12));
            out_info.xcltx(a) = in_tfact*(mean(all_fits_r(:,13))^2-w0x^2);
            out_info.xclty(a) = in_tfact*(mean(all_fits_r(:,14))^2-w0y^2);
            out_info.xclpx(a) = mean(all_fits_r(:,15));
            out_info.xclpy(a) = mean(all_fits_r(:,16));
        end
        
        out_info.ns(1:num_fits,a) = all_fits(:,10);
        out_info.nxs(1:num_fits,a) = all_fits(:,2);
        out_info.nys(1:num_fits,a) = all_fits(:,3);
        out_info.txs(1:num_fits,a) = in_tfact*((all_fits(:,4)).^2-w0x^2);
        out_info.tys(1:num_fits,a) = in_tfact*((all_fits(:,5)).^2-w0y^2);
        out_info.pxs(1:num_fits,a) = all_fits(:,8);
        out_info.pys(1:num_fits,a) = all_fits(:,9);        
        out_info.wxs(1:num_fits,a) = all_fits(:,4);
        out_info.wys(1:num_fits,a) = all_fits(:,5);
        
        
        if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
            out_info.seps(1:num_fits,a) = all_fits_r(:,11);
        elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
            out_info.cfs(1:num_fits,a) = all_fits_r(:,11);
        elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
            out_info.xclnxs(1:num_fits,a) = all_fits_r(:,11);
            out_info.xclnys(1:num_fits,a) = all_fits_r(:,12);
            out_info.xcltxs(1:num_fits,a) = in_tfact*(all_fits_r(:,13).^2-w0x^2);
            out_info.xcltys(1:num_fits,a) = in_tfact*(all_fits_r(:,14).^2-w0y^2);
            out_info.xclpxs(1:num_fits,a) = all_fits_r(:,15);
            out_info.xclpys(1:num_fits,a) = all_fits_r(:,16);
        end
        if size(all_fits_r,1)>1
            out_info.sn(a) = std(all_fits(:,10))/sqrt(size(all_fits,1)-1);
            out_info.snx(a) = std(all_fits_r(:,2))/sqrt(size(all_fits_r,1)-1);
            out_info.sny(a) = std(all_fits_r(:,3))/sqrt(size(all_fits_r,1)-1);
            out_info.stx(a) = in_tfact*2*mean(all_fits_r(:,4))*std(all_fits_r(:,4))/sqrt(size(all_fits_r,1)-1);
            out_info.sty(a) = in_tfact*2*mean(all_fits_r(:,5))*std(all_fits_r(:,5))/sqrt(size(all_fits_r,1)-1);
            out_info.spx(a) = std(all_fits_r(:,8))/sqrt(size(all_fits_r,1)-1);
            out_info.spy(a) = std(all_fits_r(:,9))/sqrt(size(all_fits_r,1)-1);
             out_info.swx(a) = std(all_fits_r(:,4))./sqrt(size(all_fits_r,1)-1);
            out_info.swy(a) = std(all_fits_r(:,5))./sqrt(size(all_fits_r,1)-1);
            
            if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
                out_info.ssep(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1)-1);
            elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
                out_info.scf(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1)-1);
            elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
                out_info.sxclnx(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1)-1);
                out_info.sxclny(a) = std(all_fits_r(:,12))/sqrt(size(all_fits_r,1)-1);
                out_info.sxcltx(a) = in_tfact*2*mean(all_fits_r(:,13))*std(all_fits_r(:,13))/sqrt(size(all_fits_r,1)-1);
                out_info.sxclty(a) = in_tfact*2*mean(all_fits_r(:,14))*std(all_fits_r(:,14))/sqrt(size(all_fits_r,1)-1);
                out_info.sxclpx(a) = std(all_fits_r(:,15))/sqrt(size(all_fits_r,1)-1);
                out_info.sxclpy(a) = std(all_fits_r(:,16))/sqrt(size(all_fits_r,1)-1);
            end
        else
            out_info.sn(a) = std(all_fits(:,10))/sqrt(size(all_fits,1));
            out_info.snx(a) = std(all_fits_r(:,2))/sqrt(size(all_fits_r,1));
            out_info.sny(a) = std(all_fits_r(:,3))/sqrt(size(all_fits_r,1));
            out_info.stx(a) = in_tfact*2*mean(all_fits_r(:,4))*std(all_fits_r(:,4))/sqrt(size(all_fits_r,1));
            out_info.sty(a) = in_tfact*2*mean(all_fits_r(:,5))*std(all_fits_r(:,5))/sqrt(size(all_fits_r,1));
            out_info.spx(a) = std(all_fits_r(:,8))/sqrt(size(all_fits_r,1));
            out_info.spy(a) = std(all_fits_r(:,9))/sqrt(size(all_fits_r,1));            
            out_info.swx(a) = std(all_fits_r(:,4))./sqrt(size(all_fits_r,1));
            out_info.swy(a) = std(all_fits_r(:,5))./sqrt(size(all_fits_r,1));
            
            if isfield(params,'fit_fun') && strcmp(params.fit_fun,'dbl')
                out_info.ssep(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1));
            elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'bimodal')
                out_info.scf(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1));
            elseif isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
                out_info.sxclnx(a) = std(all_fits_r(:,11))/sqrt(size(all_fits_r,1));
                out_info.sxclny(a) = std(all_fits_r(:,12))/sqrt(size(all_fits_r,1));
                out_info.sxcltx(a) = in_tfact*2*mean(all_fits_r(:,13))*std(all_fits_r(:,13))/sqrt(size(all_fits_r,1));
                out_info.sxclty(a) = in_tfact*2*mean(all_fits_r(:,14))*std(all_fits_r(:,14))/sqrt(size(all_fits_r,1));
                out_info.sxclpx(a) = std(all_fits_r(:,15))/sqrt(size(all_fits_r,1));
                out_info.sxclpy(a) = std(all_fits_r(:,16))/sqrt(size(all_fits_r,1));   
            end
        end
    end
    acquiring = ~acquiring;
    if ~acquiring
        num_complete = worst;
    elseif num_complete >= size(shots,1)
        done = true;
    end
end

if isfield(out_info,'so_far')
    out_info = rmfield(out_info,'so_far');
end
if exist('my_img','var')
    out_info.img = my_img;
end
if exist('fit_params','var')
    out_info.tracex = fit_params.tracex;
    out_info.tracey = fit_params.tracey;
    out_info.fittracex = fit_params.fittracex;
    out_info.fittracey = fit_params.fittracey;
    if isfield(params,'fit_fun') && strcmp(params.fit_fun,'xcl')
        out_info.xclfittracex = fit_params.xclfittracex;
        out_info.xclfittracey = fit_params.xclfittracey;
    end
end
%{
figure
for a=1:size(allimgs,3)
 subplot(ceil(sqrt(size(allimgs,3))),ceil(sqrt(size(allimgs,3))),a)
 imagesc(squeeze(allimgs(:,:,a)));
end
%}

plot_lifetime_process_multi(out_info,params,fig_num);

