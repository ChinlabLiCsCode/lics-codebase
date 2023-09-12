function num_pulses = lv_seq_count_pulses(in_seq,which_channel,edge)

if nargin < 3
    trig_rise = true;
    trig_fall = false;
elseif strcmpi(edge,'both')
    trig_rise = true;
    trig_fall = true;
elseif strcmpi(edge,'falling')
    trig_rise = false;
    trig_fall = true;
else
    trig_rise = true;
    trig_fall = false;
end

freeze_number = 4;
min_diff = 20/(2^16);

if ischar(which_channel)
	if strcmpi(which_channel,'all')
		channels = 0:(numel(in_seq.primary_analog.name)+numel(in_seq.digital.name)+numel(in_seq.secondary_analog.name)-1);
	else
		channels = lv_seq_get_channels_by_name(in_seq,which_channel);
	end
else
	channels = which_channel;
end

num_pulses = zeros(size(channels));

channel_info = cell(1,numel(channels));
for c = 1:numel(channels)
	channel_info{c}.global_time = zeros(1,0);
	channel_info{c}.ramp_res = zeros(1,0);
	channel_info{c}.voltage = zeros(1,0);
end

for a = 1:(in_seq.proc_details.dims(1))
    if in_seq.procedures.enabled(a);
        for b = 1:(in_seq.proc_details.dims(2))
            for c = 1:numel(channels)
                if in_seq.proc_details.channel_no(a,b) == channels(c) && in_seq.proc_details.enabled(a,b)
                    channel_info{c}.global_time(end+1) = lv_seq_var_lookup(in_seq.ramp_params,in_seq.proc_details.time(a,b))+lv_seq_var_lookup(in_seq.ramp_params,in_seq.procedures.time(a));
                    channel_info{c}.ramp_res(end+1) = in_seq.proc_details.ramp_res(a,b);
                    channel_info{c}.voltage(end+1) = lv_seq_var_lookup(in_seq.ramp_params,in_seq.proc_details.voltage(a,b));
                end
            end
        end
    end
end

for c = 1:numel(channels)
    is_frozen = false;
    this_chan = lv_seq_get_channel_by_no(in_seq,channels(c));
    old_val = this_chan.ival;
    [~, sort_order] = sort(channel_info{c}.global_time);
    for a = sort_order
        if ~is_frozen || channel_info{c}.ramp_res(a) == freeze_number
            if channel_info{c}.ramp_res(a) == freeze_number
                is_frozen = ~is_frozen;
            end
            diff = channel_info{c}.voltage(a)-old_val;
            old_val = channel_info{c}.voltage(a);
            if diff > min_diff && trig_rise
                num_pulses(c) = num_pulses(c) + 1;
            elseif diff < -min_diff && trig_fall
                num_pulses(c) = num_pulses(c) + 1;
            end
        end
    end
end