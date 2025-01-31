import tkinter as tk
import logging
from functools import partial

class tester(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)
		self.master = master

		self.f = tk.Frame(self.master)
		self.f.pack()

		self.optionVar = tk.StringVar()
		self.options = ["First", "second", "third"]
		self.optionVar.set(self.options[0])

		self.o = tk.OptionMenu(self.f, self.optionVar, *self.options)
		self.o.pack()
		logging.debug("Done with init of options")

		self.l = tk.Label(text=self.optionVar.get())
		self.l.pack()

		def updateLabel(*args):
			newOption = self.optionVar.get()
			logging.debug(newOption)
			self.l['text'] = newOption
			
			if str(newOption) == "third":
				logging.debug("Comparison Successful")
				menu = self.o['menu']
				menu.add_command(label="new", command=partial(self.optionVar.set, 'new'))
				for i in range(self.o['menu'].index("end") + 1):
					logging.debug(self.o['menu'].entrycget(i, 'command'))
				#menu.delete(0,tk.END)	

				#menu.add_command(label="New Label!")
				#self.optionVar="New Label!"		
			
			'''
		    menu = self.optionmenu_b['menu']
	        menu.delete(0, 'end')

	        for country in countries:
	            menu.add_command(label=country, command=lambda nation=country: self.variable_b.set(nation))
			'''
			


		self.optionVar.trace_add("write", updateLabel)

		for i in self.o.keys():
			logging.debug(i)
		logging.debug("--------------------------------")
		for i in dir(self.o['menu']):
			logging.debug(i)
		logging.debug("--------------------------------")
		for i in range(self.o['menu'].index("end") + 1):
			logging.debug(self.o['menu'].entrycget(i, 'command'))

		


		

if __name__ == '__main__':

	logging.basicConfig(level=logging.DEBUG)

	root = tk.Tk()
	root.wm_title("Optionbox Test")
	test = tester(master=root)

	test.mainloop()