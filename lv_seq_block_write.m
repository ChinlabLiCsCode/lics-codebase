function out_seq = lv_seq_block_write(in_seq, in_proc_no, times, time_offsets, channel_nos, voltages, ramp_res)

sort_seq = lv_seq_sort(in_seq);

proc_len = size(sort_seq.proc_details.enabled,2);
repeat_len = numel(time_offsets);

for b = 1:repeat_len
	temp = lv_seq_get_channels_by_name(in_seq,channel_nos{b});
	real_channel_nos(b) = temp(1);
end

max_val = max(sort_seq.proc_details.enabled(in_proc_no,:).*(1:proc_len));

for a = 1:length(times)
	if max_val + a*repeat_len > proc_len
		break
	end
	for b = 1:repeat_len
		sort_seq.proc_details.enabled(in_proc_no,max_val+(a-1)*repeat_len+b) = 1;
		sort_seq.proc_details.time(in_proc_no,max_val+(a-1)*repeat_len+b) = times(a)+time_offsets(b);
		sort_seq.proc_details.channel_no(in_proc_no,max_val+(a-1)*repeat_len+b) = real_channel_nos(b);
		sort_seq.proc_details.ramp_res(in_proc_no,max_val+(a-1)*repeat_len+b) = ramp_res(b);
		sort_seq.proc_details.voltage(in_proc_no,max_val+(a-1)*repeat_len+b) = voltages(b);
	end
end

out_seq = in_seq;
out_seq.proc_details.enabled(in_proc_no,:) = sort_seq.proc_details.enabled(in_proc_no,:);
out_seq.proc_details.time(in_proc_no,:) = sort_seq.proc_details.time(in_proc_no,:);
out_seq.proc_details.ramp_res(in_proc_no,:) = sort_seq.proc_details.ramp_res(in_proc_no,:);
out_seq.proc_details.channel_no(in_proc_no,:) = sort_seq.proc_details.channel_no(in_proc_no,:);
out_seq.proc_details.voltage(in_proc_no,:) = sort_seq.proc_details.voltage(in_proc_no,:);