"""
This script shows an example of data parsing using the tools in the LumParser package
"""

import os
import src.parsertools as pt

# Data paths
# input
td_in = os.path.join(os.getcwd(), "data", "test_input_data", "td")
parsed_in = os.path.join(os.getcwd(), "data", "test_input_data", "parsed")

# output
parsed_out = os.path.join(os.getcwd(), "data", "output_data", "parsed")
csv_out = os.path.join(os.getcwd(), "data", "output_data", "csv")

# expected output
parsed_exp = os.path.join(os.getcwd(), "data", "expected_put_data", "parsed")
csv_exp = os.path.join(os.getcwd(), "data", "expected_put_data", "csv")


# Parsing a single file
# Create a time drive data object from the first file in the input folder
td_files = pt.list_td_files(td_in)
test_file_01 = td_files[0]
td_data_01 = pt.TimeDriveData(test_file_01, td_in)



## First example: parsing one file
# make a dataset of the first file in the list
name01 = all_files[0]["name"]
directory01 = all_files[0]["directory"]
dataset01 = pt.TimeDriveData(name01, directory01)

# get all signals from the dataset
allsignals01 = dataset01.extract_signals(starting_point=0, threshold=0.3)
# save all the found signals to a csv file
pt.signals_to_csv(allsignals01, "Example01.csv", csv_folder)

## Second example: parsing all files at once and picking signals
parser = pt.Parser()
# Load all the time drive files into the parser
parser.import_ascii(import_folder)
# Adjust settings if desired
for num in ["03","04","08","11","12","15","16"]: # numbers of the files that should be changed
    parser.set_vars("Timedrive{}.td".format(num), "threshold", 0.2)
# Execute signal detection
for setname in parser.datasets:
    parser.update_signals(setname)
# Export all signals
print(parser.signals)
for name, dataset in parser.datasets.items():
    print(name)
    parser.export_csv(name, name.replace(".td", ".csv"), csv_folder, normal=True, integrate=True)
# Or pick signals to create a signalgroup and do further analysis
allsignals = []
for name, signallist in parser.signals.items():
    allsignals.append(signallist[0])    # pick first detected signal from each file
signalgroup = pt.SignalGroup(allsignals, "Example02.parsed")
# fit all signals to the luminescence model
for s in signalgroup:
    funct, popt, perr, p = s.fit_to("Exponential", init_str="10000, 1, .3")
# export the fits and the parameters that were found
signalgroup.export_csv("Fits_of_Example02.csv", csv_folder, normal=False, integrate=True, fit=True)
signalgroup.export_parameters("Fitparams_of_Example02.csv", csv_folder)

# save the files for later use
signalgroup.change_filename("test_output.parsed")
signalgroup.save(parsed_folder)
