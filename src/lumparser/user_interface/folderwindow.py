"""
NAME
folderwindow

DESCRIPTION
Script with functions to execute only the first time after installation that the program is run.

CLASSES

FUNCTIONS
create_datafolder                 Create a datafolder in the user directory to store lumparser data
fill_datafolder_with_examples     Move example files into the folder
"""

import os
import tkinter as tk
from tkinter import W, E, N, S, TOP, BOTH, END
try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources
from shutil import copy
from . import config
import lumparser.parsertools as pt


prompt_change_directory = resources.open_text(config, 'prompt_change_directory.txt')


class CreateFolderWindow(tk.Toplevel):
    """
    Open window to let user choose where to create data folder.

    Call open_set upon finish to open an analysis window with the chosen data.
    """

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.title("Saving directory")

        data_directories = resources.open_text(config, 'data_directories.txt')
        for line in data_directories.readlines():
            if line.startswith("import_folder"):
                label, csv_folder = line.split("=")
        data_folder = os.path.dirname(csv_folder)
        self.input_path = tk.StringVar(value=data_folder)
        question = tk.Label(self, text="Where would you like to save your data when using this program?")
        question.grid(row=1, column=0, columnspan=4, sticky=N + S + E + W)
        label = tk.Label(self, text="Save my data here:  ")
        label.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self, textvariable=self.input_path)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)

        self.show_window = tk.BooleanVar()
        self.show_window.set(True if prompt_change_directory.read() == "True" else False)
        self.make_examples = tk.BooleanVar()
        self.make_examples.set(True)
        self.show_window_button = tk.Checkbutton(self, text="show this window on program start",
                                                 variable=self.show_window, onvalue=True, offvalue=False)
        self.show_window_button.grid(row=3, column=0, columnspan=3, sticky=W)
        self.make_examples_button = tk.Checkbutton(self, text="create example data in the new folder",
                                                 variable=self.make_examples, onvalue=True, offvalue=False)
        self.make_examples_button.grid(row=4, column=0, columnspan=3, sticky=W)

        save_button = tk.Button(self, text="Save",
                                command=lambda *args: self.create_datafolder(self.input_path.get()))
        save_button.grid(row=5, column=3, sticky=N + S + E + W)

        self.bind('<Return>', lambda *args: self.create_datafolder(self.input_path.get()))

    def create_datafolder(self, path):
        """Create a datafolder in the user directory."""
        # give feedback to user
        print("Files will be saved at '{0}'.".format(path))
        # save the setting to show the change directory window next time or not
        with open(os.path.join(pt.defaultvalues.project_root, "user_interface", "config", "prompt_change_directory.txt"), "w") as f:
            f.write(str(self.show_window.get()))
        # check if chosen saving location exists; if not, create it
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except WindowsError:
                print("The given path name is not valid.")
                return
        import_folder = os.path.join(path, "td")  # where to find .td files
        parsed_folder = os.path.join(path, "parsed")  # where to find and save .parsed files
        csv_folder = os.path.join(path, "csv")  # where to save .csv files
        # check if all subfolders exist and create them if not
        if not os.path.exists(import_folder):
            os.mkdir(import_folder)
        if not os.path.exists(parsed_folder):
            os.mkdir(parsed_folder)
        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)
        # save subfolder locations
        with open(os.path.join(pt.defaultvalues.project_root, "user_interface", "config",
                               "data_directories.txt"), "w") as f:
            f.write('import_folder={}\n'.format(str(import_folder)) +
                    'parsed_folder={}\n'.format(str(parsed_folder)) +
                    'csv_folder={}'.format(str(csv_folder))
                    )
        # if the make_examples setting is ticked, fill the created folders with example data
        if self.make_examples.get() is True:
            self.fill_datafolder_with_examples(import_folder, parsed_folder)
        else:
            pass
        self.destroy()    # destroy window when done creating datafolder and filling it

    def fill_datafolder_with_examples(self, import_folder, parsed_folder):
        """Move example files into the folder."""
        import_example_files = [
            "Example01.td",
            "Example02.td",
            "Example03.td",
            "Example04.td",
            "Example05.td"
        ]
        for import_example_file in import_example_files:
            copy(os.path.join(pt.defaultvalues.project_root, "data", "td", import_example_file),
                 os.path.join(import_folder, import_example_file))
        parsed_example_file = "Example_data.parsed"
        copy(os.path.join(pt.defaultvalues.project_root, "data", "parsed", parsed_example_file),
             os.path.join(parsed_folder, parsed_example_file))
