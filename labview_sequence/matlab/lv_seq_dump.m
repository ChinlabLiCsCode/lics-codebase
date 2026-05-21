%% Use this code to dump entire sequence into text file. The first input
%is specified in the same way as lv_channel_report, and the second is the
%desired text file output path. -KP 
function lv_seq_dump(in_seq,in_target,options)

if nargin < 3
	options = struct();
end

if ~isfield(options,'sort')
	options.sort = true;
end
if ~isfield(options,'show_disabled')
	options.show_disabled = false;
end
if ~isfield(options,'seperate_disabled') || options.show_disabled
	options.seperate_disabled = false;
end

my_fid = fopen(in_target,'w');

try
	fprintf(my_fid,'header\n------\n');
    fprintf(my_fid,'version:%d\n',in_seq.version);
	fprintf(my_fid,'timing:%d\nnever ramp:%d\nalways_ramp:%d\n',in_seq.timing,in_seq.never_ramp,in_seq.always_ramp);
	
	num_channels = numel(in_seq.primary_analog.name)+numel(in_seq.digital.name)+numel(in_seq.secondary_analog.name);
	fprintf(my_fid,'number of channels:%d\n',num_channels);
	
	num_procs = numel(in_seq.procedures.name);
	fprintf(my_fid,'number of procedures:%d\n',num_procs);
	
	fprintf(my_fid,'\nch no\tname\t\t\t\t\t\t  init val\tanalog?\n-----\t----\t\t\t\t\t\t  --------\t-------\n');
	for a = 0:(num_channels-1);
		this_chan = lv_seq_get_channel_by_no(in_seq,a);
		fprintf(my_fid,'%03d\t\t%-24.24s\t%10.4f\t\t%d\n',a,this_chan.name,this_chan.ival,this_chan.is_analog);
	end
	
	fprintf(my_fid, '\nproc no\tname\t\t\t\t\t\t\t  time\t\tenabled\n-------\t----\t\t\t\t\t\t\t  ----\t\t------\n');
	for a = 1:num_procs
		fprintf(my_fid,'%03d\t\t',a-1);
		fprintf(my_fid,'%-24.24s\t',in_seq.procedures.name{a});
		fprintf(my_fid,'%10.4f\t\t',in_seq.procedures.time(a));
		fprintf(my_fid,'%d\n',in_seq.procedures.enabled(a));
	end
	
	for a = 1:num_procs
		fprintf(my_fid,'\nprocedure %03d: %s\n',a-1,in_seq.procedures.name{a});
		
		fprintf(my_fid,'\nenabled\t\ttime\tchannel\t\t\t\t\t\t   voltage\tramp\n------\t\t----\t-------\t\t\t\t\t\t   -------\t----\n');
		
		[sorted_times sort_order] = sort(in_seq.proc_details.time(a,:));
		default_order = 1:length(sorted_times);
		
		if options.sort
			final_order = sort_order;
		else
			final_order = default_order;
		end
		
		for b = 1:(in_seq.proc_details.dims(2))
			if options.show_disabled || in_seq.proc_details.enabled(a,final_order(b))
				fprintf(my_fid,'%d\t\t',in_seq.proc_details.enabled(a,final_order(b)));
				fprintf(my_fid,'%10.4f\t',in_seq.proc_details.time(a,final_order(b)));
				this_chan = lv_seq_get_channel_by_no(in_seq,in_seq.proc_details.channel_no(a,final_order(b)));
				fprintf(my_fid,'%-24.24s\t',this_chan.name);
				fprintf(my_fid,'%10.6f\t',in_seq.proc_details.voltage(a,final_order(b)));
				switch in_seq.proc_details.ramp_res(a,final_order(b))
					case 0
						fprintf(my_fid,'JUMP\n');
					case 1
						fprintf(my_fid,'FINE\n');
					case 2
						fprintf(my_fid,'COARSE\n');
					otherwise
						fprintf(my_fid,'????\n');
				end
			end
		end
		if options.seperate_disabled
			for b = 1:(in_seq.proc_details.dims(2))
				if ~in_seq.proc_details.enabled(a,final_order(b))
					fprintf(my_fid,'%d\t\t',in_seq.proc_details.enabled(a,final_order(b)));
					fprintf(my_fid,'%10.4f\t',in_seq.proc_details.time(a,final_order(b)));
					this_chan = lv_seq_get_channel_by_no(in_seq,in_seq.proc_details.channel_no(a,final_order(b)));
					fprintf(my_fid,'%-24.24s\t',this_chan.name);
					fprintf(my_fid,'%10.4f\t',in_seq.proc_details.voltage(a,final_order(b)));
					switch in_seq.proc_details.ramp_res(a,final_order(b))
						case 0
							fprintf(my_fid,'JUMP\n');
						case 1
							fprintf(my_fid,'FINE\n');
						case 2
							fprintf(my_fid,'COARSE\n');
						otherwise
							fprintf(my_fid,'????\n');
					end
				end
			end
		end
	end
	
	fprintf(my_fid,'\ncode\t   cur val\t\tstart\t\tstop\t\tstep\tevery\t next\n----\t   -------\t\t-----\t\t----\t\t----\t-----\t ----\n');
	for a = 1:(in_seq.ramp_params.num)
		fprintf(my_fid,'%05d\t',65499+a);
		fprintf(my_fid,'%10.4f\t',in_seq.ramp_params.cur_val(a));
		fprintf(my_fid,'%10.4f\t',in_seq.ramp_params.start_val(a));
		fprintf(my_fid,'%10.4f\t',in_seq.ramp_params.end_val(a));
		fprintf(my_fid,'%10.4f\t\t',in_seq.ramp_params.incr_val(a));
		fprintf(my_fid,'%d\t\t',in_seq.ramp_params.ramp_every(a));
		fprintf(my_fid,'%d\n',in_seq.ramp_params.next_ramp(a));
	end
	
	fclose(my_fid);
catch my_err
	fclose(my_fid);
	rethrow(my_err);
end