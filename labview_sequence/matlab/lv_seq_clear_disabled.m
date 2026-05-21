function in_seq = lv_seq_clear_disabled(in_seq)

for a = 1:(in_seq.proc_details.dims(1))
	for b = 1:(in_seq.proc_details.dims(2))
		if ~in_seq.proc_details.enabled(a,b)
			in_seq.proc_details.time(a,b) = 0;
			in_seq.proc_details.voltage(a,b) = 0;
			in_seq.proc_details.channel_no(a,b) = 0;
			in_seq.proc_details.ramp_res(a,b) = 0;
		end
	end
end