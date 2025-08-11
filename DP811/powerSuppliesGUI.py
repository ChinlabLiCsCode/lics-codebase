import sys
import time
import threading
import yaml
from yaml.loader import FullLoader
import rpyc
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox
)
from PyQt6.QtGui import QAction

"""
GUI for controlling Rigol DP800 series power devices
Before running
    1. Update the yml config file with your device configurations, make sure the formatting is the same
    2. Update yml file path in readConfig function and json file path in DP832.py DP832Service class
    3. update for loop range in DP832Service class sync function to match the number of channels you're using
"""
class GUI(QMainWindow):
    def __init__(self, deviceName:str):
        super().__init__()
        
        self.deviceName = deviceName
          
        self.shouldUpdate = False
        self.correctDeviceName = False

        #read the config file
        self.readConfig()

        #init main Window
        self.initMainWindow()

        #init devices
        self.initDevice()

        #variables to store values
        self.currentValue = None
        self.voltageValue = None

    def readConfig(self):
        #read the config file
        self.filePath = "/Users/mouhamedmbengue/Desktop/ArgonneInternshipCode/YbLabMonitoring/deviceFiles/guiConfig.yml"
        with open(self.filePath) as f:
            self.config = yaml.load(f, Loader=FullLoader)

        #get the necessary variables
        self.guiVars = self.config["GUI Settings"]
        
        #Check that the device name is correct
        try:
            self.deviceVars = self.config[self.deviceName + " Settings"]
            self.correctDeviceName = True
        
        except KeyError:
            print("Incorrect input")
            while self.correctDeviceName == False:
                try:
                    self.deviceName = input("Input the correct device name: ")
                    self.deviceVars = self.config[self.deviceName + " Settings"]
                    self.correctDeviceName = True
                except KeyError:
                    print("Incorrect Input")

        self.deviceSN = self.deviceVars[0]["SN"]
        self.channelVars = self.deviceVars[1]["Channel Settings"]
        self.deviceLimits = self.deviceVars[2]["Device Limits"]

    def initMainWindow(self):
        self.setWindowTitle(self.deviceName)
        self.setGeometry(0, 0, 500, 300)

        #add a menu bar
        self.menu = self.menuBar()
        self.channelMenu = self.menu.addMenu("Channels")

    def initDevice(self):
        try:
            self.device = (rpyc.connect("localhost", 18861)).root
        except:
            print("No Device Connected")
            sys.exit()

        #check which channels are on and init those channels
        self.i = 0
        self.channels = []
        self.channelIndex = []
        
        for chValue in self.channelVars:
            if self.channelVars.get(chValue) == True:
                self.i+=1

                #store the channel name and number number
                self.channels.append("Channel " + str(self.i))
                self.channelIndex.append(self.i)

                #initialize the channel
                self.initChannel(("ch" + str(self.i)), self.i)
            else:
                self.i+=1
        
        #Group all active channels into a dictionary for future reference
        self.chDictionary = {self.channels[i]: self.channelIndex[i] for i in range(len(self.channelIndex))}

        #refresh the window when a channel is triggered
        self.channelMenu.triggered[QAction].connect(self.newWindow)

    def initChannel(self, chName:str, chNum:int):
        self.chName = chName
        self.chNum = chNum
        
        #add the channel to the menu and create a new window when clicked
        self.channelMenu.addAction(("Channel " + str(self.chNum)))
        
    def newWindow(self, ch):
        self.chName = ch.text()
        self.chNum = self.chDictionary[self.chName]

        #get the current and voltage values from the device
        self.currentValue  = self.device.get_current(self.deviceSN, self.chNum)
        self.voltageValue = self.device.get_voltage(self.deviceSN, self.chNum)

        #Create a new window
        self.chWindow = QWidget()
        self.mainLayout = QHBoxLayout()

        #change the window title
        self.setWindowTitle(self.deviceName + " " + self.chName)

        #add labels for the set current and and voltage spin boxes
        self.currentLabel = QLabel("Set Current (A)")
        self.voltageLabel = QLabel("Set Voltage (V)")

        #add spin boxes to set the current and voltage with max and min from the config file
        self.currentSpinBox = QDoubleSpinBox()
        self.currentSpinBox.setMaximum(float(self.deviceLimits.get("currentMax")))
        self.currentSpinBox.setMinimum(float(self.deviceLimits.get("currentMin")))
        self.currentSpinBox.valueChanged.connect(self.setCurrent)

        self.voltageSpinBox = QDoubleSpinBox()
        self.voltageSpinBox.setMaximum(float(self.deviceLimits.get("voltageMax")))
        self.voltageSpinBox.setMinimum(float(self.deviceLimits.get("voltageMin")))
        self.voltageSpinBox.valueChanged.connect(self.setVoltage)

        #add a label to display the voltage and current values
        self.currentDisplay = QLabel(str(self.currentValue) + " (A)")
        self.voltageDisplay = QLabel(str(self.voltageValue) + " (V)")

        #add display widgets to the display layout
        self.displayLayout = QVBoxLayout()
        self.displayLayout.addWidget(self.currentDisplay)
        self.displayLayout.addWidget(self.voltageDisplay)

        #add the control widgets to the control layout
        self.controlLayout = QVBoxLayout()
        self.controlLayout.addWidget(self.currentLabel)
        self.controlLayout.addWidget(self.currentSpinBox)
        self.controlLayout.addWidget(self.voltageLabel)
        self.controlLayout.addWidget(self.voltageSpinBox)

        #add the sub layouts to the main layout
        self.mainLayout.addLayout(self.displayLayout)
        self.mainLayout.addLayout(self.controlLayout)
        self.chWindow.setLayout(self.mainLayout)

        #reset the window
        self.setCentralWidget(self.chWindow)

        #start updating the window if one of the values change
        self.t1 = threading.Thread(target=self.updateDisplay)

    def setVoltage(self):
        self.voltageValue = self.voltageSpinBox.value()
        self.device.set_voltage(self.deviceSN, self.chNum, self.voltageValue)
        self.shouldUpdate = True

        #start the update thread if it isn't already running
        if self.t1.is_alive() == False:
            self.t1.start()

    def setCurrent(self):
        self.currentValue = self.currentSpinBox.value()
        self.device.set_current(self.deviceSN, self.chNum, self.currentValue)
        self.shouldUpdate = True 

        #start the update thread if it isn't already running
        if self.t1.is_alive() == False:
            self.t1.start()

    def updateDisplay(self):
        #get the refresh rate
        self.refreshRate = self.guiVars[0]["refreshRate"]
        
        while self.shouldUpdate:
            try:
                #update the current
                self.currentValue = self.device.get_current(self.deviceSN, self.chNum)
                self.currentDisplay.setText(str(self.currentValue) + " (A)")
            
                #update the voltage
                self.voltageValue = self.device.get_voltage(self.deviceSN, self.chNum)
                self.voltageDisplay.setText(str(self.voltageValue) + " (V)")

                time.sleep(int(self.refreshRate))

            except:
                self.shouldUpdate = False
                print("stopped update")
        
    def closeEvent(self, event):
        try:
            #stop update
            self.shouldUpdate = False
            self.t1.join()

            print("closed")
        except:
            print("Closed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GUI(input("DeviceName: "))
    window.show()
    sys.exit(app.exec())