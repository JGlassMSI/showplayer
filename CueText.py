import tkinter as tk
import tkinter.font as tkFont
import logging
from functools import partial
from CueListener import CueListener

class CueText(tk.Text, CueListener):

    defaultColors = {
        'highlight' : '#41C73A',
    }

    def __init__(self, parent, cuelist, colors=defaultColors, **options):
        super().__init__(parent, **options)
        self.cuelist = cuelist
        self.colors=colors

    def parseCuelist(self):
        self.parseSteps(self.cuelist.cues)

    def parseSteps(self, showSteps):
        self.delete(1.0, tk.END)

        for i in range(len(showSteps)):
            step = showSteps[i]
            stepType = type(step).__name__
            tagType = {
                'Label_Item':'label',
                'Delay_Item':'delay',
                'Trigger_Item':'trigger',
                'Delay_Or_Skip_Item':'continue'
            }.get(stepType, 'command')
            logging.debug(f"Parsing step {i} of type {stepType}")

            linetag = "line"+str(i)
            self.tag_config(linetag, background="#41C73A") #highlighted line color
            self.tag_lower(linetag)

            if stepType == 'Label_Item': 
                logging.debug("Adding label item")
                self.insert(tk.END,str('Label'), (tagType,linetag))
                self.insert(tk.END, "\t" + str(step.name.upper()), (tagType,linetag))
            elif stepType == 'Delay_Item':
                logging.debug("Adding delay item")
                self.insert(tk.END,str('Delay'), (tagType,linetag))
                self.insert(tk.END,"\t"+str(step.postDelay), (tagType,linetag))
                self.insert(tk.END," (ms)", (tagType,linetag))
            elif stepType == 'Trigger_Item':
                logging.debug("Adding trigger item")
                self.insert(tk.END,str('Wait/Cancel '), (tagType,linetag))
                self.insert(tk.END,"\t"+str(step.timeoutTime), (tagType,linetag))
                self.insert(tk.END," (ms) Timeout", (tagType,linetag))
            elif stepType == 'Delay_Or_Skip_Item':
                logging.debug("Adding continue item")
                self.insert(tk.END,str('Wait/Continue'), (tagType,linetag))
                self.insert(tk.END,"\t"+str(step.timeoutTime), (tagType,linetag))
                self.insert(tk.END," (ms) Timeout", (tagType,linetag))
            else:
                logging.debug("Adding other item")
                self.insert(tk.END,"\t"+step.name, (tagType,linetag))
            self.insert(tk.END,"\n", (tagType,linetag))

    def clearSteps(self):
        self.delete(1.0, tk.END)

    def updateHighlight(self):
        self.highlightOnlyLine(self.cuelist.currentCueNum)

    def highlightLine(self, lineNum):
        if lineNum >=0:
            linetag = "line"+str(lineNum)
            self.tag_raise(linetag)

    def highlightOnlyLine(self, line):
        logging.debug(f"Highlighting only line {line} in CueText")
        for i in range(len(self.cuelist)):
            linetag = "line"+str(i)
            self.tag_lower(linetag)
        self.highlightLine(line)
    
    def unhighlightAll(self):
        logging.debug("Un-highlighed all members of CueText")
        for i in range(len(self.cuelist)):
            linetag = "line"+str(i)
            self.tag_lower(linetag)


    def unhighlightLastLine(self):
        lastStep = len(self.cues)-1
        linetag = "line"+str(lastStep)
        self.tag_lower(linetag)
        logging.debug("Removing highlight from last line of show")

    def cueSignal(self, cuenum, master):
        logging.debug(f"This textbox received the signal {cuenum} from one of its cuelists")
        return

        #TODO: make this update work so CueText can display current cue:        
        if cuenum >= 0: nextFunc =  partial(self.highlightOnlyLine, cuenum)
        
        else: nextFunc = partial(self.unhighlightAll)
        nextFunc.__name__ = 'nextFunction'
        master.after(10, nextFunc)
        #self.highlightOnlyLine(cuenum)
