import pytest
from fosslight_scanner._get_input import get_input, ask_to_run, get_input_mode

def test_get_input(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "user_input")
    assert get_input("Enter something:") == "user_input"

    monkeypatch.setattr('builtins.input', lambda _: "")
    assert get_input("Enter something:", "default") == "default"

def test_ask_to_run(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "y")
    assert ask_to_run("Run?") == True

    monkeypatch.setattr('builtins.input', lambda _: "n")
    assert ask_to_run("Run?") == False

def test_get_input_mode(monkeypatch):
    # Mock user inputs for option 2
    inputs = iter(["2", "/path/to/analyze", "dep_args"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    src_path, dep_arguments, url_to_analyze = get_input_mode("/executed/path")
    assert src_path == "/path/to/analyze"
    assert dep_arguments == "dep_args"
    assert url_to_analyze == ""

    # Mock user inputs for option 1
    inputs = iter(["1", "http://example.com"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    src_path, dep_arguments, url_to_analyze = get_input_mode("/executed/path")
    assert src_path == ""
    assert dep_arguments == ""
    assert url_to_analyze == "http://example.com"