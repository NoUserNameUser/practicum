'''
Created on May 6, 2017

@author: findj
'''
import Tkinter as tk
from client import ClientSide
import socket

LARGE_FONT = ("Verdana", 12)
CONNECTION = {
    'host' : "localhost",
    'port' : 8888
}

class appGUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        # initialize the app
        self.app = ClientSide()

        # initialize the GUI
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="")
        self.win_conf("FiSher")

        # configure frame inside the window
        window = tk.Frame(self)
        window.pack(side="top", fill="both", expand=True)
        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0, weight=1)

        # alter window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # initialize content holders
        self.user = {} # holds user info

        # manipulate multiple frames/pages of the app
        self.frames = {}
        for F in (StartPage, MainPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        self.app.connectTo(CONNECTION['host'], CONNECTION['port'])
        # try:
        #     self.app.connectTo(CONNECTION['host'], CONNECTION['port'])
        # except socket.error, e:
        #     print e
        #     print "Unable to reach server."
        #     # self.show_error(window, "Unable to reach the server.")
        #     return

    # function to configure the main app window
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

    # function to bring a frame on top
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # function to bring error page on top
    def show_error(self, parent, errMsg):
        frame = ErrorPage(parent, self, errMsg)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

    def on_closing(self):
        self.app.disconnect()
        self.destroy()

# Start page of the app
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Log in.", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        #---- textbox ----
        # create string variable for tracing changes
        self.svar = tk.StringVar()
        self.svar.trace("w", self.entry_onchange)

        self.textbox = tk.Entry(self, textvariable=self.svar)
        # textbox is bind to Return button
        self.textbox.bind('<Return>', lambda x: self.login_validation(controller))
        self.textbox.pack(pady=10, padx=10)

        # ---- submit button ----
        self.submit = tk.Button(self, text="Login", command=lambda : self.login_validation(controller), state=tk.DISABLED)
        self.submit.pack()

    # function to validate users and redirect to other frames
    def login_validation(self, controller):
        # username variable
        uname = self.textbox.get()
        if uname:
            result = controller.app.login_auth(uname)
            if result:
                controller.show_frame(MainPage)
            else:
                print "incorrect username"

    def entry_onchange(self, *args):
        self.submit.config(state=(tk.NORMAL if self.svar.get() else tk.DISABLED))

# another page
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Welcome!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Logout", command=lambda : controller.show_frame(StartPage))
        button1.pack()

# error page
class ErrorPage(tk.Frame):
    def __init__(self, parent, controller, errMsg):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text=errMsg, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Retry", command=lambda: controller.show_frame(StartPage))
        button1.pack()


# main function
if __name__ == "__main__":
    print CONNECTION
    app = appGUI()
    app.mainloop()

    

