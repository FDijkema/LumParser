"""
Tools for parsing of luminescence time drive files


Created for Python version 3.7

There are three option to analyse your luminescence data: use the user interface,
 run this script directly or import the tools to another script.

Use the user interface that is based of this script:
    This script comes with a user interface that makes the data analysis more
    intuitive. The signal analysis can be followed visually. To use this, execute
    "mainwindow.py"
    The user interface is the easiest way to use the script, but also the least
    flexible.

Run this script:
    If run directly, the executed code is found at the end of the file.
    Parameters can be changed there.
    The code will take each time drive file that is present in the same directory
    as the script and analyse the signals in it. Signal detection depends on the
    parameter values that are given. Each detected signal is corrected for the
    background noise detected by the program. All signals in the file are then
    saved in one comma separated values file (.csv) that is saved in the working
    directory and can be viewed in Excel.

Import this script into your own script and use the tools to do custom analysis:
    All classes and functions in this script can be used to do analysis from your
    own script directly. Functions that are not meant to be used directly are
    preceded by an underscore (example: _method1()). The classes and functions in
    this script are described below. See also the example of use script that is
    included.

Classes in this script:

Dataset - A dataset object holds the data from one time drive file, that can then
    be analysed to correct it and create signal objects from the corrected data.
    The data in the set can be retrieved or saved to a csv file.
Signal - Signal objects are created from a dataset. They store information about
    their file of origin and hold the corrected data from their time drive.
    The data and information can be retrieved, the signal can also be fitted to a model
    curve. Signals can be saved using the function signals_to_csv. See functions.

Although the Dataset and Signal classes can be useful by themselves, they are most
useful via the Parser and Signalgroup classes. These classes allow for handling
more data at once and provide extra options for analysing it.

Parser - The parser is used to manage datasets and signals. It holds a dataset
    for each file in the given directory. Per file the desired analysis settings
    can be given, after which a list of signals is created for each file. This
    entire list can be saved to one csv file. A signal group can also be made out
    of it.
Signalgroup - A signalgroup is an object storing information about multiple
    signals. It can either be initiated from a list of signals (created from a
    dataset) or from a previously saved file. It can also be made from a selection
    of signals from different datasets. Signals can be accessed by name or
    index, renamed, added, moved in the sequence or removed.
    The entire signalgroup can be saved to work on later or the signals and fits
    can be exported to csv files.

Functions in this script:

list_files(data_folder) - give a dict of filenames and the directory to open them
    for all .td files in the given directory
signals_to_csv(signals, file_name, data_folder) - Save all signals in the list
    to one csv file of the given name in the given folder. This can be only one
    signal.
"""

import os
import copy
import itertools
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare


def list_files(data_folder):
    """give list of dicts with name and directory of files as keys for all files ending in .td in directory"""
    folder = data_folder
    files = []
    for f in os.listdir(folder):
        if f.lower().endswith('.td'):
            directory = os.path.join(folder, f)
            files.append({"name": f, "directory": directory})
    return files


def signals_to_csv(signals, file_name, data_folder):
    """save the data of one or more signals to the assigned filename in csv format"""
    output = ""
    columns = []
    for signal in signals:
        header = signal._get_header()
        data = signal.get_xy()
        column1 = header[0] + data[0]
        column2 = header[1] + data[1]
        columns.append(column1)
        columns.append(column2)
    rows = itertools.zip_longest(*columns)
    for line in rows:
        output_line = ",".join(map(str, line)) + "\n"
        output += output_line
    # save the string to the file
    outfile = open(os.path.join(data_folder, file_name), "w")
    outfile.write(output)
    outfile.close()


if __name__ == "__main__":
    data_folder = os.getcwd()
    for thisfile in list_files(data_folder):
        fname = thisfile["name"]
        file_dataset = Dataset(fname, thisfile["directory"])
        ##########################################################################
        ### Put in custom variables in next line                               ###
        ### Starting point: first point where signal is expected [#datapoints] ###
        ### Threshold: minimum increase to detect signal [RLU]                 ###
        ### Bg bounds: what timepoints to include in background signal [s]     ###
        ###     "start_short": (0,10)                                          ###
        ###     "start_long": (0,100)                                          ###
        ###     "peak_short": (pk-10, pk)                                      ###
        ###     "peak_long": (pk-100, pk)                                      ###
        ###     custom: (left, right)                                          ###
        ##########################################################################
        file_signals = file_dataset.analyse(starting_point=0, threshold=0.3, bg_bounds="start_short")
        ##########################################################################
        if len(file_signals) > 0:
            signals_to_csv(file_signals, fname.replace(".td", ".csv"), os.cwd())
        else:
            print("No signals found in %s" % fname)