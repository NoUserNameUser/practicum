'''
Created on May 6, 2017

@author: findj
'''
import Tkinter as tk

def render(frame):
    frame.mainloop()
    return

def init(title, width, height):
    window = tk.Tk()
    window.title(title)
    window.geometry(str(width)+'x'+str(height))
    return window

# main function
if __name__ == "__main__":
    frame = init('myApp', 1200, 900)
    render(frame)
    
    

