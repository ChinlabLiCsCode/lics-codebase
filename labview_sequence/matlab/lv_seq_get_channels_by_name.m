function out_chan_nos = lv_seq_get_channels_by_name(in_seq,channel_name)

out_chan_nos = [];

groups = {in_seq.primary_analog, in_seq.digital, in_seq.secondary_analog};

if in_seq.version < 4
    chan_offset = [-1 15 45];
else
    chan_offset = [-1 23 85];
end

for a = 1:3
	for b = 1:(groups{a}.dims(2))
		if ~isempty(strfind(upper(groups{a}.name{b}), upper(channel_name)))
			out_chan_nos(end+1) = b+chan_offset(a);
			%out_struct.ival = groups{a}.ival(b);
			%out_struct.name = groups{a}.name{b};
			%out_struct.is_analog = groups{a}.is_analog(b);
		end
	end
end
	