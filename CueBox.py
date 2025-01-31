import tkinter as tk
from Cuelist import *

class CueBox(tk.Listbox):
    """
    docstring
    """

    prefixes = {
        Cuelist_Item: "",
        Label_Item: "Label: ",
        Delay_Item: "Delay: "
    }

    def __init__(self, parent, cuelist, **options):
        super().__init__(parent, **options)
        self.cuelist = cuelist

    def updateFromCues(self):
        self.delete(0, tk.END)
        for cue in self.cuelist:
            if type(cue) != Delay_Item:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Other: ")}{cue.name}')
            else:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Other: ")}{cue.postDelay}')

    def updateFromGivenCues(self, cues):
        self.delete(0, tk.END)
        for cue in cues:
            if type(cue) == Delay_Item:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Delay: ")}{cue.postDelay}')
            elif type(cue) == Trigger_Item:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Wait/Cancel: ")}{cue.timeoutTime}')
            elif type(cue) == Delay_Or_Skip_Item:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Wait/Continue: ")}{cue.timeoutTime}')
            else:
                self.insert(tk.END, f'{CueBox.prefixes.get(type(cue), "Other: ")}{cue.name}')
            
                
