function out_val = lv_seq_var_lookup(ramp_params,in_val)

if in_val <= 65499.6
	out_val = in_val;
else
	index = round(in_val-65499);
	out_val = ramp_params.cur_val(index);
end