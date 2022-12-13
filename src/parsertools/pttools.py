"""
NAME
pttools

DESCRIPTION
Tools for parsing of luminescence time drive files, collection of functions to be used by other modules.

FUNCTIONS
get_xy
get_highest
list_td_files
make_header
signals_to_csv
"""

import os
import itertools


def get_xy(data: list):
    """
    Return list of time and list of values

    :param data: list of dicts containing (numerical) time: value datapoints. Format example:
        [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 2.0}, {"time": 0.2, "value": 3.0}]
    :return: two lists, one with timepoint and one with valuepoints. Not necessarily sorted by time, but with matching
        order
    """
    timelist = [datapoint["time"] for datapoint in data]
    valuelist = [datapoint["value"] for datapoint in data]
    return timelist, valuelist


def get_highest(data: list):
    """
    Return time and value of the datapoint with the highest value

    For normal signal this will be the time and value of the peak
    For integrated signal this will be the total integral

    :param data: list of dicts containing (numerical) time: value datapoints. Format example:
        [{"time": 0.0, "value": 1.0}, {"time": 0.1, "value": 5.0}, {"time": 0.2, "value": 3.0}]
    :return: time and value of the time point where the value is the highest
    """
    highest_value = 0.
    highest_time = 0.
    for point in data:
        if point["value"] >= highest_value:
            highest_value = point["value"]
            highest_time = point["time"]
    return highest_time, highest_value


def list_td_files(data_folder):
    """give list of dicts with name and directory of files as keys for all files ending in .td in directory"""
    folder = data_folder
    files = []
    for f in os.listdir(folder):
        if f.lower().endswith('.td'):
            directory = os.path.join(folder, f)
            files.append({"name": f, "directory": directory})
    return files


def make_header(signal, datatype="normal"):
    """
    Return list of header columns

    Headers give information about signal and function as titles for columns of
    data in a csv file
    """
    nameheader = [signal.name, ""]
    startheaders = ["Start at [s]:", "%.6g" % signal.start]
    infoheaders = {
        "normal": ["Peak height [RLU]:", "%.6g" % signal.peak_height],
        "integrated": ["Total integral [RLU*s]:", "%.6g" % signal.total_int],
        "fit": ["", ""]
    }
    typeheaders = {
        "normal": ["Time[s]", "Light signal[RLU]"],
        "integrated": ["Time[s]", "Integrated light signal[RLU]"],
        "fit": ["Time[s]", "Fit of integrated light signal[RLU]"]
    }
    header = [list(h) for h in zip(nameheader, startheaders, infoheaders[datatype], typeheaders[datatype])]
    return header


def signals_to_csv(signals, file_name, data_folder, normal=1, integrated=0, fit=0):
    """save the data of one or more signals to the assigned filename in csv format"""
    output = ""
    columns = []
    for signal in signals:
        if normal:
            x, y = get_xy(signal.signal_data)
            header = make_header(signal, datatype="normal")
            columns.extend([header[0] + x, header[1] + y])
        if integrated:
            x, y = get_xy(signal.integrated_data)
            header = make_header(signal, datatype="integrated")
            columns.extend([header[0] + x, header[1] + y])
        if fit:
            x, y = get_xy(signal.fit_data)
            header = make_header(signal, datatype="fit")
            columns.extend([header[0] + x, header[1] + y])
    rows = itertools.zip_longest(*columns)
    for line in rows:
        output_line = ",".join(map(str, line)) + "\n"
        output += output_line
    # save the string to the file
    outfile = open(os.path.join(data_folder, file_name), "w")
    outfile.write(output)
    outfile.close()
