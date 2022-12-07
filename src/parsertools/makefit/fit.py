import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from src.parsertools import FUNCTIONS, make_func


def prepare_inits(initstring, **kwargs):
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
        for arg_name, arg_value in kwargs.items():
            if str(arg_name) in num:
                num = num.replace(str(arg_name), arg_value)
        if "__" in num:
            num = ""
            print("Value not allowed")
        num = eval(num, {'__builtins__': {}})
        try:
            inits.append(float(num))
        except ValueError:
            print("Initial parameter %s is not valid" % str(num))
    return inits


def fit_data(x, y, start=0, fct="Exponential", inits=(), func_str='', param_str=''):
    """
    Fit x and y and fit to given function, return fit information

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

    # create function from user input if desired, otherwise use preset function
    if fct in FUNCTIONS:
        pass
    elif fct == "Other":
        make_func(func_str, param_str)
    else:
        print("function type not recognised")
        return
    func = FUNCTIONS[fct]

    # check initial values
    if len(inits) != len(func.params):
        print('Number of parameters does not match number of initial values.')
        return
    inits = np.array(inits, dtype=np.float64)

    # fit signal
    # only take signal after peak, easier to fit
    x = [item for item in x if item >= start]
    y = y[-len(x):]
    x = np.array(x, dtype=np.float64)  # transform data to numpy array
    y = np.array(y, dtype=np.float64)
    with np.errstate(over="ignore"):
        try:
            popt, pcov = curve_fit(func, x, y, inits, bounds=func.bounds)
        except RuntimeError as RE:
            print("Signal can't be fitted.")
            print(RE)
            return
    perr = np.sqrt(np.abs(np.diag(pcov)))
    chisq, p = chisquare(y, f_exp=func(x, *popt))
    return func, popt, perr, p
