"""
Parser interface for luminescence time drive data

This is the script that opens the main window and controls the parser and
analysis windows.
Parser_tools contains the underlying methods and deals with all data operations.

The script contains two classes:
Std_redirector - used to redirect printed messages to the interface instead of
    printing them on the console.
App - the application that is created.
    The __init__ method creates all visible objects on the screen, which in turn
    call the other methods upon user interaction.
"""

import sys
import os
import src.parsertools as pt
from src.user_interface.anawindow import AnaFrame
from src.user_interface.parsewindow import ParseFrame
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import N, S, W, E, TOP, BOTH, END
from src.user_interface.stdredirector import StdRedirector


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        # initialise the main window
        tk.Tk.__init__(self, *args, **kwargs)
        self.state("zoomed")

        # set attributes for window display
        self.windownames = []
        self.windows = {}
        self.active_window = None
        self.controller = self
        self.default_name = "parsed_file"
        self.name_count = 0
        # set path names for data retrieval
        self.data_folder = os.path.join(os.getcwd(), "../..", "data")
        self.import_folder = os.path.join(self.data_folder, "td")

        # create screen layout
        self.mainframe = tk.Frame(self)
        self.mainframe.pack(side=TOP, fill=BOTH, expand=1)
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_rowconfigure(0, weight=1)

        # create text widget displaying printed messages
        scrollb = tk.Scrollbar(self.mainframe)
        scrollb.grid(row=0, column=1, sticky=N + S + E + W)
        self.textout = tk.Text(self.mainframe, width=90, height=15)
        self.textout.grid(row=0, column=0, sticky=N + W + S + E)
        scrollb.config(command=self.textout.yview)
        sys.stdout = StdRedirector(self.textout)
        print("Welcome to the Gaussia Luciferase data analysis kit")
        print("Click Start-Import to start importing .td files")
        print("Click Start-Open to load previously parsed files")

        # create menubar at top of screen. Buttons: Start, Window, Output
        self.menubar = tk.Menu(self)
        # Start menu for importing data for parser or opening parsed files for
        # analysis
        startmenu = tk.Menu(self.menubar)
        startmenu.add_command(label="Import", command=self.start_import)
        startmenu.add_command(label="Open", command=self.launch_open)
        startmenu.add_separator()
        startmenu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="Start", menu=startmenu)
        self.config(menu=self.menubar)
        # View menu to change between windows
        # updated when windows are opened or closed
        self.viewmenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Window", menu=self.viewmenu)
        # Output menu to save data or parse from parsing window to start analysis
        # updated when changed from one window to another
        self.outputmenu = tk.Menu(self.menubar)
        self.menubar.add_cascade(label="Output", menu=self.outputmenu)

    def start_import(self):
        """Go to the parsing window. If it does not exist yet, open one."""
        name = "parsing"
        if name in self.windownames:
            self.show_frame(name)
        else:
            self.windownames.append(name)
            self.windows[name] = ParseFrame(self.mainframe, self.controller)
            self.windows[name].grid(row=0, column=0, columnspan=2, sticky=N + E + S + W)
            self.show_frame(name)

    def launch_open(self):
        """
        Open window to let user pick parsed file to open in Analysis window.

        Call open_set upon finish to open an analysis window with the chosen data.
        """
        self.open_window = tk.Toplevel(self)
        loader = tk.Frame(self.open_window)
        loader.pack(side=TOP, fill=BOTH, expand=1)
        loader.grid_columnconfigure(0, weight=1)
        loader.grid_columnconfigure(1, weight=1)
        loader_title = tk.Label(loader, text="Select a file to open:  ")
        loader_title.grid(row=0, column=0, sticky=W)
        loader_scrollbar = tk.Scrollbar(loader)
        loader_scrollbar.grid(row=1, column=2, sticky=N + S)
        self.open_box = tk.Listbox(loader, exportselection=0,
                                   yscrollcommand=loader_scrollbar.set, width=40)
        self.open_box.grid(row=1, column=0, columnspan=2, sticky=W + E + N + S)
        loader_scrollbar.config(command=self.open_box.yview)

        folder = os.path.join(self.data_folder, "parsed")  # directory of script
        files = []
        for f in os.listdir(folder):
            if f.endswith('.parsed'):
                directory = os.path.join(folder, f)
                files.append({"name": f, "directory": directory})
                self.open_box.insert(END, f)
        loader_button = tk.Button(loader, text="Open",
                                  command=lambda *args: self.open_set(files))
        loader_button.grid(row=2, column=1, columnspan=2, sticky=N + S + E + W)

    def open_set(self, files):
        """Open an analyis window with the chosen data."""
        index = self.open_box.index("active")
        self.open_window.destroy()
        group = pt.Signalgroup.loadfrom(files[index]["directory"])
        name = group.filename
        if name in self.windownames:
            self.show_frame(name)
            return
        self.windownames.append(name)
        self.windows[name] = AnaFrame(self.mainframe, self.controller, signalgroup=group)
        self.windows[name].grid(row=0, column=0, columnspan=2, sticky=N + E + S + W)
        self.show_frame(name)

    def show_frame(self, name):
        """Display the given window."""
        try:
            self.active_window.grid_remove()   # remove the active window
        except AttributeError:
            pass
        self.windows[name].grid()   # show the new window
        self.active_window = self.windows[name]  # and update the active window

        # update widgets to display in active window
        plt.figure(self.active_window.fig.number)   # plot
        sys.stdout = StdRedirector(self.active_window.textout)  # text widget

        # update the view menu
        self.viewmenu.delete(0, END)
        for name in self.windownames:
            self.viewmenu.add_command(label=name, command=lambda name=name: self.show_frame(name))
        self.viewmenu.add_separator()
        self.viewmenu.add_command(label="close current", command=lambda: self.close_frame())
        # update the output menu
        self.menubar.entryconfig(3, menu=self.active_window.outputmenu)
        self.active_window.bind_all("<Control-s>", lambda *args: self.active_window.save_set())

    def close_frame(self):
        """Close the window that is currently active and destroy it."""
        try:
            name = self.active_window.signalgroup.filename
        except AttributeError:
            name = "parsing"
        # destroy window and remove from list of windows
        self.active_window.destroy()
        self.windownames.remove(name)
        self.windows.pop(name)
        self.active_window = None
        # update the View menu
        self.viewmenu.delete(0, END)
        for w_name in self.windownames:
            self.viewmenu.add_command(label=w_name, command=lambda w_name=w_name: self.show_frame(w_name))
        # update the Output menu
        self.menubar.entryconfig(3, menu=self.outputmenu)

if __name__ == "__main__":
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
    app.quit()