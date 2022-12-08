"""
This script shows an example of data parsing using tools.py
"""

import os
import src.parsertools as pt

# location to store data
data_folder = os.path.join(os.getcwd(), "..", "data")
csv_folder = os.path.join(data_folder, "csv")
parsed_folder = os.path.join(data_folder, "parsed")
# location to load time drive files from
import_folder = os.path.join(data_folder, "td")

# retrieve a list of files
all_files = pt.list_files(import_folder)
print(all_files)


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
signalgroup = pt.Signalgroup(allsignals, "Example02.parsed")
# fit all signals to the luminescence model
for s_name in signalgroup.indexed:
    funct, popt, perr, p = signalgroup.fit_signal(s_name, "Luminescence model",
                                                  init_str="10000, 1, .3, .004")
# export the fits and the parameters that were found
signalgroup.export_fits("Fits_of_Example02.csv", csv_folder, "Luminescence model")
signalgroup.export_parameters("Fitparams_of_Example02.csv", csv_folder)

# save the files for later use
signalgroup.save(parsed_folder)