import os
import tkinter as tk
from tkinter import N, S, W, E, EXTENDED, LEFT, END, ANCHOR
import src.parsertools as pt


class ToolFrame(tk.Frame):

    def __init__(self, parent, controller, borderwidth=5):
        self.parent = parent
        self.controller = controller
        self.signalgroup = self.controller.signalgroup
        tk.Frame.__init__(self, self.parent, borderwidth=borderwidth)

        # fill the toolbar (left side of the screen)
        self.browser = tk.Frame(self)
        self.browser.grid(row=0, column=0, columnspan=2, pady=2, sticky=N + S + W + E)
        ## notes on the file
        notes_title = tk.Label(self.browser, text="Dataset notes:  ")
        notes_title.grid(row=0, column=0, columnspan=2, sticky=W)
        self.browser_notes = tk.Text(self.browser, width=30, height=5)
        self.browser_notes.insert(END, self.signalgroup.notes)
        self.browser_notes.grid(row=1, column=0, columnspan=2, sticky=N + E + S + W)
        ## browsing through the signals in the file
        browser_title = tk.Label(self.browser, text="Signals in dataset:  ")
        browser_title.grid(row=2, column=0, columnspan=2, sticky=W)
        browser_scrollbar = tk.Scrollbar(self.browser)
        browser_scrollbar.grid(row=3, column=2, sticky=N + S)
        self.browser_box = tk.Listbox(self.browser, exportselection=0,
                                      selectmode=EXTENDED, yscrollcommand=browser_scrollbar.set)
        self.browser_box.grid(row=3, column=0, columnspan=2, sticky=W + E + N + S)
        self.update_browser_box()
        browser_scrollbar.config(command=self.browser_box.yview)
        ## buttons with options for signal operations
        delete_button = tk.Button(self.browser, text="Delete", command=self.remove_signal)
        delete_button.grid(row=4, column=0, sticky=N + E + S + W)
        move_button = tk.Button(self.browser, text="Move", command=self.launch_move)
        move_button.grid(row=4, column=1, columnspan=2, sticky=N + E + S + W)
        ## options for keyboard operated signal operations
        self.browser_box.bind('<Control-Up>', self.move_signal_up)
        self.browser_box.bind('<Control-Down>', self.move_signal_down)
        self.browser_box.bind('<<ListboxSelect>>', self.on_select)
        self.browser_box.bind('<Double-1>', lambda *args: self.open_rename_window())
        self.browser_box.bind('<Control-n>', lambda *args: self.open_rename_window())
        ## signal information
        signalframe = tk.Frame(self)
        signalframe.grid(row=2, column=0, pady=2, sticky=N + E + S + W)
        self.controller.selected_signal = tk.StringVar()
        signal_title = tk.Label(signalframe, textvariable=self.controller.selected_signal)
        signal_title.grid(row=0, column=0, sticky=W)
        self.signal_info = tk.StringVar()
        info_label = tk.Label(signalframe, textvariable=self.signal_info, justify=LEFT)
        info_label.grid(row=1, column=0, sticky=W)
        ## plot settings
        plotsetter = tk.LabelFrame(self, text="Settings for view")
        plotsetter.grid(row=3, column=0, pady=2, sticky=N + S + W + E)
        plotsetter.grid_columnconfigure(0, weight=1)
        plotsetter.grid_columnconfigure(1, weight=1)
        selected_button = tk.Button(plotsetter, text="Show selected", command=self.controller.show_selected)
        selected_button.grid(row=1, column=0, sticky=N + E + S + W)
        all_button = tk.Button(plotsetter, text="Show all", command=self.controller.show_all)
        all_button.grid(row=1, column=1, sticky=N + E + S + W)
        menulabel = tk.Label(plotsetter, text="Plot type:")
        menulabel.grid(row=0, column=0, sticky=W + N + S)
        self.active_plot = tk.StringVar(value="signals")
        self.optionslist = ["signals", "integrated"]
        self.plotoptions = tk.OptionMenu(plotsetter, self.active_plot, *self.optionslist)
        self.plotoptions.grid(row=0, column=1, sticky=N + E + S)
        print("sucessfully created toolframe")

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
        x, y = pt.get_xy(signal.signal_data)
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
        labeltext1 = "Peak maximum:  %.6g RLU at %.6g s" % (signal.peak_height, signal.peak_time)
        labeltext2 = "Total integral:  %.6g RLU*s" % signal.total_int
        labeltext3 = "Peak start:  %.6g s" % signal.start
        labeltext4 = "File of origin:  %s" % signal.filename
        self.controller.selected_signal.set("Selected signal: " + signal.name)
        self.signal_info.set("\n".join([labeltext1, labeltext2, labeltext3, labeltext4]))
        self.controller.fit_signal = signal
        self.controller.title_text.set(signal.name)
        self.controller.plot([signal])
