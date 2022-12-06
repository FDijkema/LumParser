import os
import copy
import itertools
from src.parsertools import Signal


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
