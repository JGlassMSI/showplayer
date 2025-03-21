#relayUtils.py

import sys, os, time
import ctypes
import logging
import threading

##Utility Functions

def exc(msg):  return Exception(msg)

def fail(msg) : raise exc(msg)

if sys.version_info.major >= 3:
    def charpToString(charp):
        return str(ctypes.string_at(charp), 'ascii')
    def stringToCharp(s) :   
        return bytes(s, "ascii")
else:
  def charpToString(charp) :
     return str(ctypes.string_at(charp))
  def stringToCharp(s) :   
    return bytes(s)  #bytes(s, "ascii")

#Enumeration Functions

#USB Function Definitions

usb_relay_lib_funcs = [
# TYpes: h=handle (pointer sized), p=pointer, i=int, e=error num (int), s=string
  ("usb_relay_device_enumerate",               'h', None),
  ("usb_relay_device_close",                   'e', 'h'),
  ("usb_relay_device_open_with_serial_number", 'h', 'si'),
  ("usb_relay_device_get_num_relays",          'i', 'h'),
  ("usb_relay_device_get_id_string",           's', 'h'),
  ("usb_relay_device_next_dev",                'h', 'h'),
  ("usb_relay_device_get_status_bitmap",       'i', 'h'),
  ("usb_relay_device_open_one_relay_channel",  'e', 'hi'),
  ("usb_relay_device_close_one_relay_channel", 'e', 'hi'),
  ("usb_relay_device_close_all_relay_channel", 'e', None)
  ]

##Class definitions



class relayBoard():
    def __init__(self, libpath='.', logLevel = 5):
        self.libpath = libpath

        self.libfile = {'nt':   "usb_relay_device.dll", 
               'posix': "usb_relay_device.so",
               'darwin':"usb_relay_device.dylib",
               } [os.name]

        self.DLL = None

        #All of these will be initialize in openDevById after we know how many relays there are:
        self.blinking = {}#True or false, depending on if a pin is blinking
        self.blinks = None #holds blinking threads
        self.numRelays = 0
        self.loglevel = logLevel

    def __getstate__(self):
      myDict = self.__dict__
      myDict['blinkThread'] = None
      myDict['DLL'] = None
      return  myDict

    def __setstate__(self, state):
      self.__dict__= state
      self.loadLibAndInit()

    def loadLib(self):
        if not self.DLL:
            logging.log(self.loglevel, "Loading DLL: %s" % ('/'.join([self.libpath,self.libfile])))
            try:
                self.DLL = ctypes.CDLL( '/'.join([self.libpath, self.libfile]) )
            except OSError:
                fail("Failed to load lib")
        else:
            print("Lib already loaded")
        self.getLibFunctions()
        logging.log(self.loglevel, "Lib functions successfully loaded")

    def getLibFunctions(self):
        if self.DLL == None:
            raise AttributeError("DLL does not exist or not loaded")
        else:
            self.libver = self.DLL.usb_relay_device_lib_version() 
            logging.log(self.loglevel, "%s version: 0x%X" % (self.libfile,self.libver))

            retVal = self.DLL.usb_relay_init()
            if retVal != 0: fail("Failed to initialize library")

            """
            Tweak imported C functions
            This is required in 64-bit mode. Optional for 32-bit (pointer size=int size)
            Functions that return and receive ints or void work without specifying types.
            """            

            ctypemap = { 'e': ctypes.c_int, 'h':ctypes.c_void_p, 'p': ctypes.c_void_p,
                      'i': ctypes.c_int, 's': ctypes.c_char_p}
          
            for x in usb_relay_lib_funcs :
                fname, ret, param = x
                try:
                  f = getattr(self.DLL, fname)
                except Exception:  
                  fail("Missing lib export:" + fname)
          
                ps = []
                if param :
                  for p in param :
                    ps.append( ctypemap[p] )
                f.restype = ctypemap[ret]
                f.argtypes = ps
                setattr(self.DLL, fname, f)

            #added so as not to crash on some 64 bit systems:
            self.DLL.usb_relay_device_close_all_relay_channel.argtypes = [ctypes.c_longlong]

    def openDevById(self, idstr):
        logging.log(self.loglevel, "Trying to open device with id: " + idstr)   
        if self.DLL: self.device = self.DLL.usb_relay_device_open_with_serial_number(stringToCharp(idstr), 5)
        if not self.device: fail("Cannot open device with id: " + idstr)

        if self.DLL: self.numRelays = self.DLL.usb_relay_device_get_num_relays(self.device)
        if self.numRelays <= 0 or self.numRelays > 8: fail("Too many or too few channels, should be 1-8, but is:" + str(self. numRelays))
        
        self.blinkAlive = True #set to false to kill 
        for i in range(1, self.numRelays+1):
          self.blinking[i] = False # = [False for i in range(1, self.numRelays+1)]
        self.blinkThread = threading.Thread(target=self.__blink) #[threading.Thread(target=self.__blink, args=(i,)) for i in range (1, self.numRelays+1)]
        self.blinkThread.setDaemon(True)
        self.blinkThread.start()



        logging.log(self.loglevel, "Number of relays on device with ID=%s: %d" % (idstr, self.numRelays))

    def enumDevs(self):
      devids = []
      if self.DLL: enuminfo = self.DLL.usb_relay_device_enumerate()
      while enuminfo :
        if self.DLL: idstrp = self.DLL.usb_relay_device_get_id_string(enuminfo)
        idstr = charpToString(idstrp)
        logging.info("Found ID string: " + idstr)
        assert len(idstr) == 5
        if not idstr in devids : devids.append(idstr)
        else : logging.warning("Warning! found duplicate ID=" + idstr)
        if self.DLL: enuminfo = self.DLL.usb_relay_device_next_dev(enuminfo)

      logging.info("Found devices: %d" % len(devids))
      return devids

    def closeDev(self):
        if self.DLL:  self.DLL.usb_relay_device_close(self.device)
        self.device = None
        self.blinkAlive = False
        time.sleep(2)
        logging.info("Device Closed")

    def unloadLib(self):
        if self.device: self.closeDev()
        if self.DLL: self.DLL.usb_relay_exit()
        self.DLL = None
        logging.info("Lib closed")

    def loadLibAndInit(self):
      self.loadLib()
      ids = self.enumDevs()
      if len(ids) > 0:
        self.openDevById(ids[0])

    def _open(self, num):
        if self.DLL: retVal = self.DLL.usb_relay_device_close_one_relay_channel(self.device, num)
        if retVal != 0:
         fail("Faied to close relay channel " + num)
        else: return 0

    def _close(self, num):
        if self.DLL: retVal = self.DLL.usb_relay_device_open_one_relay_channel(self.device, num)
        if retVal != 0:
         fail("Faied to close relay channel " + num)
        else: return 0

    def closeRelay(self, num):
      if 0 < num <= self.numRelays:
        self.blinking[num-1] = False
        retVal = self._close(num)
        if retVal != 0:
         fail("Faied to close relay channel " + num)
        else: return 0
    
    def openRelay(self, num):
      if 0 < num <= self.numRelays:
        self.blinking[num-1] = False
        retVal = self._open(num)
        if retVal != 0:
         fail("Faied to close relay channel " + num)
        else: return 0
    
    def closeAllRelays(self, *args):
      for i in range (1, self.numRelays+1):
        retVal = self.closeRelay(i)
        if retVal != 0:
           fail("Failed OPEN all!")
      return 0
    
    def openAllRelays(self, *args):
      for i in range (1, self.numRelays+1):
        retVal = self.openRelay(i)
        if retVal != 0:
           fail("Failed OPEN all!")
      return 0

    def blinkRelay(self, num, timing = 1):
        self.blinking[num] = True

    def noBlink(self, num):
        self.blinking[num] = False

    def __blink(self):
        while (self.blinkAlive):
          logging.log(self.loglevel, self.blinking)
          for i in range(1, self.numRelays+1):
            if self.blinking[i] == True:
              self._close(i)
              logging.log(self.loglevel, "Blink Close: " + str(i))

          time.sleep(1)

          logging.log(self.loglevel, self.blinking)
          for i in range(1, self.numRelays+1):
            if self.blinking[i] == True:
              self._open(i)
              logging.log(self.loglevel, "Blink Open: " + str(i))
          time.sleep(1)

        logging.info("Blink Thread stopped")


