"""
NAME
timedriveparser

DESCRIPTION
Module describing the time drive Parser object. Used to parse all files in a directory at once, with optional different
parsing settings for each.

CLASSES
Parser
"""

from src.parsertools.defaultvalues import default_threshold, default_starting_point, default_background_bounds
from src.parsertools.pttools import list_td_files, signals_to_csv
from src.parsertools.timedrivedata import TimeDriveData


class Parser:
    """
    Collection of TimeDriveData sets from all td files in a directory, including parsing settings and found signals


    The parser is used to manage time drive datasets and signals. It holds a dataset
    for each file in the given directory. Per file the desired analysis settings
    can be given, after which a list of signals is created for each file. This
    entire list can be saved to one csv file. A signal group can also be made out
    of it.

    ATTRIBUTES
    :ivar datasets:         dict with time drive filenames as keys and corresponding TimeDriveData objects as values
    :ivar parse_settings:   dict with time drive filenames as keys and settings for parsing time drive data in that file
                            as values
    :ivar default_settings: dict of parsing settings to copy as initial settings for the parsing of each time drive file
    :ivar signals:          dict with filenames as keys and a list of signals found wih the current settings as values

    METHODS
    import_ascii    create a dataset for each file in the given directory and default analysis settings for each dataset
    remove_file     remove the dataset of the given filename from the datasets to be analysed
    set_vars        set the analysis variable var_name" to the value "var_value" for the given dataset
    apply_all       same as set_vars, but for all datasets in the parser instead of only for one.
    update_signals  create or update the list of signal objects for the given dataset, save them in the self.signals
                    dictionary, with the filename as key. The settings that are associated with the dataset in
                    parse_settings are used.
    export_csv      export all signals of one dataset to the given folder with given name. Either the normal or
                    integrated data can be stored or both.
    """

    def __init__(self):
        """Create an empty parser object"""
        self.datasets = {}  # dict of datasets to be analysed, by filename
        self.parse_settings = {}   # settings for parsing from td, saved by filename
        self.default_settings = {   # the default analysis settings
            "starting_point": default_starting_point,
            "threshold": default_threshold,
            "bg_bound_L": default_background_bounds[0],
            "bg_bound_R": default_background_bounds[1]
        }
        self.signals = {}   # list of signals per dataset, by filename

    def import_ascii(self, data_folder: str):
        """
        Create datasets and store settings for all files in the given directory

        The dataset is stored in the self.datasets dict, under the filename
        The settings for analysis are set to default and stored in self.parse_settings,
        also under the filename.

        :param data_folder: string of the path to the datafolder to load datasets from
        """
        for thisfile in list_td_files(data_folder):
            # dataset
            filename = thisfile["name"]
            file_dataset = TimeDriveData(filename, thisfile["directory"])
            self.datasets[filename] = file_dataset    # save the data so it can be retrieved by filename
            # variables used per file (initialize default)
            self.parse_settings[filename] = self.default_settings.copy()    # very important to copy!!

    def remove_file(self, filename: str):
        """Remove this dataset and the associated settings from the analysis."""
        del self.datasets[filename]
        del self.parse_settings[filename]

    def set_vars(self, td_name: str, var_name: str, var_value: float):
        """Set the given analysis variable for the dataset to the value given"""
        self.parse_settings[td_name][var_name] = var_value

    def apply_all(self, var_name: str, var_value: float):
        """Set the given analysis variable to the value given for all datasets"""
        for setname in self.parse_settings:
            self.parse_settings[setname][var_name] = var_value

    def update_signals(self, td_name: str):
        """Create or update the list of signals for a dataset using the stored parameters"""
        stp = self.parse_settings[td_name]["starting_point"]
        th = self.parse_settings[td_name]["threshold"]
        bg = (self.parse_settings[td_name]["bg_bound_L"], self.parse_settings[td_name]["bg_bound_R"])
        self.signals[td_name] = self.datasets[td_name].extract_signals(starting_point=stp,
                                                                       threshold=th, bg_bounds=bg)

    def export_csv(self, td_name: str, exportname: str, data_folder: str, normal=True, integrate=False):
        """
        Export all signals in the given dataset to a csv file

        Either the normal data or the integrated data of all signals can be saved,
        or both. The latest saved version of the signals is used. If the analysis
        parameters were changed afterwards, the signals need to be updated first.

        :param td_name: string, name of the dataset of which the signals should be saved
        :param exportname: string, name of the file to save to, should end in .csv
        :param data_folder: string, location to save the file
        :param normal: True or False, should normal data be saved?
        :param integrate: True or False, should integrated data be saved?
        normal and integrate cannot both be false. Either normal or integrated
            must be saved.
        """
        signals_to_csv(self.signals[td_name], exportname, data_folder, normal=normal, integrated=integrate, fit=False)
