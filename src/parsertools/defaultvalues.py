import os

# saving location
default_import_folder = os.path.join(os.getcwd(), os.pardir, os.pardir, "data", "td")
default_parsed_folder = os.path.join(os.getcwd(), os.pardir, os.pardir, "data", "parsed")
default_csv_folder = os.path.join(os.getcwd(), os.pardir, os.pardir, "data", "csv")
default_data_folder = os.path.join(os.getcwd(), os.pardir, os.pardir, "data")

# default parameters for finding signal start
default_starting_point = 0
default_threshold = 0.3
default_background_bounds = (0, 10)

