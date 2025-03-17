import tkinter as tk
import tkinter.font as tkFont
import logging

from .plane_controls import *

class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master
		self.pack()
		self.create_widgets()

	def create_widgets(self):
		self.titleStyle = tkFont.Font(family="Lucida Grande", size=30)
		self.titleLabel = tk.Label(self, text="727 Controller Automation Controller", font=self.titleStyle)
		self.titleLabel.grid(column=0, row=0, columnspan=4)

		#self.hi_there = tk.Button(self)
		#self.hi_there["text"] = "Hello World\n(click me)"
		#self.hi_there["command"] = self.say_hi
		#self.hi_there.pack(side="top")

		self.quit = tk.Button(self, text="QUIT", fg="red",
							  command=self.master.destroy)
		self.quit.grid(row=1)

	def say_hi(self):
		print("hi there, everyone!")

if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG)

	root = tk.Tk()
	app = Application(master=root)