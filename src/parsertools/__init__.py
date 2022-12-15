"""
NAME
parsertools

DESCRIPTION
Package for processing luminescence time drive (.td) files.

Created for Python version 3.7

Beside the option to import this package and use the tools directly, a user interface is provided.

PACKAGE CONTENTS
defaultvalues
pttools
fitting (package)
timedrivedata
signal
timedriveparser
signalgroup

CLASSES
TimeDriveData
Signal
Parser
Signalgroup

FUNCTIONS
get_xy
get_highest
list_td_files
make_header
signals_to_csv
fitting.prepare_inits
fitting.fit_data
fitting.make_func

VARIABLES
default_values.default_import_folder
default_values.default_csv_folder
default_values.default_parsed_folder
default_values.default_starting_point
default_values.default_threshold
default_values.default_background_bounds
fitting.FUNCTIONS (dict, function names as keys, functions as values)
fitting.DEFAULT_INITS (dict, function names as keys, lists of default initial parameters per function type as values)

DETAILED CONTENTS AND USE
TimeDriveData - A dataset object holds the data from one time drive file, that can then
    be analysed to correct it and create signal objects from the corrected data.
    The data in the set can be retrieved or saved to a csv file.
Signal - Signal objects are created from time drive data. They store information about
    their file of origin and hold the corrected data from their time drive.
    The data and information can be retrieved, the signal can also be fitted to a model
    curve. Signals can be saved using the function signals_to_csv. See functions.

Although the TimeDriveData and Signal classes can be useful by themselves, they are most
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

pttools contains some common functions that are used by different classes:
get_xy - convert dict of time and value data of a signal to an x and y list
get_highest - extract the timepoint and value where the value in signal data is the highest
list_files - list all files ending in .td in a directory
make_header - create headers for a csv file for given signals
signals_to_csv - save the data from given signals to a csv file

defaultvalues contains default data locations and settings for parsing, used both as defaults in class methods in
    parsertools classes and also as default values in the user interface

fitting contains functions for fitting data to a curve in fitting.fittools and functions that this data can be fit to in
fitting.functions. Additional functions can be defined in the same format as the existing ones.
"""

import src.parsertools.fitting as fitting
import src.parsertools.defaultvalues
from .timedrivedata import TimeDriveData
from .timedriveparser import Parser
from .signal import Signal
from .signalgroup import SignalGroup
from .pttools import list_td_files, signals_to_csv, get_xy, get_highest
