import src.parsertools as pt


def test_fitting_a_single_signal_to_predefined_exponential_function_should_create_fit_data_list():
    signal_data = [
        {"time": 0.0, "value": 0.4},
        {"time": 1.0, "value": 100.0},
        {"time": 2.0, "value": 80.0},
        {"time": 3.0, "value": 70.0},
        {"time": 4.0, "value": 65}
    ]
    testsignal = pt.Signal("signal01", signal_data, "fake_file.td")
    testsignal.fit_to("Exponential", "100,1,.01")
    print(testsignal.fit_data)
    output = testsignal.fit_data
    expected_output = [
        {"time": 0.0, "value": 12.157501483095226},
        {"time": 1.0, "value": 100.18867621682197},
        {"time": 2.0, "value": 179.39191188368923},
        {"time": 3.0, "value": 250.65249154851924},
        {"time": 4.0, "value": 314.76692035198636}
    ]
    assert output == expected_output


def test_fitting_a_signal_to_a_custom_function_should_create_fit_data_list():
    signal_data = [
        {"time": 0.0, "value": 0.4},
        {"time": 1.0, "value": 100.0},
        {"time": 2.0, "value": 80.0},
        {"time": 3.0, "value": 70.0},
        {"time": 4.0, "value": 65}
    ]
    testsignal = pt.Signal("signal01", signal_data, "fake_file.td")
    testsignal.fit_to("Custom", "100,1,.01", func_str="a * (b - (exp(-k * x)))", param_str="a, b, k")
    output = testsignal.fit_data
    expected_output = [
        {"time": 0.0, "value": 12.157501768785286},
        {"time": 1.0, "value": 100.18867626403923},
        {"time": 2.0, "value": 179.39191182768370},
        {"time": 3.0, "value": 250.65249149981307},
        {"time": 4.0, "value": 314.76692039997300}
    ]
    assert output == expected_output
