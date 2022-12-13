"""
NAME
functions

DESCRIPTION
This module contains functions to fit to using the accompanying module fittools. Functions are defined as private
functions at the bottom of the file and are accessible through the dictionary FUNCTIONS. DEFAULT_INITS stores the
corresponding initial parameters that are needed to initiate the curve fitting.
Custom functions can be created on the fly using make_func, but this is mainly useful through the LumParsing user
interface.

FUNCTIONS
make_func

VARIABLES
FUNCTIONS (dict, function names as keys, functions as values)
DEFAULT_INITS (dict, function names as keys, lists of default initial parameters per function type as values)
"""

import numpy as np
from math import acos, asin, atan, atan2, pow
from numpy import ceil, cos, cosh, degrees, e, exp, fabs, floor, fmod, frexp, hypot, ldexp, \
    log, log10, modf, pi, radians, sin, sinh, sqrt, tan, tanh

FUNCTIONS = {"Custom": None}
DEFAULT_INITS = {"Custom": ""}


def make_func(mystring, myparams):
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

    func.name = "Custom"
    func.formula = mystring
    func.params = params
    func.bounds = (-np.inf, np.inf)
    FUNCTIONS["Custom"] = func


# MAY BE CHANGED #
# preset functions
def _exp_func(x, a, b, k):
    return a * (b - (np.exp(-k * x)))
_exp_func.name = "Exponential"
_exp_func.formula = "a * (b - (exp(-k * x)))"
_exp_func.params = ["a", "b", "k"]
_exp_func.bounds = (np.array([0, 0.5, 0]), np.array([np.inf, 1.5, 1]))
FUNCTIONS[_exp_func.name] = _exp_func
DEFAULT_INITS[_exp_func.name] = "I, 1, .005"


def _dexp_func(x, a, b, c, k1, k2):
    return a * (b - (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)))
_dexp_func.name = "Double exponential"
_dexp_func.formula = "a * (b - (c * exp(-k1 * x) + (1 - c) * exp(-k2 * x)))"
_dexp_func.params = ["a", "b", "c", "k1", "k2"]
_dexp_func.bounds = (-np.inf, np.inf)
FUNCTIONS[_dexp_func.name] = _dexp_func
DEFAULT_INITS[_dexp_func.name] = "I, 1, .3, .04, .0025"


def _dexp_func_2(x, a, b, c, k1):
    return a * (b - (c * np.exp(-k1 * x) + (1 - c) * np.exp(-0.032 * x)))
_dexp_func_2.name = "Double exponential, fixed k2"
_dexp_func_2.formula = "a * (b - (c * exp(-k1 * x) + (1 - c) * exp(-0.032 * x)))"
_dexp_func_2.params = ["a", "b", "c", "k1"]
_dexp_func_2.bounds = (-np.inf, np.inf)
FUNCTIONS[_dexp_func_2.name] = _dexp_func_2
DEFAULT_INITS[_dexp_func_2.name] = "I, 1, .3, .04"


def _dexp_baseline(x, a, c, k1, k2, d, b):
    return a - a * (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)) + d * x + b
_dexp_baseline.name = "Double with baseline"
_dexp_baseline.formula = "a - a * (c * np.exp(-k1 * x) + (1 - c) * np.exp(-k2 * x)) + a*d*x + a*b"
_dexp_baseline.params = ["a", "c", "k1", "k2", "d", "b"]
_dexp_baseline.bounds = (np.array([0, 0, 0, 0, -np.inf, -np.inf]), np.array([np.inf, np.inf, 0.1, 0.02, np.inf, np.inf]))
FUNCTIONS[_dexp_baseline.name] = _dexp_baseline
DEFAULT_INITS[_dexp_baseline.name] = "I, .3, .04, .0025, 1, 1"
