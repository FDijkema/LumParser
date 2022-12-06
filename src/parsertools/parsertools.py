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
    for all .td files in the given diretory
signals_to_csv(signals, file_name, data_folder) - Save all signals in the list
    to one csv file of the given name in the given folder. This can be only one
    signal.
"""

import os
import copy
import itertools
import numpy as np
from scipy.optimize import curve_fit, minimize, least_squares
from scipy.stats import chisquare
from math import *

class Dataset:
    """
    Extract the data from a given time drive file and store it in a dataset instance.

    Analyse data to find the background and start of peak signals.
    Export the data to csv.
    Create signal instances from the data, that can then be used for further
        analyses.
    """

    def __init__(self, name, directory):
        """
        Initialize data object from file.

        params:
            name (str): storing the filename for later use
            directory (str): where to find the file

        The file is expected to be in text format.
        Data should be preceded by a line reading "#DATA"
        The data should be in sequential lines of two numerical values separated by whitespace
        Example:
        #DATA
        0.1   2.001
        0.2   2.030
        0.3   3.502
        """
        self.name = name
        self.raww = self._unpack(directory)
        self.data = self._clean()
        self.corrected = None

    def _unpack(self, directory):
        """read the file at the directory"""
        input = open(directory)
        try:
            raww = input.readlines()
        except UnicodeDecodeError:
            raww = ""
            print("There was a problem reading file %s: unknown character." % self.name)
        input.close()
        return raww

    def _clean(self):
        """extract only the numerical data from self.raww"""
        data = []
        record = False
        for line in self.raww:
            # look for the start of the data
            if line.startswith("#DATA"):
                record = True  # start recording  from the next line in the file
                continue
            elif record:
                try:
                    time, value = line.split()
                    data.append({"time": float(time), "value": float(value)})
                except ValueError:
                    pass
        return data

    def _find_peaks(self, starting_point, threshold):
        """
        Find sudden increases in value (the signal starts).

        Record a signal start when the value is higher than the average of the previous 10 values
        by at least the treshold.
        Values before the starting point do not count.
        Signals cannot be closer together than 100 datapoints.

        parameters:
            starting point [#datapoints]: datapoint after which signals are expected
            treshold [relative light units]: minimum value increase to record signal
        """
        stp = starting_point
        th = threshold
        data = self.data

        signal_starts = []  # list of observed peaks
        local = []  # list of local datapoints
        i = 0
        while i < len(data):
            value = data[i]["value"]
            # create a list of 10 most recent points, calc average
            local.append(value)
            if len(local) > 10:
                local = local[-10:]
                local_average = sum(local) / len(local)
                # start looking for signals after the expected time point
                if i > stp and value > (local_average + th):  # sudden increase
                    for index in range(i, i + 100):
                        try:
                            value = data[index]["value"]
                            if value < local_average:  # no signal
                                i += 1
                                break
                        except IndexError:  # the end of the file has been reached
                            continue
                    else:  # there is a signal
                        signal_starts.append(i)
                        i += 100  # skip 100 points ahead to avoid counting the same signal twice
                        local = []
                else:  # no signal
                    i += 1
            else:  # we cannot compare to an average yet
                i += 1
        if signal_starts == []:
            print("No signals were found in {}. Try to adjust the starting point or threshold.".format(self.name))
        return signal_starts  # right now, this is the count at which the signal occurs

    def _get_bg(self, first_peak, bounds):
        """
        Define the background boundaries and calculate the average signal between them.
        Use different preset modes or put in boundaries of background.
        """
        # unit = seconds
        data = self.data
        pk = first_peak
        preset_bounds = {
            "start_short": (0, 10),
            "start_long": (0, 100),
            "peak_short": (pk - 10, pk),
            "peak_long": (pk - 100, pk)
        }
        if bounds in preset_bounds:
            left, right = preset_bounds[bounds]
        else:  # find out if the input consist of valid numbers
            try:
                left, right = bounds
                if right > pk:
                    print("Background of {} could not be calculated: background "
                          "boundary at {} seconds overlaps with peak at {} "
                          "seconds".format(self.name, right, pk))
                    return 0
                elif right < left:
                    right, left = left, right
            except:
                print("Background could not be calculated: "
                      "%s not recognised as background boundaries" % bounds)
                return 0
        bg_sum = 0
        num = 0
        for point in data:
            if point["time"] > right:
                break
            elif point["time"] > left:
                num += 1
                bg_sum += point["value"]
        background = bg_sum / float(num)
        # now check if the signal doesn't dip below the perceived background
        # if so, the background should be adjusted
        end_sum = 0
        for datapoint in data[-100:]:
            end_sum += datapoint["value"]
        end_avg = end_sum/100
        if end_avg < background:
            background = end_avg
        return background

    def _correct(self, correction):
        """subtract the value from all values in self.data, assign self.corrected"""
        corrected = []
        for point in self.data:
            # correct the background for each point
            time = point["time"]
            value = point["value"]
            corr_value = value - correction
            corrected.append({"time": time, "value": corr_value})
        self.corrected = corrected

    def analyse(self, starting_point=0, threshold=0.3, bg_bounds="start_short"):
        """
        Analyse the data, return a list of corrected signals.

        First, signal starts are detected by a minimum increase of the value over the
        average of the last 10 values.
        Then, the average background noise is calculated.
        Signal objects are created from the data. A signal start at a detected signal
        start and ends at the beginning of the next signal or the end of the data.
        The values in the signal object data are corrected for the background noise.
        The time where the signal starts is reset to 0.

        parameters:
            starting point [#datapoints]: the earliest time when the peak is expected
            threshold [rlu]: the smallest increase that will count as peak start
            bg_bounds [s]:
                tuple (left, right) OR
                string, preset options:
                    "start_short": (0,10)
                    "start_long": (0,100)
                    "peak_short": (pk-10, pk)
                    "peak_long": (pk-100, pk)
        """
        peaks = self._find_peaks(starting_point, threshold)
        if peaks == []:
            return []
        first_peak_time = self.data[peaks[0]]["time"]
        self.background = self._get_bg(first_peak_time, bounds=bg_bounds)
        self._correct(self.background)

        signals = []
        peakends = peaks[1:]
        peakends.append(len(self.corrected))
        for i in range(len(peaks)):
            signal_data = copy.deepcopy(self.corrected[peaks[i]:peakends[i]])  # beginning and end of respective lists
            signal_name = "%s %i" % (self.name, i + 1)
            signals.append(Signal(signal_name, signal_data, self.name))  # create a Signal instance
        return signals  # list of signal objects

    def get_xy(self, oftype="original"):
        """
        Output list of time and list of values.

        Parameters:
            oftype ["original" or "corrected"]: indicates whether the original data
                or the data corrected for the background noise and reset to t0 = 0
                should be used
        """
        typedict = {"original": self.data, "corrected": self.corrected}
        data = typedict[oftype]
        timelist = [datapoint["time"] for datapoint in data]
        valuelist = [datapoint["value"] for datapoint in data]
        return timelist, valuelist

    def export_to_csv(self, filename, data_folder, oftype="original"):
        """Save data to the assigned filename."""
        output = ""
        columns = []
        header = ([self.name, ""], [oftype, ""])
        data = self.get_xy()
        # put informative headers above the data
        column1 = header[0] + data[0]
        column2 = header[1] + data[1]
        columns.append(column1)
        columns.append(column2)
        # restructure the data from columns to rows
        rows = itertools.zip_longest(*columns)
        for line in rows:
            output_line = ",".join(map(str, line)) + "\n"
            output += output_line
        # save the string to the file
        outfile = open(os.path.join(data_folder, filename), "w")
        outfile.write(output)
        outfile.close()


class Signal:
    """
    Signal object contains the data and information for one signal found in a time drive.

    Information about the object can be retrieved via the following methods:
    signal.integrate()      Return a new signal object containing the integrated
                            data. The _datatype parameter of the new object is "integrated".
                            When an integrated signal is put in, this parameter is used
                            to recognise it as already integrated and the input signal is returned.
    signal.get_xy()         Return a list of timevalues and a list of datavalues
                            in a tuple ([time], [data]). Can be used to write the
                            data to csv. The header fits above these columns.
    signal.get_highest()    Return the highest value in the signal data. This is
                            the peak for normal data and the total integral for
                            integrated data.
    signal.get_info()       Return a string stating the peak height or total integral
                            depending on the data type (normal or integrated)
    signal.fit_to(self, fct="Exponential", init_str='', func_str='', param_str='')
                            Fit the signal to a model curve. fct is a string indicating
                            one of the preset function types or "Other". inits is
                            a string consisting of initial parameter values
                            separated by comma's. The number of parameters needed
                            determined by the function type. func_str and param_str
                            are only used with fct="Other" and give a string with
                            the function formula and list of paramter names,
                            respectively.
    """
    def __init__(self, name, data, filename, _datatype="normal"):
        """
        Signal object contains the data for the duration of that signal

        Time is reset to 0 at signal start.

        Parameters:
        name (str)      signal name, used to identify
        data (dict) {time1: value1,
                    time2: value2}
                        dictionary containing the signal data in time, value pairs.
        filename (str)  original filename of the time drive the signal was taken from
        _datatype ("normal" or "integrated")
                        used to identify is the data is integrated or not

        Attributes:
        self.start      starting time of the signal in the original time drive
        self.name       name of the signal. Automatically generated, can be altered
                        by user
        self.signal_data
                        dictionary of datapoints
        """
        data = data
        self.start = data[0]["time"]
        for i, point in enumerate(data):
            data[i]["time"] = point["time"] - self.start
        self.name = name
        self.signal_data = data
        self.peak_time, self.peak_height = self.get_highest()
        self.filename = filename
        self.datatype = _datatype

    def integrate(self):
        """Integrate the signal and return a new signal object with that data"""
        if self.datatype != "integrated":  # prevent accidental double integration
            int_data = []
            prev_time = 0.
            prev_val = 0.
            for point in self.signal_data:
                value = point["value"]
                cur_time = point["time"]
                cur_val = prev_val + (cur_time - prev_time) * value
                int_data.append({"time": cur_time, "value": cur_val})
                # update
                prev_time = cur_time
                prev_val = cur_val
            new_signal = Signal(self.name, int_data, self.filename, _datatype="integrated")
            new_signal.start = self.start
            new_signal.peak_time, new_signal.peak_height = self.get_highest()
            new_signal.total_int = new_signal.get_highest()[1]
            self.total_int = new_signal.get_highest()[1]
            return new_signal
        else:
            # optional:
            # print("Signal is already integrated")
            return self

    def _get_header(self):
        """
        Return list of header columns

        Headers give information about signal and function as titles for columns of
        data in a csv file
        """
        nameheader = [self.name, ""]
        startheaders = ["Start at [s]:", "%.6g" % self.start]
        infoheaders = {
            "normal": ["Peak height [RLU]:", "%.6g" % self.get_highest()[1]],
            "integrated": ["Total integral [RLU*s]:", "%.6g" % self.get_highest()[1]]
        }
        typeheaders = {
            "normal": ["Time[s]", "Light signal[RLU]"],
            "integrated": ["Time[s]", "Integrated light signal[RLU]"]
        }
        header = [list(h) for h in
                  zip(nameheader, startheaders, infoheaders[self.datatype], typeheaders[self.datatype])]
        return header

    def get_xy(self):
        """Return list of time and list of values"""
        timelist = [datapoint["time"] for datapoint in self.signal_data]
        valuelist = [datapoint["value"] for datapoint in self.signal_data]
        return timelist, valuelist

    def get_highest(self):
        """
        Return time and value of the highest value

        For normal signal this will be the time and value of the peak
        For integrated signal this will be the total integral
        """
        highest_value = 0.
        highest_time = 0.
        for point in self.signal_data:
            if point["value"] >= highest_value:
                highest_value = point["value"]
                highest_time = point["time"]
        return highest_time, highest_value

    def get_info(self):
        """
        Return a string with most important signal features

        This is the the peak height or total integral
        depending on the data type (normal or integrated)
        """
        time, value = self.get_highest()
        if self.datatype == "normal":
            return "Peak maximum:%.6g RLU at %.2f s" % (value, time)
        elif self.datatype == "integrated":
            return "Total integral: %.6g" % value
        else:
            # if this happens, the user has tinkered with the signal type
            # invalid
            return "Shitty signal type: not recognised"

    def _prepare_inits(self, initstring):
        """
        Calculate initial values for fit parameters and check if they are numerical

        Return a list of floats that is save to use as inits for fit.
        Input for initstring should be a string of numbers separated by comma's.
        Letters I and P are accepted to denote total integral and peak height.
        """
        if initstring == "":
            print("Please add initial estimates for the parameter values.")
            return
        rawinits = [r.strip() for r in initstring.split(",")]
        inits = []
        for num in rawinits:
            num = num.replace("P", str(self.get_highest()[1]))
            intsignal = self.integrate()
            num = num.replace("I", str(intsignal.get_highest()[1]))
            if "__" in num:
                num = ""
                print("Value not allowed")
            num = eval(num, {'__builtins__': {}})
            try:
                inits.append(float(num))
            except ValueError:
                print("Initial parameter %s is not valid" % str(num))
        return inits

    def _make_func(self, mystring, myparams):
        """
        Create a customisable function to fit data to

        :param mystring: a string describing a mathematical function
        :param myparams: string of parameters, split by comma's
        :return: a python function that takes in a value for x and the given
                parameters and outputs the result of the function
        """
        # check if the function string contains x
        if not "x" in mystring:
            print("Formula must be defined in terms of x. Please try again.")
            return

        # prepare parameters for use
        params = []
        for p in myparams.split(","):
            ps = p.strip()
            # check if proposed parameter is alphabetic character, for safety reasons
            if ps.isalpha():
                params.append(ps)
            else:
                print('Parameters not recognised. Please use alphabetic characters as parameters.')
                break

        def func(x, *paramvalues):
            # note! the values must be checked to be numerical before using them here
            paramdict = dict(zip(params, paramvalues))
            map(exec, ['{} = {}'.format(par, paramdict[par]) for par in paramdict])
            safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
                         'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor',
                         'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10',
                         'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt',
                         'tan', 'tanh']
            safe_dict = dict([(sf, globals().get(sf, None)) for sf in safe_list])
            safe_dict['x'] = x
            safe_dict.update(paramdict)
            try:
                return eval(mystring, {"__builtins__": None}, safe_dict)
            except (SyntaxError, TypeError):
                print('Syntax error in formula. Please try again.')
                return

        func.name = "Other"
        func.formula = mystring
        func.params = params
        return func

    def fit_to(self, fct="Exponential", init_str='', func_str='', param_str=''):
        """
        Take the signal data and fit to given function, return fit information

        Two modes of use possible:
        1) put in a preset function name for fct:
            "Exponential" - exponential function
            "Double exponential" - double exponential function
            "Luminescence model" - luminescence model
        2) fct = "Other"
            In this case func_str and param_str must further describe the function
            func_str should be a string stating the  mathematical expression
                for the function
            param_str should give the parameters to optimise in the fit in this
                format: 'param1, param2, param3'. X should not be included.
            The function can only contain mathematical expression and parameters
                that are described in the parameter string.

        :param fct: string that describes desired type of function
        :param init_str: string of initial values for parameters. String of numbers separated by comma's.
            Letters I and P are accepted to denote total integral and peak height.
        :param func_str: for fct='Other', function formula should be put in here
        :param param_str: for fct='Other', function parameters should be put in here
        :return: func, popt, perr, p
            # func is function object used to fit
                # includes func.name (str), func.formula (str) and func.params (list of str)
            # popt is array of parameters
            # pcov is covariance of those parameters, variance on diagonal
            # perr is standard deviation error in one number
        """

        # preset functions
        global pcov

        def exp_func(x, a, b, k):
            return a * (b - (np.exp(-k * x)))
        exp_func.name = "Exponential"
        exp_func.formula = "a * (b - (exp(-k * x)))"
        exp_func.params = ["a", "b", "k"]
        exp_func.bounds = (np.array([0, 0.5, 0]), np.array([np.inf, 1.5, 1]))

        def dexp_func(x, a, b, c, k1, k2):
            return a * (b - (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)))
        dexp_func.name = "Double exponential"
        dexp_func.formula = "a * (b - (c * exp(-k1 * x) + (1 - c) * exp(-k2 * x)))"
        dexp_func.params = ["a", "b", "c", "k1", "k2"]
        dexp_func.bounds = (-np.inf, np.inf)

        def dexp_func_2(x, a, b, c, k1):
            return a * (b - (c * np.exp(-k1 * x) + (1 - c) * np.exp(-0.032 * x)))
        dexp_func_2.name = "Double exponential, fixed k2"
        dexp_func_2.formula = "a * (b - (c * exp(-k1 * x) + (1 - c) * exp(-0.032 * x)))"
        dexp_func_2.params = ["a", "b", "c", "k1"]
        dexp_func_2.bounds = (-np.inf, np.inf)

        def dexp_baseline(x, a, c, k1, k2, d, b):
            return a - a * (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)) + d*x + b
        dexp_baseline.name = "Double with baseline"
        dexp_baseline.formula = "a - a * (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)) + a*d*x + a*b"
        dexp_baseline.params = ["a", "c", "k1", "k2", "d", "b"]
        dexp_baseline.bounds = (np.array([0, 0, 0, 0, -np.inf, -np.inf]), np.array([np.inf, np.inf, 0.1, 0.02, np.inf, np.inf]))

        #def lum_model(x, E0, S0, kcat, kE):
        #    return 450.3E9 * kcat*E0*S0*np.exp((-kE-0.0003)*x + kcat/kE*E0*np.exp(-kE*x))
        # lum_model.name = "Luminescence model"
        # lum_model.formula = "450.3E9 * kcat*E0*S0*exp((-kE-0.0003)*x + kcat/kE*E0*exp(-kE*x))"
        # lum_model.params = ["E0", "S0", "kcat", "kE"]

        funcs = {
            "Exponential": exp_func,
            "Double exponential": dexp_func,
            "Double exponential 2": dexp_func_2,
            "Double with baseline": dexp_baseline,
        }

        # create function from user input if desired, otherwise use preset function
        if fct == "Other":
            func = self._make_func(func_str, param_str)
        elif fct in funcs:
            func = funcs[fct]
        else:
            print("function type not recognised")
            return

        # check and prepare initial values
        initlist = self._prepare_inits(init_str)
        if len(initlist) != len(func.params):
            print('Number of parameters does not match number of initial values.')
            return
        inits = np.array(initlist, dtype=np.float64)

        # fit signal
        xa, y = self.get_xy()
        # only take signal after peak, easier to fit
        x = [item for item in xa if item >= self.peak_time]
        y = y[-len(x):]
        x = np.array(x, dtype=np.float64)  # transform data to numpy array
        y = np.array(y, dtype=np.float64)
        with np.errstate(over="ignore"):
            try:
                popt, pcov = curve_fit(func, x, y, inits, bounds=func.bounds)
            except RuntimeError as RE:
                print("Signal %s can't be fitted." % self.name)
                print(RE)
                return
        perr = np.sqrt(np.abs(np.diag(pcov)))
        chisq, p = chisquare(y, f_exp=func(x, *popt))
        return func, popt, perr, p


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
         datsets to be analysed
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
        self.anasettings = {}   # settings for analysis, saved by filename
        self.default_settings = {   # the default analysis settings
            "starting_point": 0,
            "threshold": 0.3,
            "bg_bound_L": 0,
            "bg_bound_R": 10
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
            file_dataset = Dataset(filename, thisfile["directory"])
            self.datasets[filename] = file_dataset  # save the data so it can be retrieved by filename
            # variables used per file (initialize default)
            self.anasettings[filename] = self.default_settings.copy()  # very important to copy!!

    def remove_file(self, filename):
        """Remove this dataset and the associated settings from the analysis."""
        del self.datasets[filename]
        del self.anasettings[filename]

    def set_vars(self, setname, var_name, var_value):
        """Set the given analysis variable for the dataset to the value given"""
        self.anasettings[setname][var_name] = var_value

    def apply_all(self, var_name, var_value):
        """Set the given analysis variable to the value given for all datasets"""
        for setname in self.anasettings:
            self.anasettings[setname][var_name] = var_value

    def update_signals(self, setname):
        """Create or update the list of signals for a dataset using the stored parameters"""
        stp = self.anasettings[setname]["starting_point"]
        th = self.anasettings[setname]["threshold"]
        bg = (self.anasettings[setname]["bg_bound_L"], self.anasettings[setname]["bg_bound_R"])
        self.signals[setname] = self.datasets[setname].analyse(starting_point=stp,
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
        signals_to_export = []
        if normal:
            signals_to_export.extend(self.signals[setname])
        if integrate:
            integrated_signals = []
            for signal in self.signals[setname]:
                integrated = signal.integrate()
                integrated_signals.append(integrated)
            signals_to_export.extend(integrated_signals)
        elif not normal:
            print("Could not save: normal and integrate cannot both be false.")
            return
        signals_to_csv(signals_to_export, exportname, data_folder)


class Signalgroup:
    """
    Hold multiple signals, possibly from different files, and analyse them

    A signalgroup is an object storing information about multiple
    signals. It can either be initiated from a list of signals (created from a
    dataset) or from a previously saved file. It can also be made from a selection
    of signals from different datasets. Signals can be accessed by name or
    index, renamed, added, moved in the sequence or removed.
    The entire signalgroup can be saved to work on later or the signals, fits
    and fit parameters of all signals can be created and exported to csv at once.

    Two ways to create signalgroup:
    __init__(signals, filename, notes="") - initiate signalgroup form a list of
        signals, giving it a filename and possibly some notes for user
    Signalgroup.loadfrom(directory) - loading a signalgroup from a saved file
    """

    def __init__(self, signals, filename, notes=""):
        """Initiate signalgroup from list of signals, storing information."""
        self.signals = {}   # dict of signals by signal name
        self.indexed = []   # list of signal names (by index)
        self.add(signals)   # this way signals are added both by name and index
        self.notes = notes  # notes are for user
        self.filename = filename    # filename is used for saving
        self.fits = {}  # latest created fits of signals by signal name

    @classmethod
    def loadfrom(cls, directory):
        """Load signalgroup from file. Returns itself. Alternative init method"""
        # read the file
        input = open(directory)
        raww = input.readlines()
        input.close()
        # get and store the information
        signals = []
        r_notes = False
        r_signal = False
        r_data = False
        data = []
        s_info = {}
        for line in raww:
            if line.startswith("NOTES"):
                r_notes = True
                notes = ""
            elif line.startswith("SIGNAL"):
                r_signal = True
            elif line.startswith("DATA"):
                r_data = True
            elif r_data:
                if line.startswith("END"):  # create a new signal
                    signal = Signal(s_info["name"], data, s_info["filename"])
                    for name in s_info:
                        setattr(signal, name, s_info[name])
                    signals.append(signal)
                    data = []
                    s_info = {}
                    r_signal = False
                    r_data = False
                else:
                    time, value = line.split(",")
                    data.append({"time": float(time), "value": float(value)})
            elif r_signal:
                name, value = line.split("=")
                try:
                    s_info[name] = float(value)
                except ValueError:
                    s_info[name] = value.strip("\n")
            elif r_notes:
                notes += line
            else:
                filename = line.strip("\n")
        signalgroup = Signalgroup(signals, filename, notes)
        return signalgroup

    def add(self, signals):
        """Append signals to group, both by name and index"""
        for signal in signals:
            new_signal = copy.copy(signal)
            self.signals[new_signal.name] = new_signal
            self.indexed.append(new_signal.name)

    def rename(self, old_name, new_name):
        """Rename the signal."""
        # the indexed list
        index = self.indexed.index(old_name)
        del (self.indexed[index])
        self.indexed.insert(index, new_name)
        # the dict of signal objects
        self.signals[new_name] = self.signals[old_name]
        del (self.signals[old_name])
        # the signal attribute
        self.signals[new_name].name = new_name

    def remove(self, signal_name, seq=False):
        """
        Remove signals from group by name.

        To remove multiple signals at once, input a list of names for signal_name
        instead of a single string and set seq=True.
        """
        if seq:
            for s_name in signal_name:
                del (self.signals[s_name])
                self.indexed.remove(s_name)
        else:
            del (self.signals[signal_name])
            self.indexed.remove(signal_name)

    def remove_at(self, index, seq=False):
        """
        Remove signals from group by index.

        To remove multiple signals at once, input a list of indices for index
        instead of a single number and set seq=True.
        """
        if seq:
            for i in index:
                del (self.signals[self.indexed[i]])
                del (self.indexed[i])
        else:
            del (self.signals[self.indexed[index]])
            del (self.indexed[index])

    def get(self, signal_name, seq=False):
        """
        Return the signal object when given the name.

        To retrieve multiple signals, input a list of names and set seq=True.
        """
        if seq:
            signals_list = []
            for s_name in signal_name:
                signals_list.append(self.signals[s_name])
            return signals_list
        else:
            return self.signals[signal_name]

    def get_at(self, index, seq=False):
        """
        Return signal object for index.

        To retrieve multiple signal objects, input a list of indices and set
        seq=True.
        """
        if seq:
            signals_list = []
            for i in index:
                signals_list.append(self.signals[self.indexed[i]])
            return signals_list
        else:
            return self.signals[self.indexed[index]]

    def get_index(self, signal_name, seq=False):
        """Return index for name or list of indices for list of names."""
        if seq:
            indices = []
            for s_name in signal_name:
                indices.append(self.indexed.index(s_name))
            return indices
        else:
            return self.indexed.index(signal_name)

    def get_all(self):
        """Return a list of all signal objects in the group."""
        signals_list = []
        for s_name in self.indexed:
            signals_list.append(self.signals[s_name])
        return signals_list

    def move_up(self, signal_names):
        """Move the given signals up in the indexed list by 1"""
        for s_name in signal_names:
            index = self.indexed.index(s_name)
            self.indexed.insert(index - 1, self.indexed.pop(index))

    def move_down(self, signal_names):
        """Move the given signals down in the indexed list by 1"""
        for s_name in signal_names:
            index = self.indexed.index(s_name)
            self.indexed.insert(index + 1, self.indexed.pop(index))

    def move_up_at(self, indices):
        """Move the signals at the given indices up in the indexed list by 1"""
        for index in indices:
            self.indexed.insert(index - 1, self.indexed.pop(index))

    def move_down_at(self, indices):
        """Move the signals at the given indices down in the indexed list by 1"""
        for index in indices:
            self.indexed.insert(index + 1, self.indexed.pop(index))

    def update_notes(self, new_notes=""):
        """Replace the user notes with the string that is put in for new_notes"""
        self.notes = new_notes

    def change_filename(self, new_name):
        """Set the filename of the signalgroup to new_name"""
        self.filename = new_name
        if self.filename.endswith(".parsed"):
            pass
        else:
            self.filename += ".parsed"

    def fit_signal(self, signal_name, fct="Exponential", init_str='', func_str='', param_str=''):
        """
        Take the signal of given name and fit to function, return fit information

        Two modes of use possible:
        1) put in a preset function name for fct:
            "Exponential" - exponential function
            "Double exponential" - double exponential function
            "Luminescence model" - luminescence model
        2) fct = "Other"
            In this case func_str and param_str must further describe the function
            func_str should be a string stating the  mathematical expression
                for the function
            param_str should give the parameters to optimise in the fit in this
                format: 'param1, param2, param3'. X should not be included.
            The function can only contain mathematical expression and parameters
                that are described in the parameter string.

        Advantage of using this function over Signal.fit_to method directly is
        that the parameters and fit get stored in the signalgroup and can be
        exported to csv.

        :param signal_name: string, name of the signal that should be fitted
        :param fct: string that describes desired type of function
        :param init_str: string of initial values for parameters. String of numbers separated by comma's.
            Letters I and P are accepted to denote total integral and peak height.
        :param func_str: for fct='Other', function formula should be put in here
        :param param_str: for fct='Other', function parameters should be put in here
        :return: func, popt, perr, p
            # func is function object used to fit
                # includes func.name (str), func.formula (str) and func.params (list of str)
            # popt is array of parameters
            # pcov is covariance of those parameters, variance on diagonal
            # perr is standard deviation error in one number
        """
        print("Fitting: {}".format(signal_name))
        s = self.get(signal_name)
        s = s.integrate()
        funct, popt, perr, p = s.fit_to(fct, init_str=init_str, func_str=func_str,
                                        param_str=param_str)  # calculating the fit
        #  add the fit to the list
        x, y = s.get_xy()
        x = np.array(x)
        self.fits[signal_name] = (list(x), list(funct(x, *popt)))
        # add the parameters to the list
        if funct.name == "Double exponential":
            poptlist = list(popt)
            if poptlist[4] > poptlist[2]:  # k2 > k1: always put biggest first
                poptlist[1:5] = poptlist[3:5] + poptlist[1:3]  # swap 1 and 2
            outparams = dict(zip(funct.params, poptlist))
        else:
            outparams = dict(zip(funct.params, list(popt)))
        outparams["p"] = p
        for P in outparams:
            setattr(self.get(signal_name), P, outparams[P])
        return funct, popt, perr, p

    def save(self, data_directory):
        """Save the signalgroup to the given directory, by it's stored filename"""
        output = str(self.filename) + "\n"
        output += "NOTES\n" + self.notes + "\n"
        for s_name in self.indexed:
            signal = self.signals[s_name]
            output += "SIGNAL\n"
            for var in vars(signal):
                if var != "signal_data":
                    output += "%s=%s\n" % (var, str(vars(signal)[var]))
            output += "DATA\n"
            x, y = signal.get_xy()
            rows = zip(x, y)
            for line in rows:
                output_line = ",".join(map(str, line)) + "\n"
                output += output_line
            output += "END\n"
        # write output to file
        outfile = open(os.path.join(data_directory, self.filename), "w")
        outfile.write(output)
        outfile.close()

    def export_csv(self, exportname, data_folder, normal=True, integrate=False):
        """
        Export the data of the signals in the signalgroup to a csv file

        Either the normal data or the integrated data of all signals can be saved,
        or both.

        Parameters:
        :param exportname: string, name of the file to save to, should end in .csv
        :param data_folder: string, location to save the file
        :param normal: True or False, should normal data be saved?
        :param integrate: True or False, should integrated data be saved?
        normal and integrate cannot both be false. Either normal or integrated
            must be saved.
        """
        signals_to_export = []
        for s_name in self.indexed:
            if normal:
                signals_to_export.append(self.signals[s_name])
            if integrate:
                signals_to_export.append(self.signals[s_name].integrate())
            elif not normal:
                print("Could not save: no type of plot selected.")
                return
        signals_to_csv(signals_to_export, exportname, data_folder)

    def export_fits(self, exportname, data_folder, fit_type):
        """
        Export all the latest fits that were made of the signals in the group

        Note: when fits are created, only the latest fit for each signal is saved.
        So when saving, make sure that all fit types are the same. Otherwise,
        correct by hand.

        :param exportname: string of desired file name to save to
        :param data_folder: string of desired location to save file
        :param fit_type: name or formula of the curve that the signal was fitted to
        """
        output = ""
        row1 = []
        row2 = []
        rest = []
        for s_name, f in self.fits.items():
            row1 += ["Fit of " + s_name + " to", fit_type]
            row2 += ["Time[s]", "Fitted integrated light intensity [RLU*s]"]
            rest.extend(f)
        rows = [row1, row2] + list(itertools.zip_longest(*rest))
        for line in rows:
            output_line = ",".join(map(str, line)) + "\n"
            output += output_line
        # save the string to the file
        outfile = open(os.path.join(data_folder, exportname), "w")
        outfile.write(output)
        outfile.close()

    def export_parameters(self, exportname, data_folder):
        """
        Export all the latest fit parameters that were saves for the signals in the group

        Note: only the parameters that are saved for the first signal in the sequence
        are saved. The values of all signals are saved, but if not the same
        parameters are saved for all signals, or if some values are overwritten,
        this is not taken into account.

        :param exportname: string of desired file name to save to
        :param data_folder: string of desired location to save file
        """
        output = "name, filename,"
        some_signal = self.get_at(0)
        for var in vars(some_signal):  # create the title row
            try:
                float(vars(some_signal)[var])
            except (ValueError, TypeError):  # only take attributes with numeric values
                pass
            else:
                output += str(var) + ","
        output += "\n"
        for signal in self.get_all():  # row of values for each signal
            line = signal.name + ", " + signal.filename + ","
            for var in vars(signal):
                try:
                    float(vars(signal)[var])
                except (ValueError, TypeError):  # only take attributes with numeric values
                    pass
                else:
                    line += str(vars(signal)[var]) + ","
            output += line + "\n"
        # save the string to the file
        outfile = open(os.path.join(data_folder, exportname), "w")
        outfile.write(output)
        outfile.close()


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