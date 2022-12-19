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


def test_extracting_time_drive_data_from_a_single_file_and_exporting_to_csv_should_create_correct_csv_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "a_single_time_drive.csv"))
    # start test
    test_file_01 = td_files[0]["name"]
    td_data_01 = pt.TimeDriveData(test_file_01, os.path.join(td_in, test_file_01))
    td_data_01.export_to_csv("a_single_time_drive.csv", csv_out, oftype="original")
    outfile = os.path.join(csv_out, "a_single_time_drive.csv")
    expected_outfile = os.path.join(csv_exp, "a_single_time_drive.csv")
    assert filecmp.cmp(outfile, expected_outfile, shallow=False)


def test_after_extracting_signals_timedrivedata_object_should_contain_list_of_signals_with_correct_properties():
    test_file_01 = td_files[0]["name"]
    td_data_01 = pt.TimeDriveData(test_file_01, os.path.join(td_in, test_file_01))
    signals = td_data_01.extract_signals(starting_point=0, threshold=0.3, bg_bounds=(0.0, 10.0))
    output = (signals[1].name, signals[1].peak_height, signals[1].total_int)
    expected_output = ("Timedrive01.td 2", 3.37204, 874.894)
    assert output == expected_output


def test_extracting_signals_from_td_and_exporting_them_to_csv_should_create_csv_file():
    # remove outfile to prevent false positive outcome when not saving
    os.remove(os.path.join(csv_out, "signals_from_td01.csv"))
    # start test
    test_file_01 = td_files[0]["name"]
    td_data_01 = pt.TimeDriveData(test_file_01, os.path.join(td_in, test_file_01))
    signals = td_data_01.extract_signals(starting_point=0, threshold=0.3, bg_bounds=(0.0, 10.0))
    pt.signals_to_csv(signals, "signals_from_td01.csv", csv_out, normal=True, integrated=True, fit=False)
    outfile = os.path.join(csv_out, "signals_from_td01.csv")
    expected_outfile = os.path.join(csv_exp, "signals_from_td01.csv")
    assert filecmp.cmp(outfile, expected_outfile, shallow=False)
