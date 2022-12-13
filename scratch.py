
if __name__ == "__main__":
    data_folder = os.getcwd()
    for thisfile in parsertools.list_td_files(data_folder):
        fname = thisfile["name"]
        file_dataset = parsertools.TimeDriveData(fname, thisfile["directory"])
        ##########################################################################
        ### Put in custom variables in next line                               ###
        ### Starting point: first point where signal is expected [#datapoints] ###
        ### Threshold: minimum increase to detect signal [RLU]                 ###
        ### Bg bounds: what timepoints to include in background signal [s]     ###
        ###     "start_short": (0,10)                                          ###
        ###     "start_long": (0,100)                                          ###
        ###     "peak_short": (pk-10, pk)                                      ###
        ###     "peak_long": (pk-100, pk)                                      ###
        ###     custom: (left, right)                                          ###
        ##########################################################################
        file_signals = file_dataset.extract_signals(starting_point=0, threshold=0.3, bg_bounds="start_short")
        ##########################################################################
        if len(file_signals) > 0:
            parsertools.signals_to_csv(file_signals, fname.replace(".td", ".csv"), os.cwd())
        else:
            print("No signals found in %s" % fname)