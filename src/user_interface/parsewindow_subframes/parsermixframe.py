"""
Right side tool frame for the Parse window of the luminescence time drive data parser.

This module is part of the user interface of the LumParsing package for working with luminescence time drive data.
The parser mix frame is controlled by the Parse window.
This frame lets the user see what signals are detected in a time drive (.td) file with certain parsing settings.
There is also an option to pick and mix signals from different time drives to create a mixed dataset.

The class ParserMixFrame describes the interactions of the frame.
In the interface, it is initiated with the frame it resides within as parent and the Parse window as controller.

Plotting data, choosing files and setting parse settings are controlled by the Parse window and its
sub frame the parser tool frame, respectively.

User interactions through mouse and keyboard:

Mouse:
Left-click on a signal              Select the signal
Double left-click on a signal in
     the box of detected signals
     (Signalbox)                    Add the signal to the mixed dataset
Double left-click on a signal in
    the mixed dataset               Remove the signal from the mixed dataset

Keyboard:
Space                               Add the selected signal to the mixed dataset
Arrow up                            Select the signal above the current selection
Arrow down                          Select the signal below the current selection
Left arrow                          Move to the file selection box in the parser tool frame and select the last
                                    selected file
Delete                              Remove the selected signal from the mixed dataset
Backspace                           Remove the selected signal from the mixed dataset
"""

import copy
import src.parsertools as pt
import tkinter as tk
from tkinter import N, S, W, E, EXTENDED, END
from src.parsertools.defaultvalues import default_import_folder


class ParserMixFrame(tk.Frame):

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.import_folder = default_import_folder
        self.parser = pt.Parser()
        tk.Frame.__init__(self, self.parent)

        self.mixsignals = []

        # extra options (right side of the screen)
        self.signal_info = tk.LabelFrame(self, text="Signal information")
        self.signal_info.grid(row=0, column=0, columnspan=3, pady=2, sticky=N + S + W + E)

        self.mixframe = tk.LabelFrame(self, text="Signals in mixed dataset")
        self.mixframe.grid(row=2, column=0, columnspan=3, pady=2, sticky=N + S + W + E)

        ##signal information
        self.signal_info.grid_columnconfigure(0, weight=1)
        signalbox_label = tk.Label(self.signal_info, text="Signals in current file:  ")
        signalbox_label.grid(row=1, column=0, sticky=W)
        signal_scrollbar = tk.Scrollbar(self.signal_info)
        signal_scrollbar.grid(row=2, column=2, sticky=N + S)
        self.signalbox = tk.Listbox(self.signal_info, name="signalbox", exportselection=0, selectmode=EXTENDED,
                                    yscrollcommand=signal_scrollbar.set)
        self.signalbox.grid(row=2, column=0, columnspan=2, sticky=N + S + E + W)
        signal_scrollbar.config(command=self.signalbox.yview)
        self.signalbox.bind('<Double-1>', self.add_signal)
        self.signalbox.bind('<space>', self.add_signal)
        self.signalbox.bind('<Left>', lambda *args: self.controller.tools.loader_box.focus_set())
        self.signalbox.bind('<Control-n>', lambda *args: self.controller.tools.open_rename_window())
        self.cur_type = tk.StringVar()
        type_label = tk.Label(self.signal_info, textvariable=self.cur_type)
        type_label.grid(row=3, column=0, columnspan=3, sticky=W)

        ##mixbox
        mixlabel1 = tk.Label(self.mixframe, text="Double click on a signal to add it to the dataset")
        mixlabel1.grid(row=3, column=0, columnspan=2, sticky=W)
        mixpadding1 = tk.Frame(self.mixframe)
        mixpadding1.grid(row=4, column=0, columnspan=2, sticky=E + W)
        mixbox_label = tk.Label(self.mixframe, text="Signals in dataset:  ")
        mixbox_label.grid(row=5, column=0, sticky=W)
        mix_scrollbar = tk.Scrollbar(self.mixframe)
        mix_scrollbar.grid(row=6, column=2, sticky=N + S)
        self.mixbox = tk.Listbox(self.mixframe, name="mixbox", exportselection=0, selectmode=EXTENDED,
                                 yscrollcommand=mix_scrollbar.set)
        self.mixbox.grid(row=6, column=0, columnspan=2, sticky=N + S + E + W)
        mix_scrollbar.config(command=self.mixbox.yview)
        # self.mixbox.bind('<<ListboxSelect>>', lambda *args: self.mixbox.focus_set())
        self.mixbox.bind('<Delete>', self.remove_signal)
        self.mixbox.bind('<BackSpace>', self.remove_signal)
        self.mixbox.bind('<Double-1>', self.remove_signal)
        mixpadding1 = tk.Frame(self.mixframe)
        mixpadding1.grid(row=8, column=0, columnspan=2, sticky=E+W)

    def add_signal(self, event):
        """Add the selected signal the mixed dataset of signals."""
        selection = self.signalbox.curselection()
        thisfile = self.controller.tools.loader_box.get("active")
        for index in selection:
            signal = copy.copy(self.controller.tools.parser.signals[thisfile][index])
            self.mixsignals.append(signal)
        self.update_mixbox()

    def remove_signal(self, event):
        """Remove the selected signal from the mixed dataset of signals."""
        selection = self.mixbox.curselection()
        end_index = selection[0]
        for index in reversed(selection):
            del (self.mixsignals[index])
        self.update_mixbox()
        if len(self.mixsignals) > end_index:
            self.mixbox.activate(end_index)
        else:
            self.mixbox.activate(END)

    def update_mixbox(self):
        """Update to display the signals that are currently in the mixed dataset."""
        self.mixbox.delete(0, END)
        for signal in self.mixsignals:
            self.mixbox.insert(END, signal.name)
