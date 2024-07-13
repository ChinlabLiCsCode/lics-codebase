function out_param = lv_seq_get_parameter(in_seq,param_name)

out_param = [];

switch(param_name)
	case 'current'
		out_param = in_seq.ramp_params.cur_val(4);
end