import os
import copy
import itertools
import numpy as np
from src.parsertools import Signal


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
        rawlines = input.read().splitlines()
        input.close()
        # get and store the information
        signals = []
        filename = rawlines[0]
        for i, line in enumerate(rawlines):
            if line.startswith("NOTES"):
                start_notes = i
            elif line.startswith("SIGNAL"):
                start_signal = i
            elif line.startswith("DATA"):
                start_data = i
            elif line.startswith("END"):  # create a new signal
                end = i
                notes = "\n".join(rawlines[start_notes+1:start_signal])
                s_info = {line.split("=")[0]:line.split("=")[1] for line in rawlines[start_signal+1, start_data]}
                try:
                    s_info[name] = float(value)    # convert numbers to floats
                except ValueError:
                    pass
                data = [{"time": float(line.split(",")[0]), "value": float(line.split(",")[1])} for line in rawlines[start_data+1, end]]
                signal = Signal(s_info["name"], data, s_info["filename"])
                for name in s_info:
                    setattr(signal, name, s_info[name])
                signals.append(signal)
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
        funct, popt, perr, p = s.fit_data(fct, init_str=init_str, func_str=func_str,
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
