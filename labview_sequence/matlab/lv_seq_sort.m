function in_seq = lv_seq_sort(in_seq)

for a = 1:(in_seq.proc_details.dims(1))
	[sorted_times init_sort_order] = sort(in_seq.proc_details.time(a,:));
	[sorted_enablings sort_order] = sort(in_seq.proc_details.enabled(a,init_sort_order),'descend');
	final_order = init_sort_order(sort_order);
	in_seq.proc_details.enabled(a,:) = sorted_enablings;
	in_seq.proc_details.time(a,:) = in_seq.proc_details.time(a,final_order);
	in_seq.proc_details.voltage(a,:) = in_seq.proc_details.voltage(a,final_order);
	in_seq.proc_details.channel_no(a,:) = in_seq.proc_details.channel_no(a,final_order);
	in_seq.proc_details.ramp_res(a,:) = in_seq.proc_details.ramp_res(a,final_order);
end