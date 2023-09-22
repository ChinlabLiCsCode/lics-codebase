function lv_insert_fieldjump(in_file_name, initial_v, final_v, out_num, out_date)
% in_file_name can be a string, just a number (for today), or a date+number
% in a struct. initial v is the initial voltage, and final is final.

%% Frank Edition: the number version is not working. So please input a structure
% User example: lv_insert_fieldjump(   struct('num',20,'date',[2023 09 18]),   4.75,3.25,   1801,[2023 09 32])

%
%% handle varargsin    ////////////////////////--> Is this part written wrong??
if nargin < 4
    if ~isstruct(in_file_name)
        out_num = in_file_name + 5000;
    else
        out_num = in_file_name.num + 5000;
    end
end
%% declare constants
fieldjump_proc_name = 'Smart_Shim_Jump';
jump_channel_name = '5.15_Bias_3/4_HH_y';

% our target jump times 
j_times = [
    -0.1000
    0
    0.1000
    0.2000
    0.3400
    0.5400
    0.7400
    0.9400
    1.1600
    1.2400
    1.4000
    1.5000
    1.7000
    1.8000
    2.1000];
% we need this line because the written jump seems to actually start .1 ms
% late
j_times = j_times - 6;

% our target jump voltages
j_voltages = [
    5.5000
    0.0548
    2.0731
    2.9145
    3.3045
    3.5276
    3.8274
    3.9670
    4.0933
    4.1337
    4.0891
    4.1092
    4.0991
    4.0790
    4.0000];
j_correction = [
    0
    0
    0
    0.080
    0.080
    0.100
    0.080
   -0.040
   -0.040
   -0.060
   -0.060
   -0.060
    0
    0
    0];
j_voltages = j_voltages + j_correction;
% we need this line because the written jump is from 5.5 to 4, but we want
% 0 to 1.
j_voltages = 1 + ((j_voltages - 4) ./ (-1.5));



%% read existing sequence

s = lv_seq_read(in_file_name);
%% figure out which process index corresponds to the field jump process 
N = s.proc_details.dims(1); % number of processes
T = s.proc_details.dims(2); % number of events per process

j_ind = -1;
for n = 1:N
    if strcmp(fieldjump_proc_name, s.procedures.name{n})
        j_ind = n;
    end
end
if j_ind == -1
    disp('Sequence lacks appropriate procedure. Quitting.');
    return
end


%% figure out which channel no corresponds to the channel we want
dnames = s.digital.name;
anames1 = s.primary_analog.name;
anames2 = s.secondary_analog.name;
jchan_no = -1;
for i = 1:length(dnames)
    if strcmp(dnames{i}, jump_channel_name)
        jchan_no = i - 1;
    end
end
for i = 1:length(anames1)
    if strcmp(anames1{i}, jump_channel_name)
        jchan_no = i + length(dnames) - 1;
    end
end
for i = 1:length(anames2)
    if strcmp(anames2{i}, jump_channel_name)
        jchan_no = i + length(dnames) + length(anames1) - 1;
    end
end

if jchan_no == -1
    disp('Couldnt find channel. Quitting.');
    return
end

%% clear this process
s.proc_details.channel_no(j_ind, :) = 0;
s.proc_details.enabled(j_ind, :) = 0;
s.proc_details.ramp_res(j_ind, :) = 0;
s.proc_details.time(j_ind, :) = 0;
s.proc_details.voltage(j_ind, :) = 0;

%% compute the values that go into this process
% scale the jump voltages for the specified jump
write_voltages = (j_voltages .* (final_v - initial_v)) + initial_v;
% how many samples do we actually need?
A = length(write_voltages); % 

%% insert them into the process
s.proc_details.channel_no(j_ind, 1:A) = jchan_no;
s.proc_details.enabled(j_ind, 1:A) = 1;
s.proc_details.ramp_res(j_ind, 1:2) = 0; % the first two entries are jumps
s.proc_details.ramp_res(j_ind, 3:A) = 1; % the rest are fine ramps
s.proc_details.time(j_ind, 1:A) = j_times;
s.proc_details.voltage(j_ind, 1:A) = write_voltages;

%% save it in the stated filename 
% Frank: edited 2023-Sept-16--> I made it a structure
%out_file_name = in_file_name;
out_file_name.num = out_num;
out_file_name.date = out_date;
lv_seq_write(s, out_file_name)

%% return the saved file date and number
fprintf('saved as %04d%02d%02d #%d.\n', out_file_name.date(1), out_file_name.date(2), out_file_name.date(3), out_file_name.num);

end