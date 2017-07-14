'''
Created on May 6, 2017

@author: findj
'''
import Tkinter as tk

LARGE_FONT = ("Verdana", 12)

class appgui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.win_conf("FiSi")
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, ExamplePage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def win_conf(self, title):
        self.title(title)

        # get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # resize the app based on screen resolution
        app_width = screen_width * 2 / 3
        app_height = screen_height * 2 / 3

        # offset to center the app window
        offsetX = screen_width / 2 - app_width / 2
        offsetY = screen_height / 2 - app_height / 2
        self.geometry("%dx%d+%d+%d" % (app_width, app_height, offsetX, offsetY))

        # configure the background color
        self.configure(background="white")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Please log in.", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Login", command=lambda : controller.show_frame(ExamplePage))
        button1.pack()

    def qf(self, message):
        print message

class ExamplePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Logout", command=lambda : controller.show_frame(StartPage))
        button1.pack()


# main function
if __name__ == "__main__":
    app = appgui()
    app.mainloop()

    

