import os
import filecmp
import src.parsertools as pt

# Data paths
# input
td_in = os.path.join(os.getcwd(), "data", "test_input_data", "td")
parsed_in = os.path.join(os.getcwd(), "data", "test_input_data", "parsed")

# output
parsed_out = os.path.join(os.getcwd(), "data", "output_data", "parsed")
csv_out = os.path.join(os.getcwd(), "data", "output_data", "csv")

# expected output
parsed_exp = os.path.join(os.getcwd(), "data", "expected_output_data", "parsed")
csv_exp = os.path.join(os.getcwd(), "data", "expected_output_data", "csv")


# input files to use
td_files = pt.list_td_files(td_in)


def test_create_mixed_dataset_fit_and_save_parameters_should_create_correct_csv_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "parameters_from_fit.csv"))
    # start test
    parser = pt.Parser()
    parser.import_ascii(td_in)
    parser.update_all_signals()
    selected_signals = [signals[1] for signals in parser.signals.values()]    # take second signal in each time drive
    signalgroup = pt.SignalGroup(selected_signals, "a_group_of_mixed_signals.parsed", notes="Hello world!")
    for signal in signalgroup:
        fit_info = signal.fit_to(fct="Exponential", init_str="10000, 1, 0.005")  # fitting
    signalgroup.export_parameters("parameters_from_fit.csv", csv_out)
    outfile = os.path.join(csv_out, "parameters_from_fit.csv")
    expected_outfile = os.path.join(csv_exp, "parameters_from_fit.csv")
    assert filecmp.cmp(outfile, expected_outfile)
