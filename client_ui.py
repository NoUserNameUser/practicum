'''
Created on May 6, 2017

@author: findj
'''
import Tkinter as tk, ttk
from client import ClientSide
from tkFileDialog import askopenfilename
import tkMessageBox
import socket

LARGE_FONT = ("Verdana", 12)

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

        # manipulate multiple frames/pages of the app
        self.frames = {}
        for F in (StartPage, MainPage, GroupCreationPage, GroupJoinPage):
            frame = F(window, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)
        # self.show_frame(MainPage)
        self.app.connectTo()


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

    def get_frame(self, cont):
        frame = self.frames[cont]
        return frame

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
                controller.frames[MainPage].setWelcomeText(controller.app.user['username']+" #"+str(controller.app.user['_id']))
                controller.show_frame(MainPage)

                # feed group information to the treebox in main page
                mp = controller.get_frame(MainPage)
                mp.tree_insert(controller.app.groups)
            else:
                print "incorrect username"

    def entry_onchange(self, *args):
        # strip all white spaces on the left
        input = self.svar.get()
        input = input.lstrip()
        self.svar.set(input)

        # button state changer
        self.submit.config(state=(tk.NORMAL if self.svar.get() else tk.DISABLED))

# another page
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        # ---- label ----
        self.welcomeText = tk.StringVar()
        label = tk.Label(self, textvariable=self.welcomeText, font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # ---- create new group button ----
        new_group_button = tk.Button(self, text="Create new share group!", command=lambda : controller.show_frame(GroupCreationPage))
        new_group_button.pack()

        # ---- join group button ----
        new_group_button = tk.Button(self, text="Join a group!",
                                     command=lambda: controller.show_frame(GroupJoinPage))
        new_group_button.pack()

        # ---- Treeview groups box ----
        self.tree = ttk.Treeview(self)
        self.tree.bind("<Button-3>", self.do_popup)
        self.tree.pack()

        # ---- logout button ----
        button1 = tk.Button(self, text="Logout", command=lambda : self.logout(controller))
        button1.pack()

    def logout(self, controller):
        if controller.app.logout():
            controller.show_frame(StartPage)
        else:
            print 'Unexpected error encountered when logging out.'

    def setWelcomeText(self, text):
        self.welcomeText.set(text)

    def tree_insert(self, items):
        # ---- tree view for groups ----
        # tree = ttk.Treeview(self)
        self.tree_del_all_child()
        for i in items:
            print i
            index = 0
            g = self.tree.insert('', index, i['_id'], text=i['name']) # display the list of group
            for f in i['files']:
                print f
                findex = 0
                self.tree.insert(g, findex, f['f_id'], text=f['file_name']) # display the list of the files
                findex += 1
            index += 1

    def tree_del_all_child(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def group_control_menu(self, gid):
        self.popup = tk.Menu(self, tearoff=0)
        self.popup.add_command(label="Create share phrase", command=lambda : self.create_share_phrase(gid))
        self.popup.add_command(label="Upload files", command=lambda : self.file_to_group(gid))
        # self.popup.add_separator()

    def file_control_menu(self, fid, fname, pid):
        self.popup = tk.Menu(self, tearoff=0)
        self.popup.add_command(label="Download", command=lambda : self.file_download(fid, fname, pid))

    def do_popup(self, e):
        # display the popup menu
        iid = self.tree.identify_row(e.y)
        if iid:
            pid = self.tree.parent(iid)
            if pid:  # a child item is selected
                self.file_control_menu(iid, self.tree.item(iid)['text'], pid)
            else:  # top level is selected, populate group menu items
                self.group_control_menu(iid)

            self.tree.selection_set(iid)
            self.popup.post(e.x_root, e.y_root)
        else:
            pass

    def file_to_group(self, gid):
        fpath = askopenfilename()
        # file copy and do encryption
        # upload to server
        if not fpath:
            return False;
        self.controller.app.file_transfer(fpath, gid)
        self.tree_insert(self.controller.app.groups)

    def create_share_phrase(self, gid):
        result = self.controller.app.make_phrase(gid)
        msg = result['phrase']
        self.clipboard_clear()
        self.clipboard_append(msg)
        msg = "One-time share phrase "+msg+" created. It's in your clipboard now! Go ahead and paste it to your friend."
        tkMessageBox.showinfo("Your phrase", msg)

    def file_download(self, fid, fname, gid):
        self.controller.app.file_download(fid, fname, gid)

class GroupCreationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Enter a name for your group.", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # ---- textbox to insert group name ----
        self.svar = tk.StringVar()
        self.svar.trace("w", self.entry_onchange)

        self.textbox = tk.Entry(self, textvariable=self.svar)
        # textbox is bind to Return button
        self.textbox.bind('<Return>', lambda x: self.new_group_button_handler(controller))
        self.textbox.pack(pady=10, padx=10)

        # ---- submit button ----
        self.create_group_button = tk.Button(self, text="Create!", command=lambda : self.new_group_button_handler(controller), state=tk.DISABLED)
        self.create_group_button.pack()

        # ---- back button ----
        button1 = tk.Button(self, text="Back", command=lambda: controller.show_frame(MainPage))
        button1.pack()

    def new_group_button_handler(self, controller):
        gname = self.textbox.get()
        # TODO handle duplicate group names
        if gname:
            result = controller.app.create_share_group(gname)
            if result:
                controller.show_frame(MainPage)

                # update group information to the treebox in main page
                mp = controller.get_frame(MainPage)
                mp.tree_insert(controller.app.groups)
            else:
                print "Unexpected error encountered when creating group."

    def entry_onchange(self, *args):
        # strip all white spaces on the left
        input = self.svar.get()
        input = input.lstrip()
        self.svar.set(input)

        # button state changer
        self.create_group_button.config(state=(tk.NORMAL if self.svar.get() else tk.DISABLED))

class GroupJoinPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Enter share phrase", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        # ---- textbox to insert group name ----
        self.svar = tk.StringVar()
        self.svar.trace("w", self.entry_onchange)

        self.textbox = tk.Entry(self, textvariable=self.svar)
        # textbox is bind to Return button
        self.textbox.bind('<Return>', lambda x: self.join_group_button_handler(controller))
        self.textbox.pack(pady=10, padx=10)

        # ---- submit button ----
        self.join_group_button = tk.Button(self, text="Join!",
                                             command=lambda: self.join_group_button_handler(controller),
                                             state=tk.DISABLED)
        self.join_group_button.pack()

        # ---- back button ----
        button1 = tk.Button(self, text="Back", command=lambda: controller.show_frame(MainPage))
        button1.pack()

    def join_group_button_handler(self, controller):
        sharephrase = self.textbox.get()
        if sharephrase:
            result = controller.app.join_share_group(sharephrase)
            if result == 't':
                # update group information to the treebox in main page
                mp = controller.get_frame(MainPage)
                mp.tree_insert(controller.app.groups)
                controller.show_frame(MainPage)
            elif result == 'e':
                tkMessageBox.showinfo("Alert", "You've already joined this group!")
                print "User already joined this group"
            else:
                tkMessageBox.showinfo("Alert", "Incorrect share phrase!")


    def entry_onchange(self, *args):
        # strip all white spaces on the left
        input = self.svar.get()
        input = input.lstrip()
        self.svar.set(input)

        # button state changer
        self.join_group_button.config(state=(tk.NORMAL if self.svar.get() else tk.DISABLED))

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
    app = appGUI()
    app.mainloop()

    

