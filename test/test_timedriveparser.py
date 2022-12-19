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


def test_importing_multiple_td_files_should_create_datasets_in_parser():
    parser = pt.Parser()
    parser.import_ascii(td_in)
    output = parser.datasets.keys()
    expected_output = [
        "Timedrive01.td",
        "Timedrive02.td",
        "Timedrive03.td",
        "Timedrive04.td",
        "Timedrive05.td"
    ]
    assert output == expected_output


def test_exporting_a_time_drive_to_csv_through_a_parser_should_create_csv_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "single_time_drive_through_parser.csv"))
    # start test
    parser = pt.Parser()
    parser.import_ascii(td_in)
    parser.update_signals()
    parser.export_csv("Timedrive01.td", "single_time_drive_through_parser.csv", csv_out, normal=True, integrate=False)
    outfile = os.path.join(csv_out, "single_time_drive_through_parser.csv")
    expected_outfile = os.path.join(csv_exp, "single_time_drive_through_parser.csv")
    assert filecmp.cmp(outfile, expected_outfile)


def test_change_parse_settings_should_change_the_obtained_signals():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "signals_after_changing_settings.csv"))
    # start test
    parser = pt.Parser()
    parser.import_ascii(td_in)
    parser.set_vars("Timedrive02.td", "threshold", 3.0)
    parser.update_signals()
    parser.export_csv("Timedrive02.td", "signals_after_changing_settings.csv", csv_out, normal=True, integrate=False)
    outfile = os.path.join(csv_out, "signals_after_changing_settings.csv")
    expected_outfile = os.path.join(csv_exp, "signals_after_changing_settings.csv")
    assert filecmp.cmp(outfile, expected_outfile)


def test_create_mixed_dataset_should_create_signalgroup_with_signals_from_different_files():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(parsed_out, "a_group_of_mixed_signals.parsed"))
    # start test
    parser = pt.Parser()
    parser.import_ascii(td_in)
    parser.update_signals()
    selected_signals = [signals[1] for signals in parser.signals.values()]    # take second signal in each time drive
    signalgroup = pt.SignalGroup(selected_signals, "a_group_of_mixed_signals.parsed", notes="Hello world!")
    signalgroup.save(parsed_out)
    outfile = os.path.join(parsed_out, "a_group_of_mixed_signals.parsed")
    expected_outfile = os.path.join(parsed_exp, "Example_data.parsed")
    assert filecmp.cmp(outfile, expected_outfile)
