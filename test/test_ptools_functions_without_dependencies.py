import os
import src.parsertools as pt


def test_get_xy_should_convert_data_to_x_list_and_y_list():
    test_input = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 5.0},
        {"time": 0.2, "value": 4.0}
    ]
    expected_output = ([0.0, 0.1, 0.2], [1.0, 5.0, 4.0])
    output = pt.get_xy(test_input)
    assert output == expected_output


def test_get_highest_should_give_time_and_datapoint_with_highest_value():
    test_input = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 5.0},
        {"time": 0.2, "value": 4.0}
    ]
    expected_output = (0.1, 5.0)
    output = pt.get_highest(test_input)
    assert output == expected_output


def test_list_td_files_should_return_list_of_dicts_for_all_td_files_in_folder():
    td_in = os.path.join(os.getcwd(), "data", "test_input_data", "td")
    expected_output = [
        {"name": "Timedrive01.td", "path": os.path.join(td_in, "Timedrive01.td")},
        {"name": "Timedrive02.td", "path": os.path.join(td_in, "Timedrive02.td")},
        {"name": "Timedrive03.td", "path": os.path.join(td_in, "Timedrive03.td")},
        {"name": "Timedrive04.td", "path": os.path.join(td_in, "Timedrive04.td")},
        {"name": "Timedrive05.td", "path": os.path.join(td_in, "Timedrive05.td")}
    ]
    output = pt.list_td_files(td_in)
    assert output == expected_output
