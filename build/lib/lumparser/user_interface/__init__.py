"""
NAME
user_interface

DESCRIPTION
This package defines the user interface of the LumParsing package for working with luminescence time drive data.
Time drive data can be parsed from .td text files using the parsing window (parsewindow), saved as a parsed file or exported to csv.
In the analysis window (anawindow) parsed data can be analysed, fitted and plotted.

mainwindow contains the class App, which initiates and controls all other windows and frames.
parsewindow  Used to open .td ascii files and export the data to csv or parse it to work with it in an AnaFrame
anawindow    Used to analyse signal, either parsed from ascii in ParseFrame or previously savec

StdRedirector is used to redirect output from print statements to a widget in the application

PACKAGE CONTENTS
mainwindow
anawindow
anawindow_subframes (package)
parsewindow
parsewindow_subframes (package)
stdredirector
"""

from .mainwindow import App


def run_app():
    app = App()
    app.mainloop()  # initialize event loop (start interaction with user)
