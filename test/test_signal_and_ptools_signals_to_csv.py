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

# make a very simple signal for testing
signal_data = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 5.0},
        {"time": 0.2, "value": 4.0}
    ]
testsignal = pt.Signal("signal01", signal_data, "fake_file.td")


def test_calling_str_on_signal_should_print_string_representation_of_signal():
    expected_output = "Signal object signal01 from fake_file.td\n" \
                      "Time[s]    Value[RLU]\n" \
                      "0.0       1.0\n" \
                      "0.1       5.0\n" \
                      "0.2       4.0"
    assert str(testsignal) == expected_output


def test_integrated_data_should_contain_correctly_integrated_data():
    expected_output = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 6.0},
        {"time": 0.2, "value": 10.0}
    ]
    assert testsignal.integrated_data == expected_output


def test_signals_to_csv_should_create_csv_file_with_signal_info():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "a_very_simple_signal.csv"))
    # start test
    pt.signals_to_csv([testsignal], "a_very_simple_signal.csv", csv_out, normal=True, integrated=True)
    outfile = os.path.join(csv_out, "a_very_simple_signal.csv")
    expected_outfile = os.path.join(csv_exp, "a_very_simple_signal.csv")
    assert filecmp.cmp(outfile, expected_outfile, shallow=False)
