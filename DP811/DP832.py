import rpyc
import pyvisa
import json
import threading
#from common.common import pack
import pickle

#If you have the common folder in your project you can delete these two functions and uncomment the import
def pack(value):
    try:
        return pickle.dumps(value)
    except Exception:
        # this happens when un-pickleable objects (e.g. functions) are assigned
        # to a parameter. In this case, we don't pickle it but transfer a netref
        # instead
        return value

def unpack(value):
    try:
        return pickle.loads(value)
    except Exception:
        return value

# Driver for RIGOL DP800 series
# DP832 3 Channels: 30V/3A, 30V/3A, 5V/3A
class DP832():

    def __init__(self, manager, port):
        self.manager = manager

        self.port = port
        self.device = None

        self._model = ''
        self._SN = ''

        self.is_connected = False
        self.connect()

    def connect(self):
        self.device = self.manager.open_resource(self.port)
        self.is_connected = True
        self.get_IDN()

    def close(self):
        self.device.close()
        self.is_connected = False
    
    # Channel number counts from 1
    # Measure return float
    def _measure(self, channel, tag):
        return (float(self.device.query(":MEAS:%s? CH%d"%(tag, channel))))
    
    def measure_voltage(self, channel):
        return (self._measure(channel, "VOLT"))
    
    def measure_current(self, channel):
        return (self._measure(channel, "CURR"))
    
    def measure_power(self, channel):
        return (self._measure(channel, "POWE"))

    # Get setvalues return float
    # SOURce: select channel
    def _getSet(self, channel, tag):
        return (float(self.device.query(":SOUR%d:%s?"%(channel, tag))))
    
    def get_voltage(self, channel):
        return (self._getSet(channel, "VOLT"))
    
    def get_current(self, channel):
        return (self._getSet(channel, "CURR"))
    
    # OCP(Overcurrent Protection) value
    def get_OCP(self, channel):
        return (self._getSet(channel, "CURR:PROT"))
    
    # OVP(Overvoltage Protection) value
    def get_OVP(self, channel):
        return (self._getSet(channel, "VOLT:PROT"))
    
    # Set
    def _set(self, channel, tag, val):
        self.device.write(":SOUR%d:%s %s"%(channel, tag, val))

    def set_voltage(self, channel, val):
        self._set(channel, "VOLT", val)
    
    def set_current(self, channel, val):
        self._set(channel, "CURR", val)
    
    def set_OCP(self, channel, val):
        self._set(channel, "CURR:PROT", val)
    
    def set_OVP(self, channel, val):
        self._set(channel, "VOLT:PROT", val)
    
    # OCP/OVP Control
    def get_OCP_enable(self, channel):
        return (self.device.query(":SOUR%d:CURR:PROT:STAT?"%channel)).__eq__('ON\n')
    
    def set_OCP_enable(self, channel, status):
        if status == True:
            self.device.write(":SOUR%d:CURR:PROT:STAT ON"%channel)
        else:
            self.device.write(":SOUR%d:CURR:PROT:STAT OFF"%channel)
    
    def get_OCP_alert(self, channel):
        return (self.device.query(":OUTP:OCP:ALAR? CH%d"%channel)).__eq__('YES\n')
    
    def set_OCP_alert(self, channel):
        self.device.write(":OUTP:OCP:CLEAR CH%d"%channel)
    
    def get_OVP_enable(self, channel):
        return (self.device.query(":SOUR%d:VOLT:PROT:STAT?"%channel)).__eq__('ON\n')
    
    def set_OVP_enable(self, channel, status):
        if status == True:
            self.device.write(":SOUR%d:VOLT:PROT:STAT ON"%channel)
        else:
            self.device.write(":SOUR%d:VOLT:PROT:STAT OFF"%channel)
    
    def get_OVP_alert(self, channel):
        return (self.device.query(":OUTP:OVP:ALAR? CH%d"%channel)).__eq__('YES\n')
    
    def set_OVP_alert(self, channel):
        self.device.write(":OUTP:OVP:CLEAR CH%d"%channel)
    
    # Power switch
    def set_enable(self, channel, status):
        if status == True:
            self.device.write(":OUTP:STAT CH%d,ON"%channel)
        else:
            self.device.write(":OUTP:STAT CH%d,OFF"%channel)

    def get_enable(self, channel):
        return (self.device.query(":OUTP:STAT? CH%d"%channel)).__eq__('ON\n')
    
    # Port attributes
    # Return 'CV', 'CC' or 'UR'
    def get_mode(self, channel):
        return (self.device.query(":OUTP:MODE? CH%d"%channel))[:-1]

    # Device info
    def get_IDN(self):
        data = self.device.query("*IDN?")
        self._model = (data.split(','))[1]
        self._SN = (data.split(','))[2]
        return data

    def get_model(self):
        return self._model
    
    def get_SN(self):
        return self._SN

# RPyC wrapper of dictionary of DP832 drivers sorted by SN
class DP832Service(rpyc.Service):
    def __init__(self):
        super().__init__()

        self.devices = {} # Create device dict container
        self.rm = pyvisa.ResourceManager('@py') # Initialize VISA manager

		# Load parameters
        with open('DP832.json', 'r') as file:
            parameters = json.load(file)
        
        for i in parameters['Ports']:
            handler = DP832(self.rm, i)
            lock = threading.Lock()
            # (device, local parameter, busy)
            self.devices[handler.get_SN()] = [handler, {}, lock]
            self.sync(handler.get_SN())
    
    def sync(self, device):
        res = {}
        res['voltage'] = []
        res['current'] = []
        res['OCP'] = []
        res['OVP'] = []
        res['OCP_enable'] = []
        res['OVP_enable'] = []
        res['enable'] = []
        for j in range(1, 2):
            (res['voltage']).append(self.devices[device][0].get_voltage(j))
            (res['current']).append(self.devices[device][0].get_current(j))
            (res['OCP']).append(self.devices[device][0].get_OCP(j))
            (res['OVP']).append(self.devices[device][0].get_OVP(j))
            (res['OCP_enable']).append(self.devices[device][0].get_OCP_enable(j))
            (res['OVP_enable']).append(self.devices[device][0].get_OVP_enable(j))
            (res['enable']).append(self.devices[device][0].get_enable(j))
        self.devices[device][1] = res

    def exposed_device_list(self):
        return pack(list(self.devices.keys()))
    
    def exposed_get_parameters(self):
        res = {}
        for i in list(self.devices.keys()):
            res[i] = self.devices[i][1]
        return pack(res)

    def exposed_connect_device(self, device):
        self.devices[device].connect()

    def exposed_close_device(self, device):
        self.devices[device].close()

    def exposed_get_voltage(self, device, channel):
        return self.devices[device][1]['voltage'][channel - 1]
    
    def exposed_set_voltage(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_voltage(channel, value)
            self.devices[device][1]['voltage'][channel - 1] = value
    
    def exposed_get_current(self, device, channel):
        return self.devices[device][1]['current'][channel - 1]
    
    def exposed_set_current(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_current(channel, value)
            self.devices[device][1]['current'][channel - 1] = value
    
    def exposed_get_OCP(self, device, channel):
        return self.devices[device][1]['OCP'][channel - 1]
    
    def exposed_set_OCP(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_OCP(channel, value)
            self.devices[device][1]['OCP'][channel - 1] = value
    
    def exposed_get_OVP(self, device, channel):
        return self.devices[device][1]['OVP'][channel - 1]
    
    def exposed_set_OVP(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_OVP(channel, value)
            self.devices[device][1]['OVP'][channel - 1] = value
    
    def exposed_get_OCP_enable(self, device, channel):
        return self.devices[device][1]['OCP_enable'][channel - 1]
    
    def exposed_set_OCP_enable(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_OCP_enable(channel, value)
            self.devices[device][1]['OCP_enable'][channel - 1] = value
    
    def exposed_get_OVP_enable(self, device, channel):
        return self.devices[device][1]['OVP_enable'][channel - 1]
    
    def exposed_set_OVP_enable(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_OVP_enable(channel, value)
            self.devices[device][1]['OVP_enable'][channel - 1] = value
    
    def exposed_get_enable(self, device, channel):
        return self.devices[device][1]['enable'][channel - 1]
    
    def exposed_set_enable(self, device, channel, value):
        with self.devices[device][2]:
            self.devices[device][0].set_enable(channel, value)
            self.devices[device][1]['enable'][channel - 1] = value
    
    def exposed_clean(self):
        for i in list(self.devices.keys()):
            self.devices[i].close()

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DP832Service(), port=18861)
    t.start()