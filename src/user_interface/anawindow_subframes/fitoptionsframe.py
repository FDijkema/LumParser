"""
Right side tool frame for the Analysis window of the luminescence time drive data parser.

This module is part of the user interface of the LumParsing package for working with luminescence time drive data.
The parser mix frame is controlled by the Analysis window.
This frame lets the user fit the selected signal to a curve and manage and plot parameters.

The class FitOptionsFrame describes the interactions of the frame.
In the interface, it is initiated with the frame it resides within as parent and the Analysis window as controller.

Plotting data, selecting signals and writing notes are controlled by the Analysis window and its sub frame
the analysis tool frame, respectively.

User interactions through mouse and keyboard:

Keyboard:
Typing in designated fields.
"""

import tkinter as tk
from tkinter import N, S, W, E, LEFT, END
from src.parsertools.fitting.functions import FUNCTIONS, DEFAULT_INITS


class FitOptionsFrame(tk.Frame):

    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.signalgroup = self.controller.signalgroup
        tk.Frame.__init__(self, self.parent)

        ## lots of fit settings and information
        # information about what signal is selected
        self.fitframe = tk.LabelFrame(self, text="Fit to curve")
        self.fitframe.grid(row=0, column=0, columnspan=3, pady=2, sticky=N + S + W + E)
        self.fit_signal = tk.StringVar()
        fitlabel1 = tk.Label(self.fitframe, textvariable=self.controller.selected_signal, width=38)
        fitlabel1.grid(row=0, column=0, columnspan=3, sticky=W)
        # options for different types of fit
        fitlabel2 = tk.Label(self.fitframe, text="Fit to:  ")
        fitlabel2.grid(row=1, column=0, sticky=W)
        self.curve_name = tk.StringVar()
        self.curve_name.trace("w", lambda *args: self.on_curve_select())
        fitlabel_options = tk.OptionMenu(self.fitframe, self.curve_name, *FUNCTIONS.keys())
        fitlabel_options.grid(row=1, column=1, columnspan=4, sticky=N + E + S + W)
        # extra options for a manual formula, only displayed in "Custom" mode
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
        self.extraframe = tk.LabelFrame(self, text="Plot fit parameters")
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
        show_plot_button = tk.Button(self.extraframe, text="Show", command=self.controller.show_custom)
        show_plot_button.grid(row=2, column=4, columnspan=2, sticky="wens")
        # information about selected parameters
        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.extra_label2 = tk.Label(self.extraframe, text="X-axis: ")
        self.extra_label2.grid(row=3, column=0, columnspan=4, sticky="wns")
        self.extra_label3 = tk.Label(self.extraframe, text="Y-axis: ")
        self.extra_label3.grid(row=4, column=0, columnspan=4, sticky="wns")

    def on_curve_select(self):
        """
        Set initial values and check if more options need to be shown

        Default initial estimates for parameters are shown depending on which
        formula is selected.

        If the selected formula type is "Custom", additional options are presented
        to the user to enter a formula and parameters.
        """
        c_name = self.curve_name.get()
        # set inits
        default = DEFAULT_INITS
        self.inits_entry.delete(0, END)
        self.inits_entry.insert(END, default[c_name])
        # display formula and parameter field for "Custom"
        if c_name == "Custom":
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
        area. If the curve type is "Custom", the formula and parameters put in
        by the user are collected first.
        :return:
        """
        s_name = self.controller.tools.browser_box.get("active")
        curve_name = self.curve_name.get()
        rawinits = self.inits_entry.get()
        if curve_name == "Custom":
            fit_formula = self.formula_entry.get()
            fit_params = self.param_entry.get()
        else:  # these parameters are not used
            fit_formula = ''
            fit_params = ''
        # fit signal data to curve
        funct, popt, perr, p = self.signalgroup.get(s_name).fit_to(
            fct=curve_name, init_str=rawinits, func_str=fit_formula, param_str=fit_params)
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
        if "fit" not in self.controller.tools.optionslist:
            self.controller.tools.optionslist.append("fit")
            self.controller.tools.plotoptions = tk.OptionMenu(self.controller.tools.plotsetter, self.controller.tools.active_plot, *self.controller.tools.optionslist)
            self.controller.tools.plotoptions.grid(row=0, column=1, sticky=N + E + S)
#            self.controller.tools.plotoptions["menu"].add_command(label="fit")
        self.controller.tools.active_plot.set("fit")
        self.controller.plot([self.signalgroup.get(s_name)])

    def fit_all(self):
        """
        All signals in the set are fitted to the selected curve.

        The parameter box is updated with the newly created parameters.
        """
        curve_name = self.curve_name.get()
        rawinits = self.inits_entry.get()
        if curve_name == "Custom":
            fit_formula = self.formula_entry.get()
            fit_params = self.param_entry.get()
        else:  # these parameters are not used
            fit_formula = ''
            fit_params = ''
        for signal in self.signalgroup:
            try:
                funct, popt, perr, p = signal.fit_to(
                    fct=curve_name, init_str=rawinits, func_str=fit_formula, param_str=fit_params)  # calculating the fit
            except TypeError:
                pass
        print("Fitted all signals")
        self.solved_fit.set("Formula:  %s" % funct.formula)
        self.update_param_box()
        if "fit" not in self.controller.tools.optionslist:
            self.controller.tools.optionslist.append("fit")
            self.controller.tools.plotoptions = tk.OptionMenu(self.controller.tools.plotsetter,
                                                              self.controller.tools.active_plot,
                                                              *self.controller.tools.optionslist)
            self.controller.tools.plotoptions.grid(row=0, column=1, sticky=N + E + S)
        #            self.controller.tools.plotoptions["menu"].add_command(label="fit")
        self.controller.tools.active_plot.set("fit")
        self.controller.plot(self.signalgroup.get_all())

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
        x = self.param_box.get("active")
        self.x_var.set(x)
        self.extra_label2.configure(text="X-axis:  " + x)

    def set_as_y(self):
        """Set selected parameter to use on Y-axis."""
        y = self.param_box.get("active")
        self.y_var.set(y)
        self.extra_label3.configure(text="Y-axis:  " + y)
