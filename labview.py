import numpy as np
import time
import os
import struct

def seq_read(in_file_name):
    """Reads a LabVIEW sequence file and returns a dictionary with the sequence information.
    
    Parameters
    ----------
    in_file_name : str or dict
        The file name of the LabVIEW sequence file to be read. If a string is passed, the file name is assumed to be
        the full path to the file. If a dictionary is passed, the file name is assumed to be the file number and the
        date of the file. The dictionary should have the keys 'num' and 'date', where 'num' is the file number and
        'date' is the date of the file in seconds since the epoch. If the file name is not passed, the function will 
        attempt to read the most recent file in the current day's directory. If the file name is passed as None, the 
        function will attempt to read the most recent file in the current day's directory. 
        
    Returns
    -------
    out_struct : dict
        A dictionary with the sequence information. The dictionary has the following keys:
    
    out_struct['version'] : int
        The version of the LabVIEW sequence file. I don't know what this does.

    out_struct['timing'] : int
        I don't know what this does.
        
    out_struct['primary_analog'] : dict
        The primary analog channels of the sequence file. The dictionary has the following keys:

        out_struct['primary_analog']['ival'] : np.ndarray
            The initial values of the primary analog channels.

        out_struct['primary_analog']['name'] : np.ndarray
            The names of the primary analog channels.

        out_struct['primary_analog']['is_analog'] : np.ndarray
            The analog status of the primary analog channels. 0 is for digital, 1 is for analog.

    out_struct['digital'] : dict
        The digital channels of the sequence file. The dictionary has the following keys:

        out_struct['digital']['ival'] : np.ndarray
            The initial values of the digital channels.

        out_struct['digital']['name'] : np.ndarray      
            The names of the digital channels.

        out_struct['digital']['is_analog'] : np.ndarray
            The analog status of the digital channels. 0 is for digital, 1 is for analog.
        
    out_struct['proc_details'] : dict
        The procedure details of the sequence file. The dictionary has the following keys:

        out_struct['proc_details']['time'] : np.ndarray
            The times of the procedure details.

        out_struct['proc_details']['voltage'] : np.ndarray
            The voltages of the procedure details.

        out_struct['proc_details']['channel_no'] : np.ndarray
            The channel numbers of the procedure details.

        out_struct['proc_details']['enabled'] : np.ndarray
            The enabled status of the procedure details. 0 is for disabled, 1 is for enabled.

        out_struct['proc_details']['ramp_res'] : np.ndarray
            The ramp resolution of the procedure details.

    
    out_struct['procedures'] : dict
        The procedures of the sequence file. The dictionary has the following keys:

        out_struct['procedures']['enabled'] : np.ndarray
            The enabled status of the procedures. 0 is for disabled, 1 is for enabled.

        out_struct['procedures']['name'] : np.ndarray
            The names of the procedures.

        out_struct['procedures']['time'] : np.ndarray
            The times of the procedures.

    out_struct['ramp_params'] : dict
        The ramp parameters of the sequence file. The dictionary has the following keys:

        out_struct['ramp_params']['num'] : int
            The number associated with the ramp parameter.

        out_struct['ramp_params']['cur_val'] : np.ndarray
            The current values of the ramp parameter.

        out_struct['ramp_params']['start_val'] : np.ndarray
            The start values of the ramp parameter.

        out_struct['ramp_params']['end_val'] : np.ndarray
            The end values of the ramp parameter.

        out_struct['ramp_params']['incr_val'] : np.ndarray
            The increment values of the ramp parameter.

        out_struct['ramp_params']['ramp_every'] : np.ndarray
            The ramp every values of the ramp parameter.

        out_struct['ramp_params']['next_ramp'] : np.ndarray
            The next ramp values of the ramp parameter.

    out_struct['secondary_analog'] : dict
        The secondary analog channels of the sequence file. The dictionary has the following keys:

        out_struct['secondary_analog']['ival'] : np.ndarray
            The initial values of the secondary analog channels.

        out_struct['secondary_analog']['name'] : np.ndarray
            The names of the secondary analog channels.

        out_struct['secondary_analog']['is_analog'] : np.ndarray
            The analog status of the secondary analog channels. 0 is for digital, 1 is for analog.

    out_struct['never_ramp'] : bool
        The never ramp status of the sequence file. True is for never ramp, False is for not never ramp.

    out_struct['always_ramp'] : bool
        The always ramp status of the sequence file. True is for always ramp, False is for not always ramp.

    Raises
    ------  
    Exception
        If the file cannot be read, an exception is raised.

    Notes
    -----
    The LabVIEW sequence file is a binary file. The file is read in as a binary file and the data is parsed into a
    dictionary. The dictionary is returned.

    """

    my_clock = np.array(time.localtime())
    

    # If no file name is passed, attempt to read the most recent file in the current day's directory
    if not isinstance(in_file_name, str):
        if not isinstance(in_file_name, dict):
            my_clock = np.array(time.localtime())
            my_num = in_file_name
        else:
            my_clock = time.localtime(in_file_name['date'])
            my_num = in_file_name['num']
        # Edit the file name to match the local file path format here
        my_file_name = f"//DESKTOP-L5NCGH6/Experimentalcontroll/ExpControl{my_clock[0]}/timingsettings/{my_clock[0]}{my_clock[1]:02d}{my_clock[2]:02d}/{my_clock[0]}{my_clock[1]:02d}{my_clock[2]:02d}{my_num:04d}"
    else:
        my_file_name = in_file_name

    # Read the file
    with open(my_file_name, 'rb') as my_fid:

        # Read the version number
        my_version = np.fromfile(my_fid, dtype=np.dtype('>i4'), count=1, sep="")[0]

        # If the version number is negative, read the timing information.
        if my_version < 0:
            out_struct = {'version': -my_version}
            out_struct['timing'] = np.fromfile(my_fid, dtype=np.dtype('>u4'), count=1, sep="")[0]
        else:
            out_struct = {'timing': my_version, 'version': 3}
        
        
        out_struct['primary_analog'] = read_array(my_fid, 2, [('ival', 'float64'), ('name', 'pstr'), ('is_analog', 'uint8')])
        out_struct['digital'] = read_array(my_fid, 2, [('ival', 'float64'), ('name', 'pstr'), ('is_analog', 'uint8')])
        out_struct['proc_details'] = read_array(my_fid, 2, [('time', 'float64'), ('voltage', 'float64'), ('channel_no', 'uint16'), ('enabled', 'uint8'), ('ramp_res', 'int16')])
        out_struct['procedures'] = read_array(my_fid, 1, [('enabled', 'uint8'), ('name', 'pstr'), ('time', 'float64')])

        out_struct['ramp_params'] = {}
        out_struct['ramp_params']['num'] = np.fromfile(my_fid, dtype=np.dtype('>u4'), count=1)[0]

        raw_ramps = np.fromfile(my_fid, dtype=np.dtype('>f8'), count=4 * out_struct['ramp_params']['num'])
        raw_ramps = np.reshape(raw_ramps, (4, out_struct['ramp_params']['num']))
        out_struct['ramp_params']['cur_val'] = raw_ramps[0, :]
        out_struct['ramp_params']['start_val'] = raw_ramps[1, :]
        out_struct['ramp_params']['end_val'] = raw_ramps[2, :]
        out_struct['ramp_params']['incr_val'] = raw_ramps[3, :]
        out_struct['ramp_params']['ramp_every'] = np.ones(out_struct['ramp_params']['end_val'].shape)
        out_struct['ramp_params']['next_ramp'] = np.zeros(out_struct['ramp_params']['end_val'].shape)

        out_struct['secondary_analog'] = read_array(my_fid, 2, [('ival', 'float64'), ('name', 'pstr'), ('is_analog', 'uint8')])

        check_num = np.fromfile(my_fid, dtype=np.dtype('>u4'), count=1)[0]
        if not my_fid.tell() == os.fstat(my_fid.fileno()).st_size:
            raw_ramps = np.fromfile(my_fid, dtype=np.dtype('>i4'), count=2 * check_num)
            raw_ramps = np.reshape(raw_ramps, (2, check_num))
            out_struct['ramp_params']['ramp_every'][:check_num] = raw_ramps[0, :]
            out_struct['ramp_params']['next_ramp'][:check_num] = raw_ramps[1, :]

        out_struct['never_ramp'] = np.fromfile(my_fid, dtype=np.dtype('>u1'), count=1)
        if len(out_struct['never_ramp']) == 0:
            out_struct['never_ramp'] = False

        out_struct['always_ramp'] = np.fromfile(my_fid, dtype=np.dtype('>u1'), count=1)
        if len(out_struct['always_ramp']) == 0:
            out_struct['always_ramp'] = False

    return out_struct



def lv_seq_write(in_seq, in_target, options=None):
    if options is None:
        options = {}

    if 'sort' not in options:
        options['sort'] = False
    if 'clear_disabled' not in options:
        options['clear_disabled'] = False

    if options['clear_disabled']:
        in_seq = lv_seq_clear_disabled(in_seq)

    if options['sort']:
        in_seq = lv_seq_sort(in_seq)

    my_fid = open(in_target, 'wb')

    try:
        # Write the version header
        if in_seq.version >= 4:
            my_fid.write(struct.pack('>i', -in_seq.version))

        # Write the timing header
        my_fid.write(struct.pack('>I', in_seq.timing))

        # Write the primary analog group
        write_array(my_fid, in_seq.primary_analog, 2, ['ival', 'name', 'is_analog'], ['>d', 'str', 'B'])

        # Write the digital group
        write_array(my_fid, in_seq.digital, 2, ['ival', 'name', 'is_analog'], ['>d', 'str', 'B'])

        # Write the procedure details
        write_array(my_fid, in_seq.proc_details, 2, ['time', 'voltage', 'channel_no', 'enabled', 'ramp_res'],
                    ['>d', '>d', '>H', 'B', '>h'])

        # Write the procedures
        write_array(my_fid, in_seq.procedures, 1, ['enabled', 'name', 'time'], ['B', 'str', '>d'])

        # Write the ramping parameters
        my_fid.write(struct.pack('>I', in_seq.ramp_params['num']))

        raw_ramps = np.zeros((4, in_seq.ramp_params['num']), dtype=np.float64)
        raw_ramps[0, :] = in_seq.ramp_params['cur_val']
        raw_ramps[1, :] = in_seq.ramp_params['start_val']
        raw_ramps[2, :] = in_seq.ramp_params['end_val']
        raw_ramps[3, :] = in_seq.ramp_params['incr_val']

        my_fid.write(raw_ramps.tobytes())

        # Write the secondary analog group
        write_array(my_fid, in_seq.secondary_analog, 2, ['ival', 'name', 'is_analog'], ['>d', 'str', 'B'])

        # Write the ramping control group
        my_fid.write(struct.pack('>I', in_seq.ramp_params['num']))
        raw_ramps = np.zeros((2, in_seq.ramp_params['num']), dtype=np.int32)
        raw_ramps[0, :] = in_seq.ramp_params['ramp_every']
        raw_ramps[1, :] = in_seq.ramp_params['next_ramp']

        my_fid.write(raw_ramps.tobytes())

        # Write the "always ramp"
        my_fid.write(struct.pack('B', in_seq.always_ramp))

        # Write the "never ramp"
        my_fid.write(struct.pack('B', in_seq.never_ramp))

        my_fid.close()
    except Exception as my_err:
        my_fid.close()
        raise my_err

def write_array(my_fid, in_struct, num_dimensions, field_names, data_format):
    num_fields = len(field_names)
    true_dims = in_struct['dims'][::-1]
    total_size = np.prod(true_dims)

    for a in range(num_dimensions):
        my_fid.write(struct.pack('>I', true_dims[a]))

    for a in range(total_size):
        for b in range(num_fields):
            field_data = in_struct[field_names[b]][a]
            if data_format[b] == '>d':
                my_fid.write(struct.pack(data_format[b], field_data))
            elif data_format[b] == 'str':
                out_strlen = len(field_data)
                my_fid.write(struct.pack('>I', out_strlen))
                my_fid.write(field_data.encode('UTF-8'))
            elif data_format[b] == 'B':
                my_fid.write(struct.pack('B', field_data))

# You'll need to define lv_seq_clear_disabled and lv_seq_sort functions if they are not already defined elsewhere.



def read_array(my_fid, num_dimensions, in_format):
        num_fields = len(in_format)

        temp_dims = np.zeros(num_dimensions, dtype=np.dtype('>u4'))
        for a in range(num_dimensions):
            temp_dims[a] = np.fromfile(my_fid, dtype=np.dtype('>u4'), count=1, sep="")[0]

        total_size = np.prod(temp_dims)
        arg_dims = temp_dims
        if len(arg_dims) == 1:
            arg_dims = [int(arg_dims), 1]

        out_struct = {}
        for b in range(num_fields):
            field_name = in_format[b][0]
            field_type = in_format[b][1]
            if field_type == 'pstr':
                out_struct[field_name] = np.empty(arg_dims, dtype=object)
            else:
                out_struct[field_name] = np.zeros(arg_dims, dtype=np.dtype('>f8') if field_type == 'float64' else np.dtype('>u4'))

        for a in range(arg_dims[0]):
            for b in range(arg_dims[1]):
                for c in range(num_fields):
                    field_name = in_format[c][0]
                    field_type = in_format[c][1]
                    if field_type == 'pstr':
                        in_strlen = np.fromfile(my_fid, dtype=np.dtype('>u4'), count=1, sep="")[0]
                        my_str = np.fromfile(my_fid, dtype=np.dtype('>u1'), count=in_strlen, sep="").tobytes().decode('utf-8')
                        out_struct[field_name][a, b] = my_str
                    else:
                        out_struct[field_name][a, b] = np.fromfile(my_fid, dtype=field_type, count=1, sep="")[0]

        out_struct['dims'] = np.flip(arg_dims)
        for b in range(num_fields):
            field_name = in_format[b][0]
            out_struct[field_name] = np.reshape(out_struct[field_name], out_struct['dims'])

        return out_struct










# Test code for lv_seq_read
if __name__ == "__main__":
    # Test 1
    my_file_name = "/Users/henry/Library/CloudStorage/GoogleDrive-henry.ando@gmail.com/My Drive/Chinlab/Code/labview/testdata/202305190000"
    my_struct = seq_read(my_file_name)
    print(my_struct)



