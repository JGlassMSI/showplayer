import logging
from abc import ABC, abstractmethod
import serial
import serial.tools.list_ports
from TimerClass import *
from time import sleep
import re


class InputAggregator():
    def __init__(self):
        pass

class InputDevice(ABC):
    """An abstract class for objects that listen to external signals (hardware or software)
    to cause showplayer to advance
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def retrieveTriggerFlag(self):
        pass

    @abstractmethod
    def beginNewTriggerMonitor(self):
        pass

    @abstractmethod
    def haltTriggerMonitor(self):
        pass

class SerialInputDevice(InputDevice):

    #How many times do we need to see a reading that's opposite to our current state
    #to be confident the state has changed
    confidenceLevel = 1

    def __init__(self, name=None, dummy=False, label='Unnamed Serial Input Device'):
        logging.debug("Initializing Serial Input Object")
        super().__init__()

        self.thread = None
        self.triggered = False
        self.newTriggerFlag = False
        self.repeatReadings = 0
        self.continueChecking = True
        self.t = TimerClass(self, self.checkForData, delay = 0.1)
        self.label = label

        if name != None:
            try:
                self.ser = serial.Serial(port = name, baudrate = 115200, timeout = 5, rtscts=False, dsrdtr=False)
                logging.info(f"Opened com port {self.ser.port} for input")
            except serial.serialutil.SerialException as err:
                self.ser = serial.Serial(port = None, baudrate = 115200, timeout = 5, rtscts=False, dsrdtr=False)
                logging.info(f"Error on serial port creation, port initialized as none")
            if self.thread == None:
                pass

        else:
             self.ser = serial.Serial(port = None, baudrate = 115200, timeout = 5, rtscts=False, dsrdtr=False)
             logging.info(f"No name supplied, creating dummy Serial input device")

    def beginNewTriggerMonitor(self):
        self.continueChecking = True
        self.newTriggerFlag = False
        self.t = TimerClass(self, self.checkForData, delay = 0.1)
        self.t.run()
        
    def haltTriggerMonitor(self):
        self.continueChecking = False
        self.newTriggerFlag = False
        self.t.stop()

    def checkForData(self):
        if self.ser.port != None:
            #logging.debug(f"Serial port exists: {self.ser.port}")
            if not self.ser.is_open: 
                try: 
                    self.ser.open()
                except serial.serialutil.SerialException as err:
                    pass
                    #logging.warning(f"Serial Exception: {err}")
                    #raise(err)
            else:
                logging.log(5, f"Port {self.ser.port} is open, let's see if there's data")
                if self.ser.in_waiting > 0:
                    #(f"There are {self.ser.in_waiting} bytes in buffer:")
                    data = self.ser.read_all()
                    isButtonPressed = self.assessData(self.parseByteData(data))
                    #print(f"Button is pressed? {isButtonPressed}")
                    if isButtonPressed != self.triggered: self.repeatReadings += 1
                    else: self.repeatReadings = 0

                    if self.repeatReadings >= SerialInputDevice.confidenceLevel:
                        self.triggered = not self.triggered
                        logging.debug(f"Serial Input Device triggered status is now {self.triggered}")
                        self.repeatReadings = 0
                        if self.triggered == True: self.newTriggerFlag = True
                        logging.debug(f"New Trigger Flag is now {self.newTriggerFlag}")

                    else:
                        pass
                        logging.log(5, "Serial port checked for data but has no bytes waiting")
        #print(f"Triggered: {self.triggered}")
        else:
            pass
            logging.debug(f"Serial input has no port: {self.ser}")

    def retrieveTriggerFlag(self):
        self.checkForData()
        if self.newTriggerFlag:
            self.newTriggerFlag = False
            logging.log(5, f"Serial trigger flag state was received and flag was cleared")
            self.continueChecking = False
            return True
        
        logging.log(5, f"Serial trigger flag status was requested but flag was not set")
        return False
        

    def parseByteData(self, data):
        try:
            stringData = data.decode('utf-8')
            pattern = re.compile(r'(CH(?P<channel>\d):(?P<value>\d\d\d\d))')
            matches = re.finditer(pattern, stringData)

            channelData = {}
            for m in matches:
                channelData[int(m.group('channel'))] = int(m.group('value'))
        except UnicodeDecodeError as err:
            logging.info("Malformed unicode byte, returning null data. Error was ", err)
            return {}

        return channelData


    def assessData(self):
        return False

class PlaneSerialInput(SerialInputDevice):
    def __init__(self,name=None,dummy=False, remoteChannel = 0, label="PlaneSerialInput"):
        super().__init__(name, dummy, label)
        self.remoteChannel = remoteChannel

    def assessData(self, channelData):
        logging.log(5, f"Asked to asses data with data {channelData}")
        #ACTIVE LOW
        return self.remoteChannel in channelData.keys() and channelData[self.remoteChannel] < 1000


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    s = PlaneSerialInput(name = "COM4")
    while(True):
        print(f"{s.checkForData()= }")
        print(f"{s.retrieveTriggerFlag()= }")
        sleep(.25)    
