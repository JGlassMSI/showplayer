#Cuelist.py

import logging
from waiting import wait, TimeoutExpired
from functools import partial
from enum import Enum
from pathlib import Path
import threading

#Number of seconds to wait between steps in manual control (ms)
MANUAL_CONTROL_WAIT_TIME_MS = 120000

class CuelistState(Enum):
    RUNNING = 1
    WAITING = 2
    STOPPED = 3


"""

Lists of runnable cues and their related functions

"""

class Cuelist():
    """
    Manages a list of cues for execution and tracks current cue.

    Attributes
    ---------
    cues : list <Cuelist_Item>
        The list of cues this Cuelist is responsible for, always executed in 
        order starting at index 0.

    name : string
        The title of this cuelist - used only for display and reference

    currentCueNum : int
        The index in self.cues of the last executed cue; which is also the cue
        whose postDelay timer is currently running. An index of -1 indicates
        that the cuelist is not currently running.

    listeners : list (CueListener)
        A list of objects that will receive a signal when the cue number changes.
        Useful for updating various displays which respond to the current cue
        number to change their highlighting    

    """

    def __init__(self, name="Unnamed Cuelist", cues = None):
        """Initialize the Cuelist object

        The list of cues will start empty, and the current cue will be 
        set to -1, to indicate that the list is not running

        Parameters
        ------
        None
        """

        if cues == None: self.cues = list()
        else: self.cues = cues

        self.name = name

        self.listeners = list()
        self.currentCueNum = -1
        self.timerList = list()
        self.loaded_from: str | Path = ""
        
        self.playbackStatus = CuelistState.STOPPED
        

    def __str__(self):
        return f"Cuelist \"{self.name}\": {len(self.cues)} cues, currently on cue {self.currentCueNum}"
 
    def __repr__(self):
        return f"Cuelist \"{self.name}\" with len {len(self.cues)} cues, currently on cue {self.currentCueNum}. Cues are: {self.cues}"

    def clearAll(self):
        self.cues = list()

    def isActive(self):
        """Is this Cuelist current running through cues?

        Parameters
        ----------
        None

        Returns
        -------
        bool
            True if the cuelist is currently running through cues, False otherwise
        
        """
        return self.currentCueNum != -1 and self.playbackStatus != CuelistState.STOPPED

    def runShow(self, master, inputs = None, manual_trigger=False):
        """
        Begins the process of actually running a cue stack.

        This method does some logging, then calls doStep(0) to begin the running
        of the cuestack.
        
        This method will not run if the cue stack is currently active.

        Parameters
        ----------
        None

        Returns
        -------
        None


        """
        if inputs == None: inputs = dict()
        if self.isActive():
            return
        elif len(self.cues) == 0:
            logging.warning("Attempted to run a Cuelist with 0 cues")
        else:
            self.doStep(0, inputs=inputs, master=master, manual_trigger=manual_trigger)

    def doStep(self, num, inputs = dict(), master=None, manual_trigger=False):
        """Runs a step of the CueList, then starts a timer for when to start the following cue

        Parameters
        ----------
        num : int
            The number of the cue to run. This will be the index of that cue in the Cuelist

        Returns
        -------
        None        

        """
        if num >= len(self.cues):
            self.currentCueNum = -1
            logging.info("Last cue of show has run, ending show run")
            for i in inputs.values():
                i.continueChecking = False
                i.t.stop()
            self.emitCue(master)
            self.halt() #sets playback state to STOPPED
            return
        else:
            logging.info(f"Running cue number {num} with master {master} and {manual_trigger= }")
            self.currentCueNum = num
            self.playbackStatus = CuelistState.RUNNING

            curCue = self.cues[self.currentCueNum]

            #tell listeners that the current cue has changed
            self.emitCue(master)

            if type(curCue) == Trigger_Item:
                for i in inputs.values():
                    i.continueChecking = True
                    i.beginNewTriggerMonitor()
            else:
                for i in inputs.values():
                    i.continueChecking = False
                    i.t.stop()

            #If this show was triggered manually, extend time between major 
            delay_time = curCue.postDelay/1000

            #action is none for wait or timeout cues
            if curCue.action != None:
                if manual_trigger and hasattr(curCue.action, 'func') and curCue.action.func == waitThenGo:
                    logging.info(f"Extendable delay detected. {curCue.action.args= }")
                    cueResult = waitOnInputThenContinue(curCue.action.args[0], MANUAL_CONTROL_WAIT_TIME_MS )
                else:
                    cueResult = curCue.action()
                if cueResult == "wait":
                    self.playbackStatus = CuelistState.WAITING
            else:
                cueResult = None
                
            if cueResult == "timeout":
                logging.info("Cue timed out, jumping to last cue of list")
                #self.doStep(len(self.cues)-1, inputs)
                self.doStep(len(self.cues)-1, inputs=inputs, master=master, manual_trigger = manual_trigger)
            else:
                #elif self.playbackStatus != CuelistState.WAITING:
                logging.info(f"Waiting {delay_time} seconds")

                if cueResult == "button press":
                    nextCueManualMode = True
                else:
                    nextCueManualMode = manual_trigger

                timer = threading.Timer(delay_time, self.doStep, args=[num+1, inputs, master, nextCueManualMode])
                timer.start()
                #nextFunc =  partial(self.doStep, num+1, inputs=inputs, master=master)
                #nextFunc.__name__ = 'nextFunction'
                #master.after(curCue.postDelay, nextFunc)

    def halt(self):
        """Halts all of the currently executing actions in the cuelist to prevent further execution
        """
        #for t in self.timers:
            #t.cancel()

        self.playbackStatus = CuelistState.STOPPED
        self.timerList = list()


    def addListener(self, listener):
        """Adds a listener object, which will receive signals based on the current cue when it changes

        Args:
            listener (CueListener): The object to signal
        """

        if listener not in self.listeners: self.listeners.append(listener)
        logging.debug(f"Cuelist {self.name} has added listener {listener}")

    def removeListener(self, listener):
        """If the given listener is in this cuelist's list of listeners, removes it

        Args:
            listener (CueListener): The listener to be removed
        """

        if listener in self.listeners: self.listeners.remove(listener)

    def emitCue(self, master):
        logging.debug(f"Emitting Cue {self.currentCueNum} to listeners: {self.listeners} with master {master}")
        for lis in self.listeners:
            logging.debug(f"Cuelist {self.name} is sending cue number {self.currentCueNum} to listener {lis}")
            lis.cueSignal(self.currentCueNum, master)

    def __getitem__(self, item):
        """Subscripting a Cuelist item returns the cue with the given index

        Args:
            item (int): Index of the cue to be returned

        Returns:
            Cuelist_Item: The cue with the given index, if it exists.
        """
        return self.cues[item]

    def get(self, item, default=None):
        """Wrapper for __getitem__ which returns a Nonetype object if the index is out of range

        Args:
            item (int): Index of the cue to be returned

        Returns:
            Cuelist_Item: The cue with the given index, or None if the index is out of range
        """
        if item >= 0 and item < len(self.cues): return self.cues[item]
        else: return None
    
    def __len__(self):
        """Return the number of cues in this cuelist

        Returns:
            int: Number of cues in self.cues
        """
        return len(self.cues)

class Cuelist_Item():

    def __init__(self, name="", action = None, postDelay = 20):

        self.name = name
        self.action = action

        #Number of milliseconds after this cue runs before the next cue can run.
        #This should be used to allow for behaviors of the action sender, i.e. time to
        #Send a serial message, toggle a relay, etc.
        #Longer pauses and actual cueing should use a Delay_Item
        self.postDelay = postDelay

    def __str__(self):
        return (f"Cuelist_Item: <name={self.name} action={self.action} postDelay={self.postDelay}>")

    def __repr__(self):
        return (f"Cuelist_Item @ {id(self)} <name={self.name} action={self.action} postDelay={self.postDelay}>")

    def __getstate__(self):
        myDict = self.__dict__
        if 'init' in str(myDict['action']):
            logging.info(f"Found 'init' in action: {str(myDict['action'])}")
            myDict['action'] = ("init", 0)
            print(myDict['action'])
        elif 'Serial' in str(myDict['action']):
            logging.info(f"Found 'serial' in action: {str(myDict['action'])}")
            myDict['action'] = ("serial", *myDict['action'].args)
            print(myDict['action'])
        return  myDict

    def __setstate__(self, state):
        self.__dict__ = state

class Delay_Item(Cuelist_Item):

    def __init__(self, name="Delay", postDelay=1000):
        super().__init__(name=name, action=None, postDelay=postDelay)

class Label_Item(Cuelist_Item):

    def __init__(self, name="", labelText = "LABELTEXT"):
        super().__init__(name=name, action=None, postDelay=0)
        self.labelText = labelText

#-----TIME DELAY FUNCTIONS------

'''def tkWaitOnInputThenTimeout(inputFunction, timeoutTime = 120, master=None):
    if master == None:
        raise ValueError(f"tkWait called with master still None: \n{traceback.format_exc()}")
    else:
        logging.debug(f"tkWait waiting for {timeoutTime} seconds with input functino {inputFunction}")
        '''

def waitOnInputThenContinue(inputFunction, timeoutTime = 120000):
    logging.info(f"Waiting for input for {round(timeoutTime)} milliseconds then timing out")
    try:
        wait(inputFunction, sleep_seconds=.25, timeout_seconds=timeoutTime/1000)
    except TimeoutExpired as err:
        logging.debug("waitOnInputThenContinue timed out waiting for input")
        return "timeout"
    else:
        logging.info("Button press detected")
        return "button press"

def waitThenGo(inputFunction, timeoutTime = 120000):
    logging.info(f"Waiting for input for {round(timeoutTime)} seconds then continueing till next cue")
    try:
        wait(inputFunction, sleep_seconds=.25, timeout_seconds=timeoutTime/1000)
    except TimeoutExpired as err:
        logging.debug("waitOnInputThenContinue timed out waiting for input")
        return "continue"
    else:
        logging.info("Button press detected")
        return "button press"

class Trigger_Item(Cuelist_Item):
    def __init__(self, inputFunction, name="Trigger Item", labelText = "TRIGGERTEXT", timeoutTime = 120000):
        super().__init__(name=name, action=partial(waitOnInputThenContinue, inputFunction, timeoutTime), postDelay=0)
        self.labelText = labelText
        self.inputFunction = inputFunction
        self.timeoutTime = timeoutTime

class Delay_Or_Skip_Item(Cuelist_Item):
    def __init__(self, inputFunction, name="Delay or Skip Item", labelText = "DELAYORSKIPTEXT", timeoutTime = 30000):
        super().__init__(name=name, action = partial(waitThenGo, inputFunction, timeoutTime), postDelay = 0)
        self.labelText = labelText
        self.inputFunction = inputFunction
        self.timeoutTime = timeoutTime


if __name__=='__main__':
    
    from time import sleep

    logging.basicConfig(level=logging.DEBUG)

    CL = Cuelist()

    def twoSecondsTrue():
        return False

    CL.cues.append(Cuelist_Item("First Cue"))
    CL.cues.append(Delay_Item( "Delay Cue", 5000))
    CL.cues.append(Label_Item("Label", "LabelText"))
    CL.cues.append(Trigger_Item(twoSecondsTrue, "Trigger Cue", "Trigger Text", 5))
    CL.cues.append(Label_Item("Cue 5", "Label"))
    CL.cues.append(Delay_Item("Delay again", 3000))
    CL.cues.append(Label_Item("Last Cue", "Cue 7"))

    CL.runShow(master=None)

    #sleep(10)
