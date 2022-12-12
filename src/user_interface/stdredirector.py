from tkinter import END


class StdRedirector(object):
    def __init__(self, widget):
        self.widget = widget

    def flush(self):
        pass

    def write(self, string):
        self.widget.insert(END, string)
        self.widget.see(END)
