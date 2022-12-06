import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare


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

    def _get_header(self, datatype="normal"):
        """
        Return list of header columns

        Headers give information about signal and function as titles for columns of
        data in a csv file
        """
        nameheader = [self.name, ""]
        startheaders = ["Start at [s]:", "%.6g" % self.start]
        infoheaders = {
            "normal": ["Peak height [RLU]:", "%.6g" % get_highest(self.signal_data)[1]],
            "integrated": ["Total integral [RLU*s]:", "%.6g" % get_highest(self.integrated_data)[1]]
        }
        typeheaders = {
            "normal": ["Time[s]", "Light signal[RLU]"],
            "integrated": ["Time[s]", "Integrated light signal[RLU]"]
        }
        header = [list(h) for h in
                  zip(nameheader, startheaders, infoheaders[datatype], typeheaders[datatype])]
        return header

    def get_info_string(self):
        """
        Return a string with most important signal features
        """
        return """Peak maximum:%.6g RLU at %.2f s
                  Total integral: %.6g""" % (self.peak_height, self.peak_time, self.total_int)

    def _prepare_inits(self, initstring):
        """
        Calculate initial values for fit parameters and check if they are numerical

        Return a list of floats that is safe to use as inits for fit.
        Input for initstring should be a string of numbers separated by comma's.
        Letters I and P are accepted to denote total integral and peak height.
        """
        if initstring == "":
            print("Please add initial estimates for the parameter values.")
            return
        rawinits = [r.strip() for r in initstring.split(",")]
        inits = []
        for num in rawinits:
            num = num.replace("P", str(self.peak_height))
            num = num.replace("I", str(self.total_int))
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
        xa, y = get_xy(self.integrated_data)
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


def get_xy(data_dictionary):
    """Return list of time and list of values"""
    timelist = [datapoint["time"] for datapoint in data_dictionary]
    valuelist = [datapoint["value"] for datapoint in data_dictionary]
    return timelist, valuelist

def get_highest(data_dictionary):
    """
    Return time and value of the highest value

    For normal signal this will be the time and value of the peak
    For integrated signal this will be the total integral
    """
    highest_value = 0.
    highest_time = 0.
    for point in data_dictionary:
        if point["value"] >= highest_value:
            highest_value = point["value"]
            highest_time = point["time"]
    return highest_time, highest_value
