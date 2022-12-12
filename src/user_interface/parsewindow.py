"""
Parsing window of the luminescence time drive data parser.

This script is part of the parser interface for luminescence time drive data. The
Parsing window is controlled by the Main_window.
This window deals with the parsing of time drive files into workable data.
Settings for data parsing can be chosen, after which the data can be exported
directly or opened in a parsed file in the Analysis window.
The imported script Parser_self.tools deals with all data operations, whereas user
interactions are described below.

The class ParseFrame describes the interactions of the Parser window.
The __init__ method creates all objects on the screen, which then call the other
methods upon user interaction.
"""

import copy
import os
import sys
import src.parsertools as pt
from src.user_interface.anawindow import AnaFrame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import N, S, W, E, DISABLED, EXTENDED, TOP, LEFT, X, BOTH, END
from src.user_interface.parsertoolframe import ParserToolFrame
from src.user_interface.stdredirector import StdRedirector


class ParseFrame(tk.Frame):

    def __init__(self, parent, controller):
        # link the frame to the parent frame and controller for interactions with
        # the main frame
        self.parent = parent
        self.controller = controller

        self.mixsignals = []

        # initiate the frame and start filling it up
        tk.Frame.__init__(self, self.parent)

        # create a custom output menu in the menubar at the top of the main window
        self.outputmenu = tk.Menu(self.controller.menubar)
        self.outputmenu.add_command(label="Export selected file", command=self.launch_export)
        self.outputmenu.add_command(label="Parse selected file", command=self.parse_file)
        self.outputmenu.add_command(label="Parse mixed dataset", command=self.parse_mixed)

        # make sure the analysis window fills the entire main window
        main_window = tk.PanedWindow(self)  # the parseframe itself is the master
        main_window.pack(fill=BOTH, expand=1)
        main_window.grid_columnconfigure(1, weight=1)
        main_window.grid_rowconfigure(0, weight=1)

        # create the overall layout of the screen:
        # tools on the left, plot and terminal in the middle and extra options
        # on the right
        self.tools = ParserToolFrame(main_window, self, borderwidth=5)
        self.tools.grid(row=0, rowspan=2, column=0, sticky="nswe", pady=2)

        plotframe = tk.LabelFrame(main_window, borderwidth=1, text="View")
        plotframe.grid(row=0, column=1, sticky="nswe", pady=2, padx=2)

        terminal_frame = tk.Frame(main_window)
        terminal_frame.grid(row=1, column=1, sticky=N+S+W+E, pady=10)

        self.parse_options = tk.Frame(main_window)
        self.parse_options.grid(row=0, rowspan=2, column=2, pady=2, sticky=N+S+W+E)

        # plot settings
        plotsetter = tk.LabelFrame(self.tools, text="Settings for view")
        plotsetter.grid(row=2, column=0, pady=2, sticky=N + S + W + E)
        plotsetter.grid_columnconfigure(0, weight=1)
        menulabel = tk.Label(plotsetter, text="Plot type:  ")
        menulabel.grid(row=0, column=0, sticky=W)
        self.active_plot = tk.StringVar()
        self.active_plot.set("original")
        self.plot_options = tk.OptionMenu(plotsetter, self.active_plot,
                                          "original", "corrected", "signals", "integrated")
        self.plot_options.config(state=DISABLED)
        self.plot_options.grid(row=0, column=1, sticky=W)
        self.active_plot.trace_variable("w", lambda *args: self.tools.display(self.tools.loader_box.get("active")))

        # plot
        self.title_text = tk.StringVar()
        self.title_text.set("-no file selected-")
        plot_top = tk.Frame(plotframe)
        plot_top.pack(side=TOP, fill=BOTH)
        self.file_title = tk.Label(plot_top, textvariable=self.title_text)
        self.file_title.pack(side=LEFT, expand=1)
        self.fig = plt.figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plotframe)
        toolbar = NavigationToolbar2Tk(self.canvas, plotframe)
        toolbar.update()
        toolbar.pack(side=TOP, fill=X)
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        plt.xlabel("time [s]")
        plt.ylabel("Intensity [RLU]")

        # terminal
        terminal_frame.columnconfigure(0, weight=1)
        scrollb = tk.Scrollbar(terminal_frame, )
        scrollb.grid(row=0, column=1, sticky=N + S + E + W)
        self.textout = tk.Text(terminal_frame, width=90, height=15)
        self.textout.grid(row=0, column=0, sticky=N + W + S + E)
        scrollb.config(command=self.textout.yview)
        sys.stdout = StdRedirector(self.textout)
        print("Welcome to the Gaussia Luciferase data parser interface. Click \"Import\" to import files")

        # extra options (right side of the screen)
        self.signal_info = tk.LabelFrame(self.parse_options, text="Signal information")
        self.signal_info.grid(row=0, column=0, columnspan=3, pady=2, sticky=N + S + W + E)

        self.mixframe = tk.LabelFrame(self.parse_options, text="Signals in mixed dataset")
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
        self.signalbox.bind('<Left>', lambda *args: self.tools.loader_box.focus_set())
        self.signalbox.bind('<Control-n>', lambda *args: self.tools.open_rename_window())
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

    def plot_file(self, thisfile):
        # start by clearing current plot
        plt.clf()

        # check if the background was calculated, otherwise just plot the
        # uncorrected data
        if not hasattr(self.tools.parser.datasets[thisfile], "background"):
            x, y = pt.get_xy(self.tools.parser.datasets[thisfile].data)
            plt.plot(x, y)
            plt.xlabel("Time (s)")
            plt.ylabel("Light intensity (RLU)")
            plt.tight_layout()
            plt.gcf().canvas.draw()  # plt.draw() doesn't work
            return

        # if the background can be calculated, continue plotting
        # plot based on what plot type is selected by user
        plottype = self.active_plot.get()
        if plottype == "original":  # uncorrected data as in the time drive
            # plot data
            x, y = pt.get_xy(self.tools.parser.datasets[thisfile].data)
            plt.plot(x, y)
            # set axes names
            plt.xlabel("Time (s)")
            plt.ylabel("Light intensity (RLU)")
            # create some extra features to visualise detected background and
            # signals, based on latest variable settings
            for signal in self.tools.parser.signals[thisfile]:
                x_line = signal.start
                plt.axvline(x=x_line, color="r")  # vertical line at detected signal starts
            L = self.tools.parser.parse_settings[thisfile]["bg_bound_L"]
            R = self.tools.parser.parse_settings[thisfile]["bg_bound_R"]
            background = self.tools.parser.datasets[thisfile].background
            if background > 0.1:
                height = 10 * background
            else:
                height = 1
            plt.plot([L, L], [0, height], color='g')
            plt.plot([R, R], [0, height], color='g')
        elif plottype == "corrected":   # corrected time drive data
            # plot data
            x, y = pt.get_xy(self.tools.parser.datasets[thisfile].corrected)
            plt.plot(x, y)
            # set axes names
            plt.xlabel("Time (s)")
            plt.ylabel("Light intensity (RLU)")
        elif plottype == "signals":  # detected signals separately
            names = []
            # set axes names
            plt.xlabel("Time (s)")
            plt.ylabel("Light intensity (RLU)")
            # plot data for all signals in the selected time drive
            for signal in self.tools.parser.signals[thisfile]:
                x, y = pt.get_xy(signal.signal_data)
                plt.plot(x, y)
                names.append(signal.name + "at %s s" % signal.start)
            # show the signal names in a legend
            plt.legend(names, loc=(1.04, 0))
        elif plottype == "integrated":  # detected signals, integrated
            names = []
            # set axes names
            plt.xlabel("Time (s)")
            plt.ylabel("Integrated light intensity (RLU*s)")
            # plot integrated data for all signals in the selected time drive
            for signal in self.tools.parser.signals[thisfile]:
                x, y = pt.get_xy(signal.integrated_data)
                plt.plot(x, y)
                names.append(signal.name + "at %s s" % signal.start)
            # show the signal names in a legend
            plt.legend(names, loc=(1.04, 0))
        # adjust the plot size and show the created plot
        plt.tight_layout()
        plt.gcf().canvas.draw()  # plt.draw() doesn't work

    def add_signal(self, event):
        """Add the selected signal the mixed dataset of signals."""
        selection = self.signalbox.curselection()
        thisfile = self.tools.loader_box.get("active")
        for index in selection:
            signal = copy.copy(self.tools.parser.signals[thisfile][index])
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

    def launch_export(self):
        """
        Open a window to set options for export to csv.

        The default name for saving is created by taking the name of the original
        time drive and replacing the extension. See set_default_name.
        Call export_files upon finish.
        """
        # create some variables that can be changed for the export
        self.export_type = tk.StringVar()
        self.export_file = tk.StringVar()
        file_list = list(self.tools.parser.datasets.keys())
        self.export_type.set(self.active_plot.get())
        self.export_file.set(self.tools.loader_box.get("active"))

        #create the window layout
        self.export_window = tk.Toplevel()
        self.export_window.title("Export data to csv - settings")
        label1 = tk.Label(self.export_window, text="File:  ")
        label1.grid(row=0, column=0, columnspan=2, sticky=W)
        file_options = tk.OptionMenu(self.export_window, self.export_file, *file_list)
        file_options.grid(row=0, column=2, columnspan=2, sticky=N + S + E + W)
        label2 = tk.Label(self.export_window, text="Plot type:  ")
        label2.grid(row=1, column=0, columnspan=2, sticky=W)
        self.type_options = tk.OptionMenu(self.export_window, self.export_type,
                                          "original", "corrected", "signals")
        self.type_options.grid(row=1, column=2, columnspan=2, sticky=N + S + E + W)
        self.export_name = tk.StringVar()
        self.export_name.set(self.export_file.get().replace(".td", ".csv").replace(".TD", ".csv"))
        self.export_file.trace("w", self.set_default_name)
        self.export_type.trace("w", self.check_type)
        label3 = tk.Label(self.export_window, text="File name:  ")
        label3.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self.export_window, textvariable=self.export_name)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)

        # options for signal export are only displayed if the export type is
        # "signals", see check_type
        self.export_normal = tk.BooleanVar(value=True)
        self.export_normal_option = tk.Checkbutton(self.export_window, text="Include normal data",
                                                   variable=self.export_normal)
        self.export_normal_option.grid(row=3, column=2, columnspan=2, sticky=W)
        self.export_normal_option.grid_remove()
        self.export_int = tk.BooleanVar(value=False)
        self.export_int_option = tk.Checkbutton(self.export_window, text="Include integrated data",
                                                variable=self.export_int)
        self.export_int_option.grid(row=4, column=2, columnspan=2, sticky=W)
        self.export_int_option.grid_remove()

        export_button = tk.Button(self.export_window, text="Save",
                                  command=lambda *args: self.export_files(self.export_name.get()))
        export_button.grid(row=5, column=3, sticky=N + S + E + W)

    def set_default_name(self, *args):
        self.export_name.set(self.export_file.get().replace(".td", ".csv"))

    def check_type(self, *args):
        """Display extra options for exporting signals."""
        if self.export_type.get() == "signals":
            self.export_normal_option.grid()
            self.export_int_option.grid()
        else:
            self.export_normal_option.grid_remove()
            self.export_int_option.grid_remove()

    def export_files(self, exportname):
        """Export the data based on the user input, then close export window."""
        filename = self.export_file.get()
        if self.export_type.get() == "original":
            self.tools.parser.datasets[filename].export_to_csv(exportname, os.path.join(self.controller.data_folder, "csv"), oftype="original")
        elif self.export_type.get() == "corrected":
            self.tools.parser.datasets[filename].export_to_csv(exportname, os.path.join(self.controller.data_folder, "csv"), oftype="corrected")
        elif self.export_type.get() == "signals":
            normal = self.export_normal.get()
            inte = self.export_int.get()
            self.tools.parser.export_csv(filename, exportname, os.path.join(self.controller.data_folder, "csv"), normal=normal, integrate=inte)
        print("Exported file as {}".format(exportname))
        self.export_window.destroy()

    def parse_file(self):
        """Parse the data in the selected time drive and open in analysis window."""
        thisfile = self.tools.loader_box.get("active")
        signals = self.tools.parser.signals[thisfile]
        group = pt.Signalgroup(signals, thisfile)
        name = group.filename
        if name in self.controller.windownames:
            print("File is already parsed. Please change the name of the parsed file before parsing again")
        self.controller.windownames.append(name)
        self.controller.windows[name] = AnaFrame(self.controller.mainframe, self.controller, signalgroup=group)
        self.controller.windows[name].grid(row=0, column=0, columnspan=2, sticky=N + E + S + W)
        self.controller.show_frame(name)

    def parse_mixed(self):
        """Parse the data of the mixed group of signals and open in analysis window."""
        group = pt.Signalgroup(self.mixsignals, "")
        group.change_filename(self.controller.default_name + "_" + str(self.controller.name_count))
        self.controller.name_count += 1
        name = group.filename
        self.controller.windownames.append(name)
        self.controller.windows[name] = AnaFrame(self.controller.mainframe, self.controller, signalgroup=group)
        self.controller.windows[name].grid(row=0, column=0, columnspan=2, sticky=N + E + S + W)
        self.controller.show_frame(name)

    def save_set(self):
        """Parse the mixed dataset if there is one, else parse selected file."""
        if len(self.mixsignals)>0:
            self.parse_mixed()
        else:
            self.parse_file()
