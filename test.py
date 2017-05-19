'''
Created on May 3, 2017

@author: findj
'''
import Tkinter as tk
import sys


class Start(object):
    def __init__(self, master):
        self.authenticated = False  # <---
        master.grid()
        self.create_widgets()

    def create_widgets(self):
        return

    def reveal(self):
        content = self.password.get()
        if content == "password":
            self.authenticated = True  # <---
            root.destroy()
        else:
            message = "denied"
            self.text.insert(0.0,message)

root = tk.Tk()
root.title("Password")
root.geometry("250x150")
app = Start(root)
root.mainloop()

if not app.authenticated:  # <---
    sys.exit()  # <---