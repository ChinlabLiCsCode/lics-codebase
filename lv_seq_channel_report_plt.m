function lv_seq_channel_report_plt(in_seq,which_channel,out_file,options)

%Initialize plot variables
tvals=[]; vvals=[]; rampo='';


 


default_details = true;
if ischar(which_channel)
	if strcmpi(which_channel,'all')
		channels = 0:(numel(in_seq.primary_analog.name)+numel(in_seq.digital.name)+numel(in_seq.secondary_analog.name)-1);
		default_details = false;
	else
		channels = lv_seq_get_channels_by_name(in_seq,which_channel);
	end
else
	channels = which_channel;
end

if nargin < 4
	options = struct();
end

if ~isfield(options,'details')
	options.details = default_details;
end
if ~isfield(options,'on_only')
	options.on_only = true;
end
if ~isfield(options,'proc_on_only')
	options.proc_on_only = true;
end

channel_info = cell(1,numel(channels));
for c = 1:numel(channels)
	channel_info{c}.proc_enabled = zeros(1,0);
	channel_info{c}.enabled = zeros(1,0);
	channel_info{c}.global_time = zeros(1,0);
	channel_info{c}.ramp_res = zeros(1,0);
	channel_info{c}.voltage = zeros(1,0);
	channel_info{c}.proc_name = cell(1,0);
    
end

for a = 1:(in_seq.proc_details.dims(1))
	proc_enabled = in_seq.procedures.enabled(a);
	proc_name = in_seq.procedures.name{a};
	for b = 1:(in_seq.proc_details.dims(2))
		for c = 1:numel(channels)
			if in_seq.proc_details.channel_no(a,b) == channels(c)
				channel_info{c}.proc_enabled(end+1) = proc_enabled;
				channel_info{c}.enabled(end+1) = in_seq.proc_details.enabled(a,b);
				channel_info{c}.global_time(end+1) = lv_seq_var_lookup(in_seq.ramp_params,in_seq.proc_details.time(a,b))+lv_seq_var_lookup(in_seq.ramp_params,in_seq.procedures.time(a));
				channel_info{c}.ramp_res(end+1) = in_seq.proc_details.ramp_res(a,b);
				channel_info{c}.voltage(end+1) = lv_seq_var_lookup(in_seq.ramp_params,in_seq.proc_details.voltage(a,b));
				channel_info{c}.proc_name{end+1} = proc_name;
			end
		end
	end
end

if isstr(out_file)
    my_fid = fopen(out_file,'w');
else
    my_fid = 1;
end

try
	fprintf(my_fid,'ch no\tname\t\t\t\t\t\t  init val\tanalog?\t\tused  enabled\tproc enabled\n');
	fprintf(my_fid,'-----\t----\t\t\t\t\t\t  --------\t-------\t\t----  -------\t------------\n');
	for c = 1:(numel(channels))
		this_chan = lv_seq_get_channel_by_no(in_seq,channels(c));
		fprintf(my_fid,'%03d\t\t',this_chan.chan_no);
		fprintf(my_fid,'%-24.24s\t',this_chan.name);
		fprintf(my_fid,'%10.4f\t\t',this_chan.ival);
		fprintf(my_fid,'%d\t\t',this_chan.is_analog);
		fprintf(my_fid,'%d\t\t',numel(channel_info{c}.enabled) > 0);
		fprintf(my_fid,'%d\t\t',any(channel_info{c}.enabled));
		fprintf(my_fid,'%d\n',any(channel_info{c}.enabled.*channel_info{c}.proc_enabled));
	end
	
	if options.details
		for c = 1:(numel(channels))
			this_chan = lv_seq_get_channel_by_no(in_seq,channels(c));
			fprintf(my_fid,'\nchannel %03d: %s\n\n',this_chan.chan_no,this_chan.name);
            channelname = this_chan.name;
			fprintf(my_fid,'global time\tpr enbl\tenabled\t\tvoltage\tramp\tproc name\n');
			fprintf(my_fid,'-----------\t-------\t-------\t\t-------\t----\t---------\n');
			[time_sort ordered_times] = sort(channel_info{c}.global_time);
            
            
			for d = ordered_times
				if (channel_info{c}.proc_enabled(d) && channel_info{c}.enabled(d)) || (~options.proc_on_only && channel_info{c}.enabled(d)) || (~options.proc_on_only && ~options.on_only)
					fprintf(my_fid,'%10.4f\t\t',channel_info{c}.global_time(d));
					fprintf(my_fid,'%d\t\t',channel_info{c}.proc_enabled(d));
					fprintf(my_fid,'%d\t',channel_info{c}.enabled(d));
					fprintf(my_fid,'%10.4f\t',channel_info{c}.voltage(d));
                    vvals(d) = channel_info{c}.voltage(d);
                    tvals(d) = channel_info{c}.global_time(d);
                 
               
				    switch channel_info{c}.ramp_res(d)
					    	case 0
							fprintf(my_fid,'JUMP\t');
                            rampo='JUMP';
						case 1
							fprintf(my_fid,'FINE\t');
                            rampo='FINE'
						case 2
							fprintf(my_fid,'COARSE\t');
                            rampo='COARSE';
						otherwise
							fprintf(my_fid,'????\t');
                            rampo='????'

                    end
                    
					fprintf(my_fid,'%s\n',channel_info{c}.proc_name{d});

                 
    
 
			end
		end
   
	
    if isstr(out_file)
        fclose(my_fid);
    end
    
    %plot output :)
    [sX,sI] = sort(tvals);
    sY = vvals(sI);
  
    figure;
                    box on;
                    plot(sX, sY)
                    
                    dcm_obj = datacursormode(gcf);
                    set(dcm_obj, 'UpdateFcn', {@customDatatip, tvals,vvals channel_info{c}.proc_name(sI), channel_info{c}.ramp_res(sI)});

             
                    xlabel('Time (ms)'); 
                    ylabel('Channel Voltage');
                    trw= channelname,'Interpreter','none';
                    title("Channel "+channelname(1:4));
                    

				end
    
    
    
    
    
  


%catch my_err
 %   if isstr(out_file)
%        fclose(my_fid);
%    end
%	rethrow(my_err);


end

end 
end 
function output_txt = customDatatip(~, event,tvals,vvals, proc_names, ramp_res)
    pos = get(event, 'Position');
    idx = get(event, 'DataIndex');

    x = tvals(idx);
    y = vvals(idx);

    proc_name = proc_names{idx};
    proc_name = strrep(proc_name, '_', ' ');

    switch ramp_res(idx)
        case 0
            rampo = 'JUMP';
        case 1
            rampo = 'FINE';
        case 2
            rampo = 'COARSE';
        otherwise
            rampo = '????';
    end

    output_txt = {...
        ['Time: ', num2str(pos(1))], ...
        ['Voltage: ', num2str(pos(2))], ...
        ['Ramp Type: ', rampo],...
        ['Procedure Name: ', proc_name]};
end
    
       

