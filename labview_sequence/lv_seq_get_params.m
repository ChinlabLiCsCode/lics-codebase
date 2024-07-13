function out_params = lv_seq_get_params(in_base_name,in_nums,in_param)

out_params = zeros(size(in_nums(:)));
my_filename = in_base_name;

for a = 1:length(out_params)
	my_filename = sprintf(in_base_name,in_nums(a));
	out_params(a) = lv_seq_get_parameter(lv_seq_read(my_filename),in_param);
end