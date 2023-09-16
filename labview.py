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

        raw_ramps = [read_single(fid, 'float64') for i in range(4 * seq.ramp_params['num'])]
        raw_ramps = np.reshape(raw_ramps, (4, seq.ramp_params['num']))
        seq.ramp_params['cur_val'] = raw_ramps[0, :]
        seq.ramp_params['start_val'] = raw_ramps[1, :]
        seq.ramp_params['end_val'] = raw_ramps[2, :]
        seq.ramp_params['incr_val'] = raw_ramps[3, :]
        seq.ramp_params['ramp_every'] = np.ones(seq.ramp_params['end_val'].shape)
        seq.ramp_params['next_ramp'] = np.zeros(seq.ramp_params['end_val'].shape)


        # read secondary analog
        seq.secondary_analog = read_array(fid, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])

        # read the ramping control group
        check_num = read_single(fid, 'uint32')
        
        raw_ramps = [read_single(fid, 'int32') for i in range(2 * check_num)]
        raw_ramps = np.reshape(raw_ramps, (2, check_num))
        seq.ramp_params['ramp_every'][:check_num] = raw_ramps[0, :]
        seq.ramp_params['next_ramp'][:check_num] = raw_ramps[1, :]

        # read "never ramp"
        seq.never_ramp = bool(read_single(fid, 'uint8'))

        # read "always ramp"
        seq.always_ramp = bool(read_single(fid, 'uint8'))

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

        raw_ramps = np.zeros((4, seq.ramp_params['num']), dtype=np.float64)
        raw_ramps[0, :] = seq.ramp_params['cur_val']
        raw_ramps[1, :] = seq.ramp_params['start_val']
        raw_ramps[2, :] = seq.ramp_params['end_val']
        raw_ramps[3, :] = seq.ramp_params['incr_val']

        raw_ramps = np.reshape(raw_ramps, (4 * seq.ramp_params['num']))
        for r in raw_ramps:
            write_single(fid, 'float64', r)

        # Write the secondary analog group
        write_array(fid, seq.secondary_analog, 2, [
            ['ival', 'float64'],
            ['name', 'str'],
            ['is_analog', 'uint8']])

        # Write the ramping control group
        write_single(fid, 'uint32', seq.ramp_params['num'])

        raw_ramps = np.zeros((2, seq.ramp_params['num']), dtype=int)
        raw_ramps[0, :] = seq.ramp_params['ramp_every']
        raw_ramps[1, :] = seq.ramp_params['next_ramp']
        raw_ramps = np.reshape(raw_ramps, (2 * seq.ramp_params['num']))

        for r in raw_ramps:
            write_single(fid, 'int32', r)

        # Write the "always ramp"
        write_single(fid, 'uint8', seq.always_ramp)

        # Write the "never ramp"
        write_single(fid, 'uint8', seq.never_ramp)


def read_array(fid, num_dimensions, in_format):
        """
        Reads a single array from the LabVIEW sequence file format. This code is nearly identical to the MATLAB version.

        Parameters
        ----------
        fid : file
            The file object to read from.

        num_dimensions : int
            The number of dimensions of the array. 

        in_format : list
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
        
        num_fields = len(in_format)

        # Read the dimensions of the array
        dims = [1, 1]
        for a in range(num_dimensions):
            dims[a] = read_single(fid, 'uint32')

        # Initialize the output dictionary
        arr = {}
        arr['dims'] = dims

        # rectify dims not to be dumb
        if dims[1] == 1:
            dims = [dims[0]]

        # initialize arrays
        for b in range(num_fields):
            field_name = in_format[b][0]
            field_type = in_format[b][1]
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
                field_name = in_format[c][0]
                field_type = in_format[c][1]
                arr[field_name][ind] = read_single(fid, field_type)

        return arr


def write_array(fid, in_struct, num_dimensions, out_format):
    """
    Writes a single array to the LabVIEW sequence file format. This code is nearly identical to the MATLAB version.

    Parameters
    ----------
    fid : file   
        The file object to write to.

    in_struct : dict

    num_dimensions : int
        The number of dimensions of the array.

    out_format : list
        A list of 2-part tuples, containing the field name and the data format. The data formats should be one of the
        following: 'str', 'float64', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32'.
    

    Notes
    -----
    The LabVIEW sequence file is a binary file. The file is written as a binary file and the data is parsed from a
    dictionary. The dictionary is passed as an argument.

    """
    
    num_fields = len(out_format)
    dims = in_struct['dims']

    for a in range(num_dimensions):
        write_single(fid, 'uint32', dims[a])

    dims = in_struct[out_format[0][0]].shape

    for ind in np.ndindex(tuple(dims)):
        for b in range(num_fields):
            data = in_struct[out_format[b][0]][ind]
            fmt = out_format[b][1]
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
    print(test_seq2)
