from fosslight_scanner._parse_setting import parse_setting_json


def test_parse_setting_json_valid(capsys):
    # given
    data = {
        "mode": ["source", "binary"],
        "path": ["/path/to/scan"],
        "dep_argument": "--arg",
        "output": "output_directory",
        "format": "excel",
        "link": "https://example.com",
        "db_url": "***host/db",
        "timer": True,
        "raw": True,
        "core": 4,
        "no_correction": True,
        "correct_fpath": "sbom-info.yaml",
        "ui": False,
        "exclude": ["excluded/path"],
        "selected_source_scanner": "scanner",
        "source_write_json_file": True,
        "source_print_matched_text": False,
        "source_time_out": 300,
        "binary_simple": True
    }
    expected_output = (
        ["source", "binary"], ["/path/to/scan"], "--arg", "output_directory", "excel",
        "https://example.com", "***host/db", True, True, 4, True, "sbom-info.yaml",
        False, ["excluded/path"], "scanner", True, False, 300, True
    )

    # when
    result = parse_setting_json(data)

    # then
    assert result == expected_output

    # Check no warning is printed
    captured = capsys.readouterr()
    assert 'Ignoring some values with incorrect format in the setting file.' not in captured.out


def test_parse_setting_json_invalid(capsys):
    # given
    data = {
        "mode": "source",  # Should be list
        "path": "/path/to/scan",  # Should be list
        "core": "not_an_int",  # Should be int
        "timer": "not_a_bool",  # Should be bool
        "source_time_out": "not_an_int",  # Should be int
    }
    expected_output = (
        [], [], '', '', '', '', '', False, False, -1, False, '',
        False, [], '', False, False, 120, False
    )

    # when
    result = parse_setting_json(data)

    # then
    assert result == expected_output

    # Check warning is printed
    captured = capsys.readouterr()
    assert 'Ignoring some values with incorrect format in the setting file.' in captured.out
