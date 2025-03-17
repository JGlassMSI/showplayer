import tkinter as tk
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog
from functools import partial, partialmethod

import json
import pickle

from .plane_controls import *
from .WrappedPartial import *
from .CueText import *
from .Cuelist import *
from .configurationWindow import *
from .inputs import *
from .TimerClass import *
from .tkextensions import VerticalScrolledFrame
from .autoDialog import *

from datetime import datetime, timedelta
from datetime import time as dttime
import ntpath
import sys
from os import path, makedirs
import logging
import logging.handlers
import atexit


class showplayer(tk.Frame):
    def __init__(self, master=None, title="Title"):
        super().__init__(master)
        self.master = master
        #self.master.title = title
        
        #These are here so they can be freely referenced by the initialzation objects, perhaps before they are created
        self.showList = [Cuelist("Empty Cuelist")]
        self.currentShow = self.showList[0]
        self.showBoxes = list()
        self.nextLabel= tk.Label(self,text="")
        self.nextShowTime = None
        self.timeVar = tk.StringVar(self.master)
        self.conf = {}
        self.controller = SerialPlaneController()
        #self.lxController = RelayLightingController()
        self.lxController = NetworkLightingController()
        self.inputs = {'serial': PlaneSerialInput()}
        self.runShowOnButtonInput = False
        self.showRunning = False
        self.inputStarter = TimerClass(self.checkForInputToStartShow, None, delay=.2)

        self.grid()
        self.create_widgets()
        self.master.focus_set()
        self.time()

    #TODO Need to adapt this to multiple cuelists
    def time(self):
        self.timeVar.set(str(datetime.now().replace(microsecond=0)))
        

        if str(self.timeVar.get()) == str(self.nextShowTime) and self.dayVars[self.days[datetime.today().weekday()]].get() != "Disabled":
            if datetime.now() > self.todayEndTime:
                logging.debug("Would run now, but we are past the latest run time of the day.")
            else:
                logging.info(f"Current time {self.timeVar.get()} equals next show time {self.nextShowTime}, running show")
                self.runShow()

        if self.controller.ser != None:
            s = self.controller.ser
            if s.isOpen(): self.serialNameVar.set(f"{s.port}  is OPEN @ {s.baudrate }baud, {s.bytesize} bits, {s.parity} parity, {s.stopbits} stopbit(s)")
            else: self.serialNameVar.set(f"{self.controller.ser.port}  {self.controller.ser.baudrate}baud  is NOT OPEN")
        else:
            self.serialNameVar.set(f"No Serial Port Active")

        if datetime.now().second == 15 or datetime.now().second == 45:
            self.updateDailyTimes("Heartbeat Timer")
        self.master.after(1000, self.time)

    def clearAllListboxSteps(self, lb):
        if lb.size() > 0:
            for i in range(lb.size()-1, -1, -1):
                lb.delete(i)

    def getShowIndex(self, showName):
        logging.debug("Getting index in showList for " + showName)
        #return next((index for (index, d) in enumerate(self.showList) if d['name'] == showName), None)
        return [i for i, d in enumerate(self.showList) if d.name == showName][0]

    def setInspectShow(self, showName):
        index = self.getShowIndex(showName)
        self.inspectShowVar.set(index)

    def updateShowStepDisplay(self, *args):
        #showName = self.inspectShowVar.get()
        logging.debug("Updating show step display to " + str(self.currentShow.name))
        self.stepText.cuelist = self.currentShow
        self.stepText.parseCuelist()

        """ for i in range(len(self.currentShow)):
            step = self.currentShow[i]
            #step = self.show['steps'][i]
            if step[0] == 'delay': stepType = 'delay'
            elif step[0] == 'label': stepType = 'label'
            elif step[0] == 'command': stepType = 'command'
            else: stepType = 'instruction'

            linetag = "line"+str(i)
            self.stepText.tag_config(linetag, background="#41C73A") #highlighted line color
            self.stepText.tag_lower(linetag)

            if stepType == 'label': 
                self.stepText.insert(tk.END,str('Label'), (stepType,linetag))
                self.stepText.insert(tk.END, "\t" + str(step[1]).upper(), (stepType,linetag))
            elif stepType == 'delay':
                self.stepText.insert(tk.END,str('Delay'), (stepType,linetag))
                self.stepText.insert(tk.END,"\t"+step[1], (stepType,linetag))
                if step[0] == 'delay': self.stepText.insert(tk.END," (ms)", (stepType,linetag))
            elif stepType == 'command':
                self.stepText.insert(tk.END,str(step[1][0]), (stepType,linetag))
                self.stepText.insert(tk.END,"\t"+step[1][1], (stepType,linetag))
            self.stepText.insert(tk.END,"\n", (stepType,linetag)) """

    def clearShowStepDisplay(self, *args):
        logging.debug("Clearing show step display")
        self.stepText.clearSteps()

    def updateInspectStepDisplay(self, *args):
        showName = self.inspectShowVar.get()
        logging.debug("Updating inspect step display to " + str(showName))
        
        selectedShow = self.showList[self.getShowIndex(showName)]

        self.inspectStepText.cuelist = selectedShow

        logging.debug(f"About to parse {len(selectedShow)} cues")
        self.inspectStepText.parseCuelist()
        logging.debug("Done parsing")

        """ for i in range(len(selectedShow['steps'])):
            step = selectedShow['steps'][i]
            #step = self.show['steps'][i]
            if step[0] == 'delay': stepType = 'delay'
            elif step[0] == 'label': stepType = 'label'
            elif step[0] == 'command': stepType = 'command'
            else: stepType = 'instruction'

            linetag = "line"+str(i)
            self.inspectStepText.tag_config(linetag, background="#41C73A") #highlighted line color, green
            self.inspectStepText.tag_lower(linetag)

            if stepType == 'label': 
                self.inspectStepText.insert(tk.END, "\t" + str(step[1]).upper(), (stepType,linetag))
            elif stepType == 'delay':
                self.inspectStepText.insert(tk.END,str('Delay'), (stepType,linetag))
                self.inspectStepText.insert(tk.END,"\t"+step[1], (stepType,linetag))
                if step[0] == 'delay': self.inspectStepText.insert(tk.END," (ms)", (stepType,linetag))
            elif stepType == 'command':
                self.inspectStepText.insert(tk.END,str(step[1][0]), (stepType,linetag))
                self.inspectStepText.insert(tk.END,"\t"+step[1][1], (stepType,linetag))
            self.inspectStepText.insert(tk.END,"\n", (stepType,linetag)) """

    def updateShowListDisplays(self):
        #Update list of shows on management tab
        for l in [self.showManageList,]:
            self.clearAllListboxSteps(l)
            logging.debug("Deleted all listbox steps")
            for s in self.showList:
                logging.debug(f"Re-adding show to listbox: {s}")
                l.insert(tk.END,s.name)

        #update list of shows on inspector tab
        self.inspectShowSelect['menu'].delete(0, "end")
        for s in self.showList:
            self.inspectShowSelect['menu'].add_command(label=s.name, command=partial(self.inspectShowVar.set, s.name))

        #update list of shows for default on schedule tab
        self.defaultShowList['menu'].delete(0, "end")
        for s in self.showList:
            self.defaultShowList['menu'].add_command(label=s.name, command=partial(self.defaultShowVar.set, s.name))	

        #update lists of shows in special-schedule-per-day frames on Scheduling tab
        for d in self.days:
            l = self.dayFrames[d]['showList']
            l['menu'].delete(0,"end")
            for s in self.showList:
                l['menu'].add_command(label=s.name, command=partial(self.dayFrames[d]['showVar'].set, s.name))		

    def updateScheduleSelections(self, *args):
        oldShow = self.currentShow
        def getNamedSchedule(name):
            logging.debug(f"Getting schedule item with name {name}")
            return next((item for item in self.showList if item.name == name), None)

        #Update label on operations tab:
        weekday = self.days[datetime.today().weekday()]
        mode = self.dayVars[weekday].get()
        if mode == 'Special':
            show = self.dayFrames[weekday]['showVar'].get()
            self.schedLabel['text'] = "Today's show is: " + show + " (set special for this day of the week)"
            self.currentShow = getNamedSchedule(show)
            self.runButton['state'] = 'normal'

            #Handle listeners so that stepText responds to (highlights) the current cue
            self.currentShow.addListener(self.stepText)
            self.stepText.cuelist = self.currentShow
            if oldShow is not self.currentShow: oldShow.removeListener(self.stepText)

            
        elif mode == 'Default':
            show = self.defaultShowVar.get()
            self.schedLabel['text'] = "Today's show is: " + show + " (default)"
            self.currentShow = getNamedSchedule(show)
            self.runButton['state'] = 'normal'

            self.currentShow.addListener(self.stepText)
            self.stepText.cuelist = self.currentShow
            if oldShow is not self.currentShow: oldShow.removeListener(self.stepText)
        elif mode == 'Disabled':
            self.schedLabel['text'] = "Shows are disabled today"
            self.runButton['state'] = 'disabled'
        else: logging.warning("Unknown value for self.dayVars[weekday]: " + mode)

        logging.info(f"Current Show is now {self.currentShow} with listeners {self.currentShow.listeners}")

        self.updateDailyTimes(*args)
        self.updateShowListDisplays()
        self.updateShowStepDisplay()

        if mode == 'Disabled': self.clearShowStepDisplay()

    def updateDailyTimes(self, *args):
        logging.debug("Updating daily times - triggered by change in: " + str(args))
        weekday = self.days[datetime.today().weekday()]
        mode = self.dayVars[weekday].get()

        if mode == 'Special':
            if (self.dayFrames[weekday]['startVar'].get()) == 1: #checkbox is checked in special program:
                #self.todayStartTime = time(hour=self.dayFrames[weekday]['start_hourstr'], minute=self.dayFrames[weekday]['start_minstr'])
                self.todayStartTime = datetime.now().replace(hour=int(self.dayFrames[weekday]['start_hourstr'].get()), minute=int(self.dayFrames[weekday]['start_minstr'].get()), second=0, microsecond=0)
            else: #Checkbox is unchecked, start immediately
                self.todayStartTime = datetime.now()
            logging.debug("Today's start time (special): " + str(self.todayStartTime))

            if (self.dayFrames[weekday]['endVar'].get()) == 1: #checkbox is checked in special program:
                #self.todayStartTime = time(hour=self.dayFrames[weekday]['start_hourstr'], minute=self.dayFrames[weekday]['start_minstr'])
                self.todayEndTime = datetime.now().replace(hour=int(self.dayFrames[weekday]['end_hourstr'].get()), minute=int(self.dayFrames[weekday]['end_minstr'].get()), second=0, microsecond=0)
            else: #Checkbox is unchecked, start immediately
                self.todayEndTime = datetime.now()
            logging.debug("Today's end time (special): " + str(self.todayStartTime))

            self.todayIncrement = timedelta(minutes=int(self.dayFrames[weekday]['every_minstr'].get()))
            logging.debug("Today's increment (special): " + str(self.todayIncrement))

        elif mode == 'Default':
            if (self.defaultStartVar.get()) == 1: #checkbox is checked in special program:
                #self.todayStartTime = time(hour=self.dayFrames[weekday]['start_hourstr'], minute=self.dayFrames[weekday]['start_minstr'])
                self.todayStartTime = datetime.now().replace(hour=int(self.start_hourstr.get()), minute=int(self.start_minstr.get()), second=0, microsecond=0)
            else: #Checkbox is unchecked, start immediately
                self.todayStartTime = datetime.now()
            logging.debug("Today's start time (Default): " + str(self.todayStartTime))

            if (self.defaultEndVar.get()) == 1: #checkbox is checked in special program:
                #self.todayStartTime = time(hour=self.dayFrames[weekday]['start_hourstr'], minute=self.dayFrames[weekday]['start_minstr'])
                self.todayEndTime = datetime.now().replace(hour=int(self.end_hourstr.get()), minute=int(self.end_minstr.get()), second=0, microsecond=0)
            else: #Checkbox is unchecked, start immediately
                self.todayEndTime = datetime.now().replace(hour=23,minute=59)
            logging.debug("Today's end time (Default): " + str(self.todayEndTime))

            self.todayIncrement = timedelta(minutes=int(self.every_minstr.get()))
            logging.debug("Today's increment (Default): " + str(self.todayIncrement))

        elif mode == 'Disabled':
            self.nextLabel['text'] = "No showtimes for today (disabled)."

        else: raise ValueError("Uknown mode: " + mode)

        if mode != 'Disabled':
            if self.todayStartTime >= datetime.now():
                self.nextShowTime = self.todayStartTime
                self.nextLabel['text'] = f"The next show will be at {self.nextShowTime} (first of the day)"
            else:
                tempTime = self.todayStartTime
                while tempTime < datetime.now():
                    tempTime += self.todayIncrement
                self.nextShowTime = tempTime
                self.nextLabel['text'] = f"The next show will be at {self.nextShowTime}"
    
    def playerInputFunction(self):
        result = False
        for i in self.inputs.values():
            #We want to make sure we iterate over all the inputs, so all their flags are cleared
            result = result or i.retrieveTriggerFlag()
        return result

    def importShow(self, fileGiven = None):
        if fileGiven == None: f = filedialog.askopenfilename(filetypes=[("727 Shows",'*.727show'),('All Files','*')])
        else: f = fileGiven
        if f is None or f == '':
            return

        with open(f, mode="rb") as infile:
            try:
                newShow = pickle.load(infile)
                newShow.name = ntpath.basename(f.split('.')[0])
                logging.debug(f"Loaded new show: {newShow}")
                for cue in newShow.cues:
                    if cue.action != None:
                        if type(cue.action) == tuple:
                            if cue.action[0] == 'serial':
                                command = cue.action[1]
                                cue.action = partial(self.controller.sendDOSCommand, command)
                            elif cue.action[0] == 'init':
                                cue.action = self.controller.initThePlane
                        else:        
                            if 'Serial' in str(cue.action.func):
                                if 'DOS' in str(cue.action.func)  and len(cue.action.args) > 0:
                                    cue.action = partial(self.controller.sendDOSCommand, cue.action.args[0])
                                    logging.debug (f"Replaced cue action with new one with args {cue.action.args}")
                                elif 'init' in str(cue.action.func):
                                    cue.action = self.controller.initThePlane
                                    logging.debug("Replaced init action with new one in current serial port??")
                                else: raise ValueError(f"Could not recognize serial function {cue.action.func}")
                            elif type(cue) == Trigger_Item:
                                cue.action = partial(waitOnInputThenContinue, self.playerInputFunction, cue.timeoutTime)
                                logging.debug(f"Replaced input trigger with new input function with args {cue.action.args}")
                            elif type(cue) == Delay_Or_Skip_Item:
                                cue.action = partial(waitThenGo, self.playerInputFunction, cue.timeoutTime)
                                logging.debug(f"Replaced WaitThenGo with new input function with args {cue.action.args}")

                print(">>>>>>")
                print(newShow.cues)


                



                """ inputDict = json.load(infile)
                logging.debug(f"Loaded dictionary: {(str(inputDict))}")
                stepList = inputDict['steps']
                name = inputDict.get('name','Show:' + f.split('/')[-1]) """
            except ValueError as e:	
                msg = mb.showerror("Unable to load file",
                    "Unable to load the specified file - please check the format and try again")
            else:
                errname = ntpath.basename(f.split('.')[0])
                self.showList.append(newShow)
                self.updateShowListDisplays()
                #self.updateShowStepDisplay()

    def deleteShow(self):
        selection = self.showManageList.curselection()
        if selection == ():
            return
        else:
            del self.showList[selection[0]]
        self.updateShowListDisplays()

    def saveConfig(self):
        #Make JSON file of all relevant attributes, load into show
        #Attributes are:
        #	-Showlist, with all included shows
        #	-Scheduling Paramters, including:
        #		-Modes per day of the week
        #		-Schedule info day of week, including show, checkboxes, start and end times
        
        output = {}
        output['showList'] = [c.name for c in self.showList]
        output['defaultShow'] = self.defaultShowVar.get()
        output['runEvery'] = self.every_minstr.get()
        output['startCheck'] = self.defaultStartVar.get()
        output['startHour'] = self.start_hourstr.get()
        output['startMin'] = self.start_minstr.get()
        output['endCheck'] = self.defaultEndVar.get()
        output['endHour'] = self.end_hourstr.get()
        output['endMin'] = self.end_minstr.get()
        output['outputMode'] = self.outputModeVar.get()

        output['outputPort'] = self.controller.ser.port
        output['inputPort'] = self.inputs['serial'].ser.port

        output['runOnButton'] = self.runShowOnButtonInput

        for d in self.days:
            output[d] = {}
            output[d]['scheduleMode'] = self.dayVars[d].get()
            output[d]['showSelection'] = self.dayFrames[d]['showVar'].get()
            #logging.debug(f"Adding {d}:{self.dayVars[d].get()} to output")
            output[d]['runEvery'] = self.dayFrames[d]['every_minstr'].get()
            output[d]['startCheck'] = self.dayFrames[d]['startVar'].get()
            output[d]['startHour'] = self.dayFrames[d]['start_hourstr'].get()
            output[d]['startMin'] = self.dayFrames[d]['start_minstr'].get()
            output[d]['endCheck'] = self.dayFrames[d]['endVar'].get()
            output[d]['endHour'] = self.dayFrames[d]['end_hourstr'].get()
            output[d]['endMin'] = self.dayFrames[d]['end_minstr'].get()

        f = filedialog.asksaveasfilename(defaultextension=".727config", filetypes=[("727 Configurations",'*.727config'),('All Files','*')])
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        
        with open(f, mode="w", encoding='utf-8') as outfile:
            json.dump(output, outfile)
        self.updateConf('lastConfig', str(f))

    def loadConfigDialog(self):
        f = filedialog.askopenfilename(filetypes=[("727 Configurations",'*.727config'),('All Files','*')])
        if f is None or f == '':
            return
        else: self.loadConfig(f)

    def loadConfig(self, f):
        with open(f, mode="r", encoding='utf-8') as infile:
            #TODO: Make this try/catch block handle mismatch dictionaries in some graceful way.
            try:
                inputDict = json.load(infile)
                logging.debug(inputDict)

                for s in inputDict['showList']:
                    if s != 'Empty Cuelist':
                        try:
                            self.importShow(s+'.727show')
                        except FileNotFoundError as err:
                            logging.info(f"Issue loading file {s}, {err} skipping")

                self.defaultShowVar.set(inputDict['defaultShow'])
                self.every_minstr.set(inputDict['runEvery'])
                self.defaultStartVar.set(inputDict['startCheck'])
                self.start_hourstr.set(inputDict['startHour'])
                self.start_minstr.set(inputDict['startMin'])
                self.defaultEndVar.set(inputDict['endCheck'])
                self.end_hourstr.set(inputDict['endHour'])
                self.end_minstr.set(inputDict['endMin'])
                self.outputModeVar.set(inputDict['outputMode'])

                self.runShowOnButtonInput = inputDict['runOnButton']
                self.setInputMonitoring(value = inputDict['runOnButton'])

                logging.debug(">>>>>END of globals, loading by day:>>>>")
                for d in self.days:
                    self.dayVars[d].set(inputDict[d]['scheduleMode'])
                    logging.debug(f"--------{d}:{self.dayVars[d].get()}")
                    self.dayFrames[d]['showVar'].set(inputDict[d]['showSelection'])
                    self.dayFrames[d]['every_minstr'].set(inputDict[d]['runEvery'])
                    self.dayFrames[d]['startVar'].set(inputDict[d]['startCheck'])
                    self.dayFrames[d]['start_hourstr'].set(inputDict[d]['startHour'])
                    self.dayFrames[d]['start_minstr'].set(inputDict[d]['startMin'])
                    self.dayFrames[d]['endVar'].set(inputDict[d]['endCheck'])
                    self.dayFrames[d]['end_hourstr'].set(inputDict[d]['endHour'])
                    self.dayFrames[d]['end_minstr'].set(inputDict[d]['endMin'])

                self.updateConf('lastConfig', str(f))
            except Exception as e:
                raise(e)
            
            #Handle serial inputs/outputs
            try:
                self.controller.ser.port = inputDict['outputPort']
                self.inputs['serial'].ser.port = inputDict['inputPort']
            except Exception as e:
                mb.showerror("Error Loading Serial Ports", f"Could not open one or more serial ports from configuration; please adjust the serial ports in preferences and re-save the configuration.\nError:{e}")

        self.updateShowListDisplays()
        self.updateScheduleSelections()

    def validateShow(self, showErrors=False):
        #TODO Fix or Remove Validation
        return True

        """ if len(self.currentShow) <= 0:
            if self.showErrors: msg = mb.showerror("No Show Present",
                    "The current show has no steps - please import a show before validating.")
        else:
            logging.info("Beginning to validate show")

            for i in range(len(self.currentShow)):
                retVal = self.validateStep(self.currentShow[i])
                if retVal == False: return False

            logging.info("Show successfully validated")
            return True """

    def validateStep(self, step):
        if step[0] == 'command': #if step[0] != 'delay' and step[0] != 'label':
            inst = step[1][0]
            if inst not in SerialPlaneController.com():
                if self.showErrors: msg = mb.showerror("Invalid Instruction", str(inst) + " is not a valid instruction according to the plane controller")
                return False
        elif step[0] == 'delay':
            if step[1] == '': 
                if self.showErrors: msg = mb.showerror("Invalid Delay", "The value for delay is blank.")
                return False
            else:
                try:
                    x = int(step[1])
                except ValueError as e:
                    if showErrors: msg = mb.showerror("Invalid Delay", str(step[1]) + " is not a valid value for a delay.")	
                    return False
                return True
        elif step[0] == 'label':
            return True
        else:
            if showErrors: msg = mb.showerror("Invalid Part", str(step[0]) + " is not a valid instruction, 'delay', or 'label'.")	
            return False

    def runShow(self, manual_trigger=False):
        logging.info(f"Running show at top level with {manual_trigger= }")

        if len(self.currentShow) <= 0:
            msg = mb.showerror("No Show Present",
                    "The current show has no steps - please import a show before running.")
        elif self.showRunning:
            logging.info(f"Wanted to run show at {str(self.timeVar.get())} but show is already running")
        else:
            logging.info("Beginning to run show")
            
            #self.stopButton['state'] = 'normal'
            self.showRunning = True
            if not self.validateShow(showErrors=True):
                msg = mb.showerror("Show is Invalid",
                    "Your current showfile has errors - please fix and rerun")
                return

            self.currentShow.addListener(self)
            self.currentShow.runShow(inputs = self.inputs, master=self.master, manual_trigger=manual_trigger)
            #self.stepText.updateHighlight()

    def doStep(self, stepNum, totalSteps=None):
        if totalSteps == None: totalSteps = len(self.currentShow)

        if stepNum >= totalSteps: 
            logging.info("Show completed successfully")
            self.master.after(500, self.unhighlightLastLine)
            self.stopButton['state'] = 'disabled'
            self.after(60*1000, self.updateDailyTimes)
            return
        elif not self.showRunning:
            self.stopButton['state'] = 'disabled'
            self.updateDailyTimes()
        else:
            self.highlightOnlyLine(stepNum)
            step = self.currentShow[stepNum]
            wasError = False

            if step[0] == 'delay':
                logging.info("Delaying for " + str(step[1]) + " milliseconds")
                self.master.after(step[1], self.doStep, stepNum+1)
            elif step[0] == 'label':
                logging.info("Label " + str(step[0]))
                self.doStep(stepNum+1)
            elif step[0] == 'command':
                logging.info(f"Running command:  {step[1][0]}")
                if self.outputModeVar.get() == 'live':
                    try:
                        self.controller.sendCommand(step[1][0], step[1][1])
                    except serial.serialutil.SerialException as e:
                        logging.warning(e)
                        msg = mb.showerror("Serial Port Error",
                            "There was an error with the Serial Port when sending, please try again." + 
                            "\n Error was: " + str(e))
                        wasError = True
                    except OSError as e:
                        logging.warning(e)
                        msg = mb.showerror("OS Error",
                            "There was an error in opening or sending via the serial port" + 
                            "\n Error was: " + str(e))
                        wasError = True
                    except ValueError as e:
                        logging.warning(e)
                        msg = mb.showerror("Command Error",
                            "There was an error with the content or format of the command; double-check" +
                            "your command syntax and try again." 
                            "\n Error was: " + str(e))
                        wasError = True	

                else:
                    logging.info("Not running in live; no actual commands were output")
                if not wasError: self.doStep(stepNum+1)

            #elif step[0] != 'dewlay' and step[0] != 'label':
            #	inst = step[0]
            #	logging.info("Running instruction " + str(inst))
            #	self.doStep(stepNum+1)
            else: raise ValueError("Something went wrong - step given as " + str(step[0]) + " while running")

    def stopShow(self):
        logging.debug("Stopping Show due to Halt button press")
        self.stopButton['state'] = 'disabled'
        self.showRunning = False
        for i in range(len(self.currentShow)):
            linetag = "line"+str(i)
            self.stepText.tag_lower(linetag)
        logging.debug("Removing highlight from last run line of show")
        self.currentShow.halt()
        self.currentShow.removeListener(self)

    def cueSignal(self, cueNum, master):
        logging.debug(f"Showplayer received cueSignal {cueNum} from a Cuelist")
        if cueNum == -1:
            self.stopShow()
            if self.runShowOnButtonInput:
                self.inputStarter.stop()
                self.inputStarter = TimerClass(self.checkForInputToStartShow, None, delay=.2)
                self.inputStarter.run()
                logging.debug("InputStarter has started at end of Cuelist")

    def setDayScheduleMode(self, *args):
        logging.debug("Updating schedule mode of days - triggered by change in: " + str(args))
        #logging.debug("New value is: " + self.dayVars[args[0]].get())

        day = args[0]
        #print (self.dayFrames[day])

        if self.dayVars[args[0]].get() != 'Special': 
            logging.debug("Hidden Mode")
            self.dayFrames[day]['frame'].grid_remove()
        else:
            logging.debug("Special schedule needed, gridding frame")
            self.dayFrames[day]['frame'].grid()

        self.updateScheduleSelections(args)

    def sendTrigger(self, command1, command2, delay=1000):
        command1()
        self.master.after(delay, command2)

    def create_fonts(self):
        self.basicFont = tkFont.Font(family="Lucida Grande", size=13)
        self.smallButtonFont = tkFont.Font(family="Lucida Grande", size=11)
        self.bigButtonFont = tkFont.Font(family="Lucida Grande", size=20)
        self.tabHeaderFont = tkFont.Font(family="Lucida Grande", size=20)
        self.tabSubsectionFont =  tkFont.Font(family="Lucida Grande", size=16)

    def create_globals(self):
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.scheduleModes = ['Default', 'Special', 'Disabled']
        self.dayFrames = {}
        self.dayVars = {}
        self.todayEvery = timedelta()
        self.todayStartTime = dttime()
        self.todayEndTime = dttime()
        self.nextShowTime = dttime()
        self.defaultStartVar = tk.IntVar(self.master)
        self.defaultEndVar = tk.IntVar(self.master)
        self.showErrors = True
        self.showRunning = False

        self.activeButtonColor = "#AAFFAA"
        self.inactiveButtonColor = "#FFFFFF"
        self.cancelButtonColor = "#FFAAAA"

    def create_title(self):
        self.titleStyle = tkFont.Font(family="Lucida Grande", size=20)
        self.titleLabel = tk.Label(self.master, text="727 Controller Automation Controller", font=self.titleStyle)
        self.titleLabel.grid(column=0, row=0, columnspan=3)

    def create_menubar(self):
        self.menubar = tk.Menu(self.master)

        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        #self.fileMenu.add_command(label="New",command=self.newFile)
        #self.fileMenu.add_command(label="Export",command=self.exportFile)
        self.fileMenu.add_command(label="Save Configuration", command=self.saveConfig)
        self.fileMenu.add_command(label="Load Configuration", command=self.loadConfigDialog)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Import Show",command=self.importShow)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit",command=exit)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)

        self.optionsMenu = tk.Menu(self.menubar, tearoff=0)
        self.optionsMenu.add_command(label="Preferences", command = self.openConfigWindow)
        self.menubar.add_cascade(label="Options", menu=self.optionsMenu)

        #self.stepsMenu = tk.Menu(self.menubar, tearoff=0)
        #self.stepsMenu.add_command(label="Clear All Steps", command = self.clearAllSteps)
        #self.menubar.add_cascade(label="Steps", menu=self.stepsMenu)

        self.master.config(menu=self.menubar)

    def create_footer(self):
        self.footerFrame = tk.Frame(self.master)
        self.footerFrame.grid(column=0,row=2,sticky='w')

        self.footerLabel = tk.Label(self.footerFrame,text="Showplayer v.0.1.1", anchor='w')
        self.footerLabel.grid(row=0,column=0)
        self.footerFrame.grid_columnconfigure(0, weight=1)

        self.timeLabel = tk.Label(self.footerFrame,text="",textvariable=self.timeVar, anchor='e')
        self.timeLabel.grid(row=0,column=1,padx=10, sticky='e')
        self.footerFrame.grid_columnconfigure(1, weight=1)

        self.serialNameVar = tk.StringVar()
        self.serialNameVar.set("Serial Name Here")
        self.serialLabel = tk.Label(self.footerFrame,text="",textvariable=self.serialNameVar, anchor='e')
        self.serialLabel.grid(row=0,column=2,padx=10,sticky='e')
        self.footerFrame.grid_columnconfigure(2, weight=1)

    def create_notebook(self):
        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('Lucida Grande','14') )

        self.book = ttk.Notebook(self.master)
        self.book.grid(row=1, column=0, sticky='ew')

    def create_manualtab(self):
        #-----Manual Tab-----
        # This tab will allow the user to manually send individual action and cancel messages
        # To control inidivudual actions of the plane
        # It should display the actual serial command being sent
        # This will, of necessity, be fairly strongly coupled to the Plane Controller Architecture

        self.manFrame = tk.Frame(self.book,width=200,height=100)
        self.book.add(self.manFrame,text="Manual Control")

        self.manFrame.grid_columnconfigure(0, weight=1)
        self.manFrame.grid_rowconfigure(0, minsize=1, weight=1)
        self.manFrame.grid_rowconfigure(1, weight=1)

        self.fillFrame = tk.Frame(self.manFrame,width=200, height=0)
        self.fillFrame.grid(row=0,column=0,sticky='ew')
        self.manualInstructions = tk.Message(self.fillFrame, text="Clicking any of the Activate/Cancel buttons below will immediately send the corresponding" +
                                                 " request to the PLC in the belly of the 727 via serial",
                                                 font=self.basicFont)
        self.manualInstructions.pack(fill='x',expand=1)
        #self.fillFrame.grid_columnconfigure(0, weight=1)

        self.buttonFrame = tk.Frame(self.manFrame, width=200, height=100)
        self.buttonFrame.grid(row=1, column=0, sticky='nw')
        self.buttonFrame.grid_columnconfigure(0, weight=1)
        self.buttonFrame.grid_columnconfigure(1, weight=1, minsize=100)
        self.buttonFrame.grid_columnconfigure(2, weight=1)

        
        coms = self.controller.com()

        self.sepFrame = tk.Frame(self.buttonFrame, bg='black', relief="raised")
        self.sepFrame.grid(column=1, row=0, columnspan=int(len(coms)/2+1))

        row = 0
        column=0
        for c in coms:
            rowFrame = tk.Frame(self.buttonFrame)
            rowFrame.grid_columnconfigure(0, minsize=150)
            rowFrame.grid_columnconfigure(1, minsize=40)
            label = tk.Label(rowFrame,text=str(c),font=self.smallButtonFont, anchor='w')
            label.grid(column=0, row=0, sticky='w')

            actButton = tk.Button(rowFrame, text="Activate", font=self.basicFont, bg=self.activeButtonColor, command=partial(self.controller.sendCommand, c, 'activate'))
            actButton.grid(column=1, row=0)

            cancelButton = tk.Button(rowFrame, text="Cancel", font=self.basicFont, bg=self.cancelButtonColor, command=partial(self.controller.sendCommand, c, 'cancel'))
            cancelButton.grid(column=2, row=0)

            if row >= len(coms)/2:
                row=0
                column=2
            rowFrame.grid(column=column, row=row, sticky='w')

            row += 1
        initButton = tk.Button(self.buttonFrame, text="Init the Plane", font=self.basicFont, bg=self.activeButtonColor, command=self.controller.initThePlane)
        initButton.grid(column=0, row=row+1, rowspan=2, sticky='ew')

    def create_operationstab(self):
        #------OPERATIONS FRAME------
        # This frame will contain the following purposes:
        #	- Status Display:
        #		- Show currently running, not running, manual ops
        #		- Reason for running: scheduled, manual run, manual ops
        #	- Enable/disable override of running the show
        #	- Manual Show Triggering, pausing, stopping
        #	- Manual "init the plane"

        self.opFrame = tk.Frame(self.book,width=200,height=100)
        self.book.insert(self.scheduleFrame, self.opFrame,text="Operations")
        self.opFrame.grid_columnconfigure(0, weight=1)

        self.opHeaderFrame=tk.Frame(self.opFrame)
        self.opHeaderFrame.grid(row=0,column=0, sticky='ew')
        self.opHeaderFrame.grid_columnconfigure(0, weight = 1)

        todayText = "Today is " + datetime.today().strftime("%A, %B %d %Y")
        self.testLabel = tk.Label(self.opHeaderFrame, text=todayText, font=self.basicFont, anchor=tk.W)
        self.testLabel.grid(row=1, column=0, pady=5, sticky='w')

        weekday = self.days[datetime.today().weekday()]
        show = self.dayFrames[weekday]['showVar'].get()
        scheduleText = "Today's show is: " + show
        self.schedLabel = tk.Label(self.opHeaderFrame, text=scheduleText, font=self.basicFont, anchor=tk.W)
        self.schedLabel.grid(row=2, column=0, pady=5, sticky='w')

        self.nextLabel = tk.Label(self.opHeaderFrame, text="-", font=self.basicFont, anchor=tk.W)
        self.nextLabel.grid(row=4, column=0, pady=5, sticky='w')

        self.updateDailyTimes()

        self.showControlFrame = tk.Frame(self.opFrame)#, bg="#CCCCCC")
        self.showControlFrame.grid_columnconfigure(0, minsize=100, weight=1)
        self.showControlFrame.grid(row=1, column=0, sticky='nsew')

        self.modeLabel = tk.Label(self.showControlFrame, text="Output Mode", font = self.basicFont)
        self.modeLabel.grid(row=0,column=0, sticky='w')

        self.outputModeVar = tk.StringVar(self.master)
        self.outputModeVar.set('live')
        self.outputModeLive = tk.Radiobutton(self.showControlFrame, text='Live', variable=self.outputModeVar, value='live', font = self.basicFont)
        self.outputModeLive.grid(row=1, column=0, sticky='w')

        self.outputModeDebug = tk.Radiobutton(self.showControlFrame, text='Debug (No Serial Output)', variable=self.outputModeVar, value='debug', font = self.basicFont)
        self.outputModeDebug.grid(row=2, column=0, sticky='w')

        self.showButtonFrame = tk.Frame(self.showControlFrame)
        self.showButtonFrame.grid(row=3, column=0)

        self.runButton = tk.Button(self.showButtonFrame, text='RUN NOW', command=self.runShow, font=self.bigButtonFont, bg="#AAFFAA")
        self.runButton.grid(row=0,column=0, sticky='nsew',pady=10)

        self.stopButton = tk.Button(self.showButtonFrame, text='HALT', command=self.stopShow, font=self.bigButtonFont, bg="#FFCCCC")
        self.stopButton['state'] = 'disabled'
        self.stopButton.grid(row=0, column=1,sticky='nsew',pady=10)

        #self.opStepFrame = tk.Frame(self.opFrame)
        self.opStepFrame = VerticalScrolledFrame(self.opFrame, width=200,height=400)
        self.opStepFrame.grid(row=2, column=0, sticky='nsew')

        self.stepsLabel = tk.Label(self.opStepFrame, text="Show Steps:")
        self.stepsLabel.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.stepFont = tkFont.Font(family="Lucida Grande", size=14)

        #self.stepText = tk.Text(self.opStepFrame, padx=5, pady=5, font=self.stepFont, width=50)
        self.stepText = CueText(self.opStepFrame, self.currentShow, padx=5, pady=5, font=self.stepFont, width=50)
        self.currentShow.addListener(self.stepText)
        self.stepText.grid(row=3, column=0, columnspan=2)
        self.stepText.configure(tabs=('6c',), spacing1=3, spacing3=3)
        self.stepText.tag_configure('command',background="#DDFFDD")
        self.stepText.tag_configure('delay',background="#FFFFDD")
        self.stepText.tag_configure('label',background="#DDDDFF")
        self.stepText.tag_configure('trigger', background='#FFDDFF')
        self.stepText.tag_configure('instruction',background="#DDFFDD")
        self.stepText.tag_configure('continue',background="#FFDDDD")
        

        #self.yScroll = tk.Scrollbar(self.opStepFrame, orient=tk.VERTICAL)
        #self.yScroll.grid(row=3, column=2, sticky='nw')
        #self.stepText.configure(yscrollcommand=self.yScroll.set)
        #self.yScroll['command'] = self.stepText.yview

    def create_planeviewertab(self):
        #------Plane Viewer------
        # This frame will contain the following purposes:
        #	- Show each control axis of the plane and its current state, according to the controller 
        #		- May do this as a GUI (list of axes) or visually (image) or both
        #	- Manual control of each axis from this tab
        #		-Think about how to interlock this with the operations tab so they cooperate
        pass

    def create_scheduletab(self):
        #------Scheduling-------
        # This frame will contain the following purposes:
        #	- Using the shows loaded using the load-show frame, create a schedule, with options
        #	- Day of the week selector. Each day shall have the options via radioboxes:
        #		- Default schedule
        #		- Specific schedule (select)
        #		- Disabled
        #	- A pane to select the default schedule
        #	- For each day of the week that has a 'specific schedule', a pane/location to select the specific schedule
        #	- A schedule has options:
        #		- Name (mandatory)
        #		- Every x minutes (spinbox)
        #		- Starting at (time) (checkbox + spinbox?)
        #		- No later than (time) (checkbox + spinbox?)
        #		- Exceptions? 

        self.scheduleFrame = tk.Frame(self.book,width=200,height=100)
        self.book.add(self.scheduleFrame,text="Schedule",sticky='nsew')

        #Day of week Selector
        self.dayChoicesFrame = tk.Frame(self.scheduleFrame)
        self.dayChoicesFrame.grid(row=0,column=0,sticky='new',pady=10)

        for d in range(len(self.days)):
            day = tk.Label(self.dayChoicesFrame,text=self.days[d], font=self.basicFont)
            day.grid(row=0,column=d+1,sticky='ew')
            self.dayChoicesFrame.grid_columnconfigure(d+1, weight=1)
            
            self.dayVars[self.days[d]] = tk.StringVar(self.master, self.scheduleModes[0], name=self.days[d])
            self.dayVars[self.days[d]].trace_add("write", self.setDayScheduleMode)

            #create radiobuttons
            for c in range(len(self.scheduleModes)):
                btn = tk.Radiobutton(self.dayChoicesFrame, text='', variable=self.dayVars[self.days[d]], value = self.scheduleModes[c])
                btn.grid(row=c+1, column=d+1)


        for c in range(len(self.scheduleModes)):
            choice = tk.Label(self.dayChoicesFrame, text=self.scheduleModes[c], font=self.basicFont)
            choice.grid(row=c+1, column=0,sticky='nsw')


        self.sep_sched_0 = ttk.Separator(self.scheduleFrame, orient=tk.HORIZONTAL)
        self.sep_sched_0.grid(row=1,column=0,sticky='ew',pady=15)

        #self.scheduleChoicesFrame = tk.Frame(self.scheduleFrame, height=400)
        self.scheduleChoicesFrame = VerticalScrolledFrame(self.scheduleFrame, height=400)
        self.scheduleChoicesFrame.grid(row=2,column=0,sticky='nsew')
        self.scheduleFrame.grid_rowconfigure(2, weight=1) 
        self.scheduleFrame.grid_columnconfigure(0, weight=1)

        #Default schedule frame:
        tf = tk.Frame(self.scheduleChoicesFrame)
        tf.grid(row=2,column=0,sticky='new')

        self.defaultShowVar = tk.StringVar(self.master, self.showList[0].name, name="defaultShowVar")
        self.defaultShowVar.trace_add("write", self.updateScheduleSelections)
        self.defaultShowVar.trace_add("write", self.updateDailyTimes)

        self.defaultScheduleLabel = tk.Label(tf, text="Default Show: ",font=self.basicFont)
        self.defaultScheduleLabel.grid(row=0,column=0)

        self.defaultShowList = tk.OptionMenu(tf, self.defaultShowVar, *[s.name for s in self.showList])
        self.defaultShowList.grid(row=0,column=1,sticky='ew')

        self.everyLabel = tk.Label(tf, text="Runs every (mins):", font=self.basicFont)
        self.everyLabel.grid(row=2, column=1)

        self.every_minstr=tk.StringVar(self,'15',name="every_minstr")
        self.every_minstr.trace_add("write", self.updateDailyTimes)
        self.every_last_value = ""
        self.every_min = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=self.every_minstr,width=2,state="readonly")
        self.every_min.grid(row=2,column=2, sticky='w')
        tf.grid_columnconfigure(2, weight=5)


        tf.grid_columnconfigure(0, weight=1)
        self.defaultStartVar = tk.IntVar(self.master, value=0, name="defaultStartVar")
        self.defaultStartTimeCheck = tk.Checkbutton(tf, variable=self.defaultStartVar)
        self.defaultStartTimeCheck.grid(row=3, column=0, sticky='e')
        self.defaultStartVar.trace_add("write", self.updateDailyTimes)

        self.defaultStartLabel = tk.Label(tf, text="Starting at:", font=self.basicFont)
        self.defaultStartLabel.grid(row=3,column=1)
        tf.grid_columnconfigure(0, weight=10)

        #Start Time Select Spinner
        self.start_hourstr=tk.StringVar(self,'9',name="start_hourstr")
        self.start_hourstr.trace_add("write", self.updateDailyTimes)
        self.start_hour = tk.Spinbox(tf,from_=0,to=23,wrap=True,textvariable=self.start_hourstr,width=2,state="readonly")
        self.start_minstr=tk.StringVar(self,'30',name="start_minstr")
        self.start_minstr.trace_add("write", self.updateDailyTimes)
        self.start_last_value = ""
        self.start_min = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=self.start_minstr,width=2,state="readonly")
        self.start_hour.grid(row=3,column=2, sticky='e')
        self.start_min.grid(row=3,column=3, sticky='w')
        tf.grid_columnconfigure(2, weight=5)
        tf.grid_columnconfigure(3, weight=5)

        self.defaultEndVar = tk.IntVar(self.master, value=0,name="defaultEndVar")
        self.defaultEndVar.trace_add("write", self.updateDailyTimes)
        self.defaultEndTimeCheck = tk.Checkbutton(tf, variable=self.defaultEndVar)
        self.defaultEndTimeCheck.grid(row=3, column=4, sticky='e')
        tf.grid_columnconfigure(4, weight=1)

        self.defaultEndLabel = tk.Label(tf, text="End at:", font=self.basicFont)
        self.defaultEndLabel.grid(row=3,column=5)
        tf.grid_columnconfigure(5, weight=10)

        #End time select spinner
        self.end_hourstr=tk.StringVar(self,'16', name="end_horustr")
        self.end_hourstr.trace_add("write", self.updateDailyTimes)
        self.end_hour = tk.Spinbox(tf,from_=0,to=23,wrap=True,textvariable=self.end_hourstr,width=2,state="readonly")
        self.end_minstr=tk.StringVar(self,'40', name="end_minstr")
        self.end_minstr.trace_add("write", self.updateDailyTimes)
        self.end_last_value = ""
        self.end_min = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=self.end_minstr,width=2,state="readonly")
        self.end_hour.grid(row=3,column=6, sticky='e')
        self.end_min.grid(row=3,column=7, sticky='w')
        tf.grid_columnconfigure(6, weight=5)
        tf.grid_columnconfigure(7, weight=5)

        
        #Day Frames:
        for d in range(len(self.days)):
            tf = tk.Frame(self.scheduleChoicesFrame, height=200)
            tf.grid(row = 3+d, column=0, columnspan=10, sticky='nsew')
            tf.grid_columnconfigure(0,weight=1)

            sep = ttk.Separator(tf, orient=tk.HORIZONTAL)
            sep.grid(row=0,column=0, columnspan=10,sticky='ew',pady=10)

            l = tk.Label(tf, text=self.days[d], font=self.basicFont, anchor='w')
            l.grid(row=1,column=0,sticky='w')

            dayParts = {}

            #Time Setting:

            dayParts['showVar'] = tk.StringVar(self.master, self.showList[0].name, name=self.days[d] + ":showVar")
            dayParts['showVar'].trace_add("write", self.updateScheduleSelections)

            dayParts['scheduleLabel'] = tk.Label(tf, text="Schedule for " + self.days[d] + ":",font=self.basicFont)
            dayParts['scheduleLabel'].grid(row=2,column=0)

            dayParts['showList'] = tk.OptionMenu(tf, dayParts['showVar'], *[s.name for s in self.showList])
            dayParts['showList'].grid(row=2,column=1,sticky='ew')

            dayParts['everyLabel'] = tk.Label(tf, text="Runs every (mins):", font=self.basicFont)
            dayParts['everyLabel'].grid(row=3, column=0)

            dayParts['every_minstr']=tk.StringVar(self,'15', name=self.days[d] + ":every_minstr")
            dayParts['every_minstr'].trace_add("write", self.updateDailyTimes)
            dayParts['every_last_value'] = ""
            dayParts['every_min'] = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=dayParts['every_minstr'],width=2,state="readonly")
            dayParts['every_min'].grid(row=3,column=1, sticky='w')
            tf.grid_columnconfigure(3, weight=5)


            tf.grid_columnconfigure(0, weight=1)
            dayParts['startVar'] = tk.IntVar(self.master, value=0, name=self.days[d] + ":startVar")
            dayParts['startVar'].trace_add("write", self.updateDailyTimes)
            dayParts['startTimeCheck'] = tk.Checkbutton(tf, variable=dayParts['startVar'])
            dayParts['startTimeCheck'].grid(row=3, column=2, sticky='e')

            dayParts['startLabel'] = tk.Label(tf, text="Starting at:", font=self.basicFont)
            dayParts['startLabel'].grid(row=3,column=3)
            tf.grid_columnconfigure(0, weight=10)

            #Start Time Select Spinner
            dayParts['start_hourstr']=tk.StringVar(self,'9', name=self.days[d] + ":start_hourstr")
            dayParts['start_hourstr'].trace_add("write", self.updateDailyTimes)
            dayParts['start_hour'] = tk.Spinbox(tf,from_=0,to=23,wrap=True,textvariable=dayParts['start_hourstr'],width=2,state="readonly")
            dayParts['start_minstr']=tk.StringVar(self,'30', name=self.days[d] + ":start_minstr")
            dayParts['start_minstr'].trace_add("write", self.updateDailyTimes)
            dayParts['start_last_value'] = ""
            dayParts['start_min'] = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=dayParts['start_minstr'],width=2,state="readonly")
            dayParts['start_hour'].grid(row=3,column=4, sticky='e')
            dayParts['start_min'].grid(row=3,column=5, sticky='w')
            tf.grid_columnconfigure(4, weight=5)
            tf.grid_columnconfigure(5, weight=5)

            dayParts['endVar'] = tk.IntVar(self.master, value=0, name=self.days[d] + ":endVar")
            dayParts['endVar'].trace_add("write", self.updateDailyTimes)
            dayParts['endTimeCheck'] = tk.Checkbutton(tf, variable=dayParts['endVar'])
            dayParts['endTimeCheck'].grid(row=3, column=6, sticky='e')
            tf.grid_columnconfigure(6, weight=1)

            dayParts['endLabel'] = tk.Label(tf, text="End at:", font=self.basicFont)
            dayParts['endLabel'].grid(row=3,column=7)
            tf.grid_columnconfigure(7, weight=10)

            tk.Label(tf, text="").grid(row=3,column=7)
            tf.grid_columnconfigure(7, weight=10)

            #End time select spinner
            dayParts['end_hourstr']=tk.StringVar(self,'16', name=self.days[d] + ":end_hourstr")
            dayParts['end_hourstr'].trace_add("write", self.updateDailyTimes)
            dayParts['end_hour'] = tk.Spinbox(tf,from_=0,to=23,wrap=True,textvariable=dayParts['end_hourstr'],width=2,state="readonly")
            dayParts['end_minstr']=tk.StringVar(self,'40', name=self.days[d] + ":end_minstr")
            dayParts['end_minstr'].trace_add("write", self.updateDailyTimes)
            dayParts['end_last_value'] = ""
            dayParts['end_min'] = tk.Spinbox(tf,from_=0,to=59,wrap=True,textvariable=dayParts['end_minstr'],width=2,state="readonly")
            dayParts['end_hour'].grid(row=3,column=9, sticky='e')
            dayParts['end_min'].grid(row=3,column=10, sticky='w')
            tf.grid_columnconfigure(9, weight=5)
            tf.grid_columnconfigure(10, weight=5)

            self.dayFrames[self.days[d]] = {'frame':tf}
            self.dayFrames[self.days[d]].update(dayParts)
            #tf.grid_forget()
            tf.grid_remove()

        self.updateDailyTimes()

    def create_lightingtab(self):
        #------Lighting Frame------

        lightingLabels = self.lxController.com()
        
        self.lxFrame = tk.Frame(self.book, width=200,height=100)
        self.book.add(self.lxFrame,text="Lighting")

        self.lxButtonFrame = tk.Frame(self.lxFrame, width=200,height=100)
        self.lxButtonFrame.grid(row=1, column=0, sticky='nw')

        coms = self.lxController.com()

        row = 0
        column=0
        for c in coms:
            rowFrame = tk.Frame(self.lxButtonFrame)
            rowFrame.grid_columnconfigure(0, minsize=40)
            rowFrame.grid_columnconfigure(1, minsize=240)
            label = tk.Label(rowFrame,text=str(c), font=self.smallButtonFont, anchor=tk.W)
            label.grid(column=1, row=0, sticky='ew')

            actButton = tk.Button(rowFrame, text="Press", font=self.basicFont, bg="#CCFFCC", command=partial(self.lxController.sendCommand, c, 'press'))
            actButton.grid(column=0, row=0, sticky=tk.E)


            if row >= len(coms)/2:
                row=0
                column=2
            rowFrame.grid(column=column, row=row, sticky=tk.W)

            row += 1

        pass

    def create_remotetab(self):
        #------Remote input-------
        # 	What do we do about remote input?
        #	Configuration tab here....
        pass

    def create_managetab(self):
        #------Manage Shows Frame------	

        self.manageShowsFrame = tk.Frame(self.book, width=200, height=100)
        self.book.add(self.manageShowsFrame, text="Manage Shows")

        self.manageShowsFrame.grid_columnconfigure(0, minsize=200)
        self.manageShowsFrame.grid_columnconfigure(1, minsize=200)

        self.yScroll_showManageList = tk.Scrollbar(self.manageShowsFrame, orient=tk.VERTICAL)
        self.yScroll_showManageList.grid(row=1, column=2, sticky='nsw')

        self.showManageList = tk.Listbox(self.manageShowsFrame, font=self.basicFont, yscrollcommand=self.yScroll_showManageList.set, activestyle='none')
        self.yScroll_showManageList['command'] = self.showManageList.yview

        self.showManageList.grid(row=1, column=1)

        self.importButtonFrame = tk.Frame(self.manageShowsFrame, bg="#CCCCCC")
        self.importButtonFrame.grid_columnconfigure(0, minsize=100)
        self.importButtonFrame.grid(row=1, column=0, sticky='nsew')

        self.importButton = tk.Button(self.importButtonFrame, text="Import Show", command=self.importShow, font=self.bigButtonFont)
        self.importButton.grid(row=0, column=0,sticky='ew')

        self.deleteShowButton = tk.Button(self.importButtonFrame, text="Delete Show", command=self.deleteShow, font=self.bigButtonFont)
        self.deleteShowButton.grid(row=1, column=0, sticky='ew')

    def create_inspecttab(self):
        #------Inspect Show FRAME----

        self.inspectFrame = tk.Frame(self.book, width=200, height=100)
        self.book.add(self.inspectFrame, text="Inspect Show")

        self.dataFrame = tk.Frame(self.inspectFrame)
        self.dataFrame.grid(row=1)

        self.selectLabel = tk.Label(self.inspectFrame, text="Select a Show:", font=self.basicFont, anchor=tk.E)
        self.selectLabel.grid(row=0, column=0, sticky='ew')

        self.inspectShowVar = tk.StringVar()
        #TODO - this will cause an error if the showlist is empty
        self.inspectShowVar.set(self.showList[0].name)
        self.inspectShowVar.trace_add("write", self.updateInspectStepDisplay)
        self.inspectShowSelect = tk.OptionMenu(self.inspectFrame, self.inspectShowVar, *[s.name for s in self.showList])
        self.inspectShowSelect.grid(row=0,column=1,sticky='ew')

        self.showNameLabel = tk.Label(self.dataFrame, text="Show Name:", font=self.basicFont, anchor=tk.W)
        self.showNameLabel.grid(row=0, column=0, sticky='ew')

        self.showNameDisplay = tk.Label(self.dataFrame, text="---", font=self.basicFont, anchor=tk.W)
        self.showNameDisplay.grid(row=0, column=1, sticky='ew')

        self.showNotesLabel = tk.Label(self.dataFrame, text="Show Notes: ", font=self.basicFont, anchor=tk.W)
        self.showNotesLabel.grid(row=1, column=0, sticky='ew')

        self.showNotesDisplay = tk.Label(self.dataFrame, text="---", font=self.basicFont, anchor=tk.W)
        self.showNameDisplay.grid(row=1, column=1, sticky='ew')

        self.inspectStepsLabel = tk.Label(self.inspectFrame, text="Show Steps:")
        self.inspectStepsLabel.grid(row=2, column=0, columnspan=2, sticky='ew')

        self.inspectStepsFont = tkFont.Font(family="Lucida Grande", size=14)

        self.inspectStepText = CueText(self.inspectFrame, self.currentShow, padx=5, pady=5, font=self.inspectStepsFont, width=50)
        self.inspectStepText.grid(row=3, column=0, columnspan=2)
        self.inspectStepText.configure(tabs=('6c',), spacing1=3, spacing3=3)
        self.inspectStepText.tag_configure('instruction',background="#DDFFDD")
        self.inspectStepText.tag_configure('delay',background="#FFFFDD")
        self.inspectStepText.tag_configure('label',background="#DDDDFF")
        self.inspectStepText.tag_configure('trigger',background="#FFDDFF")
        self.inspectStepText.tag_configure('command',background="#DDFFDD")

        self.inspectYScroll = tk.Scrollbar(self.inspectFrame, orient=tk.VERTICAL)
        self.inspectYScroll.grid(row=3, column=2, sticky='nsw')
        self.stepText.configure(yscrollcommand=self.inspectYScroll.set)
        self.inspectYScroll['command'] = self.inspectStepText.yview

    def create_widgets(self):
        self.create_globals()
        self.create_fonts()
        self.create_title()
        self.create_menubar()
        self.create_notebook()

        self.create_scheduletab()
        self.create_operationstab()
        #self.create_planeviewertab()
        #self.create_remotetab()	
        self.create_managetab()
        self.create_inspecttab()
        self.create_manualtab()
        self.create_lightingtab()
        self.create_footer()

        self.updateScheduleSelections()
        self.updateShowListDisplays()

    def openConfigWindow(self):
        self.cw = ConfigWindow(self.master)

        
        if self.controller.ser.port != None:
            self.cw.outVar.set(self.controller.ser.port)
        self.cw.outVar.trace_add("write", self.setOutputPort)

        if self.inputs['serial'].ser.port != None:
            self.cw.inVar.set(self.inputs['serial'].ser.port)
        self.cw.inVar.trace_add("write", self.setInputPort)

        self.cw.startButtonVar.set(1 if self.runShowOnButtonInput else 0)
        self.cw.startButtonVar.trace_add("write", self.changeInputMonitoring)

    def setOutputPort(self, *args):
        val = self.cw.outVar.get()
        logging.debug(f"Value of serial output selector changed to {val}, attempting to update")
        if val != '':
            val = val.split(' ')[0]
            logging.debug(f"Parsed serial port is {val}")
            self.controller.ser.port = val

    def setInputPort(self, *args):
        val = self.cw.inVar.get()
        logging.debug(f"Value of serial input selector changed to {val}, attempting to update")
        if val != '':
            val = val.split(' ')[0]
            logging.debug(f"Parsed serial port is {val}")
            try:
                self.inputs['serial'].ser.port = val
            except:
                e = sys.exc_info()[0]
                logging.debug(f"Error opening serial port: {e}")

    def setInputMonitoring(self, value = 0):
        logging.debug("Enterring function setInputMonitoring")
        if value == 1:
            logging.info("value set to run - beginning to monitor input to start")
            self.runShowOnButtonInput = True
            self.inputStarter=TimerClass(self.checkForInputToStartShow, None, delay=.2)
            self.inputStarter.start()
        else:
            logging.info("value set to not run - stopping input monitoring")
            self.runShowOnButtonInput = False
            self.inputStarter.stop()
        logging.debug(f"Run Values overwritten: {value} - {self.runShowOnButtonInput}")

    def changeInputMonitoring(self, *args):
        logging.debug("Entering function changeInputMonitoring")
        
        try:
            if (self.cw != None):
                runValue = self.cw.startButtonVar.get()
        except AttributeError as err:
            logging.error(f"Called changeInputMonitoring() from somewhere other than config window, ignoring. {err}")
        else:
            if runValue == 1:
                logging.info("runValue set to run - beginning to monitor input to start")
                self.runShowOnButtonInput = True
                self.inputStarter = TimerClass(self.checkForInputToStartShow, None, delay=.2)
                self.inputStarter.start()
            else:
                logging.info("runValue set to not run - stopping input monitoring")
                self.runShowOnButtonInput = False
                self.inputStarter.stop()
            logging.debug(f"Change in preferences: {runValue} - {self.runShowOnButtonInput}")

    def checkForInputToStartShow(self):
        logging.log(5, f"Checking for button input to start show; self.showRunning is {self.showRunning}; self.runShowOnButtonInput is {self.runShowOnButtonInput}")
        if self.runShowOnButtonInput:
            inputState = False
            for i in self.inputs.values():
                inputState = inputState or i.retrieveTriggerFlag()

            if inputState and not self.showRunning:
                self.inputStarter.stop()
                logging.warning(f"Show started by input {i.label if hasattr(i, 'label') else i}")
                self.runShow(manual_trigger=True)

    def startup(self, root):
        if path.exists("player.conf"):
            with open("player.conf", "r") as infile:
                try:
                    j = json.load(infile)
                    lastConfig = j['lastConfig']

                    if path.exists(lastConfig):
                        self.loadConfig(lastConfig)
                except (json.decoder.JSONDecodeError, KeyError, ValueError) as e:
                    logging.warning(e)
                    msg = mb.showerror("Unable to load config",
                    "Unable to load the previous configuration; please reload manually" + 
                    "\n Error was: " + str(e))

        self.stopShow()

        #Run init autotomatically after 15 seconds
        d = AutoDialog(root, "Showplayer will automatically Init the Plane in 15 seconds.", "Init Now", "Cancel")
        root.after(15000, d.yes)
        root.wait_window(d)
        logging.info(f"Auto Init? : {d.answer}")
        if d.answer:
            warning = AutoWarning(root, "Now initializing the plane, please wait")
            root.after(500, self.controller.initThePlane)
            root.after(600, warning.destroy)
            #root.after(650, partial(logging.log, logging.INFO, "Finished Auto-Initialization"))
        
        root.after(700, self.changeInputMonitoring)

    def updateConf(self, k, v):
        with open ("player.conf", "w") as outfile:
            
            self.conf[k] = v

            json.dump(self.conf, outfile)

    def forceStartInputStarter(self):
        if self.inputStarter.is_alive():
            self.inputStarter.stop()
        self.inputStarter = TimerClass(self.checkForInputToStartShow, None, delay=.2)
        self.inputStarter.start()

def logAtExit():
    logging.critical("Program terminated via interrupt or other closure")

def setupLogging():

    atexit.register(logAtExit)
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('{asctime} | {levelname}: {message}', style="{")

    stream_handler = logging.StreamHandler()
    #stream_handler.setLevel(5)
    #stream_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    if not path.exists("./logs"): makedirs("./logs")

    debugLogFilePath = "./logs/showplayer_cuelist_debug.log"
    debug_file_handler = logging.handlers.TimedRotatingFileHandler(filename=debugLogFilePath, when='midnight', backupCount=30)
    debug_file_handler.setFormatter(formatter)
    debug_file_handler.setLevel(logging.DEBUG)

    logFilePath = "./logs/showplayer_cuelist.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(filename=logFilePath, when='midnight', backupCount=30)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(debug_file_handler)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.debug("-------------------------------------------")
    logger.critical("----BEGINNING START OF NEW PROGRAM RUN-----")
    logger.info("Beginning logging to standard log, debug log, and stdout")

def main():
    setupLogging()

    root = tk.Tk()
    root.wm_title("727 Show Player")
    root.protocol('WM_DELETE_WINDOW', root.destroy)
    player = showplayer(master=root, title="727 Show Player")
    player.startup(root)
    player.updateShowListDisplays()
 
    player.mainloop()       

if __name__ == '__main__':
    main()
