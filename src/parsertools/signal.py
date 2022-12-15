"""
NAME
signal

DESCRIPTION
Module describing the Signal object. A signal is a part of a time drive starting from where a peak of light occurs,
ending either at the end of the file or at the next peak. The data, integrated data and potential fits of a single
signal are stored as attributes.

CLASSES
Signal
"""

from src.parsertools.pttools import get_xy, get_highest
from src.parsertools.fitting.fittools import prepare_inits, fit_data


class Signal:
    """
    A signal object contains the data and information for one light signal found in a time drive.

    ATTRIBUTES
    :ivar start:            Starting time of the signal in the original time drive file
    :ivar name:             Name of the signal. Automatically generated, can be altered
                            by user.
    :ivar filename:         Name of the original time drive file the signal was taken from.
    :ivar peak_height:      The highest value found in the signal_data
                            (should be the initial peak at the start of the signal)
    :ivar peak_time:        The time point at which the highest value occurs
    :ivar total_int:        Total area under the signal curve, equivalent to the value at the end of the
                            integrated signal and the highest value of the integrated signal data.
    :ivar signal_data:      List of dictionaries containing (numerical) time: value datapoints.
                            Background corrected data with starting time set to t=0, from the time drive that the signal
                            was taken from.
                            Format example:
                            [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 5.0}, {"time": 0.2, "value": 3.0}]
    :ivar integrated_data:  List of dictionaries containing (numerical) time: value datapoints.
                            Integrated signal data (from signal_data).
                            Format example:
                            [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 6.0}, {"time": 0.2, "value": 9.0}]
    :ivar fit_data:         Initially, an empty dictionary. Once the integrated  signal has been fitted to a curve, the
                            fitted curve will be stored here as a list of dictionaries containing (numerical)
                            time: value datapoints.
                            Format example:
                            [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 6.0}, {"time": 0.2, "value": 10.0}]

    METHODS
    fit_to                  Fits the integrated signal data to a curve.
    """
    def __init__(self, name: str, data: list, filename: str):
        """
        Construct a signal object.

        Time is reset to 0 at signal start.

        :param name:        Name to use for the signal, to identify it by.
        :param data:        List of dictionaries containing (numerical) time: value datapoints.
                            Background corrected data, from the time drive that the signal
                            was taken from.
                            Format example:
                            [{"time": 10.0, "value": 1.0}, {"time": 10.1, "value": 5.0}, {"time": 10.2, "value": 3.0}]
        :param filename:    Original filename of the time drive the signal was taken from.
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

    def __str__(self):
        x, y = get_xy(self.signal_data)
        lines = ["   ".join(rowlist) for rowlist in zip(x, y)]
        description = "Signal object " + self.name + " from " + self.filename + "\n" \
                      + "Time[s]    Value[RLU]\n" \
                      + "\n".join(lines)
        return description

    def __repr__(self):
        return "Signal({}, {}, {})".format(self.name, self.signal_data, self.filename)

    def _integrate(self):
        """Integrate the signal and return integrated data as a list of data point dictionaries"""
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
        return int_data    # Format example: [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 6.0}]

    def fit_to(self, fct: str, init_str: str, func_str='', param_str=''):
        """
        Take the signal data and fit to given function, return fit information.

        Two modes of use possible:
        1) put in a preset function name for fct. This function must be a key in fitting.FUNCTIONS, written in
            the module fitting.functions.
        2) fct = "Custom"
            In this case func_str and param_str must further describe the function
            func_str should be a string stating the  mathematical expression
                for the function
            param_str should give the parameters to optimise in the fit in this
                format: 'param1, param2, param3'. X should not be included.
            The function can only contain mathematical expressions and parameters
                that are described in the parameter string.

        :param fct: String with the name of the desired type of function. This function must be a key in
                    fitting.FUNCTIONS, written in the module fitting.functions.
        :param init_str: string of initial values for parameters. String of numbers separated by comma's.
                    Letters I and P are accepted to denote total integral and peak height.
        :param func_str: for fct='Custom', function formula should be put in here. The formula may only contain
                    mathematical expressions and parameters that are described in the parameter string.
        :param param_str: for fct='Custom', function parameters should be put in here
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
