#####################################################################
#                                                                   #
# /LiCs_devices/DP832/blacs_worker.py                               #
#                                                                   #
# This code is adapted from naqslab with modifications              #
# made to enable compatibility with the rigol DP832 power supply    #
#####################################################################

import numpy as np

from LiCs_devices.VISA.blacs_workers import VISAWorker
from labscript import LabscriptError 
from labscript_utils import dedent

import labscript_utils.h5_lock, h5py

class DP832Worker(VISAWorker):
    # ident_string = 'E364'
    supported = ['DP832']
    # define instrument specific read and write strings
    write_both_string = 'APPL %.5f, %.5f'
    write_volt_string = 'VOLT %.5f'
    write_current_string = 'CURR %.5f'
    read_string = 'APPL? %s'

    def read_parser(self,response):
        '''Parses the Voltage & Amplitude response string

        Args:
            response (str): Instrument response to current voltage/current query.
                            Has format of "d.ddddd, d.ddddd"

        Returns:
            (tuple): containing

                V (float): Current Voltage Setting
                A (float): Current Current Setting
        '''
        info, V, A = response[1:-3].split(',')
        return float(V), float(A) 
    
    def init(self):
        # Call the VISA init to initialise the VISA connection
        VISAWorker.init(self)

        response = self.connection.query('*IDN?')
        model = response.split(',')[1]
        if model not in self.supported:
            msg = f''' Rigol DP832 does not support:\t{response}'''
            raise LabscriptError(msg)
        
        if self.limited == 'volt':
            self.write_string = self.write_volt_string
            self.tag='VOLT'
        else:
            self.write_string = self.write_current_string
            self.tag="CURR"
        
        # initialize the smart cache
        self.smart_cache = {'CURRENT_DATA': 
                                {'channel %d'%i:None for i in self.allowed_outputs}
                            }
    
    def check_remote_values(self):
        # Get the currently output values:
        results = {}
        
        # these query strings and parsers depend heavily on device
        for i in self.allowed_outputs:
            response = self.connection.query(self.read_string%("CH" + str(i)))
            V, A = self.read_parser(response)
            results['channel %d'%i] = V if self.limited == 'volt' else A

        return results
    
    def program_manual(self,front_panel_values):

        currentVals = self.check_remote_values()
        
        for output, val in front_panel_values.items():
            if val != currentVals[output]:
                chNum = ''.join([i for i in output if i.isdigit()])
                self.connection.write(":SOUR%d:%s %s"%(int(chNum), self.tag, val))
                # invalidate smart cache after manual update
                self.smart_cache['CURRENT_DATA'][output] = None
        
        return self.check_remote_values()        

    def transition_to_buffered(self,device_name,h5file,initial_values,fresh):
        # call parent method to do basic preamble
        VISAWorker.transition_to_buffered(self,device_name,h5file,initial_values,fresh)
        data = None
        final_values = initial_values
        # Program static values
        with h5py.File(h5file,'r') as hdf5_file:
            group = hdf5_file['/devices/'+device_name]
            # If there are values to set the unbuffered outputs to, set them now:
            if 'STATIC_DATA' in group:
                data = group['STATIC_DATA'][:][0]
                print("The data:")
                print(data)
        print("The current data:")
        print(self.smart_cache['CURRENT_DATA'])
        if data is not None:
            if fresh or data != self.smart_cache['CURRENT_DATA']:
                
                # only program channels as needed
                channels = [int(name[-1]) for name in data.dtype.names]
                print("The channels:")
                print(channels)
                for i in channels:
                    if data[i-1] != self.smart_cache['CURRENT_DATA']['channel %d'%i]:
                        #self.connection.write(self.write_string%(data[i]))
                        self.connection.write(":SOUR%d:%s %s"%(i, self.tag, data[i-1]))
                        final_values['channel %d'%i] = data[i-1]
                        self.smart_cache['CURRENT_DATA']['channel %d'%i] = data[i-1]                
   
            else:
                final_values = self.initial_values
                 
        return final_values

    def check_status(self):
        pass
