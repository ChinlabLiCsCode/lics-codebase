import numpy as np
import time
import os
import struct
from dataclasses import dataclass, field

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
    channels: list = field(default_factory=list)


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
            

def channel_report(in_seq: LabviewSeq, which_channel, out_file=None, *,
                   details=None, on_only=True, proc_on_only=True) -> str:
    """Channel report for one or more channels. Matches lv_seq_channel_report.m.

    Parameters
    ----------
    in_seq : LabviewSeq
    which_channel : str or list of int
        'all', a name substring, or a list of channel numbers.
    out_file : str or None
        Output file path. If None, returns content as a string.
    details : bool or None
        Per-channel event table. Defaults to True unless which_channel='all'.
    on_only : bool, default True
        In the detail table, skip events where the event itself is disabled.
    proc_on_only : bool, default True
        In the detail table, skip events where the parent procedure is disabled.

    Returns
    -------
    str
        File path if out_file was given; content string if out_file is None.
    """
    # Resolve channels
    if isinstance(which_channel, str) and which_channel.upper() == 'ALL':
        num_channels = (len(in_seq.primary_analog['name']) +
                        len(in_seq.digital['name']) +
                        len(in_seq.secondary_analog['name']))
        channels = list(range(num_channels))
        default_details = False
    elif isinstance(which_channel, str):
        channels = get_channels_by_name(in_seq, which_channel)
        default_details = True
    else:
        channels = list(which_channel)
        default_details = True

    if details is None:
        details = default_details

    # Collect per-channel event lists
    ch_info = [{'proc_enabled': [], 'enabled': [], 'global_time': [],
                 'ramp_res': [], 'voltage': [], 'proc_name': []}
               for _ in channels]

    num_procs = in_seq.proc_details['dims'][0]
    num_events = in_seq.proc_details['dims'][1]

    for a in range(num_procs):
        proc_enabled = int(in_seq.procedures['enabled'][a])
        proc_name = in_seq.procedures['name'][a]
        proc_t = var_lookup(in_seq.ramp_params, in_seq.procedures['time'][a])
        for b in range(num_events):
            ch_no = int(in_seq.proc_details['channel_no'][a, b])
            for c, chan in enumerate(channels):
                if ch_no == chan:
                    t = var_lookup(in_seq.ramp_params, in_seq.proc_details['time'][a, b])
                    ch_info[c]['proc_enabled'].append(proc_enabled)
                    ch_info[c]['enabled'].append(int(in_seq.proc_details['enabled'][a, b]))
                    ch_info[c]['global_time'].append(t + proc_t)
                    ch_info[c]['ramp_res'].append(int(in_seq.proc_details['ramp_res'][a, b]))
                    ch_info[c]['voltage'].append(
                        var_lookup(in_seq.ramp_params, in_seq.proc_details['voltage'][a, b]))
                    ch_info[c]['proc_name'].append(proc_name)

    ramp_labels = {0: 'JUMP', 1: 'FINE', 2: 'COARSE'}
    out = []

    # Summary table
    out.append('ch no\tname\t\t\t\t\t\t  init val\tanalog?\t\tused  enabled\tproc enabled\n')
    out.append('-----\t----\t\t\t\t\t\t  --------\t-------\t\t----  -------\t------------\n')
    for c, chan in enumerate(channels):
        ch = get_channel_by_no(in_seq, chan)
        en = ch_info[c]['enabled']
        pe = ch_info[c]['proc_enabled']
        used = int(len(en) > 0)
        any_en = int(any(en))
        any_proc_en = int(any(e * p for e, p in zip(en, pe)))
        out.append(
            f"{ch['chan_no']:03d}\t\t{ch['name'][:24]:<24}\t{ch['ival']:10.4f}\t\t"
            f"{int(ch['is_analog'])}\t\t{used}\t\t{any_en}\t\t{any_proc_en}\n"
        )

    # Per-channel detail tables
    if details:
        for c, chan in enumerate(channels):
            ch = get_channel_by_no(in_seq, chan)
            out.append(f'\nchannel {ch["chan_no"]:03d}: {ch["name"]}\n\n')
            out.append('global time\tpr enbl\tenabled\t\tvoltage\tramp\tproc name\n')
            out.append('-----------\t-------\t-------\t\t-------\t----\t---------\n')
            order = sorted(range(len(ch_info[c]['global_time'])),
                           key=lambda d: ch_info[c]['global_time'][d])
            for d in order:
                pe_d = ch_info[c]['proc_enabled'][d]
                en_d = ch_info[c]['enabled'][d]
                if (pe_d and en_d) or (not proc_on_only and en_d) or (not proc_on_only and not on_only):
                    ramp_str = ramp_labels.get(ch_info[c]['ramp_res'][d], '????')
                    out.append(
                        f"{ch_info[c]['global_time'][d]:10.4f}\t\t"
                        f"{pe_d}\t\t"
                        f"{en_d}\t"
                        f"{ch_info[c]['voltage'][d]:10.4f}\t"
                        f"{ramp_str}\t"
                        f"{ch_info[c]['proc_name'][d]}\n"
                    )

    content = ''.join(out)

    if out_file is None:
        return content

    with open(out_file, 'w') as f:
        f.write(content)
    return out_file



def seq_dump(in_seq: LabviewSeq, in_target: str = None, *, sort: bool = True,
             show_disabled: bool = False, seperate_disabled: bool = False) -> str:
    """Dumps the sequence to a human-readable text format. Matches lv_seq_dump.m.

    Parameters
    ----------
    in_seq : LabviewSeq
    in_target : str, optional
        Output file path. If None, returns content as a string instead of writing.
    sort : bool, default True
        Sort events by time within each procedure.
    show_disabled : bool, default False
        Include disabled events inline with enabled events.
    seperate_disabled : bool, default False
        Append disabled events in a separate block after enabled ones.
        Forced to False when show_disabled=True (matches MATLAB behaviour).

    Returns
    -------
    str
        File path if in_target was given; content string if in_target is None.
    """
    if show_disabled:
        seperate_disabled = False

    out = []

    # Header
    out.append('header\n------\n')
    out.append(f'version:{in_seq.version}\n')
    out.append(f'timing:{in_seq.timing}\nnever ramp:{int(in_seq.never_ramp)}\nalways_ramp:{int(in_seq.always_ramp)}\n')

    num_channels = (len(in_seq.primary_analog['name']) +
                    len(in_seq.digital['name']) +
                    len(in_seq.secondary_analog['name']))
    out.append(f'number of channels:{num_channels}\n')

    num_procs = len(in_seq.procedures['name'])
    out.append(f'number of procedures:{num_procs}\n')

    # Channel table
    out.append('\nch no\tname\t\t\t\t\t\t  init val\tanalog?\n'
               '-----\t----\t\t\t\t\t\t  --------\t-------\n')
    for a in range(num_channels):
        ch = get_channel_by_no(in_seq, a)
        out.append(f"{a:03d}\t\t{ch['name'][:24]:<24}\t{ch['ival']:10.4f}\t\t{int(ch['is_analog'])}\n")

    # Procedure table
    out.append('\nproc no\tname\t\t\t\t\t\t\t  time\t\tenabled\n'
               '-------\t----\t\t\t\t\t\t\t  ----\t\t------\n')
    for a in range(num_procs):
        out.append(
            f"{a:03d}\t\t{in_seq.procedures['name'][a][:24]:<24}\t"
            f"{in_seq.procedures['time'][a]:10.4f}\t\t{int(in_seq.procedures['enabled'][a])}\n"
        )

    # Per-procedure event listings
    ramp_labels = {0: 'JUMP', 1: 'FINE', 2: 'COARSE'}
    num_events = in_seq.proc_details['dims'][1]

    for a in range(num_procs):
        out.append(f'\nprocedure {a:03d}: {in_seq.procedures["name"][a]}\n')
        out.append('\nenabled\t\ttime\tchannel\t\t\t\t\t\t   voltage\tramp\n'
                   '------\t\t----\t-------\t\t\t\t\t\t   -------\t----\n')

        if sort:
            order = np.argsort(in_seq.proc_details['time'][a, :], kind='stable')
        else:
            order = np.arange(num_events)

        for b in range(num_events):
            idx = order[b]
            if show_disabled or in_seq.proc_details['enabled'][a, idx]:
                ch = get_channel_by_no(in_seq, int(in_seq.proc_details['channel_no'][a, idx]))
                ramp_str = ramp_labels.get(int(in_seq.proc_details['ramp_res'][a, idx]), '????')
                out.append(
                    f"{int(in_seq.proc_details['enabled'][a, idx])}\t\t"
                    f"{in_seq.proc_details['time'][a, idx]:10.4f}\t"
                    f"{ch['name'][:24]:<24}\t"
                    f"{in_seq.proc_details['voltage'][a, idx]:10.6f}\t"
                    f"{ramp_str}\n"
                )

        if seperate_disabled:
            for b in range(num_events):
                idx = order[b]
                if not in_seq.proc_details['enabled'][a, idx]:
                    ch = get_channel_by_no(in_seq, int(in_seq.proc_details['channel_no'][a, idx]))
                    ramp_str = ramp_labels.get(int(in_seq.proc_details['ramp_res'][a, idx]), '????')
                    # Note: voltage uses %10.4f here (matches lv_seq_dump.m line 87, differs from main loop)
                    out.append(
                        f"{int(in_seq.proc_details['enabled'][a, idx])}\t\t"
                        f"{in_seq.proc_details['time'][a, idx]:10.4f}\t"
                        f"{ch['name'][:24]:<24}\t"
                        f"{in_seq.proc_details['voltage'][a, idx]:10.4f}\t"
                        f"{ramp_str}\n"
                    )

    # Ramp params table
    out.append('\ncode\t   cur val\t\tstart\t\tstop\t\tstep\tevery\t next\n'
               '----\t   -------\t\t-----\t\t----\t\t----\t-----\t ----\n')
    for a in range(in_seq.ramp_params['num']):
        out.append(
            f"{65500 + a:05d}\t"
            f"{in_seq.ramp_params['cur_val'][a]:10.4f}\t"
            f"{in_seq.ramp_params['start_val'][a]:10.4f}\t"
            f"{in_seq.ramp_params['end_val'][a]:10.4f}\t"
            f"{in_seq.ramp_params['incr_val'][a]:10.4f}\t\t"
            f"{int(in_seq.ramp_params['ramp_every'][a])}\t\t"
            f"{int(in_seq.ramp_params['next_ramp'][a])}\n"
        )

    content = ''.join(out)

    if in_target is None:
        return content

    with open(in_target, 'w') as f:
        f.write(content)
    return in_target


def seq_quickdump(date, num, out_path=None, **dump_kwargs) -> str:
    """Read a sequence by date/num and write a text dump. Matches lv_seq_quickdump.m.

    Parameters
    ----------
    date : sequence of int [year, month, day]
    num : int
        Sequence number.
    out_path : str or None
        Output file path. If None, uses local_path('lvseqdump', ...) from local_paths.py.
        Pass None and let seq_dump return a string by passing out_path=None after resolution
        isn't the intent here — if you want a string, use seq_dump directly.

    Returns
    -------
    str
        Path written to (or content string if out_path resolves to None via seq_dump).
    """
    import sys as _sys
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in _sys.path:
        _sys.path.insert(0, _repo_root)
    from local_paths import local_path

    year, month, day = int(date[0]), int(date[1]), int(date[2])
    seq_path = local_path('lvseqread', year=year, month=month, day=day, num=num)
    seq = seq_read(seq_path)
    if out_path is None:
        out_path = local_path('lvseqdump', year=year, month=month, day=day, num=num)
    return seq_dump(seq, out_path, **dump_kwargs)


def seq_quickreport(date, num, which_channel, out_file=None, **kwargs) -> str:
    """Read a sequence by date/num and write a channel report. Matches lv_seq_quickreport.m.

    Parameters
    ----------
    date : sequence of int [year, month, day]
    num : int
    which_channel : str or list of int
        Passed directly to channel_report.
    out_file : str or None
        Output file path. If None, returns content as a string.

    Returns
    -------
    str
        File path if out_file was given; content string if out_file is None.
    """
    import sys as _sys
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in _sys.path:
        _sys.path.insert(0, _repo_root)
    from local_paths import local_path

    year, month, day = int(date[0]), int(date[1]), int(date[2])
    seq_path = local_path('lvseqread', year=year, month=month, day=day, num=num)
    return channel_report(seq_read(seq_path), which_channel, out_file, **kwargs)


def quick_convert(date, num, out_path=None) -> str:
    """Read a sequence by date/num and convert it to a labscript Python file.

    Parameters
    ----------
    date : sequence of int [year, month, day]
    num : int
        Sequence number.
    out_path : str or None
        Output file path. If None, uses local_path('lvconvert', ...) from local_paths.py.

    Returns
    -------
    str
        Path of the written labscript file.
    """
    import sys as _sys
    _repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _repo_root not in _sys.path:
        _sys.path.insert(0, _repo_root)
    from local_paths import local_path

    year, month, day = int(date[0]), int(date[1]), int(date[2])
    seq_path = local_path('lvseqread', year=year, month=month, day=day, num=num)
    seq = seq_read(seq_path)
    if out_path is None:
        out_path = local_path('lvconvert', year=year, month=month, day=day, num=num)
    return labview_labscript_convert(seq, out_path)


def seq_block_write(in_seq: LabviewSeq, in_proc_no: int, times, time_offsets,
                    channel_nos, voltages, ramp_res) -> LabviewSeq:
    """Write a repeated block of events into a procedure. Matches lv_seq_block_write.m.

    Sorts the sequence, finds the last enabled event in in_proc_no, then appends
    len(times) repetitions of the channel block immediately after it.

    Parameters
    ----------
    in_seq : LabviewSeq
    in_proc_no : int
        0-indexed procedure number (MATLAB version is 1-indexed).
    times : sequence of float
        Base times for each repetition.
    time_offsets : sequence of float
        Per-channel time offsets within each repetition.
    channel_nos : sequence of str
        Channel name substrings; the first matching channel is used for each.
    voltages : sequence of float
        Per-channel voltages.
    ramp_res : sequence of int
        Per-channel ramp resolution values.

    Returns
    -------
    LabviewSeq
        New sequence with in_proc_no's proc_details updated; in_seq is not modified.
    """
    import copy
    sort_seq = seq_sort(copy.deepcopy(in_seq))

    proc_len = sort_seq.proc_details['dims'][1]
    repeat_len = len(time_offsets)

    real_channel_nos = [get_channels_by_name(in_seq, name)[0] for name in channel_nos]

    # max_val: 1-based index of last enabled event (0 if no enabled events).
    # Conveniently equals the 0-based insertion start index.
    indices = np.arange(1, proc_len + 1)
    max_val = int(np.max(sort_seq.proc_details['enabled'][in_proc_no, :] * indices))

    for a in range(len(times)):
        if max_val + (a + 1) * repeat_len > proc_len:
            break
        for b in range(repeat_len):
            idx = max_val + a * repeat_len + b
            sort_seq.proc_details['enabled'][in_proc_no, idx] = 1
            sort_seq.proc_details['time'][in_proc_no, idx] = times[a] + time_offsets[b]
            sort_seq.proc_details['channel_no'][in_proc_no, idx] = real_channel_nos[b]
            sort_seq.proc_details['ramp_res'][in_proc_no, idx] = ramp_res[b]
            sort_seq.proc_details['voltage'][in_proc_no, idx] = voltages[b]

    out_seq = copy.deepcopy(in_seq)
    for field in ('enabled', 'time', 'ramp_res', 'channel_no', 'voltage'):
        out_seq.proc_details[field][in_proc_no, :] = sort_seq.proc_details[field][in_proc_no, :]
    return out_seq


def seq_clear_disabled(seq: LabviewSeq) -> LabviewSeq:
    """Zero out time/voltage/channel_no/ramp_res for every disabled event. Matches lv_seq_clear_disabled.m."""
    mask = seq.proc_details['enabled'] == 0
    seq.proc_details['time'][mask] = 0
    seq.proc_details['voltage'][mask] = 0
    seq.proc_details['channel_no'][mask] = 0
    seq.proc_details['ramp_res'][mask] = 0
    return seq


def seq_sort(seq: LabviewSeq) -> LabviewSeq:
    """Sorts each procedure's events: ascending by time, with enabled events before disabled on ties.

    Matches lv_seq_sort.m exactly.
    """
    for a in range(seq.proc_details['dims'][0]):
        init_sort_order = np.argsort(seq.proc_details['time'][a, :], kind='stable')
        sort_order = np.argsort(-seq.proc_details['enabled'][a, init_sort_order], kind='stable')
        final_order = init_sort_order[sort_order]
        sorted_enablings = seq.proc_details['enabled'][a, init_sort_order][sort_order]
        seq.proc_details['enabled'][a, :] = sorted_enablings
        seq.proc_details['time'][a, :] = seq.proc_details['time'][a, final_order]
        seq.proc_details['voltage'][a, :] = seq.proc_details['voltage'][a, final_order]
        seq.proc_details['channel_no'][a, :] = seq.proc_details['channel_no'][a, final_order]
        seq.proc_details['ramp_res'][a, :] = seq.proc_details['ramp_res'][a, final_order]
    return seq


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


def labview_labscript_convert(in_seq: LabviewSeq, out_path: str) -> str:
    """Convert a LabVIEW sequence to a labscript Python script.

    Parameters
    ----------
    in_seq : LabviewSeq
    out_path : str
        Output file path for the generated labscript Python file.

    Returns
    -------
    str
        out_path
    """
    import copy, csv, re as _re

    _here = os.path.dirname(os.path.abspath(__file__))
    _repo_root = os.path.dirname(_here)

    # ── Build Full-code → connection-table attribute name from connection_table.py ──
    ct_path = os.path.join(_repo_root, 'lics_labscript_apparatus', 'connection_table.py')
    with open(ct_path) as _f:
        _ct_src = _f.read()
    _full_to_attr = {}  # e.g. 'b1c00' -> 'Bitter_Precision_Disable__b1c00'
    _attr_is_dig = {}   # attr name -> True if DigitalOut, False if AnalogOut/VirtualAnalogOut
    for _m in _re.finditer(r'self\.(\w+)\s*=\s*(Digital|Analog)Out\(', _ct_src):
        _attr = _m.group(1)
        _fm = _re.search(r'(b\d+c\d+)$', _attr)
        if _fm:
            _full_to_attr[_fm.group(1)] = _attr
            _attr_is_dig[_attr] = (_m.group(2) == 'Digital')

    # ── Virtual-channel overrides (section 8a of conversion note) ──
    # OG-prefix → ct attribute name (no __bXcXX suffix)
    _VIRTUAL = {
        '3.0': 'Bitter_V_AH', '3.7': 'Bitter_V_HH',
        '5.13': 'Bias_X_AH', '5.12': 'Bias_X_HH',
        '5.14': 'Bias_Y_AH', '5.15': 'Bias_Y_HH',
        '5.16': 'Bias_Z_AH', '5.17': 'Bias_Z_HH',
    }
    _ZEEMAN_PREFIXES = {'1.31', '1.32'}

    # ── Build OG-prefix → ct attribute name from CSV ──
    csv_path = os.path.join(_here, 'NI_channel_map.csv')
    _og_to_attr = {}  # OG prefix -> ct attr name or None
    with open(csv_path, newline='') as _f:
        for row in csv.DictReader(_f):
            og = row['OG Ch'].strip()
            if not og:
                continue
            fate = row['Fate'].strip()
            full = row['Full'].strip()
            if fate == 'Continued' and full and full in _full_to_attr:
                _og_to_attr[og] = _full_to_attr[full]
            else:
                _og_to_attr[og] = None  # defunct / unneeded / not mapped
    # Apply virtual overrides (override physical mapping)
    _og_to_attr.update(_VIRTUAL)

    def _og_prefix(lv_name):
        return lv_name.split('_', 1)[0]

    def _ct_attr(lv_name):
        """Return ct attribute name for a LabVIEW channel, or None if not mapped."""
        pfx = _og_prefix(lv_name)
        if pfx in _ZEEMAN_PREFIXES:
            return None
        return _og_to_attr.get(pfx)

    def _is_code(v):
        return v >= 65499.6

    def _code_idx(v):
        return int(round(v - 65500))

    def _fmt_v(v):
        """Format a voltage value (possibly a 655xx code) as a Python expression."""
        if _is_code(v):
            return f"code_{65500 + _code_idx(v)}"
        return f"{v:.6g}"

    def _fmt_t_offset(t_ms):
        """Format a time offset (in ms) as a Python expression: t ± Xe-3."""
        if _is_code(t_ms):
            return f"t + code_{65500 + _code_idx(t_ms)}/1e3"
        if t_ms == 0.0:
            return "t"
        elif t_ms > 0:
            return f"t + {t_ms:g}e-3"
        else:
            return f"t - {abs(t_ms):g}e-3"

    def _fmt_proc_t(t_ms):
        """Format a procedure start time (in ms) as a Python expression in seconds."""
        if _is_code(t_ms):
            return f"code_{65500 + _code_idx(t_ms)}/1e3"
        return f"{t_ms:g}e-3"

    def _fmt_dur(dur_ms):
        """Format a ramp duration (in ms) as a Python expression."""
        return f"{dur_ms:g}e-3"

    # ── Sort sequence ──
    sseq = seq_sort(copy.deepcopy(in_seq))
    num_ch = (len(sseq.primary_analog['name']) +
              len(sseq.digital['name']) +
              len(sseq.secondary_analog['name']))
    num_procs = len(sseq.procedures['name'])

    # ── Zeeman initial state from channel init values ──
    _ze = {'1.31': 5.0, '1.32': 5.0}
    for _i in range(num_ch):
        _ch = get_channel_by_no(sseq, _i)
        _p = _og_prefix(_ch['name'])
        if _p in _ze:
            _ze[_p] = float(_ch['ival'])
    _ze_init = dict(_ze)  # snapshot of Zeeman state from channel list ival

    def _zeeman_cmds(t_expr, lp):
        s31, s32 = _ze['1.31'], _ze['1.32']
        lines = []
        if s32 < 2.5:
            vals = [0, 0, 0, 0, 0]
        elif s31 < 2.5:
            vals = ['ZEEMAN_C1_CS', 'ZEEMAN_C2_CS', 'ZEEMAN_C3_CS',
                    'ZEEMAN_C4_CS', 'ZEEMAN_C5_CS']
        else:
            vals = ['ZEEMAN_C1_LI', 'ZEEMAN_C2_LI', 'ZEEMAN_C3_LI',
                    'ZEEMAN_C4_LI', 'ZEEMAN_C5_LI']
        for _i, _v in enumerate(vals, 1):
            _attr = f"Zeeman_C{_i}__b4c{9 + _i}"
            lines.append(f"{lp}ct.{_attr}.constant({t_expr}, {_v})\n")
        return lines

    def _gen_init_cmds(t_expr, lp):
        """Emit constant/go_high/go_low commands for every mapped channel at its LabVIEW init value."""
        lines = []
        _seen = set()
        _ze_emitted = False
        for _i in range(num_ch):
            _ch = get_channel_by_no(sseq, _i)
            _lv_name = _ch['name']
            _pfx = _og_prefix(_lv_name)
            _ival = float(_ch['ival'])

            if _pfx in _ZEEMAN_PREFIXES:
                if not _ze_emitted:
                    s31, s32 = _ze_init['1.31'], _ze_init['1.32']
                    if s32 < 2.5:
                        _zvals = [0, 0, 0, 0, 0]
                    elif s31 < 2.5:
                        _zvals = ['ZEEMAN_C1_CS', 'ZEEMAN_C2_CS', 'ZEEMAN_C3_CS',
                                  'ZEEMAN_C4_CS', 'ZEEMAN_C5_CS']
                    else:
                        _zvals = ['ZEEMAN_C1_LI', 'ZEEMAN_C2_LI', 'ZEEMAN_C3_LI',
                                  'ZEEMAN_C4_LI', 'ZEEMAN_C5_LI']
                    for _j, _v in enumerate(_zvals, 1):
                        _zattr = f"Zeeman_C{_j}__b4c{9 + _j}"
                        lines.append(f"{lp}ct.{_zattr}.constant({t_expr}, {_v})\n")
                    _ze_emitted = True
                continue

            _attr = _ct_attr(_lv_name)
            if _attr is None or _attr in _seen:
                continue
            _seen.add(_attr)

            _is_dig = _attr_is_dig.get(_attr, False)
            if _is_dig:
                _v_resolved = var_lookup(sseq.ramp_params, _ival)
                _method = 'go_low' if _v_resolved < 2.5 else 'go_high'
                lines.append(f"{lp}ct.{_attr}.{_method}({t_expr})\n")
            else:
                lines.append(f"{lp}ct.{_attr}.constant({t_expr}, {_ival:.6g})\n")
        return lines

    # ── Assemble output ──
    out = []

    # Section 1: Python header
    out.append(
        "from labscript import start, stop, add_time_marker, wait\n"
        "from lics_labscript_apparatus.connection_table import ConnectionTable\n"
        "\n"
        "SLOW_FREQ = 1e3   # 1 ms per edge\n"
        "FAST_FREQ = 50e3  # 20 us per edge\n"
        "\n"
        "# Cs MOT Zeeman currents\n"
        "ZEEMAN_C1_CS = 0\n"
        "ZEEMAN_C2_CS = 0.9\n"
        "ZEEMAN_C3_CS = 0.4\n"
        "ZEEMAN_C4_CS = 0.1\n"
        "ZEEMAN_C5_CS = 0.9\n"
        "\n"
        "# Li MOT Zeeman currents\n"
        "ZEEMAN_C1_LI = 5\n"
        "ZEEMAN_C2_LI = 7\n"
        "ZEEMAN_C3_LI = 7\n"
        "ZEEMAN_C4_LI = 8.5\n"
        "ZEEMAN_C5_LI = 1.6\n\n"
    )

    # Section 2: seq_dump header as comment block
    out.append("# header\n# ------\n")
    out.append(f"# version:{sseq.version}\n")
    out.append(f"# timing:{sseq.timing}\n")
    out.append(f"# never ramp:{int(sseq.never_ramp)}\n")
    out.append(f"# always_ramp:{int(sseq.always_ramp)}\n")
    out.append(f"# number of channels:{num_ch}\n")
    out.append(f"# number of procedures:{num_procs}\n\n")

    # Section 3: channel list with labscript name column
    out.append("# ch no\tname\t\t\t\t\t\t  init val\tanalog?\tnew labscript name\n")
    out.append("# -----\t----\t\t\t\t\t\t  --------\t-------\t------------------\n")
    for _i in range(num_ch):
        _ch = get_channel_by_no(sseq, _i)
        _pfx = _og_prefix(_ch['name'])
        if _pfx in _ZEEMAN_PREFIXES:
            _note = "(Zeeman logic — see section 8b of conversion note)"
        else:
            _attr = _ct_attr(_ch['name'])
            if _attr:
                _note = f"ct.{_attr}"
            else:
                out.append(
                    f"# {_i:03d}\t{_ch['name'][:24]:<24}\t"
                    f"{_ch['ival']:10.4f}\t\t{int(_ch['is_analog'])}\t# no new channel\n"
                )
                continue
        out.append(
            f"# {_i:03d}\t{_ch['name'][:24]:<24}\t"
            f"{_ch['ival']:10.4f}\t\t{int(_ch['is_analog'])}\t{_note}\n"
        )
    out.append("\n")

    # Section 4: procedure list with times in seconds
    out.append("# proc no\tname\t\t\t\t\t\t\t  time (ms)e-3\tenabled\n")
    out.append("# -------\t----\t\t\t\t\t\t\t  ------------\t------\n")
    for _i in range(num_procs):
        _t_str = _fmt_proc_t(sseq.procedures['time'][_i])
        out.append(
            f"# {_i:03d}\t\t{sseq.procedures['name'][_i][:24]:<24}\t"
            f"{_t_str}\t\t{int(sseq.procedures['enabled'][_i])}\n"
        )
    out.append("\n")

    # Section 5: 655xx code definitions
    for _i in range(sseq.ramp_params['num']):
        _code = 65500 + _i
        _cur = sseq.ramp_params['cur_val'][_i]
        _s   = sseq.ramp_params['start_val'][_i]
        _e   = sseq.ramp_params['end_val'][_i]
        _inc = sseq.ramp_params['incr_val'][_i]
        _ev  = int(sseq.ramp_params['ramp_every'][_i])
        _nx  = int(sseq.ramp_params['next_ramp'][_i])
        out.append(f"code_{_code} = {_cur:.4f}\n")
        out.append(
            f"#\t\tcur:{_cur:10.4f}  start:{_s:10.4f}  "
            f"stop:{_e:10.4f}  step:{_inc:10.4f}  every:{_ev}  next:{_nx}\n"
        )
    out.append("\n")

    # Section 6: sequence start
    out.append(
        "if __name__ == '__main__':\n"
        "    ct = ConnectionTable()\n\n"
        "    start()\n\n"
        "    # set all channels to LabVIEW init values\n"
        "    t = 10e-6\n"
    )
    out.extend(_gen_init_cmds("t", "    "))
    out.append(
        "\n"
        "    # pause for line trigger at 1 us, with a timeout of 100 ms\n"
        "    add_time_marker(t, 'Waiting for line trigger')\n"
        "    wait('line_trigger', t, timeout=0.1)\n"
    )

    # Section 7: procedures
    _ramp_labels = {0: 'JUMP', 1: 'FINE', 2: 'COARSE'}
    _num_ev = sseq.proc_details['dims'][1]

    for _pi in range(num_procs):
        _pname = sseq.procedures['name'][_pi]
        _pt_ms = sseq.procedures['time'][_pi]
        _enabled = bool(sseq.procedures['enabled'][_pi])
        _lp = "    " if _enabled else "    # "  # line prefix

        out.append(f"\n{_lp}# procedure {_pi:03d}: {_pname}\n")
        out.append(f"{_lp}t = {_fmt_proc_t(_pt_ms)}\n")
        out.append(f"{_lp}add_time_marker(t, '{_pname}')\n")

        # Collect enabled events (already sorted by seq_sort)
        _evs = []
        for _b in range(_num_ev):
            if sseq.proc_details['enabled'][_pi, _b]:
                _evs.append({
                    'idx': _b,
                    't_ms': float(sseq.proc_details['time'][_pi, _b]),
                    'ch_no': int(sseq.proc_details['channel_no'][_pi, _b]),
                    'voltage': float(sseq.proc_details['voltage'][_pi, _b]),
                    'rr': int(sseq.proc_details['ramp_res'][_pi, _b]),
                })

        # First pass: mark JUMP events that are replaced by a ramp on the same channel
        _prev_ei = {}   # ch_no -> event-list index of most recent event
        _replaced = set()
        for _ei, _ev in enumerate(_evs):
            _ch = _ev['ch_no']
            if _ev['rr'] in (1, 2) and _ch in _prev_ei:
                _pei = _prev_ei[_ch]
                _pev = _evs[_pei]
                if _pev['rr'] == 0 and _pev['t_ms'] != _ev['t_ms']:
                    _replaced.add(_pei)
            _prev_ei[_ch] = _ei

        # Second pass: emit commands
        _prev2 = {}  # ch_no -> {'t_ms', 'voltage'}
        for _ei, _ev in enumerate(_evs):
            _ch_no = _ev['ch_no']
            _t_ms  = _ev['t_ms']
            _volt  = _ev['voltage']
            _rr    = _ev['rr']
            _lv_ch = get_channel_by_no(sseq, _ch_no)
            _lv_name = _lv_ch['name']
            _pfx = _og_prefix(_lv_name)
            _t_expr = _fmt_t_offset(_t_ms)

            # Zeeman special logic
            if _pfx in _ZEEMAN_PREFIXES:
                _ze[_pfx] = _volt
                _resolved = var_lookup(sseq.ramp_params, _volt)
                out.append(
                    f"{_lp}# {_lv_name} → {_resolved:.6g} "
                    f"(Zeeman: 1.31={_ze['1.31']:.4g}, 1.32={_ze['1.32']:.4g})\n"
                )
                out.extend(_zeeman_cmds(_t_expr, _lp))
                _prev2[_ch_no] = {'t_ms': _t_ms, 'voltage': _volt}
                continue

            _attr = _ct_attr(_lv_name)

            if _attr is None:
                out.append(
                    f"{_lp}# {_lv_name}: {_fmt_v(_volt)} "
                    f"{_ramp_labels.get(_rr, '?')} — no new channel\n"
                )
                _prev2[_ch_no] = {'t_ms': _t_ms, 'voltage': _volt}
                continue

            _is_dig = _attr_is_dig.get(_attr, False)

            if _rr == 0:  # JUMP
                if _is_dig:
                    _v_resolved = var_lookup(sseq.ramp_params, _volt)
                    _method = ('go_low' if _v_resolved < 2.5 else 'go_high')
                    _cmd = f"ct.{_attr}.{_method}({_t_expr})"
                else:
                    _cmd = f"ct.{_attr}.constant({_t_expr}, {_fmt_v(_volt)})"
                if _ei in _replaced:
                    # find which ramp replaces it, for the comment
                    _ramp_t = next(
                        (_fmt_t_offset(_evs[_j]['t_ms']) for _j in range(_ei+1, len(_evs))
                         if _evs[_j]['ch_no'] == _ch_no and _evs[_j]['rr'] in (1, 2)),
                        "ramp"
                    )
                    out.append(f"{_lp}# {_cmd}  # replaced by ramp at {_ramp_t} in proc {_pi:03d}\n")
                else:
                    out.append(f"{_lp}{_cmd}\n")

            else:  # FINE or COARSE
                _sr = 'FAST_FREQ' if _rr == 1 else 'SLOW_FREQ'
                _prev = _prev2.get(_ch_no)
                if _prev and _prev['t_ms'] != _t_ms:
                    _st_ms = _prev['t_ms']
                    _init_v = _prev['voltage']
                    _st_expr = _fmt_t_offset(_st_ms)
                    out.append(
                        f"{_lp}ct.{_attr}.ramp("
                        f"t={_st_expr}, duration={_fmt_dur(_t_ms - _st_ms)}, "
                        f"initial={_fmt_v(_init_v)}, final={_fmt_v(_volt)}, "
                        f"samplerate={_sr})\n"
                    )
                else:
                    # No previous command or same-time → treat as constant
                    _init_v = _prev['voltage'] if _prev else _lv_ch['ival']
                    out.append(
                        f"{_lp}ct.{_attr}.constant({_t_expr}, {_fmt_v(_volt)})"
                        f"  # {_ramp_labels[_rr]} with no prior cmd, treated as constant\n"
                    )

            _prev2[_ch_no] = {'t_ms': _t_ms, 'voltage': _volt}

    # Compute stop time: latest absolute event time across all enabled procedures + 1 ms
    _stop_ms = 0.0
    for _pi in range(num_procs):
        if not sseq.procedures['enabled'][_pi]:
            continue
        _pt_ms = var_lookup(sseq.ramp_params, sseq.procedures['time'][_pi])
        for _b in range(_num_ev):
            if sseq.proc_details['enabled'][_pi, _b]:
                _et_ms = var_lookup(sseq.ramp_params, sseq.proc_details['time'][_pi, _b])
                _stop_ms = max(_stop_ms, _pt_ms + _et_ms)
    _stop_ms += 1.0  # 1 ms after last command

    out.append(f"\n    # set all channels back to LabVIEW init values\n    t = {_stop_ms:g}e-3\n")
    out.extend(_gen_init_cmds("t", "    "))
    out.append("    stop(t+10e-6)\n")

    content = ''.join(out)
    with open(out_path, 'w', encoding='utf-8') as _f:
        _f.write(content)
    return out_path



# Test code for the module
if __name__ == "__main__":
    # Test 1: Read a test file
    script_dir = os.path.dirname(__file__) 
    rel_path = "202409040423"
    test_file = os.path.join(script_dir, rel_path)
    test_seq = seq_read(test_file)

    # Test 2: Write that data to a new file
    rel_path = "test_write"
    test_file = os.path.join(script_dir, rel_path)
    seq_write(test_seq, test_file)
    test_seq2 = seq_read(test_file)
    # print(test_seq2)

    # Test 3: Channel report
    print(channel_report(test_seq2, '3.0'))

    # Test 4: Conversion
    
    parent_dir = os.path.dirname(script_dir)
    target_filename = "lics_labscript_apparatus/conv_20240904s423.py"
    target_name = os.path.join(parent_dir, target_filename)
    labview_labscript_convert(test_seq, target_name)
