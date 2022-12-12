import os
import tkinter as tk
from tkinter import N, S, W, E, DISABLED, EXTENDED, TOP, RIGHT, LEFT, X, Y, BOTH, END, ANCHOR
import src.parsertools as pt


class PlotOptionsFrame(tk.Frame):

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.signalgroup = self.controller.signalgroup
        tk.Frame.__init__(self, self.parent)

        ## lots of fit settings and information
        # information about what signal is selected
        self.fitframe = tk.LabelFrame(self.extra_options, text="Fit to curve")
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
                                         "Exponential", "Double exponential", "Double exponential 2",
                                         "Double with baseline", "Other")
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
        self.extraframe = tk.LabelFrame(self.extra_options, text="Plot fit parameters")
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
