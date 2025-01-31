import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk
from tkinter.messagebox import showinfo
from functools import partial
import logging

import serial
import serial.tools.list_ports

class ExternalWindow(tk.Toplevel):
    def __init__(self, master):
        print("Hello, world")
        super().__init__(master)
        print("Goodbye world")

