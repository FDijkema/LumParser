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
        default_directory = os.path.join(os.path.expanduser("~"), "Luminescence_data")
        self.input_path = tk.StringVar(value=default_directory)
        question = tk.Label(self, text="Where would you like to save your data when using this program?")
        question.grid(row=1, column=0, columnspan=4, sticky=N + S + E + W)
        label = tk.Label(self, text="Save my data here:  ")
        label.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self, textvariable=self.input_path)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)

        self.show_window = tk.BooleanVar()
        self.show_window.set(prompt_change_directory.read())
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
        print("Files will be saved at {0}.".format(self.input_path.get()))
        with open(os.path.join(pt.defaultvalues.project_root, "user_interface", "config", "prompt_change_directory.txt"), "w") as f:
            f.write(str(self.show_window.get()))
        if os.path.exists(path):
            # check if all subfolders exist and create them if not
            raise NotImplementedError
        else:
            # create the folder with all subfolders
            raise NotImplementedError
        if self.make_examples.get() is True:
            self.fill_datafolder_with_examples()
        else:
            pass
        self.destroy()    # destroy window when done creating datafolder and filling it

    def fill_datafolder_with_examples(self):
        """Move example files into the folder."""
        print("Data moved into folder.")
        raise NotImplementedError
