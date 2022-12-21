"""
NAME
parsertoolframe

DESCRIPTION
Left side tool frame for the Parse window of the luminescence time drive data parser.

This module is part of the user interface of the LumParsing package for working with luminescence time drive data.
The parser tool frame is controlled by the Parse window.
This frame lets the user interact with time drive (.td) files, to select which files to parse and to set parsing
settings per file or for all files at once.
The type of plot to show can also be adjusted.

The class ParserToolFrame describes the interactions of the frame.
In the interface, it is initiated with the frame it resides within as parent and the Parse window as controller.

Plotting data and choosing signals are controlled by the Parse window and its sub frame the parser mix frame,
respectively.

User interactions through mouse and keyboard:

Mouse:
Left click on a time drive file     Select the file and plot with current settings
Left click on a setting and type    Change the setting value

Keyboard:
Return                              Apply the changed setting
Arrow up                            Select the file above the current selection
Arrow down                          Select the file below the current selection
Right arrow                         Move to the signal box in the parser mix frame and select the first signal
                                    found in the file

CLASSES
ParserToolFrame (subclass of tk.Frame)
"""

import lumparser.parsertools as pt
import tkinter as tk
from tkinter import N, S, W, E, DISABLED, RIGHT, END, ANCHOR
from lumparser.parsertools.defaultvalues import default_import_folder


class ParserToolFrame(tk.Frame):

    def __init__(self, parent, controller, borderwidth=5):
        self.parent = parent
        self.controller = controller
        self.import_folder = default_import_folder
        self.parser = pt.Parser()
        tk.Frame.__init__(self, self.parent, borderwidth=borderwidth)

        # fill the toolbar (left side of the screen)
        ## file loading
        loader = tk.Frame(self)
        loader.grid(row=0, column=0, pady=2, sticky=N + S + W + E)
        loader.grid_columnconfigure(0, weight=1)
        loader.grid_columnconfigure(1, weight=1)
        loader_title = tk.Label(loader, text="Click to import time drive files:  ")
        loader_title.grid(row=0, column=0, sticky=W)
        self.loader_button = tk.Button(loader, text="Import", command=self.import_files)
        self.loader_button.grid(row=0, column=1, columnspan=2, sticky=N + S + E + W)
        imp = self.import_folder
        imp = (imp[:25] + '..') if len(imp) > 27 else imp
        self.dir_text = tk.Label(loader, text=imp)
        self.dir_text.grid(row=1, column=0, sticky=N + S + W)
        self.dir_button = tk.Button(loader, text="Change", command=self.launch_dir)
        self.dir_button.grid(row=1, column=1, columnspan=2, sticky=N + S + E + W)
        loader_scrollbar = tk.Scrollbar(loader)
        loader_scrollbar.grid(row=2, column=2, sticky=N + S)
        self.loader_box = tk.Listbox(loader, exportselection=0, yscrollcommand=loader_scrollbar.set)
        self.loader_box.grid(row=2, column=0, columnspan=2, sticky=W + E + N + S)
        loader_scrollbar.config(command=self.loader_box.yview)
        self.loader_box.bind('<<ListboxSelect>>', self.on_select)
        self.loader_box.bind('<Delete>', self.remove_file)
        self.loader_box.bind('<BackSpace>', self.remove_file)
        self.loader_box.bind('<Right>', lambda *args: self.controller.parse_options.signalbox.focus_set())

        ##setting adjustment
        setter = tk.LabelFrame(self, text="Settings for parsing")
        setter.grid(row=1, column=0, pady=2, sticky=N + S + W + E)
        self.variables = [
            {
                "name": "starting_point",
                "label": "Expected first peak:  ",
                "var": tk.IntVar(),
                "unit": "[datapoints]"
            },
            {
                "name": "threshold",
                "label": "Peak threshold:  ",
                "var": tk.DoubleVar(),
                "unit": "[RLU]"
            },
            {
                "name": "bg_bound_L",
                "label": "Background from:  ",
                "var": tk.DoubleVar(),
                "unit": "[s]"
            },
            {
                "name": "bg_bound_R",
                "label": "to:  ",
                "var": tk.DoubleVar(),
                "unit": "[s]"
            }
        ]
        for i, v in enumerate(self.variables):  # create an entry field with labels
            v["label"] = tk.Label(setter, text=v["label"])
            v["label"].grid(row=i, column=0, sticky=E)
            v["var"].set(0)  # default when no file is loaded
            v["field"] = tk.Entry(setter, textvariable=self.variables[i]["var"], width=6, justify=RIGHT)
            v["field"].bind("<Return>", lambda *args, v=v: self.on_change(v))
            # v["field"].bind("<FocusOut>", lambda *args, v=v: self.on_change(v))
            v["field"].grid(row=i, column=1, sticky=W)
            v["unit"] = tk.Label(setter, text=v["unit"])
            v["unit"].grid(row=i, column=2, sticky=W)
        self.apply_button = tk.Button(setter, text="Apply to all", command=self.apply_all, state=DISABLED)
        self.apply_button.grid(row=i + 1, column=2, sticky=E)

    def import_files(self):
        """
        Load all time drive files in the user directory into the parser.

        update_loaderbox will then display all time drive in the parser in the
        loaderbox. Files in the parser can be removed from the analysis and
        at the same time from the loaderbox.
        """
        self.parser.import_ascii(self.import_folder)
        self.update_loaderbox()
        print("Files loaded.\nClick on a file to show data and adjust settings.")

    def launch_dir(self):
        """
        Open window where user can change import directory.

        Call change_dir upon finish.
        """
        self.dir_window = tk.Toplevel(self)
        self.dir_window.columnconfigure(0, weight=1)
        self.import_var = tk.StringVar(value=self.import_folder)
        self.folder_field = tk.Entry(self.dir_window, textvariable=self.import_var,
                                     width=len(self.import_folder))
        self.folder_field.grid(row=0, column=0, sticky=N+E+S+W)
        change_button = tk.Button(self.dir_window, text="Save", command=self.change_dir)
        change_button.grid(row=1, column=0, sticky=N+E+S)

    def change_dir(self):
        self.import_folder = self.import_var.get()
        imp = self.import_var.get()
        imp = (imp[:25] + '..') if len(imp) > 27 else imp
        self.dir_text.config(text=imp)
        self.dir_window.destroy()

    def update_loaderbox(self):
        """Diplay all .td files in the parser in the loaderbox."""
        self.loader_box.delete(0, END)
        for filename in self.parser.datasets.keys():
            self.loader_box.insert(END, filename)

    def remove_file(self, event):
        """Remove file from the parser and thus from analysis and display."""
        clicked_file = self.loader_box.get("active")
        index = self.loader_box.index("active")
        self.parser.remove_file(clicked_file)
        self.update_loaderbox()
        if len(self.parser.datasets) > index:
            self.loader_box.activate(index)
        else:
            self.loader_box.activate(END)
        print("%s has been deleted." % clicked_file)

    def on_select(self, event):
        """When a time drive is selected, display its information and plot it."""
        self.controller.plot_options.config(state="normal")
        self.apply_button.config(state="normal")
        if self.controller.active_plot == "mixed":
            self.controller.active_plot.set("original")
        clicked_file = self.loader_box.get(self.loader_box.curselection())
        # set the displayed variables to variables of the selected file
        for i, v in enumerate(self.variables):
            value = self.parser.parse_settings[clicked_file][v["name"]]
            self.variables[i]["var"].set(value)
        self.display(clicked_file)

    def on_change(self, var):
        """When parsing variables are changed, update the plot."""
        active_file = self.loader_box.get("active")
        if active_file == []:
            print("No file is selected")
            return
        # set the file variable to the variable put in by the user
        updated_var = var["name"]
        new_value = var["var"].get()
        self.parser.set_vars(active_file, updated_var, new_value)
        self.controller.active_plot.set("original")
        self.display(active_file)

    def apply_all(self):
        """Apply the variables that are put in to all time drives."""
        active_file = self.loader_box.get(self.loader_box.curselection())
        for var in self.variables:
            varname = var["name"]
            new_value = var["var"].get()
            self.parser.apply_all(varname, new_value)
        self.display(active_file)

    def display(self, thisfile):
        """
        Display information on the given time drive and plot it.

        Recalculate signal detection with the most recent parameters given by
        user before showing.
        """
        self.controller.title_text.set(thisfile)
        self.parser.update_signals(thisfile)
        self.update_signalbox(thisfile)
        self.controller.plot_file(thisfile)

    def update_signalbox(self, thisfile):
        """Display signals detected in given file."""
        self.controller.parse_options.signalbox.delete(0, END)
        for signal in self.parser.signals[thisfile]:
            self.controller.parse_options.signalbox.insert(END, signal.name)

    def open_rename_window(self):
        """
        Open a window that lets user rename a signal.

        Call rename_signal upon finish.
        """
        thisfile = self.loader_box.get("active")
        signal_index = self.controller.parse_options.signalbox.index(ANCHOR)
        signal = self.parser.signals[thisfile][signal_index]
        self.rename_window = tk.Toplevel(self.controller.parse_options)
        self.rename_window.title("Rename signal")
        print("Note: the names of signals in a file will be automatically updated when the file is reloaded.")
        label2 = tk.Label(self.rename_window, text="Signal name:  ")
        label2.grid(row=0, column=0, columnspan=2, sticky=W)
        self.new_signal_name = tk.StringVar()
        self.new_signal_name.set(signal.name)
        name_entry = tk.Entry(self.rename_window, textvariable=self.new_signal_name)
        name_entry.grid(row=0, column=2, columnspan=2, sticky=N + S + E + W)
        name_entry.focus_set()
        name_entry.bind('<Return>',
                        lambda *args: self.rename_signal(signal, self.new_signal_name.get()))
        export_button = tk.Button(self.rename_window, text="Save",
                                  command=lambda *args: self.rename_signal(signal, self.new_signal_name.get()))
        export_button.grid(row=1, column=3, sticky=N + S + E + W)

    def rename_signal(self, signal, name):
        signal.rename(name)
        self.update_signalbox(signal.filename)
        self.rename_window.destroy()
