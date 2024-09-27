import pytest
from fosslight_scanner._get_input import get_input, ask_to_run, get_input_mode

def test_get_input(monkeypatch):
    # given
    ask_msg = "Please enter the path to analyze:"
    default_value = "default"
    
    # when
    # Mock input to return an empty string
    monkeypatch.setattr('builtins.input', lambda _: "")
    result_no_input = get_input(ask_msg, default_value)
    
    # Mock input to return "user_input"
    monkeypatch.setattr('builtins.input', lambda _: "user_input")
    result_with_input = get_input(ask_msg, "user_input")

    # then
    assert result_no_input == "default"
    assert result_with_input == "user_input"



@pytest.mark.parametrize("input_value, expected_output", [
    ("y", True),  # lowercase 'y' should return True
    ("Y", True),  # uppercase 'Y' should return True
    ("1", True),  # "1" should return True
])
def test_ask_to_run(input_value, expected_output):
    # given
    ask_msg = f"Do you want to proceed? (input: {input_value}): "

    # when
    result = input_value in ["y", "Y", "1"]

    # then
    assert result == expected_output


def test_get_input_mode(monkeypatch):
    # given
    executed_path = ""
    mode_list = ["all", "dep"]

    # Mock ask_to_run to return a predetermined input value
    monkeypatch.setattr('fosslight_scanner._get_input.ask_to_run', lambda _: "1")

    # Mock input to provide other necessary return values
    monkeypatch.setattr('builtins.input', lambda _: "https://example.com")

    # when
    src_path, dep_arguments, url_to_analyze = get_input_mode(executed_path, mode_list)

    # then
    assert src_path == ""
    assert dep_arguments == ""
    assert url_to_analyze == "https://example.com"
