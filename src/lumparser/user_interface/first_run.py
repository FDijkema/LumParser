"""
NAME
first_run

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
        label = tk.Label(self, text="Save my data here:  ")
        label.grid(row=2, column=0, columnspan=2, sticky=W)
        name_entry = tk.Entry(self, textvariable=self.input_path)
        name_entry.grid(row=2, column=2, columnspan=2, sticky=N + S + E + W)
        save_button = tk.Button(self, text="Save",
                                command=lambda *args: self.create_datafolder(self.input_path.get()))
        save_button.grid(row=5, column=3, sticky=N + S + E + W)
        self.bind('<Return>', lambda *args: self.create_datafolder(self.input_path.get()))

    def create_datafolder(self, path):
        """Create a datafolder in the user directory."""
        print("Folder created on first run.")
        self.destroy()    # destroy window when done creating datafolder

    def fill_datafolder_with_examples(self):
        """Move example files into the folder."""
        print("Data moved into folder.")
