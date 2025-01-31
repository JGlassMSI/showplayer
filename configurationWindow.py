import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.messagebox import showinfo
from functools import partial
import logging

import serial
import serial.tools.list_ports


class ConfigWindow(tk.Toplevel):
    
    def __init__(self, master):

        super().__init__(master)
        self.master = master

        self.win = tk.Frame(self)

        self.serialList = serial.tools.list_ports.comports()
        if len(self.serialList) == 0: self.serialList = []

        #For troubleshooting/testing: 
        self.stateVar = tk.StringVar()
        self.stateVar.set("Hello, world")

        #self.win.title(title)
        
        self.headerFont = tkFont.Font(family="Lucida Grande", size=20)
        self.sectionFont = tkFont.Font(family="Lucida Grande", size=16)

        self.label = tk.Label(self.win, text="Configuration Options", font=self.headerFont)
        self.label.grid(row = 0, column = 0)

        #----COMPORTS----

        self.comportsFrame = tk.Frame(self.win)
        self.comportsLabel = tk.Label(self.comportsFrame, text="Serial Ports:", font = self.sectionFont, anchor='w')
        self.comportsLabel.grid(row = 0, column = 0, sticky = 'news')
        
        self.outLabel = tk.Label(self.comportsFrame, text="Serial Output to Plane:", anchor='w')
        self.outLabel.grid(row = 1, column = 0, sticky = 'ee')

        self.inLabel = tk.Label(self.comportsFrame, text="Serial Input from Remote:", anchor='w')
        self.inLabel.grid(row = 2, column = 0, sticky = 'ew')

        self.outVar = tk.StringVar()
        if len(self.serialList) > 0:
            self.outBox = tk.OptionMenu(self.comportsFrame, self.outVar, *self.serialList)
        else:
            self.outBox = tk.OptionMenu(self.comportsFrame, self.outVar, "")
        self.outBox.grid(row=1, column=1, sticky='ww')

        self.inVar = tk.StringVar()
        if len(self.serialList) > 0:
            self.inBox = tk.OptionMenu(self.comportsFrame, self.inVar, *self.serialList)
        else:
            self.inBox = tk.OptionMenu(self.comportsFrame, self.inVar, "")
        self.inBox.grid(row = 2, column=1, sticky='ew')

        self.comportsFrame.grid(row=1, column =0, sticky='news')

        #self.button = tk.Button(self.win, text="Press me to change something on the main page", command = self.changeMainPage)
        #self.button.grid(row = 2, column = 0)

        #----Logging-----

        self.loggingFrame = tk.Frame(self.win)
        self.loggingLabel = tk.Label(self.loggingFrame, text="Logging", font = self.sectionFont, anchor='w')
        self.loggingLabel.grid(row = 0, column = 0, sticky = 'news')

        self.levelLabel = tk.Label(self.loggingFrame, text="Logging Level:", anchor='w')
        self.levelLabel.grid(row = 1, column = 0, sticky = 'ew')

        self.loggingLevels ={    'Raw'      :   5,
                                 'Debug'    :   10,
                                 'Info'     :   20,
                         'Warning'  :   30,
                         'Error'    :   40,
                         'Critical' :   50
                        }

        self.loggingVar = tk.StringVar()
        self.loggingVar.set('Debug')
        self.loggingVar.trace_add("write", self.loggingAdjust)
        self.loggingSelect  = tk.OptionMenu(self.loggingFrame, self.loggingVar, *list(self.loggingLevels.keys()))
        self.loggingSelect.grid(row = 1, column =1, sticky='news')

        self.loggingFrame.grid(row=2, column=0, sticky='news')

        ##----inputs/outputs-----

        self.ioFrame = tk.Frame(self.win)
        self.ioLabel = tk.Label(self.ioFrame, text="I/O Configuration", font = self.sectionFont, anchor = 'w')
        self.ioLabel.grid(row = 0, column = 0, sticky = 'news')

        self.buttonTriggerLabel = tk.Label(self.ioFrame, text="Begin show via external input:", anchor = 'w')
        self.buttonTriggerLabel.grid(row=1, column=0, sticky='ew')

        self.startButtonVar = tk.IntVar()
        self.ioRadioEnable = tk.Radiobutton(self.ioFrame, text="Enabled", padx = 10, variable=self.startButtonVar, value = 1)
        self.ioRadioEnable.grid(row=1,column=1,sticky='ew')

        self.ioRadioDisable = tk.Radiobutton(self.ioFrame, text="Disabled", padx = 10, variable=self.startButtonVar, value = 0)
        self.ioRadioDisable.grid(row=1,column=2,sticky='ew')

        self.ioFrame.grid(row=3, column=0, sticky='news')



        ##----Wrap Up----------

        self.closeButton = tk.Button(self.win, text="Close", command = self.closeConfigWindow)
        self.closeButton.grid(row=4, column=0, sticky='e')

        self.win.pack()
        self.grab_set()
    
    def closeConfigWindow(self):
        self.grab_release()
        self.destroy()

    def changeMainPage(self):
        print("The button has been pressed")
        self.stateVar.set("The button has been pressed")

    def loggingAdjust(self, *args):
        newDebugLevel = int(self.loggingLevels[self.loggingVar.get()])
        logger = logging.getLogger()
        logger.setLevel(newDebugLevel)
        logger.log(newDebugLevel, f"New logging level: {newDebugLevel}")


class ConfigApplication(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.mainFrame = tk.Frame()
        self.cw = None

        self.myLabel = ttk.Label(self, text="This is the text to start")
        self.myLabel.pack()

        self.button_bonus = ttk.Button(self, text="Create Config Window", command=self.createConfigWindow)
        self.button_bonus.pack()

        self.button_showinfo = ttk.Button(self, text="Show Info", command=popup_showinfo)
        self.button_showinfo.pack()

    def createConfigWindow(self):
        self.cw = configWindow()
        self.cw.stateVar.trace_add("write", self.setLabelText)

    def setLabelText(self, *args):
        print("called set label text")
        self.myLabel.config(text = self.cw.stateVar.get())
        print(f"Text is now {self.myLabel.cget('text')}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root = tk.Toplevel()    

    app = Application(root)

    root.mainloop()
