function out_file_name = lv_insert_fieldjump(in_file_name, inital_v, final_v)


%% declare constants
out_file_folder = '../20230519/';
fieldjump_proc_name = 'field_jump';
jump_channel_no = 10;

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
j_times = j_times - 0.1;

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
    disp("Sequence lacks appropriate procedure. Quitting.")
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
s.proc_details.channel_no(j_ind, 1:A) = jump_channel_no;
s.proc_details.enabled(j_ind, 1:A) = 1;
s.proc_details.ramp_res(j_ind, 1:2) = 0; % the first two entries are jumps
s.proc_details.ramp_res(j_ind, 3:A) = 1; % the rest are fine ramps
s.proc_details.time(j_ind, 1:A) = j_times;
s.proc_details.voltage(j_ind, 1:A) = write_voltages;

%% save it in the stated filename 
"test"
lv_seq_write(s, )

%% return the saved file date and number







end