import os
import copy
from numbers import Number
from src.parsertools.signal import Signal
from src.parsertools.pttools import signals_to_csv, get_xy


class SignalGroup:
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
        self._signals = {}   # dict of signals by signal name
        self._indexed = []   # list of signal names (by index)
        self.append(signals)   # this way signals are added both by name and index
        self.notes = notes    # notes are for user
        self.filename = filename    # filename is used for saving
        self._currentindex = 0

    @classmethod
    def loadfrom(cls, directory):
        """Load signalgroup from file. Returns itself. Alternative init method"""
        # read the file
        input = open(directory)
        rawlines = input.read().splitlines()
        input.close()
        # get and store the information
        signals = []
        filename = rawlines[0]
        notes_written = False
        for i, line in enumerate(rawlines):
            if line.startswith("NOTES"):
                start_notes = i
            elif line.startswith("SIGNAL"):
                start_signal = i
            elif line.startswith("DATA"):
                start_data = i
            elif line.startswith("END"):  # create a new signal
                end = i
                if not notes_written:
                    notes = "\n".join(rawlines[start_notes+1:start_signal])
                    notes_written = True
                s_info = {line.split("=")[0]:line.split("=")[1] for line in rawlines[start_signal+1: start_data]}
                for name, value in s_info.items():
                    try:
                        s_info[name] = float(value)    # convert numbers to floats
                    except ValueError:
                        pass
                data = [{"time": float(line.split(",")[0]), "value": float(line.split(",")[1])} for line in rawlines[start_data+1: end]]
                signal = Signal(s_info["name"], data, s_info["filename"])
                for name in s_info:
                    setattr(signal, name, s_info[name])
                signals.append(signal)
        signalgroup = SignalGroup(signals, filename, notes)
        return signalgroup

    def __iter__(self):
        self._currentindex=0
        return self

    def __next__(self):
        if self._currentindex < len(self._indexed):
            current_signal = self.get_at(self._currentindex)
            self._currentindex += 1
            return current_signal
        raise StopIteration

    def __len__(self):
        return len(self._indexed)

    def __str__(self):
        signal_str = "\n".join([signal.name for signal in self.get_all()])
        description = "Signalgroup " + self.filename + "\n\n" + signal_str + "\n"
        return description

    def __getitem__(self, key):
        if isinstance(key, slice):
            indices = range(len(self._signals))[key]
            return self.get_at(indices, seq=True)
        elif isinstance(key, int):
            index = key
            return self.get_at(index, seq=False)
        elif isinstance(key, str):
            return self.get(key, seq=False)
        else:
            raise TypeError("Expected slice, int or str as index, got {}".format(type(key)))

    def __contains__(self, key):
        if isinstance(key, str):
            if key in self._signals:
                return True
            else: return False
        else:
            raise TypeError("Expected name of a signal of type str, got {}".format(type(key)))

    def __delitem__(self, key):
        if isinstance(key, slice):
            indices = range(len(self._signals))[key]
            return self.remove_at(key, seq=False)
        elif isinstance(key, int):
            index = key
            return self.remove_at(index, seq=False)
        elif isinstance(key, str):
            return self.remove(key, seq=False)
        else:
            raise TypeError("Expected slice, int or str as index, got {}".format(type(key)))

    def append(self, signals):
        """Append signals to collection, both by name and index"""
        for signal in signals:
            new_signal = copy.copy(signal)
            self._signals[new_signal.name] = new_signal
            self._indexed.append(new_signal.name)

    def rename(self, old_name, new_name):
        """Rename the signal."""
        # the indexed list
        index = self._indexed.index(old_name)
        del (self._indexed[index])
        self._indexed.insert(index, new_name)
        # the dict of signal objects
        self._signals[new_name] = self._signals[old_name]
        del (self._signals[old_name])
        # the signal attribute
        self._signals[new_name].name = new_name

    def remove(self, signal_name, seq=False):
        """
        Remove signals from group by name.

        To remove multiple signals at once, input a list of names for signal_name
        instead of a single string and set seq=True.
        """
        if seq:
            for s_name in signal_name:
                del (self._signals[s_name])
                self._indexed.remove(s_name)
        else:
            del (self._signals[signal_name])
            self._indexed.remove(signal_name)

    def remove_at(self, index, seq=False):
        """
        Remove signals from group by index.

        To remove multiple signals at once, input a list of indices for index
        instead of a single number and set seq=True.
        """
        if seq:
            for i in index:
                del (self._signals[self._indexed[i]])
                del (self._indexed[i])
        else:
            del (self._signals[self._indexed[index]])
            del (self._indexed[index])

    def get(self, signal_name, seq=False):
        """
        Return the signal object when given the name.

        To retrieve multiple signals, input a list of names and set seq=True.
        """
        if seq:
            signals_list = []
            for s_name in signal_name:
                signals_list.append(self._signals[s_name])
            return signals_list
        else:
            return self._signals[signal_name]

    def get_at(self, index, seq=False):
        """
        Return signal object for index.

        To retrieve multiple signal objects, input a list of indices and set
        seq=True.
        """
        if seq:
            signals_list = []
            for i in index:
                signals_list.append(self._signals[self._indexed[i]])
            return signals_list
        else:
            return self._signals[self._indexed[index]]

    def index(self, signal_name, seq=False):
        """Return index for name or list of indices for list of names."""
        if seq:
            indices = []
            for s_name in signal_name:
                indices.append(self._indexed.index(s_name))
            return indices
        else:
            return self._indexed.index(signal_name)

    def get_all(self):
        """Return a list of all signal objects in the group."""
        signals_list = []
        for s_name in self._indexed:
            signals_list.append(self._signals[s_name])
        return signals_list

    def move_up(self, signal_names):
        """Move the given signals up in the indexed list by 1"""
        for s_name in signal_names:
            index = self._indexed.index(s_name)
            self._indexed.insert(index - 1, self._indexed.pop(index))

    def move_down(self, signal_names):
        """Move the given signals down in the indexed list by 1"""
        for s_name in signal_names:
            index = self._indexed.index(s_name)
            self._indexed.insert(index + 1, self._indexed.pop(index))

    def move_up_at(self, indices):
        """Move the signals at the given indices up in the indexed list by 1"""
        for index in indices:
            self._indexed.insert(index - 1, self._indexed.pop(index))

    def move_down_at(self, indices):
        """Move the signals at the given indices down in the indexed list by 1"""
        for index in indices:
            self._indexed.insert(index + 1, self._indexed.pop(index))

    def change_filename(self, new_name):
        """Set the filename of the signalgroup to new_name"""
        self.filename = new_name
        if self.filename.endswith(".parsed"):
            pass
        else:
            self.filename += ".parsed"

    def save(self, data_directory):
        """Save the signalgroup to the given directory, by its stored filename"""
        output = str(self.filename) + "\n"
        output += "NOTES\n" + self.notes + "\n"
        for s_name in self._indexed:
            signal = self._signals[s_name]
            output += "SIGNAL\n"
            for var in vars(signal):
                vars_to_skip = ["signal_data", "integrated_data", "fit_data"]
                if var not in vars_to_skip:
                    output += "%s=%s\n" % (var, str(vars(signal)[var]))
            output += "DATA\n"
            x, y = get_xy(signal.signal_data)
            rows = zip(x, y)
            for line in rows:
                output_line = ",".join(map(str, line)) + "\n"
                output += output_line
            output += "END\n"
        # write output to file
        outfile = open(os.path.join(data_directory, self.filename), "w")
        outfile.write(output)
        outfile.close()

    def export_csv(self, exportname, data_folder, normal=True, integrate=False, fit=False):
        """
        Export the data of the signals in the signalgroup to a csv file

        Either the normal data or the integrated data of all signals can be saved,
        or both.

        Parameters:
        :param exportname: string, name of the file to save to, should end in .csv
        :param data_folder: string, location to save the file
        :param normal: True or False, should normal data be saved?
        :param integrate: True or False, should integrated data be saved?
        :param fit: True or False, should fitted data be saved?
        normal and integrate cannot both be false. Either normal or integrated
            must be saved.
        """
        signals_to_csv(self._signals.values(), exportname, data_folder, normal=normal, integrated=integrate, fit=fit)

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
        # collect numeric variables for each signal
        numvars = []
        for var in vars(some_signal):  # create the title row
            if isinstance(vars(some_signal)[var], Number):
                numvars.append(var)
        for var in numvars:
            output += str(var) + ","
        output += "\n"
        for s_name in self._indexed:  # row of values for each signal
            signal = self._signals[s_name]
            line = signal.name + ", " + signal.filename + ","
            for var in numvars:
                line += str(vars(signal)[var]) + ","
            output += line + "\n"
        # save the string to the file
        outfile = open(os.path.join(data_folder, exportname), "w")
        outfile.write(output)
        outfile.close()
