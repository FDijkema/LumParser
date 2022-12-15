import os
import src.parsertools as pt


def test_get_xy():
    test_input = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 5.0},
        {"time": 0.2, "value": 4.0}
    ]
    expected_output = ([0.0, 0.1, 0.2], [1.0, 5.0, 4.0])
    output = pt.get_xy(test_input)
    assert output == expected_output


def test_get_highest():
    test_input = [
        {"time": 0.0, "value": 1.0},
        {"time": 0.1, "value": 5.0},
        {"time": 0.2, "value": 4.0}
    ]
    expected_output = (0.1, 5.0)
    output = pt.get_highest(test_input)
    assert output == expected_output


def test_list_td_files():
    td_in = os.path.join(os.getcwd(), "data", "test_input_data", "td")
    expected_output = [
        {"name": "Timedrive01", "directory": td_in},
        {"name": "Timedrive02", "directory": td_in},
        {"name": "Timedrive03", "directory": td_in},
        {"name": "Timedrive04", "directory": td_in},
        {"name": "Timedrive05", "directory": td_in}
    ]
    output = pt.list_td_files(td_in)
    assert output == expected_output
