#showcontrols.py

import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
import tkinter.ttk as ttk
from plane_controls import *
from sys import exit
from functools import partial
import json

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
		self.showBox = tk.Listbox(self)
		self.commandButtons = list()
		self.stateButtons = list()
		self.pack()
		self.create_widgets()

	def addItem(self):
		if self.showBox.curselection() == ():
			index = tk.END
		else:
			index = self.showBox.curselection()[0]

		text = (self.commandButtons[self.activeButtonIndex]['text'], self.stateButtons[self.activeStateIndex]['text'])
		self.showBox.insert(index, ("command", text))

	def removeSelected(self):
		for d in Reverse(self.showBox.curselection()):
			self.showBox.delete(d)

	def commandButtonActivate(self, buttonIndex):
		if self.activeButtonIndex == buttonIndex:
			self.commandButtonDeactivate(buttonIndex)
			self.activeButtonIndex = -1
		else:
			for i in range(len(self.commandButtons)):
				self.commandButtonDeactivate(i)
			self.commandButtons[buttonIndex].configure(bg = showmaker.activeButtonColor)
			self.activeButtonIndex = buttonIndex
		self.updateAddState()

	def commandButtonDeactivate(self,buttonIndex):
		self.commandButtons[buttonIndex].configure(bg = showmaker.inactiveButtonColor)

	def stateButtonActivate(self, buttonIndex):
		if self.activeStateIndex == buttonIndex:
			self.stateButtonDeactivate(buttonIndex)
			self.activeStateIndex = -1
		else:
			for i in range(len(self.stateButtons)):
				self.stateButtonDeactivate(i)
			self.stateButtons[buttonIndex].configure(bg = showmaker.activeButtonColor)
			self.activeStateIndex = buttonIndex
		self.updateAddState()

	def stateButtonDeactivate(self,buttonIndex):
		self.stateButtons[buttonIndex].configure(bg = showmaker.inactiveButtonColor)

	def updateAddState(self):
		if self.activeButtonIndex >= 0 and self.activeStateIndex >= 0:
			self.addButton.configure(state=tk.NORMAL)
		else: self.addButton.configure(state=tk.DISABLED)

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

	def addDelayItem(self):
		if self.delayEntryValidate():
			if self.showBox.curselection() == ():
				index = tk.END
			else:
				index = self.showBox.curselection()[0]

			#text = 'delay:' + str(self.delayEntry.get())
			self.showBox.insert(index, ('delay', str(self.delayEntry.get())))

	def addLabelItem(self):
		if self.showBox.curselection() == ():
				index = tk.END
		else:
			index = self.showBox.curselection()[0]

		self.showBox.insert(index, ('label', str(self.labelEntry.get())))

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

	def create_planetab(self):
		self.planeFrame = tk.Frame(self.book,width=200,height=100)
		self.book.add(self.planeFrame,text="Automation Shows", sticky='ew')

		self.showLabel = tk.Label(self.planeFrame, text="Steps", font=self.labelFont)
		self.showLabel.grid(column=4, row=0, sticky='ew')

		self.instLabel = tk.Label(self.planeFrame, text="Select Activity and State", font=self.labelFont)
		self.instLabel.grid(column=0, columnspan=3, row=1, sticky='ew')		

		coms = SerialPlaneController.com()
		#print(f"coms: {coms}")

		buttonPos = 2
		col = 0
		index = 0
		for c in coms:
			button=tk.Button(self.planeFrame,text=str(c),font=self.basicFont, bg = showmaker.inactiveButtonColor, command=partial(self.commandButtonActivate, index))
			self.commandButtons.append(button)
			index += 1
			button.grid(column=col,row=buttonPos,sticky='ew',padx=2,pady=1)
			buttonPos += 1
			if buttonPos == len(coms)/2:
				col=1
				buttonPos = 2

		self.activateButton = tk.Button(self.planeFrame,text="activate", font=self.basicFont, bg = showmaker.inactiveButtonColor, command=partial(self.stateButtonActivate, 0))
		self.activateButton.grid(column=2,row=round(len(coms)/6), rowspan=2,padx=25)
		self.stateButtons.append(self.activateButton)

		self.cancelButton = tk.Button(self.planeFrame,text="cancel", font=self.basicFont, bg = showmaker.inactiveButtonColor, command=partial(self.stateButtonActivate, 1))
		self.cancelButton.grid(column=2,row=round(2*len(coms)/6), rowspan=2,padx=25)
		self.stateButtons.append(self.cancelButton)

		self.addButton = tk.Button(self.planeFrame,text="Add",font=self.labelFont,bg='#DDFFDD', command=self.addItem, disabledforeground='#888888')
		self.addButton.grid(column=3,row=round(len(coms)/4)-1, rowspan=4)

		self.yScroll = tk.Scrollbar(self.planeFrame, orient=tk.VERTICAL)
		self.yScroll.grid(row=3, column=5, rowspan=len(coms), sticky='nsw')

		self.showBox = tk.Listbox(self.planeFrame, font=self.basicFont, yscrollcommand=self.yScroll.set, activestyle='none', selectmode=tk.MULTIPLE)
		self.yScroll['command'] = self.showBox.yview

		self.showBox.grid(column=4,row=3, columnspan=2, rowspan=len(coms), sticky='nsew', padx=3)

		self.removeButton = tk.Button(self.planeFrame, text="Remove Selected Step(s)", font=self.basicFont,bg='#FFDDDD', command=self.removeSelected)
		self.removeButton.grid(column=4,row=len(coms)+3, padx=3, pady=5)

		self.delayButton = tk.Button(self.planeFrame, text="Delay(ms)", font=self.basicFont,bg='#DDFFDD', command=self.addDelayItem)
		self.delayButton.grid(column=1, columnspan = 1, row=len(coms)+3, padx=3, pady=5, sticky='ew')

		self.delayVar = tk.StringVar()
		self.delayVar.trace_add("write", self.delayEntryCallback)
		self.delayEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont, justify=tk.RIGHT, textvariable=self.delayVar)
		self.delayEntry.grid(column=0, row=len(coms)+3, padx = 3, pady=5, sticky='ew')
		self.updateDelayButtonState()

		self.labelVar = tk.StringVar()
		self.labelVar.trace_add("write", self.labelEntryCallback)
		self.labelEntry = tk.Entry(self.planeFrame, text="", font=self.basicFont,justify=tk.RIGHT, textvariable=self.labelVar)
		self.labelEntry.grid(column=0, row=len(coms)+4, padx=3, pady=2, sticky='nesw')

		self.labelButton = tk.Button(self.planeFrame, text="Add Label", font=self.basicFont,bg='#DDFFDD', command = self.addLabelItem)
		self.labelButton.grid(column=1, row=len(coms)+4, padx=3, pady=2, sticky='ew')
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
		self.grid_columnconfigure(0, minsize=100)
		self.grid_columnconfigure(1, minsize=100)
		self.grid_columnconfigure(4, minsize=400)

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

		s = ttk.Style()
		s.configure('TNotebook.Tab', font=('Lucida Grande','14') )

		self.book = ttk.Notebook(self)
		self.book.grid(row=2, column=0, sticky='ew')

		self.create_planetab()

		# self.create_lightingtab()
		
	
	def newFile(self):
		print("Start a new file")

	def exportFile(self):
		#Make json from file list



		stepList = list()
		for l in self.showBox.get(0, self.showBox.size()-1):
			key, val = l[0], l[1]
			stepList.append((key,val))

		logging.debug(stepList)
			
		output = {'steps':stepList}
		print(output)

		f = filedialog.asksaveasfile(mode='w', defaultextension=".727show")
		if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
			return
		
		json.dump(output, f)

	def importFile(self):
		f = filedialog.askopenfilename(filetypes=[("727 Shows",'*.727show'),('All Files','*')])
		if f is None or f == '':
			return

		newDict = dict()

		with open(f, mode="r") as infile:
			try:
				inputDict = json.load(infile)
				logging.debug(f"Loaded dictionary: {(str(inputDict))}")
				stepList = inputDict['steps']
			except ValueError as e:	
				msg = tk.tkMessageBox.showerror("Unable to load file",
					"Unable to load the specified file - please check the format and try again" + 
					"\n Error was " + str(e))
			else:
				#clear existing steps
				self.clearAllSteps()
				#add new steps
				for step in stepList:
					self.showBox.insert(tk.END, str(step[0])+":"+str(step[1]))



		


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)

	root = tk.Tk()
	root.wm_title("727 Showmaker")
	app = showmaker(master=root, title="727 Showmaker")
	app.updateAddState()

	app.mainloop()


