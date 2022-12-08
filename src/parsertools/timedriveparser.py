from src.parsertools import TimeDriveData, list_files, signals_to_csv
from src.parsertools.defaultvalues import default_threshold, default_starting_point, default_background_bounds


class Parser:
    """
    Hold multiple datasets and the settings to create signals from them.


    The parser is used to manage datasets and signals. It holds a dataset
    for each file in the given directory. Per file the desired analysis settings
    can be given, after which a list of signals is created for each file. This
    entire list can be saved to one csv file. A signal group can also be made out
    of it.

    Methods:
        __init__ - create and empty parser object
        import_ascii(data_folder) - create a dataset for each file in the
            given directory and default analysis settings for each dataset
        remove_file(filename) - remove the dataset of the given filename from the
         datasets to be analysed
        set_vars(setname, var_name, var_value) - set the analysis variable
            "var_name" to the value "var_value" for the given dataset
        apply_all(var_name, var_value) - same as set_vars, but for all datasets
            in the parser instead of only for one.
        update_signals(setname) - create or update the list of signal objects
            for the given dataset, save them in the self.signals
            dictionary, with the filename as key. The settings that are associated
            with the dataset in self.anasettings are used.
        export_csv(setname, exportname, data_folder, normal=True, integrate=False)
            - export all signals of one dataset to the given folder with given
            name. Either the normal or integrated data can be stored or both.
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

    def import_ascii(self, data_folder):
        """
        Create datasets and store settings for all files in the given directory

        The dataset is stored in the self.datasets dict, under the filename
        The settings for analysis are set to default and stored in self.anasettings,
        also under the filename.

        :param data_folder: string of the datafolder to load datasets from
        """
        for thisfile in list_files(data_folder):
            # dataset
            filename = thisfile["name"]
            file_dataset = TimeDriveData(filename, thisfile["directory"])
            self.datasets[filename] = file_dataset  # save the data so it can be retrieved by filename
            # variables used per file (initialize default)
            self.parse_settings[filename] = self.default_settings.copy()  # very important to copy!!

    def remove_file(self, filename):
        """Remove this dataset and the associated settings from the analysis."""
        del self.datasets[filename]
        del self.parse_settings[filename]

    def set_vars(self, setname, var_name, var_value):
        """Set the given analysis variable for the dataset to the value given"""
        self.parse_settings[setname][var_name] = var_value

    def apply_all(self, var_name, var_value):
        """Set the given analysis variable to the value given for all datasets"""
        for setname in self.parse_settings:
            self.parse_settings[setname][var_name] = var_value

    def update_signals(self, setname):
        """Create or update the list of signals for a dataset using the stored parameters"""
        stp = self.parse_settings[setname]["starting_point"]
        th = self.parse_settings[setname]["threshold"]
        bg = (self.parse_settings[setname]["bg_bound_L"], self.parse_settings[setname]["bg_bound_R"])
        self.signals[setname] = self.datasets[setname].extract_signals(starting_point=stp,
                                                                       threshold=th, bg_bounds=bg)

    def export_csv(self, setname, exportname, data_folder, normal=True, integrate=False):
        """
        Export all signals in the given dataset to a csv file

        Either the normal data or the integrated data of all signals can be saved,
        or both. The latest saved version of the signals is used. If the analysis
        parameters were changed afterwards, the signals need to be updated first.

        :param setname: string, name of the dataset of which the signals should be saved
        :param exportname: string, name of the file to save to, should end in .csv
        :param data_folder: string, location to save the file
        :param normal: True or False, should normal data be saved?
        :param integrate: True or False, should integrated data be saved?
        normal and integrate cannot both be false. Either normal or integrated
            must be saved.
        """
        signals_to_csv(self.signals[setname], exportname, data_folder, normal=normal, integrated=integrate, fit=False)
