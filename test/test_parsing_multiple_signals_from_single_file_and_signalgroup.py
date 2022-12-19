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


def test_creating_signalgroup_from_parsed_data_and_saving_should_create_parsed_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(parsed_out, "signalgroup_from_single_file.parsed"))
    # start test
    test_file_01 = td_files[0]["name"]
    td_data_01 = pt.TimeDriveData(test_file_01, os.path.join(td_in, test_file_01))
    signals = td_data_01.extract_signals(starting_point=0, threshold=0.3, bg_bounds=(0.0, 10.0))
    my_signalgroup = pt.SignalGroup(signals, "signalgroup_from_single_file.parsed", "Hello world!")
    my_signalgroup.save(parsed_out)
    outfile = os.path.join(parsed_out, "signalgroup_from_single_file.parsed")
    expected_outfile = os.path.join(parsed_exp, "signalgroup_from_single_file.parsed")
    assert filecmp.cmp(outfile, expected_outfile)


def test_loading_signalgroup_from_parsed_file_and_saving_again_should_recreate_input_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(parsed_out, "Example_data.parsed"))
    # start test
    my_signalgroup = pt.SignalGroup.loadfrom(os.path.join(parsed_in, "Example_data.parsed"))
    my_signalgroup.save(parsed_out)
    outfile = os.path.join(parsed_out, "Example_data.parsed")
    expected_outfile = os.path.join(parsed_exp, "Example_data.parsed")
    assert filecmp.cmp(outfile, expected_outfile)


def test_loading_parsed_file_and_exporting_signals_should_save_csv_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "signals_from_example_data.csv"))
    # start test
    my_signalgroup = pt.SignalGroup.loadfrom(os.path.join(parsed_in, "Example_data.parsed"))
    my_signalgroup.export_csv("signals_from_example_data.csv", csv_out, normal=True, integrate=True, fit=False)
    outfile = os.path.join(csv_out, "signals_from_example_data.csv")
    expected_outfile = os.path.join(csv_exp, "signals_from_example_data.csv")
    assert filecmp.cmp(outfile, expected_outfile)


def test_move_signal_up_or_down_should_adjust_order_of_signals_in_signalgroup():
    my_signalgroup = pt.SignalGroup.loadfrom(os.path.join(parsed_in, "Example_data.parsed"))
    my_signalgroup.move_up("Timedrive05.td 2")
    my_signalgroup.move_up_at(-2)
    my_signalgroup.move_down("Timedrive01.td 2")
    my_signalgroup.move_down_at(1)
    output = [signal.name for signal in my_signalgroup]
    expected_output = [
        "Timedrive02.td 2",
        "Timedrive05.td 2",
        "Timedrive01.td 2",
        "Timedrive03.td 2",
        "Timedrive04.td 2"
    ]
    assert output == expected_output


def test_slicing_signalgroup_should_output_list_of_signals_in_slice():
    my_signalgroup = pt.SignalGroup.loadfrom(os.path.join(parsed_in, "Example_data.parsed"))
    output = [signal.name for signal in my_signalgroup[1:4]]
    expected_output = [
        "Timedrive02.td 2",
        "Timedrive03.td 2",
        "Timedrive04.td 2"
    ]
    assert output == expected_output
