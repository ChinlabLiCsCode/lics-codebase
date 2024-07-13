function lv_seq_write(in_seq,in_target,options)

if nargin < 3
	options = struct();
end

if ~isfield(options,'sort')
	options.sort = false;
end
if ~isfield(options,'clear_disabled')
	options.clear_disabled = false;
end

if options.clear_disabled
	in_seq = lv_seq_clear_disabled(in_seq);
end

if options.sort
	in_seq = lv_seq_sort(in_seq);
end


% Henry added this May 2023
% testA = ~isstruct(in_target)
% in_target
if ~isstr(in_target) 
    if isstruct(in_target)
        my_clock = in_target.date;
        my_num = in_target.num;
    else 
        my_clock = clock();
        my_num = in_target;
    end

    in_target = sprintf('//DESKTOP-L5NCGH6/Experimentalcontroll/ExpControl%4d/timingsettings/%04d%02d%02d/%04d%02d%02d%04d',my_clock(1),my_clock(1),my_clock(2),my_clock(3),my_clock(1),my_clock(2),my_clock(3),my_num);
end
% End Henry addition
 
my_fid = fopen(in_target,'w','ieee-be','UTF-8');

try
    %write the version header
    if in_seq.version >= 4
        fwrite(my_fid,-in_seq.version,'int32');
    end
    
	%write the timing header
	fwrite(my_fid,in_seq.timing,'uint32');
	
	%write the primary analog group
	write_array(my_fid,in_seq.primary_analog,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%write the digital group
	write_array(my_fid,in_seq.digital,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%write the procedure details
	write_array(my_fid,in_seq.proc_details,2,{'time','voltage','channel_no','enabled','ramp_res';'float64','float64','uint16','uint8','int16'});
	
	%write the procedures
	write_array(my_fid,in_seq.procedures,1,{'enabled','name','time';'uint8','pstr','float64'});
	
	%write the ramping parameters
	fwrite(my_fid,in_seq.ramp_params.num,'uint32');
	
	raw_ramps = zeros(4,in_seq.ramp_params.num);
	raw_ramps(1,:) = in_seq.ramp_params.cur_val;
	raw_ramps(2,:) = in_seq.ramp_params.start_val;
	raw_ramps(3,:) = in_seq.ramp_params.end_val;
	raw_ramps(4,:) = in_seq.ramp_params.incr_val;
	
	fwrite(my_fid,raw_ramps,'float64');
	
	%write the secondary analog group
	write_array(my_fid,in_seq.secondary_analog,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%write the ramping control group
	fwrite(my_fid,in_seq.ramp_params.num,'uint32');
	raw_ramps = zeros(2,in_seq.ramp_params.num);
	raw_ramps(1,:) = in_seq.ramp_params.ramp_every;
	raw_ramps(2,:) = in_seq.ramp_params.next_ramp;
	
	fwrite(my_fid,raw_ramps,'int32');
	
	%write the "always ramp"
	fwrite(my_fid,in_seq.always_ramp,'uint8');
	
	%write the "never ramp"
	fwrite(my_fid,in_seq.never_ramp,'uint8');
	
	fclose(my_fid);
catch my_err
	fclose(my_fid);
	rethrow(my_err);
end

end

function write_array(my_fid,in_struct,num_dimensions,in_format)
	num_fields = size(in_format,2);
	
	true_dims = fliplr(in_struct.dims);
	total_size = prod(true_dims);
	
	for a = 1:num_dimensions
		fwrite(my_fid,true_dims(a),'uint32');
	end
	
	for a = 1:total_size
		for b = 1:num_fields
			if strcmpi(in_format{2,b},'pstr')
				out_strlen = numel(in_struct.(in_format{1,b}){a});
				fwrite(my_fid,out_strlen,'uint32');
				fwrite(my_fid,in_struct.(in_format{1,b}){a},'char');
			else
				fwrite(my_fid,in_struct.(in_format{1,b})(a),in_format{2,b});
			end
		end
	end
end