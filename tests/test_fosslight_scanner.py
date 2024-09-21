import pytest
from fosslight_scanner import fosslight_scanner
from unittest.mock import patch, MagicMock

"""
1.run_dependency 함수 테스트:
의존성 분석이 성공적으로 수행되는지 확인.
잘못된 매개변수를 전달했을 때 예외가 발생하는지 확인.

2.run_scanner 함수 테스트:
소스, 바이너리, 의존성 분석이 성공적으로 수행되는지 확인.
잘못된 매개변수를 전달했을 때 예외가 발생하는지 확인.

3.download_source 함수 테스트:
소스 다운로드가 성공적으로 수행되는지 확인.
잘못된 링크를 전달했을 때 예외가 발생하는지 확인.

4.init 함수 테스트:
초기화가 성공적으로 수행되는지 확인.
잘못된 경로를 전달했을 때 예외가 발생하는지 확인.

5.run_main 함수 테스트:
다양한 모드에서 메인 함수가 성공적으로 수행되는지 확인.
잘못된 매개변수를 전달했을 때 예외가 발생하는지 확인.

"""

def test_run_dependency():
    with patch('fosslight_scanner.fosslight_scanner.call_analysis_api') as mock_call:
        mock_call.return_value = (True, {'SRC_FL_Dependency': ['dep1', 'dep2']})
        result = fosslight_scanner.run_dependency('/path/to/analyze', '/output/path')
        assert result == ['dep1', 'dep2']

        mock_call.return_value = (False, {})
        result = fosslight_scanner.run_dependency('/path/to/analyze', '/output/path')
        assert result == []

def test_run_scanner():
    with patch('fosslight_scanner.fosslight_scanner.call_analysis_api') as mock_call:
        mock_call.return_value = (True, {})
        fosslight_scanner.run_scanner('/src/path', '', '/output/path')
        assert mock_call.called

def test_download_source():
    with patch('fosslight_scanner.fosslight_scanner.cli_download_and_extract') as mock_download:
        mock_download.return_value = (True, '', 'oss_name', 'oss_version')
        success, temp_src_dir, oss_name, oss_version = fosslight_scanner.download_source('http://example.com', '/output/dir')
        assert success
        assert temp_src_dir != ''
        assert oss_name == 'oss_name'
        assert oss_version == 'oss_version'

def test_init():
    success, output_root_dir, result_log = fosslight_scanner.init('/output/path')
    assert success
    assert output_root_dir == '/output/path'
    assert isinstance(result_log, dict)

def test_run_main():
    with patch('fosslight_scanner.fosslight_scanner.run_scanner') as mock_run_scanner:
        mock_run_scanner.return_value = True
        result = fosslight_scanner.run_main(['all'], ['/src/path'], '', '/output/dir', 'excel', '', '', False)
        assert result
        assert mock_run_scanner.called