import tkinter as tk
import tkinter.messagebox as mb
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog
import tkextensions as tke
from functools import partial
from externalWindowTesting import *

class mainWindow(tk.Frame):
    def __init__(self, master=None,name="Default Name"):
        super().__init__(master)
        self.master = master

        f = tk.Frame(self)

        b = tk.Button(f, text="Show External Window", command = self.createEW)
        b.grid(row=0,column=0)
        f.pack()
        self.pack()

    def createEW(self):
        ew = ExternalWindow(self.master)

if __name__ == '__main__':

    root = tk.Tk()
    root.wm_title("Main Window")
    mw = mainWindow(master=root, name="Main Window")

    mw.mainloop()

