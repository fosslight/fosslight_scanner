import pytest
from fosslight_scanner._help import print_help_msg

def test_print_help_msg(mocker, monkeypatch):
    mock_print_help_msg = mocker.patch('fosslight_util.help.PrintHelpMsg')
    mock_print_help_msg_instance = mock_print_help_msg.return_value
    mock_print_help_msg_instance.print_help_msg = mocker.Mock()
    monkeypatch.setattr('sys.exit', lambda: None)
    print_help_msg()
    mock_print_help_msg.return_value.print_help_msg.assert_called_once_with(True)
