#showcontrols.py

import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
import tkinter.ttk as ttk
from plane_controls import *
from sys import exit
from functools import partial
import pickle
from Cuelist import *
from CueBox import *

def Reverse(tuples): 
    new_tup = () 
    for k in reversed(tuples): 
        new_tup = new_tup + (k,) 
    return new_tup

class showmaker(tk.Frame):

    activeButtonColor = "#AAFFAA"
    inactiveButtonColor = "#FFFFFF"
    activeButtonIndex = -1
    activeStateIndex = -1
    
    def __init__(self, master=None, title="title"):
        super().__init__(master)
        self.master = master
        self.master.title='Title' 
        self.title = title
        self.cuelist = Cuelist()
        self.showBox = tk.Listbox(self)
        #self.controllers = {SerialPlaneController():'#BFCBCF', RelayLightingController():'#FABCA3'}
        self.controllers = {SerialPlaneController():'#BFCBCF', NetworkLightingController():'#D2EDBB'}
        self.commandButtons = list()
        self.stateButtons = list()
        self.pack()
        self.create_widgets()

    def addItem(self, command, commandName, stateName):
        if self.showBox.curselection() == ():
            cueIndex = len(self.cuelist.cues)
        else:
            #cueIndex = int(index)
            cueIndex = min(self.showBox.curselection())

        logging.debug(f"Adding cue item {commandName}:{stateName} at index {cueIndex}")

        self.cuelist.cues.insert(cueIndex, Cuelist_Item(str(commandName)+":"+str(stateName), command))
        self.showBox.updateFromGivenCues(self.cuelist)

    def removeSelected(self):
        for d in Reverse(self.showBox.curselection()):
            logging.debug(f"About to delete {d} from showbox")
            self.showBox.delete(d)
            logging.debug(f"About to delete {d} from cuelist")
            self.cuelist.cues.pop(d)

    def updateDelayButtonState(self):
        e = self.delayEntry.get()
        if not self.delayEntryValidate():
            self.delayButton.configure(state=tk.DISABLED)
            self.delayButton.configure(bg = showmaker.inactiveButtonColor)
        else:
            self.delayButton.configure(state=tk.NORMAL)
            self.delayButton.configure(bg = showmaker.activeButtonColor)

    def delayEntryCallback(self, arg1, arg2, arg3):
        self.updateDelayButtonState()

    def delayEntryValidate(self):
        ent = self.delayEntry.get()
        if ent == '': return False
        else:
            try:
                x = int(ent)
            except ValueError as e:
                return False
            return True

    def updateWaitButtonState(self):
        e = self.waitEntry
        if not self.waitEntryValidate():
            self.waitButton.configure(state=tk.DISABLED)
            self.waitButton.configure(bg = showmaker.inactiveButtonColor)
        else:
            self.waitButton.configure(state=tk.NORMAL)
            self.waitButton.configure(bg = showmaker.activeButtonColor)

    def waitEntryCallback(self, arg1, arg2, arg3):
        self.updateWaitButtonState()
    
    def waitEntryValidate(self):
        ent = self.waitEntry.get()
        if ent == '': return False
        else:
            try:
                x = int(ent)
            except ValueError as e:
                return False
            return True

    def updatePauseButtonState(self):
        e = self.pauseEntry
        if not self.pauseEntryValidate():
            self.pauseButton.configure(state=tk.DISABLED)
            self.pauseButton.configure(bg = showmaker.inactiveButtonColor)
        else:
            self.pauseButton.configure(state=tk.NORMAL)
            self.pauseButton.configure(bg = showmaker.activeButtonColor)

    def pauseEntryCallback(self, arg1, arg2, arg3):
        self.updatePauseButtonState()
    
    def pauseEntryValidate(self):
        ent = self.pauseEntry.get()
        if ent == '': return False
        else:
            try:
                x = int(ent)
            except ValueError as e:
                return False
            return True

    def addDelayItem(self):
        if self.delayEntryValidate():
            if self.showBox.curselection() == ():
                cueIndex = len(self.cuelist.cues)
            else:
                cueIndex = min(self.showBox.curselection())
            
            logging.debug(f"Adding delay item at index {cueIndex}")

            self.cuelist.cues.insert(cueIndex, Delay_Item(postDelay=int(self.delayEntry.get())))
            self.showBox.updateFromGivenCues(self.cuelist)

    def addLabelItem(self):
        if self.showBox.curselection() == ():
            cueIndex = len(self.cuelist.cues)
        else:
             cueIndex = int(self.showBox.curselection()[0])

        logging.debug(f"Adding label item at index {cueIndex}")

        self.cuelist.cues.insert(cueIndex, Label_Item(name=str(self.labelEntry.get()), labelText=str(self.labelEntry.get())))
        self.showBox.updateFromGivenCues(self.cuelist)

    def addTimeoutCue(self):
        if self.waitEntryValidate():
            if self.showBox.curselection() == ():
                cueIndex = len(self.cuelist.cues)
            else:
                cueIndex = min(self.showBox.curselection())
            
            logging.debug(f"Adding wait-for-input cue at index {cueIndex}")

            self.cuelist.cues.insert(cueIndex, Trigger_Item(name="Trigger Item", inputFunction=None, labelText = "Wait/Cancel", timeoutTime = int(self.waitEntry.get())))
            self.showBox.updateFromGivenCues(self.cuelist)

    def addPauseCue(self):
        if self.pauseEntryValidate():
            if self.showBox.curselection() == ():
                cueIndex = len(self.cuelist.cues)
            else:
                cueIndex = min(self.showBox.curselection())
            
            logging.debug(f"Adding wait-for-input cue at index {cueIndex}")

            self.cuelist.cues.insert(cueIndex, Delay_Or_Skip_Item(name="Delay/Continue", inputFunction=None, labelText = "Wait/Continue", timeoutTime = int(self.pauseEntry.get())))
            self.showBox.updateFromGivenCues(self.cuelist)

    def labelEntryCallback(self, arg1, arg2, arg3):
        if self.labelEntry.get() == '':
            self.labelButton.configure(state=tk.DISABLED)
            self.labelButton.configure(bg = showmaker.inactiveButtonColor)
        else:
            self.labelButton.configure(state=tk.NORMAL)
            self.labelButton.configure(bg =showmaker.activeButtonColor)

    def clearAllSteps(self):
        if self.showBox.size() > 0:
            for i in range(self.showBox.size()-1, -1, -1):
                self.showBox.delete(i)
        self.cuelist.clearAll()

    def create_planetab(self):
        self.planeFrame = tk.Frame(self.book,width=200,height=100)
        self.book.add(self.planeFrame,text="Automation Shows", sticky='ew')

        self.showLabel = tk.Label(self.planeFrame, text="Steps", font=self.labelFont)
        self.showLabel.grid(column=4, row=0, sticky='ew')

        self.instLabel = tk.Label(self.planeFrame, text="Select Activity and State", font=self.labelFont)
        self.instLabel.grid(column=0, columnspan=3, row=1, sticky='ew')	

        self.activityFrame = tk.Frame(self.planeFrame,width=400,height=100)	
        
        for cont in self.controllers:
            coms = cont.com()
            controllerColor = bg=self.controllers[cont]

            #Generate labels for each command, with buttons for each state
            for commandName in coms:
                commandFrame = tk.Frame(self.activityFrame, bg=controllerColor)
                label=tk.Label(commandFrame, text=str(commandName), font=self.smallFont, anchor='w', bg=controllerColor)
                label.pack(side=tk.LEFT)
                buttonFrame = tk.Frame(commandFrame, width=100,height=40)
                for stateName in coms[commandName]:
                    button=actionButton(buttonFrame, coms[commandName][stateName], text=str(stateName),font=self.smallFont, bg = showmaker.inactiveButtonColor, command=partial(self.addItem, coms[commandName][stateName], commandName, stateName))
                    button.pack(side=tk.LEFT)
                buttonFrame.pack(side=tk.RIGHT)
                self.commandButtons.append(commandFrame)

            #Layout buttons on screen
            maxButtonRows=15

            col=0
            row=0
            for item in self.commandButtons:
                    item.grid(column=col,row=row,sticky='ew',padx=2,pady=1)
                    row +=1
                    if row > maxButtonRows:
                        col += 1
                        row = 0

        self.activityFrame.grid(column=0, row=2, sticky='nsew')
        self.planeFrame.grid_columnconfigure(0, weight=1)

        self.yScroll = tk.Scrollbar(self.planeFrame, orient=tk.VERTICAL)

        self.yScroll.grid(row=2, column=5, rowspan=len(coms), sticky='nsw')

        self.showBox = CueBox(self.planeFrame, self.cuelist, font=self.basicFont, yscrollcommand=self.yScroll.set, activestyle='none', selectmode=tk.MULTIPLE)
        self.yScroll['command'] = self.showBox.yview

        self.showBox.grid(column=3,row=2, columnspan=2, rowspan=len(coms), sticky='nsew', padx=3)
        self.planeFrame.grid_columnconfigure(4, weight=1)

        self.removeButton = tk.Button(self.planeFrame, text="Remove Selected Step(s)", font=self.basicFont,bg='#FFDDDD', command=self.removeSelected)
        self.removeButton.grid(column=4,row=len(coms)+3, padx=3, pady=5)

        self.delayButton = tk.Button(self.planeFrame, text="Delay(ms)", font=self.basicFont,bg='#DDFFDD', command=self.addDelayItem)
        self.delayButton.grid(column=1, columnspan = 1, row=len(coms)+3, padx=3, pady=5, sticky='ew')

        self.delayVar = tk.StringVar()
        self.delayVar.trace_add("write", self.delayEntryCallback)
        self.delayEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont, justify=tk.RIGHT, textvariable=self.delayVar)
        self.delayEntry.grid(column=0, row=len(coms)+3, padx = 3, pady=5, sticky='ew')
        self.updateDelayButtonState()

        self.waitButton = tk.Button(self.planeFrame, text="Wait, then Cancel", font=self.basicFont, bg='#DDFFDD', command = self.addTimeoutCue)
        self.waitButton.grid(column=1, columnspan = 1, row=len(coms)+4, padx=3, pady=5, sticky='ew')

        self.waitVar = tk.StringVar()
        self.waitVar.trace_add("write", self.waitEntryCallback)
        self.waitEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont, justify=tk.RIGHT, textvariable=self.waitVar)
        self.waitEntry.grid(column=0, row=len(coms)+4, padx = 4, pady=5, sticky='ew')
        self.updateWaitButtonState()


        self.pauseButton = tk.Button(self.planeFrame, text = "Wait, then Continue", font = self.basicFont, bg='#DDFFDD', command = self.addPauseCue)
        self.pauseButton.grid(column=1,columnspan=1, row = len(coms)+5, padx=3, pady=5, sticky='ew')

        self.pauseVar = tk.StringVar()
        self.pauseVar.trace_add("write", self.pauseEntryCallback)
        self.pauseEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont, justify=tk.RIGHT, textvariable=self.pauseVar)
        self.pauseEntry.grid(column=0, row=len(coms)+5, padx = 5, pady=5, sticky='ew')
        self.updatePauseButtonState()
        
        
        self.labelVar = tk.StringVar()
        self.labelVar.trace_add("write", self.labelEntryCallback)
        self.labelEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont,justify=tk.RIGHT, textvariable=self.labelVar)
        self.labelEntry.grid(column=0, row=len(coms)+6, padx=3, pady=2, sticky='nesw')

        self.labelButton = tk.Button(self.planeFrame, text="Add Label", font=self.basicFont,bg='#DDFFDD', command = self.addLabelItem)
        self.labelButton.grid(column=1, row=len(coms)+6, padx=3, pady=2, sticky='ew')
        self.labelEntryCallback('1','2','3')	

    def create_lightingtab(self):
        self.lxFrame = tk.Frame(self.book,width=200,height=100)
        self.book.add(self.lxFrame,text="Lighting Shows", sticky='ew')

        self.lxShowLabel = tk.Label(self.lxFrame, text="Steps", font=self.labelFont)
        self.lxShowLabel.grid(column=4, row=0, sticky='ew')

        self.lxInstLabel = tk.Label(self.lxFrame, text="Select Activity and State", font=self.labelFont)
        self.lxInstLabel.grid(column=0, columnspan=3, row=1, sticky='ew')

        r = RelayLightingController()
        coms = r.com()

    def create_widgets(self):
        self.grid_columnconfigure(0, minsize=100, weight=1)

        self.menubar = tk.Menu(self.master)

        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.fileMenu.add_command(label="New",command=self.newFile)
        self.fileMenu.add_command(label="Export",command=self.exportFile)
        self.fileMenu.add_command(label="Import",command=self.importFile)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Quit",command=exit)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)

        self.stepsMenu = tk.Menu(self.menubar, tearoff=0)
        self.stepsMenu.add_command(label="Clear All Steps", command = self.clearAllSteps)
        self.menubar.add_cascade(label="Steps", menu=self.stepsMenu)

        self.master.config(menu=self.menubar)

        self.titleStyle = tkFont.Font(family="Lucida Grande", size=30)
        self.titleLabel = tk.Label(self, text=self.title, font=self.titleStyle)
        self.titleLabel.grid(column=0, row=1, columnspan=10)

        self.labelFont = tkFont.Font(family="Lucida Grande", size=16)
        self.basicFont = tkFont.Font(family="Lucida Grande", size=13)
        self.smallFont = tkFont.Font(family="Lucida Grande", size=10)

        s = ttk.Style()
        s.configure('TNotebook.Tab', font=('Lucida Grande','14') )

        self.book = ttk.Notebook(self)
        self.book.grid(row=2, column=0, sticky='ew')

        self.create_planetab()

        #self.create_lightingtab()		
    
    def newFile(self):
        print("Start a new file")

    def exportFile(self):
        
        f = filedialog.asksaveasfile(mode='wb', defaultextension=".727show")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        
        print("Cuelist contents at export:")
        for c in self.cuelist.cues:
            print(c)
        pickle.dump(self.cuelist, f)

    def importFile(self):
        f = filedialog.askopenfilename(filetypes=[("727 Shows",'*.727show'),('All Files','*')])
        if f is None or f == '':
            return

        with open(f, mode="rb") as infile:
            try:
                self.cuelist = pickle.load(infile)
            except ValueError as e:	
                msg = tk.tkMessageBox.showerror("Unable to load file",
                    "Unable to load the specified file - please check the format and try again" + 
                    "\n Error was " + str(e))
            else:
                self.showBox.delete(0, tk.END)
                for cue in self.cuelist.cues:
                    logging.debug(f"Imported cue {cue}")
                    if type(cue).__name__ == 'Delay_Item':
                        self.showBox.insert(tk.END, 'Delay ' +  str(cue.postDelay))
                    elif type(cue).__name__ == 'Label_Item':
                        self.showBox.insert(tk.END, 'Label ' +  str(cue.labelText))
                    elif type(cue).__name__ == 'Cuelist_Item':
                        self.showBox.insert(tk.END, str(cue.name))
                    elif type(cue).__name__ == 'Trigger_Item':
                        self.showBox.insert(tk.END, 'Wait/Skip: ' + str(cue.timeoutTime))
                    elif type(cue).__name__ =='Delay_Or_Skip_Item':
                        self.showBox.insert(tk.END, 'Wait/Continue' + str(cue.timeoutTime))
                    else: raise ValueError(f"Cue {cue} not of any known type, but of type {type(cue)} with type name {type(cue).__name__}")

        print(f"{len(self.cuelist.cues)} cues in cuelist, {self.showBox.size()} cues in showBox")


class actionButton(tk.Button):
    def __init__(self, parent, action, **options):
        super().__init__(parent, **options)
        self.action=action

        


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    root = tk.Tk()
    root.wm_title("727 Showmaker")
    app = showmaker(master=root, title="727 Showmaker")
    #app.updateAddState()

    app.mainloop()


