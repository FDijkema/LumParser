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
import itertools
from src.parsertools import get_xy


def list_files(data_folder):
    """give list of dicts with name and directory of files as keys for all files ending in .td in directory"""
    folder = data_folder
    files = []
    for f in os.listdir(folder):
        if f.lower().endswith('.td'):
            directory = os.path.join(folder, f)
            files.append({"name": f, "directory": directory})
    return files


def make_header(signal, datatype="normal"):
    """
    Return list of header columns

    Headers give information about signal and function as titles for columns of
    data in a csv file
    """
    nameheader = [signal.name, ""]
    startheaders = ["Start at [s]:", "%.6g" % signal.start]
    infoheaders = {
        "normal": ["Peak height [RLU]:", "%.6g" % signal.peak_height],
        "integrated": ["Total integral [RLU*s]:", "%.6g" % signal.total_int],
        "fit": [""]
    }
    typeheaders = {
        "normal": ["Time[s]", "Light signal[RLU]"],
        "integrated": ["Time[s]", "Integrated light signal[RLU]"],
        "fit": ["Time[s]", "Fit of integrated light signal[RLU]"]
    }
    header = [list(h) for h in
              zip(nameheader, startheaders, infoheaders[datatype], typeheaders[datatype])]
    return header


def signals_to_csv(signals, file_name, data_folder, normal=1, integrated=0, fit=0):
    """save the data of one or more signals to the assigned filename in csv format"""
    output = ""
    columns = []
    for signal in signals:
        if normal:
            x, y = get_xy(signal.signal_data)
            header = make_header(signal, datatype="normal")
            columns.extend((header[0] + x, header[1] + y))
        if integrated:
            x, y = get_xy(signal.integrated_data)
            header = make_header(signal, datatype="integrated")
            columns.extend((header[0] + x, header[1] + y))
        if fit:
            x, y = get_xy(signal.fit_data)
            header = make_header(signal, datatype="fit")
            columns.extend((header[0] + x, header[1] + y))
    rows = itertools.zip_longest(*columns)
    for line in rows:
        output_line = ",".join(map(str, line)) + "\n"
        output += output_line
    # save the string to the file
    outfile = open(os.path.join(data_folder, file_name), "w")
    outfile.write(output)
    outfile.close()
