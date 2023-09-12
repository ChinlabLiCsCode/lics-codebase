function out_struct = lv_seq_read(in_file_name)

% LV_SEQ_READ reads a LabView sequence file and returns a structure
% containing the sequence information.
%	OUT_STRUCT = LV_SEQ_READ(IN_FILE_NAME) reads the sequence file
%	IN_FILE_NAME and returns a structure containing the sequence
%	information.
%	

if ~isstr(in_file_name) 
    if ~isstruct(in_file_name)
        my_clock = clock();
        my_num = in_file_name;
    else
        my_clock = in_file_name.date;
        my_num = in_file_name.num;
    end
    %exp control died
    %my_file_name = sprintf('y:/ExpControl%4d/timingsettings/%04d%02d%02d/%04d%02d%02d%04d',my_clock(1),my_clock(1),my_clock(2),my_clock(3),my_clock(1),my_clock(2),my_clock(3),my_num);
    %new path
    my_file_name = sprintf('//DESKTOP-L5NCGH6/Experimentalcontroll/ExpControl%4d/timingsettings/%04d%02d%02d/%04d%02d%02d%04d',my_clock(1),my_clock(1),my_clock(2),my_clock(3),my_clock(1),my_clock(2),my_clock(3),my_num);
    
else
    my_file_name = in_file_name;
end

try
    my_fid = fopen(my_file_name,'r','ieee-be','UTF-8');
    fclose(my_fid);
    my_fid = fopen(my_file_name,'r','ieee-be','UTF-8');
catch my_err %#ok<NASGU>
    my_file_name = sprintf('//DESKTOP-L5NCGH6/Experimentalcontroll/ExpControl%4d/timingsettings/%02d/%04d%02d%02d/%04d%02d%02d%04d',my_clock(1),my_clock(2),my_clock(1),my_clock(2),my_clock(3),my_clock(1),my_clock(2),my_clock(3),my_num);
    my_fid = fopen(my_file_name,'r','ieee-be','UTF-8');
end

try
    %read the file version header
    my_version = fread(my_fid,1,'int32');
    
	%read the timing header
    if(my_version < 0)
        out_struct.version = -my_version;
        out_struct.timing = fread(my_fid,1,'uint32');
    else
        out_struct.timing = my_version;
        out_struct.version = 3;
    end
	
	%read the primary analog group
	out_struct.primary_analog = read_array(my_fid,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%read the digital group
	out_struct.digital = read_array(my_fid,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%read the procedure details
	out_struct.proc_details = read_array(my_fid,2,{'time','voltage','channel_no','enabled','ramp_res';'float64','float64','uint16','uint8','int16'});
	
	%read the procedures
	out_struct.procedures = read_array(my_fid,1,{'enabled','name','time';'uint8','pstr','float64'});
	
	%read the ramping parameters
	out_struct.ramp_params.num = fread(my_fid,1,'uint32');
	
	raw_ramps = fread(my_fid,4*out_struct.ramp_params.num,'float64');
	raw_ramps = reshape(raw_ramps,[4,out_struct.ramp_params.num]);
	out_struct.ramp_params.cur_val = raw_ramps(1,:);
	out_struct.ramp_params.start_val = raw_ramps(2,:);
	out_struct.ramp_params.end_val = raw_ramps(3,:);
	out_struct.ramp_params.incr_val = raw_ramps(4,:);
	out_struct.ramp_params.ramp_every = ones(size(out_struct.ramp_params.end_val));
	out_struct.ramp_params.next_ramp = zeros(size(out_struct.ramp_params.end_val));
	
	%read the secondary analog group
	out_struct.secondary_analog = read_array(my_fid,2,{'ival','name','is_analog';'float64', 'pstr', 'uint8'});
	
	%read the ramping control group
	check_num = fread(my_fid,1,'uint32');
	if ~feof(my_fid)
		raw_ramps = fread(my_fid,2*check_num,'int32');
		raw_ramps = reshape(raw_ramps,[2,check_num]);
		out_struct.ramp_params.ramp_every(1:check_num) = raw_ramps(1,:);
		out_struct.ramp_params.next_ramp(1:check_num) = raw_ramps(2,:);
	end
	
	%read in "never ramp"
	out_struct.never_ramp = fread(my_fid,1,'uint8');
	if numel(out_struct.never_ramp) == 0
		out_struct.never_ramp = false;
	end
	
	%read in "always ramp"
	out_struct.always_ramp = fread(my_fid,1,'uint8');
	if numel(out_struct.always_ramp) == 0
		out_struct.always_ramp = false;
	end
	
	fclose(my_fid);
	
catch my_err
	fclose(my_fid);
	rethrow(my_err);
end

end

function out_struct = read_array(my_fid,num_dimensions,in_format)
	
	num_fields = size(in_format,2);

	temp_dims = zeros(1,num_dimensions);
	for a = 1:num_dimensions
		temp_dims(a) = fread(my_fid,1,'uint32');
	end
	
	total_size = prod(temp_dims);
	arg_dims = temp_dims;
	if numel(arg_dims) == 1
		arg_dims = [arg_dims 1];
	end
	for b = 1:num_fields
		if strcmpi(in_format{2,b},'pstr')
			out_struct.(in_format{1,b}) = cell(arg_dims);
		else
			out_struct.(in_format{1,b}) = zeros(arg_dims);
		end
	end
	for a = 1:total_size
		for b = 1:num_fields
			if strcmpi(in_format{2,b},'pstr')
				in_strlen = fread(my_fid,1,'uint32');
				my_str = fread(my_fid,in_strlen,'uint8=>char')';
				out_struct.(in_format{1,b}){a} = my_str;
			else
				out_struct.(in_format{1,b})(a) = fread(my_fid,1,in_format{2,b});
			end
		end
	end
	out_struct.dims = fliplr(arg_dims);
	for b = 1:num_fields
		out_struct.(in_format{1,b}) = reshape(out_struct.(in_format{1,b}),out_struct.dims);
	end
end