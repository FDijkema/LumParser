"""
NAME
defaultvalues

DESCRIPTION
Default values that can be used by other functions in the LumParser package.
The folders are mostly used by the user interface.
The parsing parameters are the default values used by TimeDriveParser to find signals in a time drive.

VARIABLES
default_import_folder
default_parsed_folder
default_csv_folder
default_starting_point
default_threshold
default_background_bounds
"""

import os

# saving location
default_import_folder = os.path.join(os.getcwd(), "data", "td")    # where to find .td files
default_parsed_folder = os.path.join(os.getcwd(), "data", "parsed")    # where to find and save .parsed files
default_csv_folder = os.path.join(os.getcwd(), "data", "csv")    # where to save .csv files

# default parsing parameters for finding signal start
default_starting_point = 0    # earliest time point where a signal is expected
default_threshold = 0.3    # how big should a sudden light value increase be to detect that a signal is starting
default_background_bounds = (0, 10)    # time points before the first signal, where the background light is measured

