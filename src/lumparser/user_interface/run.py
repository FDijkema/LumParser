"""Execute this file to run the LumParsing user interface"""
import tkinter as tk
from .mainwindow import App


def run_app():
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
    quit()
