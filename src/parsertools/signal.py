from src.parsertools.tools import get_xy, get_highest
from src.parsertools.fitting.fittools import prepare_inits, fit_data


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
                            the function formula and list of parameter names,
                            respectively.
    """
    def __init__(self, name, data, filename):
        """
        Signal object contains the data for the duration of that signal

        Time is reset to 0 at signal start.

        Parameters:
        name (str)      signal name, used to identify
        data (dict) {time1: value1,
                    time2: value2}
                        dictionary containing the signal data in time, value pairs.
        filename (str)  original filename of the time drive the signal was taken from
        integrated (Boolean)
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
        self.peak_time, self.peak_height = get_highest(self.signal_data)
        self.filename = filename
        self.integrated_data = self._integrate()
        self.total_int = get_highest(self.integrated_data)[1]
        self.fit_data = {}

    def _integrate(self):
        """Integrate the signal and return a new signal object with that data"""
        # initialize parameters
        int_data = []
        prev_time = 0.
        prev_val = 0.
        # calculate the integrated data
        for point in self.signal_data:
            value = point["value"]
            cur_time = point["time"]
            cur_val = prev_val + (cur_time - prev_time) * value
            int_data.append({"time": cur_time, "value": cur_val})
            # update
            prev_time = cur_time
            prev_val = cur_val
        return int_data

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
        print("Fitting: {}".format(self.name))
        x, y = get_xy(self.integrated_data)
        inits = prepare_inits(init_str, P=self.peak_height, I=self.total_int)
        func, popt, perr, p = fit_data(x, y, start=self.peak_time, fct=fct, inits=inits, func_str=func_str, param_str=param_str)
        if fct == "Double exponential":
            poptlist = list(popt)
            if poptlist[4] > poptlist[2]:  # k2 > k1: always put biggest first
                poptlist[1:5] = poptlist[3:5] + poptlist[1:3]  # swap 1 and 2
            outparams = dict(zip(func.params, poptlist))
        else:
            outparams = dict(zip(func.params, list(popt)))
        outparams["p"] = p
        for P in outparams:
            setattr(self, P, outparams[P])
        self.fit_data = []
        for time, value in zip(x, list([func(time, *popt) for time in x])):
            self.fit_data.append({"time": float(time), "value": float(value)})
        return func, popt, perr, p
