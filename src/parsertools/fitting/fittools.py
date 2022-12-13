"""
NAME
fittools

DESCRIPTION
Use this module to fit parsed luminescence data to a curve. Predefined curves are stored in the accompanying module.
functions.FUNCTIONS has the functions by function name and functions.INITS has the initial parameters needed for
fitting.

prepare_inits is mostly used by the LumParser interface to check if initital values don't contain any commands that will
break the program or your pc.
fit_data will fit a series of x, y points to a curve. If the name of the type of curve is in fitting.FUNCTIONS, it can
be retrieved by name, otherwise a formula, parameter list and initial guesses for these parameters need to be given.

FUNCTIONS
prepare_inits
fit_data
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import chisquare
from src.parsertools.fitting.functions import FUNCTIONS, make_func


def prepare_inits(initstring: str, **kwargs) -> list:
    """
    Calculate initial values for fit parameters and check if they are numerical

    Return a list of floats that is safe to use as inits for fit.
    Input for initstring should be a string of numbers separated by comma's.
    Letters are allowed if their value is specified in kwargs. (For example I for total integral and P for peak height)

    :param initstring: string of numbers separated by comma's
    :key someargument=somevalue: arguments string used in the initstring to be replaced with a numerical value
    :return: list of floats to be used as safe initial values for fit
    """
    if initstring == "":
        print("Please add initial estimates for the parameter values.")
        return
    rawinits = [r.strip() for r in initstring.split(",")]
    inits = []
    for num in rawinits:
        for arg_name, arg_value in kwargs.items():
            if str(arg_name) in num:
                num = num.replace(str(arg_name), str(arg_value))
        if "__" in num:
            num = ""
            print("Value not allowed")
        num = eval(num, {'__builtins__': {}})
        try:
            inits.append(float(num))
        except ValueError:
            print("Initial parameter %s is not valid" % str(num))
    return inits    # list of floats


def fit_data(x: list, y: list, fct: str, inits: list, func_str='', param_str='', start=0):
    """
    Fit x and y to given function, return fit information

    Two modes of use possible:
    1) put in a preset function name for fct. The name must be a key in fitting.FUNCTIONS
        if the name is a key in fitting.FUNCTIONS, a function object will be retrieved as its value
    2) fct = "Custom"
        In this case func_str and param_str must further describe the function

    :param x: list of numerical x values to fit
    :param y: list of numerical y values to fit
    :param fct: string that describes desired type of function. Should be a key in fitting.FUNCTIONS.
        If fct = "Custom", func_str and param_str must further describe the function
    :param inits: lists of floats (to prepare inits list from a string, use function prepare_inits)
    :param func_str: for fct='Custom', function formula should be put in here. Use x for variable and letters for other
        parameters. Python syntax is used for mathematical expressions.
    :param param_str: for fct='Custom', function parameters to optimise in the fit as a string separated by commas
        (example: 'param1, param2, param3') X should not be included.
    :param start: value of x from where to start fitting. Points before x are ignored.
        By default, all points are included
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
    if fct == "Custom":
        make_func(func_str, param_str)
    try:
        func = FUNCTIONS[fct]
    except KeyError:
        print("Function type not recognised.")

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
