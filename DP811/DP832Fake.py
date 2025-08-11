import sys
import rpyc
from rpyc.utils.server import ThreadedServer

class DP832(rpyc.Service):
    #define the voltage and current values
    def __init__(self, curVal:float, voltVal:float):
        self.curVal = curVal
        self.voltVal = voltVal
    
    #set current and change voltage relative to an input
    def exposed_setCurrentValue(self, input:float):
        self.curVal = input
        self.voltVal += input
    
    #set voltage and change current relative to an input
    def exposed_setVoltageValue(self, input:float):
        self.voltVal = input
        self.curVal += input
    
    #get the current value
    def exposed_getCurrentValue(self):
        return self.curVal
    
    #get the voltage vale
    def exposed_getVoltageValue(self):
        return self.voltVal

    #stop the program
    def exposed_stop(self):
        sys.exit()

if __name__ =="__main__":
    #create an instance of the server and run it
    test = ThreadedServer(service=DP832(3.14, 2.71), hostname='localhost', port=18861)
    test.start()
    test.close()