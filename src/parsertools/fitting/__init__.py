"""
NAME
fitting

DESCRIPTION
This package is part of the parsertools toolset to process luminescence time drives. It provides functions for fitting
signals to curves. The variables FUNCTIONS contains predefined types of curves that the data can be fitted to.
Additional types of curves can be defined using make_func. The corresponding initial parameter guesses are stored in
DEFAULT_INITS.
When used as a package for scripting, using fit_data directly is the easiest way. prepare_inits and make_func are used
by the interface.

FUNCTIONS
prepare_inits
fit_data
make_func

VARIABLES
FUNCTIONS (dict, function names as keys, functions as values)
DEFAULT_INITS (dict, function names as keys, lists of default initial parameters per function type as values)
"""


from src.parsertools.fitting.fittools import prepare_inits, fit_data
from src.parsertools.fitting.functions import make_func, FUNCTIONS, DEFAULT_INITS
