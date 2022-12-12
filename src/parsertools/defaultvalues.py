import os

# saving location
default_import_folder = os.path.join(os.getcwd(), "data", "td")
default_parsed_folder = os.path.join(os.getcwd(), "data", "parsed")
default_csv_folder = os.path.join(os.getcwd(), "data", "csv")

# default parameters for finding signal start
default_starting_point = 0
default_threshold = 0.3
default_background_bounds = (0, 10)

