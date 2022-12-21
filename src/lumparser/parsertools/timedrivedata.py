"""
NAME
timedrivedata

DESCRIPTION
Module describing the TimeDriveData object. When initiated, loads data from one time drive (.td) text file

CLASSES
TimeDriveData
"""

import os
import copy
import itertools
from lumparser.parsertools import default_background_bounds, default_starting_point, default_threshold
from lumparser.parsertools import get_xy
from lumparser.parsertools import Signal


class TimeDriveData:
    """
    Extract the data from a given time drive file and store it in a timedrivedata instance.

    Analyse data to find the background and start of peak signals.
    Export the data to csv.
    Create signal instances from the data, that can then be used for further
        analyses.

    ATTRIBUTES
    :ivar name:             name of the file to later associate with signals
    :ivar data:             list of data point dictionaries storing the time drive data
                            format example:
                            [{"time": 0.0, "value": 5.0}, {"time": 0.1, "value": 5.1}, {"time": 0.2, "value": 25.0}]
    :ivar background        initially 0. After extracting signals, background is calculated with the given analysis
                            parameters and stored here.
    :ivar corrected_data:   initially None. After extracting signals, background corrected data is stored here as a list
                            datapoint dicts. Format example:
                            [{"time": 0.0, "value": 0.0}, {"time": 0.1, "value": 0.1}, {"time": 0.2, "value": 20.0}]

    METHODS
    extract_signals         Create signal objects from the time drive data. A signal starts when a peak is detected and
                            ends at the beginning of the next peak or the end of the file. Data is first corrected for
                            background and stored in the attribute corrected_data.
    export_to_csv           Save the data (or corrected data) to a csv file.
    """

    def __init__(self, name, filepath):
        """
        Initialize data object from file.

        :param name:        name of the file to later associate with signals
        :param filepath:    where to find the time drive file

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
        self.data = self._data_from_td(filepath)    # extract the luminescence data portion from a td file
        self.background = 0
        self.corrected_data = None

    def _read_td(self, filepath):
        """Read the file, return the contents as a string."""
        input_file = open(filepath)
        try:
            raww = input_file.readlines()
        except UnicodeDecodeError:
            raww = ""
            print("There was a problem reading file %s: unknown character." % self.name)
        input_file.close()
        return raww

    def _data_from_td(self, filepath):
        """Extract the numerical data from a time drive (.td) file."""
        raw_data = self._read_td(filepath)    # read the contents of the td file
        data = []
        record = False
        for line in raw_data:
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
        return data    # Format example: [{"time": 0.0, "value": 5.0}, {"time": 0.1, "value": 5.1}]

    def _find_peaks(self, starting_point: int, threshold: float):
        """
        Find sudden increases in value (the signal starts).

        Record a signal start when the value is higher than the average of the previous 10 values
        by at least the threshold.
        Values before the starting point do not count.
        Signals cannot be closer together than 100 datapoints.

        :param starting_point:  index of the datapoint after which signals are expected
        :param threshold:       minimum value increase (in relative light units) to record a peak and start of a signal
        :return:                list of datapoint indices where signal starts occur
        """
        stp = starting_point
        th = threshold
        data = self.data

        x, y = get_xy(data)
        signal_starts = []  # list of observed peaks
        local = y[:9]  # list of local datapoints
        i = 9
        while i < len(data)-100:    # no signals in the last 100 datapoints of the file
            value = data[i]["value"]

            # calc average of 10 most recent points
            local.append(value)
            local = local[-10:]
            baseline = sum(local) / len(local)

            # start looking for signals after the expected time point
            if i > stp and value > (baseline + th):    # sudden increase, possible signal start
                for index in range(i, i + 100):    # check the first 100 datapoints after the putative signal start
                    value = data[index]["value"]
                    # if the light goes down below the baseline within 100 datapoints from the putative signal start,
                    # the peak is assumed to be noise and no signal is recorded
                    if value < baseline:
                        i += 1
                        break
                else:    # there is a signal
                    signal_starts.append(i)
                    i += 100    # skip 100 points ahead to avoid counting the same signal twice
                    local = []
            else:    # no signal
                i += 1

        if not signal_starts:
            print("No signals were found in {}. Try to adjust the starting point or threshold.".format(self.name))
        return signal_starts    # List of datapoint indices at which signal starts occur

    def _get_bg(self, first_peak, bounds):
        """
        Define the background boundaries and calculate the average light value between them.

        :param first_peak:  data point index at which the first signal peak occurs
        :param bounds:      background boundaries, tuple of two timepoints (left, right), both floats
        :return:            background light (float)
        """
        # unit = seconds
        data = self.data
        pk = first_peak
        # find out if the input consist of valid numbers
        left, right = bounds
        if right > pk:
            print("Background of {} could not be calculated: background "
                  "boundary at {} seconds overlaps with peak at {} "
                  "seconds".format(self.name, right, pk))
            return 0
        elif right < left:
            right, left = left, right
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
        """Subtract the value from all values in self.data, assign self.corrected_data."""
        corrected = []
        for point in self.data:
            # correct the background for each point
            time = point["time"]
            value = point["value"]
            corr_value = value - correction
            corrected.append({"time": time, "value": corr_value})
        self.corrected_data = corrected

    def extract_signals(self, starting_point=default_starting_point, threshold=default_threshold, bg_bounds=default_background_bounds):
        """
        Analyse the data, return a list of corrected signals.

        First, signal starts are detected by a minimum increase of the value over the
        average of the last 10 values.
        Then, the average background noise is calculated.
        Signal objects are created from the data. A signal start at a detected signal
        start and ends at the beginning of the next signal or the end of the data.
        The values in the signal object data are corrected for the background noise.
        The time when the signal starts is reset to 0.

        :param starting_point:  index of the datapoint where a peak is expected at the earliest
        :param threshold:       the smallest increase (in relative light units) that will count as peak start
        :param bg_bounds:       tuple giving time points (in seconds) in between which to calculate the background light
                                (left, right)
        :return:                list of signal objects
        """
        peaks = self._find_peaks(starting_point, threshold)
        if not peaks:
            return []
        first_peak_time = self.data[peaks[0]]["time"]
        self.background = self._get_bg(first_peak_time, bounds=bg_bounds)
        self._correct(self.background)

        signals = []
        peakends = peaks[1:]
        peakends.append(len(self.corrected_data))
        for i in range(len(peaks)):
            signal_data = copy.deepcopy(self.corrected_data[peaks[i]:peakends[i]])  # beginning and end of respective lists
            signal_name = "%s %i" % (self.name, i + 1)
            signals.append(Signal(signal_name, signal_data, self.name))  # create a Signal instance
        return signals  # list of signal objects

    def export_to_csv(self, filename: str, data_folder: str, oftype="original"):
        """
        Save the data to a csv file.

        :param filename:    what name to give the saved file
        :param data_folder: where to save the file
        :param oftype:      what type of data to save
                            Options:
                            # "original"    data as found in the time drive file
                            # "corrected"   data corrected for the background light
        """
        output = ""
        columns = []
        header = ([self.name, ""], [oftype, ""])
        if oftype == "original":
            data = get_xy(self.data)
        elif oftype == "corrected":
            data = get_xy(self.corrected_data)
        else:
            raise ValueError("Unexpected value for keyword argument 'oftype'. "
                             "Expected 'original' or 'corrected', got {}".format(oftype))
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
