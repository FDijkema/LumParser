"""
Analysis window of the luminescence time drive data parser.

This script is part of the parser interface for luminescence time drive data. The
Analysis window is controlled by the Main_window.
This window deals with the analysis of signals. Ao: moving and removing, saving
a file of multiple signals, exporting, fitting to a curve.
The imported script Parser_tools deals with all data operations, whereas user
interactions are described below.

The class AnaFrame describes the interactions of the Analysis window.
The __init__ method creates all objects on the screen, which then call the other
methods upon user interaction.
"""

import sys
import os
import src.parsertools as pt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import N, S, W, E, DISABLED, EXTENDED, TOP, RIGHT, LEFT, X, Y, BOTH, END, ANCHOR
from subframe_from_anaframe import ToolFrame


class Std_redirector(object):
    def __init__(self, widget):
        self.widget = widget

    def flush(self):
        pass

    def write(self, string):
        self.widget.insert(END, string)
        self.widget.see(END)


class AnaFrame(tk.Frame):

    def __init__(self, parent, controller, signalgroup=None):
        # link the frame to the parent frame and controller for interactions with
        # the main frame
        self.parent = parent
        self.controller = controller

        # takes the signalgroup object that was given as an argument and stores it
        # in an attribute for use within this class. The signalgroup contains all
        # the data and data operations.
        group = signalgroup
        if group is None:
            no_data = [{"time": 0.0, "value": 0.0}, {"time": 0.1, "value": 1.0}]
            no_signal = pt.Signal("No signals", no_data, "No file")
            group = pt.Signalgroup([no_signal], self.controller.default_name, notes="Empty")
        self.signalgroup = group
        self.signalgroup.fits = {}

        # initiate the frame and start filling it up
        tk.Frame.__init__(self, self.parent)
        self.create_output_menu()   # Create custom option in menubar

        # make sure the analysis window fills the entire main window
        self.main_window = tk.PanedWindow(self)
        self.main_window.pack(fill=BOTH, expand=1)
        self.main_window.grid_columnconfigure(1, weight=1)
        self.main_window.grid_rowconfigure(0, weight=1)

        # create the overall layout of the screen:
        # tools on the left, plot and terminal in the middle and extra options
        # on the right
        #tools = tk.Frame(self.main_window, borderwidth=5)
        tools = ToolFrame(self.main_window, self, borderwidth=5)
        tools.grid(row=0, rowspan=2, column=0, sticky="nswe", pady=2)
        tools.grid_columnconfigure(0, weight=1)

        plotframe = tk.LabelFrame(self.main_window, borderwidth=1, text="View")
        plotframe.grid(row=0, column=1, sticky="nswe", pady=2, padx=2)

        terminal_frame = tk.Frame(self.main_window)
        terminal_frame.grid(row=1, column=1, sticky=N + S + W + E, pady=10)

        extra_options = tk.Frame(self.main_window)
        extra_options.grid(row=0, rowspan=2, column=2, pady=2, sticky=N + S + W + E)

        # # fill the toolbar (left side of the screen)
        # self.browser = tk.Frame(tools)
        # self.browser.grid(row=0, column=0, columnspan=2, pady=2, sticky=N + S + W + E)
        # ## notes on the file
        # notes_title = tk.Label(self.browser, text="Dataset notes:  ")
        # notes_title.grid(row=0, column=0, columnspan=2, sticky=W)
        # self.browser_notes = tk.Text(self.browser, width=30, height=5)
        # self.browser_notes.insert(END, self.signalgroup.notes)
        # self.browser_notes.grid(row=1, column=0, columnspan=2, sticky=N + E + S + W)
        # ## browsing through the signals in the file
        # browser_title = tk.Label(self.browser, text="Signals in dataset:  ")
        # browser_title.grid(row=2, column=0, columnspan=2, sticky=W)
        # browser_scrollbar = tk.Scrollbar(self.browser)
        # browser_scrollbar.grid(row=3, column=2, sticky=N + S)
        # self.browser_box = tk.Listbox(self.browser, exportselection=0,
        #                               selectmode=EXTENDED, yscrollcommand=browser_scrollbar.set)
        # self.browser_box.grid(row=3, column=0, columnspan=2, sticky=W + E + N + S)
        # self.update_browser_box()
        # browser_scrollbar.config(command=self.browser_box.yview)
        # ## buttons with options for signal operations
        # delete_button = tk.Button(self.browser, text="Delete", command=self.remove_signal)
        # delete_button.grid(row=4, column=0, sticky=N + E + S + W)
        # move_button = tk.Button(self.browser, text="Move", command=self.launch_move)
        # move_button.grid(row=4, column=1, columnspan=2, sticky=N + E + S + W)
        # ## options for keyboard operated signal operations
        # self.browser_box.bind('<Control-Up>', self.move_signal_up)
        # self.browser_box.bind('<Control-Down>', self.move_signal_down)
        # self.browser_box.bind('<<ListboxSelect>>', self.on_select)
        # self.browser_box.bind('<Double-1>', lambda *args: self.open_rename_window())
        # self.browser_box.bind('<Control-n>', lambda *args: self.open_rename_window())
        # ## signal information
        # signalframe = tk.Frame(tools)
        # signalframe.grid(row=2, column=0, pady=2, sticky=N + E + S + W)
        # self.selected_signal = tk.StringVar()
        # signal_title = tk.Label(signalframe, textvariable=self.selected_signal)
        # signal_title.grid(row=0, column=0, sticky=W)
        # self.signal_info = tk.StringVar()
        # info_label = tk.Label(signalframe, textvariable=self.signal_info, justify=LEFT)
        # info_label.grid(row=1, column=0, sticky=W)
        # ## plot settings
        # plotsetter = tk.LabelFrame(tools, text="Settings for view")
        # plotsetter.grid(row=3, column=0, pady=2, sticky=N + S + W + E)
        # plotsetter.grid_columnconfigure(0, weight=1)
        # plotsetter.grid_columnconfigure(1, weight=1)
        # selected_button = tk.Button(plotsetter, text="Show selected", command=self.show_selected)
        # selected_button.grid(row=1, column=0, sticky=N + E + S + W)
        # all_button = tk.Button(plotsetter, text="Show all", command=self.show_all)
        # all_button.grid(row=1, column=1, sticky=N + E + S + W)
        # menulabel = tk.Label(plotsetter, text="Plot type:")
        # menulabel.grid(row=0, column=0, sticky=W + N + S)
        # self.active_plot = tk.StringVar(value="signals")
        # self.optionslist = ["signals", "integrated"]
        # self.plotoptions = tk.OptionMenu(plotsetter, self.active_plot, *self.optionslist)
        # self.plotoptions.grid(row=0, column=1, sticky=N + E + S)

        # middle part of the screen: plot and terminal
        ## plot
        self.title_text = tk.StringVar()
        self.title_text.set("-no signal selected-")
        plot_top = tk.Frame(plotframe)
        plot_top.pack(side=TOP, fill=BOTH)
        self.file_title = tk.Label(plot_top, textvariable=self.title_text)
        self.file_title.pack(side=LEFT, expand=1)
        self.fig = plt.figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=plotframe)
        toolbar = NavigationToolbar2Tk(self.canvas, plotframe)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        toolbar.pack(side=TOP, fill=X)
        plt.xlabel("time [s]")
        plt.ylabel("Intensity [RLU]")

        ## terminal
        terminal_frame.columnconfigure(0, weight=1)
        scrollb = tk.Scrollbar(terminal_frame, )
        scrollb.grid(row=0, column=1, sticky=N + S + E + W)
        self.textout = tk.Text(terminal_frame, width=90, height=15)
        self.textout.grid(row=0, column=0, sticky=N + W + S + E)
        scrollb.config(command=self.textout.yview)
        sys.stdout = Std_redirector(self.textout)
        # standard welcome message
        print("Welcome to the Gaussia Luciferase data analysis interface")

        # extra options (right side of the screen)
        ## lots of fit settings and information
        # information about what signal is selected
        self.fitframe = tk.LabelFrame(extra_options, text="Fit to curve")
        self.fitframe.grid(row=0, column=0, columnspan=3, pady=2, sticky=N + S + W + E)
        self.fit_signal = tk.StringVar()
        fitlabel1 = tk.Label(self.fitframe, textvariable=self.selected_signal, width=38)
        fitlabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        # options for different types of fit
        fitlabel2 = tk.Label(self.fitframe, text="Fit to:  ")
        fitlabel2.grid(row=1, column=0, sticky=W)
        self.curve_name = tk.StringVar()
        self.curve_name.trace("w", lambda *args: self.on_curve_select())
        fitlabel_options = tk.OptionMenu(self.fitframe, self.curve_name,
                                         "Exponential", "Double exponential", "Double exponential 2", "Double with baseline", "Other")
        fitlabel_options.grid(row=1, column=1, columnspan=4, sticky=N + E + S + W)
        # extra options for a manual formula, only displayed in "Other" mode
        self.fitlabel5 = tk.Label(self.fitframe, text="Formula: ")
        self.fitlabel5.grid(row=2, column=0, columnspan=2, sticky="wns")
        self.fitlabel5.grid_remove()
        self.formula_entry = tk.Entry(self.fitframe)
        self.formula_entry.grid(row=2, column=1, columnspan=2, sticky="wens")
        self.formula_entry.grid_remove()
        self.fitlabel6 = tk.Label(self.fitframe, text="Parameters: ")
        self.fitlabel6.grid(row=3, column=0, columnspan=2, sticky="wns")
        self.fitlabel6.grid_remove()
        self.param_entry = tk.Entry(self.fitframe)
        self.param_entry.grid(row=3, column=1, columnspan=2, sticky="wens")
        self.param_entry.grid_remove()
        # entry to input initial guess for parameter values
        fitlabel4 = tk.Label(self.fitframe, text="Initial values: ")
        fitlabel4.grid(row=4, column=0, columnspan=2, sticky="wns")
        self.inits_entry = tk.Entry(self.fitframe)
        self.inits_entry.grid(row=4, column=1, columnspan=2, sticky="wens")
        # information about created fit
        self.solved_fit = tk.StringVar()
        self.solved_fit.set("Best fit:  ")
        fitlabel3 = tk.Label(self.fitframe, textvariable=self.solved_fit, justify=LEFT)
        fitlabel3.grid(row=5, column=0, columnspan=3, sticky=W)
        # buttons to create fit or fits
        fit_button = tk.Button(self.fitframe, text="Fit", command=self.fit)
        fit_button.grid(row=6, column=1, sticky=N + E + S + W)
        fit_all_button = tk.Button(self.fitframe, text="Fit all", command=self.fit_all)
        fit_all_button.grid(row=6, column=2, sticky=N + E + S + W)

        ## layout for custom plot
        # title and some configuration of the frame for correct display
        self.extraframe = tk.LabelFrame(extra_options, text="Plot fit parameters")
        self.extraframe.grid(row=1, column=0, columnspan=3, pady=2, sticky="wens")
        self.extraframe.columnconfigure(0, weight=1)
        self.extraframe.columnconfigure(1, weight=1)
        self.extraframe.columnconfigure(2, weight=1)
        self.extraframe.columnconfigure(3, weight=1)
        self.extraframe.columnconfigure(4, weight=1)
        # parameter box
        self.extra_label1 = tk.Label(self.extraframe, text="Available parameters: ")
        self.extra_label1.grid(row=0, column=0, columnspan=5, sticky="wns")
        param_scrollbar = tk.Scrollbar(self.extraframe)
        param_scrollbar.grid(row=1, column=5, sticky="ns")
        self.param_box = tk.Listbox(self.extraframe, exportselection=0, yscrollcommand=param_scrollbar.set)
        self.update_param_box()
        self.param_box.bind('<Delete>', lambda *args: self.delete_p())
        self.param_box.bind('<BackSpace>', lambda *args: self.delete_p())
        self.param_box.grid(row=1, column=0, columnspan=5, sticky="wens")
        param_scrollbar.config(command=self.param_box.yview)
        # some buttons to control parameters and plot
        add_p_button = tk.Button(self.extraframe, text="Add custom", command=self.launch_add_p)
        add_p_button.grid(row=2, column=0, columnspan=2, sticky="wens")
        set_x_button = tk.Button(self.extraframe, text="Set as X", command=self.set_as_x)
        set_x_button.grid(row=2, column=2, sticky="wens")
        set_y_button = tk.Button(self.extraframe, text="Set as Y", command=self.set_as_y)
        set_y_button.grid(row=2, column=3, sticky="wens")
        show_plot_button = tk.Button(self.extraframe, text="Show", command=self.show_custom)
        show_plot_button.grid(row=2, column=4, columnspan=2, sticky="wens")
        # information about selected parameters
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.extra_label2 = tk.Label(self.extraframe, text="X-axis: ")
        self.extra_label2.grid(row=3, column=0, columnspan=4, sticky="wns")
        self.extra_label3 = tk.Label(self.extraframe, text="Y-axis: ")
        self.extra_label3.grid(row=4, column=0, columnspan=4, sticky="wns")

    def create_output_menu(self):
        """Fill output menu in main window with custom input."""
        # create a custom output menu in the menubar at the top of the main window
        self.outputmenu = tk.Menu(self.controller.menubar)
        self.outputmenu.add_command(label="Export dataset", command=self.launch_export)
        self.outputmenu.add_command(label="Save dataset", command=self.save_set)
        self.outputmenu.add_command(label="Save dataset as", command=self.launch_save_as)

    def open_rename_window(self):
        """
        Open new window with options for renaming signal.
        Call rename_signal upon finish.
        """
        signal_name = self.browser_box.get("active")
        self.rename_window = tk.Toplevel()
        self.rename_window.title("Rename signal")
        label2 = tk.Label(self.rename_window, text="Signal name:  ")
        label2.grid(row=0, column=0, columnspan=2, sticky=W)
        self.new_signal_name = tk.StringVar()
        self.new_signal_name.set(signal_name)
        name_entry = tk.Entry(self.rename_window, textvariable=self.new_signal_name)
        name_entry.grid(row=0, column=2, columnspan=2, sticky=N + S + E + W)
        name_entry.focus_set()
        name_entry.bind('<Return>',
                        lambda *args: self.rename_signal(signal_name, self.new_signal_name.get()))
        export_button = tk.Button(self.rename_window, text="Save",
                                  command=lambda *args: self.rename_signal(signal_name, self.new_signal_name.get()))
        export_button.grid(row=1, column=3, sticky=N + S + E + W)

    def rename_signal(self, old, new):
        index = self.browser_box.index("active")
        self.signalgroup.rename(old, new)
        self.update_browser_box()
        self.browser_box.activate(index)
        self.rename_window.destroy()

    def move_signal_up(self, event):
        selection = self.browser_box.curselection()
        self.signalgroup.move_up_at(selection)
        self.update_browser_box()
        self.browser_box.activate(selection[0])  # selection_set does not seem to work
        # so no multiple items can be selected

    def move_signal_down(self, event):
        selection = self.browser_box.curselection()
        self.signalgroup.move_down_at(selection)
        self.update_browser_box()
        self.browser_box.activate(selection[0])

    def remove_signal(self):
        selection = self.browser_box.curselection()
        self.signalgroup.remove_at(selection, seq=True)
        self.update_browser_box()
        if len(self.signalgroup.indexed) > selection[0]:
            self.browser_box.activate(selection[0])
        else:
            self.browser_box.activate(END)

    def update_browser_box(self):
        self.browser_box.delete(0, END)
        for signal in self.signalgroup:
            self.browser_box.insert(END, signal.name)

    def launch_move(self):
        """
        Open new window with options to move signal to a different file.
        move_signal is called upon finish.
        """
        self.move_window = tk.Toplevel()
        lister = tk.Frame(self.move_window)
        lister.grid(row=0, column=0, pady=2, sticky=N + S + W + E)
        lister.grid_columnconfigure(0, weight=1)
        lister_title = tk.Label(lister, text="Select a file to move to:  ")
        lister_title.grid(row=0, column=0, sticky=W)
        lister_scrollbar = tk.Scrollbar(lister)
        lister_scrollbar.grid(row=1, column=2, sticky=N + S)
        self.lister_box = tk.Listbox(lister, exportselection=0,
                                     yscrollcommand=lister_scrollbar.set)
        self.lister_box.grid(row=1, column=0, columnspan=2, sticky=W + E + N + S)
        lister_scrollbar.config(command=self.lister_box.yview)

        folder = os.path.join(self.controller.data_folder, "parsed")  # directory of script
        files = []
        for f in os.listdir(folder):
            if f.endswith('.parsed'):
                directory = os.path.join(folder, f)
                files.append({"name": f, "directory": directory})
                self.lister_box.insert(END, f)
        move_button = tk.Button(lister, text="Move",
                                command=lambda *args: self.move_signal(files))
        move_button.grid(row=2, column=1, columnspan=2, sticky=N + S + E + W)

    def move_signal(self, files):
        """Copy all information of the selected signal to a different parsed file."""
        index = self.lister_box.index("active")
        s_name = self.browser_box.get("active")
        signal = self.signalgroup.get(s_name)
        output = ("SIGNAL\n"
                  "name=%s\n"
                  "filename=%s\n"
                  "start=%.6g\n"
                  "DATA\n" % (signal.name, signal.filename, signal.start))
        x, y = signal.get_xy_bytype()
        rows = zip(x, y)
        for line in rows:
            output_line = ",".join(map(str, line)) + "\n"
            output += output_line
        output += "END\n"

        writefile = open(files[index]["directory"], "a")
        writefile.write(output)
        writefile.close()
        self.move_window.destroy()
        print("Signal copied to file")

    def on_select(self, event):
        """Display information on a signal when one is selected."""
        s_name = self.browser_box.get(ANCHOR)
        signal = self.signalgroup.get(s_name)
        peak_time, peak_value = signal.get_highest()
        intsignal = signal.integrate()
        int_time, int_value = intsignal.get_highest()
        labeltext1 = "Peak maximum:  %.6g RLU at %.6g s" % (peak_value, peak_time)
        labeltext2 = "Total integral:  %.6g RLU*s" % int_value
        labeltext3 = "Peak start:  %.6g s" % signal.start
        labeltext4 = "File of origin:  %s" % signal.filename
        self.selected_signal.set("Selected signal: " + signal.name)
        self.signal_info.set("\n".join([labeltext1, labeltext2, labeltext3, labeltext4]))
        self.fit_signal = signal
        self.title_text.set(signal.name)
        self.plot([signal])

    def on_curve_select(self):
        """
        Set initial values and check if more options need to be shown

        Default initial estimates for parameters are shown depending on which
        formula is selected.

        If the selected formula type is "Other", additional options are presented
        to the user to enter a formula and parameters.
        """
        c_name = self.curve_name.get()
        # set inits
        default = {
            "Exponential": "I, 1, .005",
            "Double exponential": "I, 1, .3, .04, .0025",
            "Double exponential 2": "I, 1, .3, .04",
            "Double with baseline": "I, .3, .04, .0025, 1, 1",
            "Other": ""
        }
        self.inits_entry.delete(0, END)
        self.inits_entry.insert(END, default[c_name])
        # display formula and parameter field for "Other"
        if c_name == "Other":
            self.fitlabel5.grid()
            self.formula_entry.grid()
            self.fitlabel6.grid()
            self.param_entry.grid()
        else:
            self.fitlabel5.grid_remove()
            self.formula_entry.grid_remove()
            self.fitlabel6.grid_remove()
            self.param_entry.grid_remove()

    def fit(self):
        """
        The selected signal is fitted to the selected curve.

        Information about the fit is presented and the fit is plotted in the plot
        area. If the curve type is "Other", the formula and parameters put in
        by the user are collected first.
        :return:
        """
        s_name = self.browser_box.get("active")
        curve_name = self.curve_name.get()
        rawinits = self.inits_entry.get()
        if curve_name == "Other":
            fit_formula = self.formula_entry.get()
            fit_params = self.param_entry.get()
        else:  # these parameters are not used
            fit_formula = ''
            fit_params = ''
        # fit signal data to curve
        funct, popt, perr, p = self.signalgroup.fit_signal(s_name, curve_name,
                                                           init_str=rawinits, func_str=fit_formula,
                                                           param_str=fit_params)
        outparams = dict(zip(funct.params, list(popt)))
        # display the parameter information
        lines = []
        for i, P in enumerate(funct.params):
            lines.append(" = ".join([P, "%.6g" % outparams[P]]))
            print("%s = %.6g +- %.6g" % (P, popt[i], perr[i]))
        paramtext = "\n".join(lines)
        print("p-value: " + str(p))
        # displaying the information
        self.solved_fit.set("Best fit:  %s\n%s" % (funct.formula, paramtext))
        # prepare plotting the fit
        if "fit" not in self.optionslist:
            self.optionslist.append("fit")
        self.active_plot.set("fit")
        self.plot([self.signalgroup.get(s_name)])

    def fit_all(self):
        """
        All signals in the set are fitted to the selected curve.

        The parameter box is updated with the newly created parameters.
        """
        curve_name = self.curve_name.get()
        rawinits = self.inits_entry.get()
        if curve_name == "Other":
            fit_formula = self.formula_entry.get()
            fit_params = self.param_entry.get()
        else:  # these parameters are not used
            fit_formula = ''
            fit_params = ''
        for s_name in self.signalgroup.indexed:
            try:
                funct, popt, perr, p = self.signalgroup.fit_signal(s_name, curve_name,
                                                               init_str=rawinits, func_str=fit_formula,
                                                               param_str=fit_params)  # calculating the fit
            except TypeError:
                pass
        print("Fitted all signals")
        self.solved_fit.set("Formula:  %s" % funct.formula)
        self.update_param_box()
        if "fit" not in self.optionslist:
            self.optionslist.append("fit")
        self.active_plot.set("fit")

    def launch_add_p(self):
        """
        Open a new window to let the user add a parameter to the parameter box.

        add_p is called upon finish.
        """
        self.p_frame = tk.Toplevel(self.extraframe)
        label1 = tk.Label(self.p_frame, text="Enter the name of the parameter to add "
                                             "and the values for all signals in the order "
                                             "they are in the list, separated by comma\'s")
        label1.grid(row=0, column=0, columnspan=2, sticky="nsw")
        name_label = tk.Label(self.p_frame, text="Name: ")
        name_label.grid(row=1, column=0, sticky="w")
        self.p_name = tk.StringVar()
        name_entry = tk.Entry(self.p_frame, textvariable=self.p_name)
        name_entry.grid(row=1, column=1, sticky="wens")
        value_label = tk.Label(self.p_frame, text="Values: ")
        value_label.grid(row=2, column=0, sticky="w")
        self.p_value = tk.StringVar()
        value_entry = tk.Entry(self.p_frame, textvariable=self.p_value)
        value_entry.grid(row=2, column=1, sticky="wens")
        add_button = tk.Button(self.p_frame, text="Add", command=self.add_p)
        add_button.grid(row=3, column=1, sticky="wens")

    def add_p(self):
        """Add a parameter to the parameter box. This can then be used in a plot."""
        name = self.p_name.get()
        value = self.p_value.get().split(",")
        if len(self.signalgroup.indexed) != len(value):
            print("The number of values does not match the number of signals. Try again")
            return
        for i, signal in enumerate(self.signalgroup):
            try:
                setattr(signal, name, float(value[i]))
            except TypeError:
                print("The values must be numbers. Try again")
                return
        self.update_param_box()
        self.p_frame.destroy()
        print("Variable %s, with values %s added to signals" % (name, str(value)))

    def delete_p(self):
        """Delete a parameter for all signal in the set."""
        selected_p = self.param_box.get("active")
        for signal in self.signalgroup:
            delattr(signal, selected_p)
        self.update_param_box()

    def update_param_box(self):
        """Make sure all existing parameters are shown to the user."""
        signal = self.signalgroup.get_at(0)
        self.param_box.delete(0, END)
        for var in vars(signal):
            try:
                float(vars(signal)[var])
            except (ValueError, TypeError):  # only take attributes with numeric values
                pass
            else:
                self.param_box.insert(END, var)

    def set_as_x(self):
        """Set selected parameter to use on X-axis."""
        X = self.param_box.get("active")
        self.x_var.set(X)
        self.extra_label2.configure(text="X-axis:  " + X)

    def set_as_y(self):
        """Set selected parameter to use on Y-axis."""
        Y = self.param_box.get("active")
        self.y_var.set(Y)
        self.extra_label3.configure(text="Y-axis:  " + Y)

    def show_custom(self):
        """Show plot of selected X and Y parameters."""
        self.title_text.set("Custom plot")
        plt.clf()
        x_name = self.x_var.get()
        y_name = self.y_var.get()
        x = []
        y = []
        for signal in self.signalgroup:
            try:
                x.append(float(getattr(signal, x_name)))
            except AttributeError:
                pass
            try:
                y.append(float(getattr(signal, y_name)))
            except AttributeError:
                pass
        plt.xlabel(x_name)
        plt.ylabel(y_name)
        plt.scatter(x, y)
        plt.tight_layout()
        plt.gcf().canvas.draw()

    def show_all(self):
        """Plot all signals in the file."""
        self.title_text.set("All signals in dataset")
        signals = [signal for signal in self.signalgroup]
        self.plot(signals)

    def show_selected(self):
        """Plot the selected signal."""
        self.title_text.set("Selected signals")
        indices = self.browser_box.curselection()
        signals = self.signalgroup.get_at(indices, seq=True)
        self.plot(signals)

    def plot(self, signals):
        """Plot the given signals in the selected plot type."""
        plt.clf()  # clear the current plot
        plottype = self.active_plot.get()  # look up which plot type is selected
        # dependent on plot type, plot the data of the given signals.
        names = []  # store the names of the signals here, to use for legend
        if plottype == "signals":  # plot signal data for given signals
            # label the axes
            plt.xlabel("Time (s)")
            plt.ylabel("Light intensity (RLU)")
            # for each signal, retrieve the data to plot and remember name
            for signal in signals:
                x, y = signal.get_xy_bytype()
                plt.plot(x, y)
                names.append(signal.name)
        elif plottype == "integrated":  # plot integrated data for given signals
            # label the axes
            plt.xlabel("Time (s)")
            plt.ylabel("Integrated light intensity (RLU*s)")
            # for each signal, retrieve the data to plot and remember name
            signals = [signal.integrate() for signal in signals]
            for signal in signals:
                x, y = signal.get_xy_bytype()
                plt.plot(x, y)
                names.append(signal.name)
        elif plottype == "fit":  # plot created fit and original data for given signals
            # label the axes
            plt.xlabel("Time (s)")
            plt.ylabel("Integrated light intensity (RLU*s)")
            # for each signal, retrieve the data to plot and remember name
            signals = [signal.integrate() for signal in signals]
            for signal in signals:
                self.title_text.set("Fit of %s" % signal.name)
                # first plot original signal data
                x, y = signal.get_xy_bytype()
                plt.plot(x, y)
                names.append(signal.name)
                # then plot the latest created fit of that data to a model curve
                fx, fy = self.signalgroup.fits[signal.name]
                plt.plot(fx, fy)
                names.append("fit")
        # display the names of plotted signals in the legend and adjust plot size
        plt.legend(names, loc=(1.04, 0))
        plt.tight_layout()
        plt.gcf().canvas.draw()

    def launch_export(self):
        """
        Open new window with export options.

        Type of data to export can be selected. Call check_type after choosing
        to display type dependent settings.

        Call export_files when finished.
        """
        # make a str variable that can be tracked
        self.export_type = tk.StringVar()
        # as a default, the currently displayed plot is exported
        self.export_type.set(self.active_plot.get())
        # create window layout and fields
        self.export_window = tk.Toplevel()
        self.export_window.title("Export data to csv - settings")
        label2 = tk.Label(self.export_window, text="Plot type:  ")
        label2.grid(row=1, column=0, columnspan=2, sticky=W)
        # let user select different plot type if desired
        self.type_options = tk.OptionMenu(self.export_window, self.export_type,
                                          "signals", "parameters", "fit")

        # if no fits have been created yet, do not show the option to export fit
        if self.signalgroup.fits == {}:
            self.type_options["menu"].entryconfigure("fit", state=DISABLED)
        self.type_options.grid(row=1, column=2, columnspan=2, sticky=N + S + E + W)

        # let user set filename for export file, default is same name as previously
        self.export_name = tk.StringVar()
        self.export_name.set(self.signalgroup.filename.replace(".parsed", ".csv"))
        self.export_type.trace("w", self.check_type)    # check_type upon change
        label3 = tk.Label(self.export_window, text="File name:  ")
        label3.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self.export_window, textvariable=self.export_name)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)

        # create fields for extra options if signal data is exported
        # hide these by default, show when export_type="signals"
        # this is checked when export type is changed, in check_type
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
        # check what type is selected when to window is opened, to decide whether
        # to display extra options
        self.check_type()

        # save button to wrap up export, calls export_files
        export_button = tk.Button(self.export_window, text="Save",
                                  command=lambda *args: self.export_files(self.export_name.get()))
        export_button.grid(row=5, column=3, sticky=N + S + E + W)

    def check_type(self, *args):
        """Display extra options in export window when export type is "signals"""
        if self.export_type.get() == "signals":
            self.export_normal_option.grid()
            self.export_int_option.grid()
        else:
            self.export_normal_option.grid_remove()
            self.export_int_option.grid_remove()

    def export_files(self, exportname):
        """Export files based on user input, close export window."""
        if self.export_type.get() == "signals":
            normal = self.export_normal.get()
            inte = self.export_int.get()
            self.signalgroup.export_csv(exportname, os.path.join(self.controller.data_folder, "csv"),
                                        normal=normal, integrate=inte)
        elif self.export_type.get() == "fit":
            fit_type = self.curve_name.get()
            self.signalgroup.export_csv(exportname, os.path.join(self.controller.data_folder, "csv"), normal=0, integrate=1, fit=1)
        elif self.export_type.get() == "parameters":
            self.signalgroup.export_parameters(exportname, os.path.join(self.controller.data_folder, "csv"))
        print("Exported as %s" % exportname)
        self.export_window.destroy()

    def save_set(self):
        """Simple save of file under current name. Run save_as if necessary"""
        if self.signalgroup.filename.startswith(self.controller.default_name):
            self.launch_save_as()
        else:
            print("Saving...")
            self.signalgroup.notes = self.browser_notes.get(1.0, END)
            self.signalgroup.save(os.path.join(self.controller.data_folder, "parsed"))
            print("Saved dataset as %s" % self.signalgroup.filename)

    def launch_save_as(self):
        """
        Open window for saving file. User can input filename.

        Call save_as to finish.
        """
        self.save_window = tk.Toplevel()
        self.save_window.title("Save - settings")
        self.save_name = tk.StringVar(value=self.signalgroup.filename)
        label = tk.Label(self.save_window, text="File name:  ")
        label.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self.save_window, textvariable=self.save_name)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)

        save_button = tk.Button(self.save_window, text="Save",
                                command=lambda *args: self.save_as(self.save_name.get()))
        save_button.grid(row=5, column=3, sticky=N + S + E + W)
        self.save_window.bind('<Return>', lambda *args: self.save_as(self.save_name.get()))

    def save_as(self, new_name):
        """Save file under name input by user, then close save window."""
        old_name = self.signalgroup.filename
        index = self.controller.windownames.index(old_name)
        # save
        self.signalgroup.notes = self.browser_notes.get(1.0, END)
        self.signalgroup.change_filename(new_name)
        new_name = self.signalgroup.filename #make sure the two names are the same to prevent errors
        print("Changed filename to {}".format(self.signalgroup.filename))
        self.signalgroup.save(os.path.join(self.controller.data_folder, "parsed"))
        # rename the window #
        if new_name != old_name:
            self.controller.windownames[index] = new_name
            self.controller.windows[new_name] = self.controller.windows.pop(old_name)
        self.controller.show_frame(new_name)
        self.create_output_menu()   # menu somehow lost when renaming window
        # finish
        print("Saved dataset as %s" % self.signalgroup.filename)
        self.save_window.destroy()