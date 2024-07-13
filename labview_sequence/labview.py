import numpy as np
import time
import os
import struct
from dataclasses import dataclass, asdict
import pandas as pd

@dataclass
class LabviewSeq:
    version: int 
    timing: int = 0
    primary_analog: dict = None
    digital: dict = None
    proc_details: dict = None
    procedures: dict = None
    ramp_params: dict = None
    secondary_analog: dict = None
    never_ramp: bool = False
    always_ramp: bool = False
    channels: list = []


def seq_read(in_file_name):
    """Reads a LabVIEW sequence file and returns an LabviewSeq data class with the sequence information.
    This code is nearly identical to the MATLAB version.
    
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
    seq : LabviewSeq
        An LabviewSeq data class with the sequence information.

    LabviewSeq has the following attributes:

    seq.version : int
    seq.timing : int
    seq.primary_analog : dict
    seq.digital : dict
    seq.proc_details : dict
    seq.procedures : dict
    seq.ramp_params : dict
    seq.secondary_analog : dict
    seq.never_ramp : bool
    seq.always_ramp : bool
    
    Raises
    ------  
    Exception
        If the file cannot be read, an exception is raised.

    Notes
    -----
    The LabVIEW sequence file is a binary file. The file is read in as a binary file and the data is parsed into a
    data class. The data class is returned.

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
    with open(my_file_name, 'rb') as fid:

        # Read the version number
        # version = np.fromfile(fid, dtype=np.dtype('>i4'), count=1, sep="")[0]
        version = read_single(fid, 'int32')

        # If the version number is negative, read the timing information.
        if version < 0:
            seq = LabviewSeq(version=-version)
            seq.timing = read_single(fid, 'uint32')
        else:
            seq = LabviewSeq(timing=version, version=3)
        
        seq.primary_analog = read_array(fid, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])
        seq.digital = read_array(fid, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])
        seq.proc_details = read_array(fid, 2, [
            ['time', 'float64'],
            ['voltage', 'float64'],
            ['channel_no', 'uint16'],
            ['enabled', 'uint8'],
            ['ramp_res', 'int16']])
        seq.procedures = read_array(fid, 1, [
            ['enabled', 'uint8'],
            ['name', 'str'],
            ['time', 'float64']])
        

        # read the ramping params
        seq.ramp_params = {}
        seq.ramp_params['num'] = read_single(fid, 'uint32')

        raw_ramps = np.array([read_single(fid, 'float64') for i in range(4 * seq.ramp_params['num'])])
        seq.ramp_params['cur_val'] = raw_ramps[0::4]
        seq.ramp_params['start_val'] = raw_ramps[1::4]
        seq.ramp_params['end_val'] = raw_ramps[2::4]
        seq.ramp_params['incr_val'] = raw_ramps[3::4]
        seq.ramp_params['ramp_every'] = np.ones(seq.ramp_params['end_val'].shape)
        seq.ramp_params['next_ramp'] = np.zeros(seq.ramp_params['end_val'].shape)


        # read secondary analog
        seq.secondary_analog = read_array(fid, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])

        # read the ramping control group
        check_num = read_single(fid, 'uint32')
        
        raw_ramps = np.array([read_single(fid, 'int32') for i in range(2 * check_num)])
        raw_ramps = np.reshape(raw_ramps, (2, check_num))
        seq.ramp_params['ramp_every'][:check_num] = raw_ramps[0::2]
        seq.ramp_params['next_ramp'][:check_num] = raw_ramps[1::2]

        # read "always ramp"
        seq.always_ramp = bool(read_single(fid, 'uint8'))

        # read "never ramp"
        seq.never_ramp = bool(read_single(fid, 'uint8'))

    return seq


def seq_write(seq: LabviewSeq, in_target):
    """Writes a LabVIEW sequence file from an LabviewSeq data class with the sequence information. This code 
    is nearly identical to the MATLAB version.

    Parameters
    ----------
    in_target : str
        The file name of the LabVIEW sequence file to be written. The file name is assumed to be the full path to the
        file.

    seq : LabviewSeq
        An LabviewSeq data class with the sequence information.

    LabviewSeq has the following attributes:

    seq.version : int
    seq.timing : int
    seq.primary_analog : dict
    seq.digital : dict
    seq.proc_details : dict
    seq.procedures : dict
    seq.ramp_params : dict
    seq.secondary_analog : dict
    seq.never_ramp : bool
    seq.always_ramp : bool

    Raises
    ------
    Exception
        If the file cannot be written, an exception is raised.

    Notes
    -----
    The LabVIEW sequence file is a binary file. The file is written as a binary file and the data is parsed from an
    LabviewSeq data class. The data class is passed as an argument.
    
    """

    with open(in_target, 'wb') as fid:

        # Write the version header
        if seq.version >= 4:
            fid.write(struct.pack('>i', -seq.version))

        # Write the timing header
        fid.write(struct.pack('>I', seq.timing))

        write_array(fid, seq.primary_analog, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])
        write_array(fid, seq.digital, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])
        write_array(fid, seq.proc_details, 2, [
            ['time', 'float64'],
            ['voltage', 'float64'],
            ['channel_no', 'uint16'],
            ['enabled', 'uint8'],
            ['ramp_res', 'int16']])
        write_array(fid, seq.procedures, 1, [
            ['enabled', 'uint8'],
            ['name', 'str'],
            ['time', 'float64']])

        # Write the ramping parameters
        write_single(fid, 'uint32', seq.ramp_params['num'])

        raw_ramps = np.zeros((4 * seq.ramp_params['num']), dtype=np.float64)
        raw_ramps[0::4] = seq.ramp_params['cur_val']
        raw_ramps[1::4] = seq.ramp_params['start_val']
        raw_ramps[2::4] = seq.ramp_params['end_val']
        raw_ramps[3::4] = seq.ramp_params['incr_val']

        for r in raw_ramps:
            write_single(fid, 'float64', r)

        # Write the secondary analog group
        write_array(fid, seq.secondary_analog, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])

        # Write the ramping control group
        write_single(fid, 'uint32', seq.ramp_params['num'])

        raw_ramps = np.zeros((2 * seq.ramp_params['num']), dtype=int)
        raw_ramps[0::2] = seq.ramp_params['ramp_every']
        raw_ramps[1::2] = seq.ramp_params['next_ramp']

        for r in raw_ramps:
            write_single(fid, 'int32', r)

        # Write the "always ramp"
        write_single(fid, 'uint8', seq.always_ramp)

        # Write the "never ramp"
        write_single(fid, 'uint8', seq.never_ramp)


def read_array(fid, num_dimensions, format):
    """
    Reads a single array from the LabVIEW sequence file format. This code is nearly identical to the MATLAB version.

    Parameters
    ----------
    fid : file
        The file object to read from.

    num_dimensions : int
        The number of dimensions of the array. 

    format : list
        A list of tuples with the field names and data types of the array. The tuples should have the following
        format: (field_name, data_type). The data types should be one of the following: 'str', 'float64', 'int8',
        'uint8', 'int16', 'uint16', 'int32', 'uint32'.

    Returns
    -------
    arr : dict
        A dictionary with the array information. The dictionary has the following keys:

    arr['dims'] : np.ndarray
        The dimensions of the array.

    arr[field_name] : np.ndarray
        The data of the array.

    Notes
    -----   
    The LabVIEW sequence file is a binary file. The file is read in as a binary file and the data is parsed into a
    dictionary. The dictionary is returned.
    
    """
    
    num_fields = len(format)

    # Read the dimensions of the array
    dims = np.ones(num_dimensions, dtype=int)
    for a in range(num_dimensions):
        dims[a] = read_single(fid, 'uint32')

    # Initialize the output array
    arr = {}
    arr['save_dims'] = dims

    # Remove singleton dimensions
    if min(dims) == 1:
        dims = [max(dims)]

    # Initialize arrays
    for b in range(num_fields):
        field_name = format[b][0]
        field_type = format[b][1]
        match field_type:
            case 'str':
                arr[field_name] = np.empty(dims, dtype=object)
            case 'float64':
                arr[field_name] = np.zeros(dims)
            case _:
                arr[field_name] = np.zeros(dims, dtype=int)
    
    # Read the data
    for ind in np.ndindex(tuple(dims)):
        for c in range(num_fields):
            field_name = format[c][0]
            field_type = format[c][1]
            arr[field_name][ind] = read_single(fid, field_type)


    # Reshape 2d arrays
    if len(dims) == 2:
        dims = np.flip(dims)
        for b in range(num_fields):
            field_name = format[b][0]
            arr[field_name] = np.transpose(arr[field_name])
    
    arr['dims'] = dims

    return arr


def write_array(fid, savearr, num_dimensions, format):
    """
    Writes a single array to the LabVIEW sequence file format. This code is nearly identical to the MATLAB version.

    Parameters
    ----------
    fid : file   
        The file object to write to.

    arr : dict

    num_dimensions : int
        The number of dimensions of the array.

    format : list
        A list of 2-part tuples, containing the field name and the data format. The data formats should be one of the
        following: 'str', 'float64', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32'.
    

    Notes
    -----
    The LabVIEW sequence file is a binary file. The file is written as a binary file and the data is parsed from a
    dictionary. The dictionary is passed as an argument.

    """
    arr = savearr.copy()
    num_fields = len(format)
    dims = arr['dims']
    save_dims = arr['save_dims']

    # Reshape 2d arrays
    if len(dims) == 2:
        dims = np.flip(dims)
        for b in range(num_fields):
            field_name = format[b][0]
            arr[field_name] = np.transpose(arr[field_name])

    # Write the dimensions of the array
    for a in range(num_dimensions):
        write_single(fid, 'uint32', save_dims[a])

    # Write the data
    for ind in np.ndindex(tuple(dims)):
        for b in range(num_fields):
            data = arr[format[b][0]][ind]
            fmt = format[b][1]
            write_single(fid, fmt, data)


def read_single(fid, type):
    """
    Reads a single value from the file 'fid' in the format 'type'.
    """
    match type:
        case 'int8':
            return struct.unpack('>b', fid.read(1))[0]
        case 'uint8':
            return struct.unpack('>B', fid.read(1))[0]
        case 'int16':
            return struct.unpack('>h', fid.read(2))[0]
        case 'uint16':
            return struct.unpack('>H', fid.read(2))[0]
        case 'int32':
            return struct.unpack('>i', fid.read(4))[0]
        case 'uint32':
            return struct.unpack('>I', fid.read(4))[0]
        case 'float64':
            return struct.unpack('>d', fid.read(8))[0]
        case 'str':
            strlen = int(struct.unpack('>I', fid.read(4))[0])
            return np.fromfile(fid, dtype=np.dtype('>u1'), count=strlen, sep="").tobytes().decode('utf-8')


def write_single(fid, type, data):
    """
    Writes 'data' to the file 'fid' in the format 'type'.
    """
    match type:
        case 'int8':
            fid.write(struct.pack('>b', data))
        case 'uint8':
            fid.write(struct.pack('>B', data))
        case 'int16':
            fid.write(struct.pack('>h', data))
        case 'uint16':
            fid.write(struct.pack('>H', data))
        case 'int32':
            fid.write(struct.pack('>i', data))
        case 'uint32':
            fid.write(struct.pack('>I', data))
        case 'float64':
            fid.write(struct.pack('>d', data))
        case 'str':
            fid.write(struct.pack('>I', len(data)))
            darr = data.encode('UTF-8')
            for d in darr:
                fid.write(struct.pack('>b', d))
            

def get_channel_info(seq: LabviewSeq, which_channel):
    """
    Returns a string with a report about the given channel.

    Parameters
    ----------
    seq : LabviewSeq

    which_channel : str or int or list
        The channel number or name to be reported. If 'all' is passed, all channels are reported. If a list of channel
        numbers or names is passed, only those channels are reported.

    Returns
    -------
    outstr : str
        A string with the report about the channel.

    """

    # Get the channel numbers to be reported
    if isinstance(which_channel, str):
        if which_channel == 'all':
            channels = list(range(len(seq.primary_analog['name']) 
                                  + len(seq.digital['name']) 
                                  + len(seq.secondary_analog['name'])))
        else:
            channels = get_channels_by_name(seq, which_channel)
    else:
        channels = which_channel
    
    # Initialize the channel info dictionary
    channel_info = {'channel_no': channels, 'events': channels} 
    for c in range(len(channels)):
        channel_info['events'][c] = pd.DataFrame(
            columns=['proc_enabled', 'enabled', 'global_time', 'ramp_res', 'voltage', 'proc_name'])

    # Populate the channel info dictionary
    for a in range(len(seq.proc_details['channel_no'])):
        proc_enabled = seq.procedures['enabled'][a]
        proc_name = seq.procedures['name'][a]

        for b in range(len(seq.proc_details['channel_no'][a])):
            for c in range(len(channels)):
                if seq.proc_details['channel_no'][a, b] == channels[c]:
                    channel_info[c]['proc_enabled'].append(proc_enabled)
                    channel_info[c]['enabled'].append(seq.proc_details['enabled'][a, b])
                    channel_info[c]['global_time'].append(
                        var_lookup(seq.ramp_params, seq.proc_details['time'][a, b]) +
                        var_lookup(seq.ramp_params, seq.procedures['time'][a]))
                    channel_info[c]['ramp_res'].append(seq.proc_details['ramp_res'][a, b])
                    channel_info[c]['voltage'].append(
                        var_lookup(seq.ramp_params, seq.proc_details['voltage'][a, b]))
                    channel_info[c]['proc_name'].append(proc_name)

    # Sort the times
    ordered_times = sorted(range(len(channel_info[c]['global_time'])), key=lambda d: channel_info[c]['global_time'][d])
    

    return channel_info



def channel_report(seq: LabviewSeq, channel_info: list):
    """
    Returns a string with a report about the given channel. Channel info can be obtained using the get_channel_info
    function.

    Parameters
    ----------
    seq : LabviewSeq

    channel_info : list of dicts 

    The dicts have the following keys:

    channel_info[c]['chan_no'] : int

    channel_info[c]['proc_enabled'] : list of bool

    channel_info[c]['enabled'] : list of bool

    channel_info[c]['global_time'] : list of float

    channel_info[c]['ramp_res'] : list of int

    channel_info[c]['voltage'] : list of float

    channel_info[c]['proc_name'] : list of str


    Returns
    -------
    outstr : str
        A string with the report about the channel.

    """

    # Create the output string
    outstr  = 'ch no  name                         init val  analog  used  enabled  proc enabled\n'
    outstr += '-----  ---------------------------  --------  ------  ----  -------  ------------\n'
    
    # Populate the channel info dictionary
    for c in range(len(channel_info)):
        this_chan = get_channel_by_no(seq, channel_info[c]['chan_no'])
        outstr += f'{this_chan["chan_no"]:03d}    '
        outstr += f'{this_chan["name"][:24]:<27s}  '
        outstr += f'{this_chan["ival"]:<8.4f}  '
        outstr += f'{this_chan["is_analog"]:<6d}  '
        outstr += f'{len(channel_info[c]["enabled"]) > 0:<4d}  '
        outstr += f'{any(channel_info[c]["enabled"]):<7d}  '
        outstr += f'{any([a*b for a, b in zip(channel_info[c]["enabled"], channel_info[c]["proc_enabled"])])}\n\n'
    
    # Create the output string
    for c in range(len(channel_info)):
        this_chan = get_channel_by_no(seq, channel_info[c]['chan_no'])
        outstr += 'global time  pr enbl  enabled  voltage  ramp    proc name\n'
        outstr += '-----------  -------  -------  -------  ------  ---------\n'
        
        # Sort the times
        ordered_times = sorted(range(len(channel_info[c]['global_time'])), key=lambda d: channel_info[c]['global_time'][d])
        for d in ordered_times:
            if (channel_info[c]['proc_enabled'][d] and channel_info[c]['enabled'][d]):
                outstr += f'{channel_info[c]["global_time"][d]:10.4f}'
                outstr += f'{channel_info[c]["proc_enabled"][d]:4}'
                outstr += f'{channel_info[c]["enabled"][d]:9d}'
                outstr += f'{channel_info[c]["voltage"][d]:15.4f}\t'
                outstr += {
                    0: 'JUMP    ',
                    1: 'FINE    ',
                    2: 'COARSE  ',
                }.get(channel_info[c]['ramp_res'][d], '??????  ')
                outstr += f'{channel_info[c]["proc_name"][d]}\n'

    outstr += '\n'

    return outstr



def var_lookup(ramp_params, in_val):
    """
    Looks up a value in the ramping parameters, or returns the input value if it is not in the ramping parameters.
    """

    if in_val <= 65499.6:
        out_val = in_val
    else:
        index = round(in_val - 65500)
        out_val = ramp_params['cur_val'][index]
    
    return out_val


def get_channels_by_name(seq: LabviewSeq, channel_name):
    """

    Parameters
    ----------
    seq : LabviewSeq
        An LabviewSeq data class with the sequence information.

    channel_name : str
        The name of the channel to be found.

    Returns
    -------
    out_chan_nos : list
        A list of the channel numbers that match the channel name.

    """
    out_chan_nos = []

    groups = [seq.primary_analog, seq.digital, seq.secondary_analog]

    if seq.version < 4:
        chan_offset = [0, 16, 46]
    else:
        chan_offset = [0, 24, 86]

    for a in range(3):
        for b in range(groups[a]['dims'][0]):
            if channel_name.upper() in groups[a]['name'][b].upper():
                out_chan_nos.append(b + chan_offset[a])

    return out_chan_nos


def get_channel_by_no(seq: LabviewSeq, in_channel_no):
    """
    Returns a dictionary with the information about a single channel.

    Parameters
    ----------
    seq : LabviewSeq
    in_channel_no : int

    Returns
    -------
    info : dict
        A dictionary with the information about the channel. The dictionary has the following keys:
    
    info['chan_no'] : int

    info['name'] : str
    
    info['is_analog'] : bool
    
    info['ival'] : float   

    """
    info = {'chan_no': in_channel_no}

    if seq.version < 4:
        if in_channel_no < 16:
            # primary analog group
            info['ival'] = seq.primary_analog['ival'][in_channel_no]
            info['name'] = seq.primary_analog['name'][in_channel_no]
            info['is_analog'] = seq.primary_analog['is_analog'][in_channel_no]
        elif in_channel_no < 46:
            # digital group
            info['ival'] = seq.digital['ival'][in_channel_no - 16]
            info['name'] = seq.digital['name'][in_channel_no - 16]
            info['is_analog'] = seq.digital['is_analog'][in_channel_no - 16]
        else:
            # secondary analog group
            info['ival'] = seq.secondary_analog['ival'][in_channel_no - 46]
            info['name'] = seq.secondary_analog['name'][in_channel_no - 46]
            info['is_analog'] = seq.secondary_analog['is_analog'][in_channel_no - 46]
    else:
        if in_channel_no < 24:
            # primary analog group
            info['ival'] = seq.primary_analog['ival'][in_channel_no]
            info['name'] = seq.primary_analog['name'][in_channel_no]
            info['is_analog'] = seq.primary_analog['is_analog'][in_channel_no]
        elif in_channel_no < 86:
            # digital group
            info['ival'] = seq.digital['ival'][in_channel_no - 24]
            info['name'] = seq.digital['name'][in_channel_no - 24]
            info['is_analog'] = seq.digital['is_analog'][in_channel_no - 24]
        else:
            # secondary analog group
            info['ival'] = seq.secondary_analog['ival'][in_channel_no - 86]
            info['name'] = seq.secondary_analog['name'][in_channel_no - 86]
            info['is_analog'] = seq.secondary_analog['is_analog'][in_channel_no - 86]

    return info



# Test code for the module
if __name__ == "__main__":
    # Test 1: Read a test file
    script_dir = os.path.dirname(__file__) 
    rel_path = "testdata/202305190000"
    test_file = os.path.join(script_dir, rel_path)
    test_seq = seq_read(test_file)

    # Test 2: Write that data to a new file
    rel_path = "testdata/test_write"
    test_file = os.path.join(script_dir, rel_path)
    seq_write(test_seq, test_file)
    test_seq2 = seq_read(test_file)
    # print(test_seq2)

    # Test 3: Channel report
    # print(test_seq.proc_details['dims'])
    # print(test_seq.proc_details['channel_no'])
    print(channel_report(test_seq2, '3.0'))
