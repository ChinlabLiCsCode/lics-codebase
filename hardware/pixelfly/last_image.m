function [new_num out_stats] = last_image(old_num, my_clock, image_type)

if nargin < 3 || image_type == 0
    image_type = 1;
    if nargin < 2
        my_clock = clock();
    end
end
file_template = 'D:\\LiCs_Data\\Data\\%1$04d%2$02d%3$02d\\%1$04d%2$02d%3$02d_%4$d.mat';

file_name = sprintf(file_template,my_clock(1),my_clock(2),my_clock(3),old_num);
%file_name = sprintf(file_template,2013,1,27,old_num);
keep_going = false;
if ~isempty(ls(file_name))
    try
        out_temp = load(file_name,'fitdata');
        out_stats = [out_temp.fitdata{:,1}];
        keep_going = true;
    catch err
        keep_going = false;
    end
    if keep_going
        if image_type == 1
            out_stats(end+1) = 8.2^2/(3*.852^2/(2*pi))*sqrt(2*pi)*out_stats(1)*out_stats(2);%Cs horizontal
            out_stats(end+1) = 8.2^2/(3*.852^2/(2*pi))*sqrt(2*pi)*out_stats(5)*out_stats(6);%Cs horizontal
        elseif image_type == 2
            out_stats(end+1) = 8.2^2/(3*.671^2/(2*pi))*sqrt(2*pi)*out_stats(1)*out_stats(2);%Li horizontal
            out_stats(end+1) = 8.2^2/(3*.671^2/(2*pi))*sqrt(2*pi)*out_stats(5)*out_stats(6);%Li horizontal
        elseif image_type == 3
            out_stats(end+1) = 2.47^2/(3*.852^2/(2*pi))*sqrt(2*pi)*out_stats(1)*out_stats(2);%Cs vertical
            out_stats(end+1) = 2.47^2/(3*.852^2/(2*pi))*sqrt(2*pi)*out_stats(5)*out_stats(6);%Cs vertical
        elseif image_type == 4
            out_stats(end+1) = 2.47^2/(3*.671^2/(2*pi))*sqrt(2*pi)*out_stats(1)*out_stats(2);%Li vertical
            out_stats(end+1) = 2.47^2/(3*.671^2/(2*pi))*sqrt(2*pi)*out_stats(5)*out_stats(6);%Li vertical
        end
        new_num = old_num + 1;
    end
end
if ~keep_going
   out_stats = zeros(0,1);
   new_num = old_num;
end