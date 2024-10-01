import pytest
import json
import sys
from fosslight_scanner.cli import main
#set_args


# def test_set_args_with_setting_file(tmp_path):
#     # given
#     setting_data = {
#         "mode": "test_mode",
#         "path": "/test/path",
#         "dep_argument": "dependency",
#         "output": "/test/output",
#         "format": "json",
#         "link": "http://example.com",
#         "db_url": "sqlite:///:memory:",
#         "timer": 30,
#         "raw": True,
#         "core": 4,
#         "no_correction": False,
#         "correct_fpath": "/correct/path",
#         "ui": False,
#         "exclude_path": ["/exclude/path"]
#     }

#     # 임시 setting 파일 생성
#     setting_file = tmp_path / "setting.json"
#     with open(setting_file, "w", encoding="utf-8") as f:
#         json.dump(setting_data, f)

#     # 초기 인자
#     mode = None
#     path = None
#     dep_argument = None
#     output = None
#     format = None
#     link = None
#     db_url = None
#     timer = None
#     raw = None
#     core = None
#     no_correction = None
#     correct_fpath = None
#     ui = None
#     exclude_path = None

#     # when
#     result = set_args(mode, path, dep_argument, output, format, link, db_url, timer,
#                       raw, core, no_correction, correct_fpath, ui, str(setting_file), exclude_path)

#     # then
#     expected_result = (
#         "test_mode", "/test/path", "dependency", "/test/output", "json",
#         "http://example.com", "sqlite:///:memory:", 30, True, 4, False, "/correct/path", False, ["/exclude/path"]
#     )

#     # Check if exclude_path is either the expected path or empty
#     assert result[:-1] == expected_result[:-1]  # Compare all items except `exclude_path`
#     assert result[-1] == expected_result[-1] or result[-1] == []  # `exclude_path` should match or be empty


def test_main_invalid_option(capsys):
    # given
    test_args = ["fosslight_scanner", "--invalid_option"]
    sys.argv = test_args

    # when
    with pytest.raises(SystemExit):  # 예상되는 SystemExit 처리
        main()

    # then
    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err  # 인식되지 않은 인자에 대한 에러 메시지 확인
