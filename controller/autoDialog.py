import tkinter as tk

class AutoDialog(tk.Toplevel):

    def __init__(self, parent, text, confirmText, cancelText):

        tk.Toplevel.__init__(self, parent)
        tk.Label(self, text=text).grid(row=0, column=0, columnspan=2, padx=50, pady=10)

        b_yes = tk.Button(self, text=confirmText, command=self.yes, width=8)
        b_yes.grid(row=1, column=0, padx=10, pady=10)
        b_no = tk.Button(self, text=cancelText, command=self.no, width=8)
        b_no.grid(row=1, column=1, padx=10, pady=10)

        self.answer = None
        self.protocol("WM_DELETE_WINDOW", self.no)

    def yes(self):
        self.answer = True
        self.destroy()

    def no(self):
        self.answer = False
        self.destroy()

class AutoWarning(tk.Toplevel):
    def __init__(self, parent, text):
        tk.Toplevel.__init__(self, parent)
        tk.Label(self, text=text).grid(row=0, column=1, columnspan=2, padx=50, pady=10)

        self.answer = None
        self.protocol("WM_DELETE_WINDOW", self.no)

    def yes(self):
        self.answer = True
        self.destroy()

    def no(self):
        self.answer = False
        self.destroy()

        
        

if __name__ == '__main__':
    root = tk.Tk()
    a = AutoWarning(root, "Hello!")
    root.after(5000, a.destroy)
    root.mainloop()
