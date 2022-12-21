"""
NAME
stdredirector

DESCRIPTION
Defines the class StdRedirector, which redirects printed text to a widget in the user interface. Relies on tk.

CLASSES
StdRedirector
"""

from tkinter import END


class StdRedirector(object):
    """"Redirects text from print statements to a widget in the user interface."""
    def __init__(self, widget):
        self.widget = widget

    def flush(self):
        pass

    def write(self, string):
        self.widget.insert(END, string)
        self.widget.see(END)
