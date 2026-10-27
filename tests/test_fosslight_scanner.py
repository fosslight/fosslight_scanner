import os
import shutil
import openpyxl
import pytest
from pathlib import Path
from fosslight_scanner.fosslight_scanner import (
    run_scanner, download_source, init, run_main, run_dependency, remove_tree
)
from fosslight_scanner import fosslight_scanner as scanner
from fosslight_util.oss_item import FileItem, ScannerItem
from fosslight_util.constant import FOSSLIGHT_BINARY, FOSSLIGHT_DEPENDENCY, FOSSLIGHT_SOURCE, SHEET_NAME_FOR_SCANNER

_SRC = SHEET_NAME_FOR_SCANNER[FOSSLIGHT_SOURCE]       # 'SRC_FL_Source'
_BIN = SHEET_NAME_FOR_SCANNER[FOSSLIGHT_BINARY]       # 'BIN_FL_Binary'
_DEP = SHEET_NAME_FOR_SCANNER[FOSSLIGHT_DEPENDENCY]   # 'DEP_FL_Dependency'
_TESTS_DIR = Path(__file__).resolve().parent
_SCAN_PROJECT_DIR = _TESTS_DIR / "fixtures" / "scan_project"
_MIN_DATA_ROWS = 2

SHEET_CHECK_PARAMS = [
    pytest.param(["all"],        [_SRC, _BIN, _DEP], id="all"),
    pytest.param(["source"],     [_SRC],             id="source"),
    pytest.param(["binary"],     [_BIN],             id="binary"),
    pytest.param(["dependency"], [_DEP],             id="dependency"),
]


def _prepare_scan_fixture(tmp_path: Path) -> Path:
    scan_path = tmp_path / "scan_project"
    shutil.copytree(_SCAN_PROJECT_DIR, scan_path)
    return scan_path


def _get_sheet_names(xlsx_path: str) -> list:
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    names = wb.sheetnames
    wb.close()
    return names


def _get_sheet_row_count(xlsx_path: str, sheet_name: str) -> int:
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    row_count = ws.max_row or 0
    wb.close()
    return row_count


def test_run_dependency(tmp_path):
    # given
    path_to_analyze = tmp_path / "test_project"
    output_file_with_path = tmp_path / "output_file"
    params = "-m 'npm' -a 'activate_cmd' -d 'deactivate_cmd' -c 'custom_dir' -n 'app_name' -t 'token_value'"
    path_to_exclude = ["node_modules"]

    # Create the directory to analyze
    path_to_analyze.mkdir(parents=True, exist_ok=True)

    # when
    _, result = run_dependency(str(path_to_analyze), str(output_file_with_path), params, path_to_exclude)

    # then
    # Check that result is an instance of ScannerItem
    assert isinstance(result, ScannerItem), "Result should be an instance of ScannerItem."


def test_run_dependency_passes_through_scanner_result(tmp_path, monkeypatch):
    item = ScannerItem("fosslight_dependency", "")
    monkeypatch.setattr(scanner, "run_dependency_scanner", lambda *args, **kwargs: (True, item))

    assert run_dependency(str(tmp_path), str(tmp_path / "dep.xlsx")) == (True, item)


def test_run_dependency_returns_false_when_scanner_raises(tmp_path, monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("dependency scanner crashed")
    monkeypatch.setattr(scanner, "run_dependency_scanner", raise_error)

    success, result = run_dependency(str(tmp_path), str(tmp_path / "dep.xlsx"))

    assert success is False
    assert isinstance(result, ScannerItem)


def test_run_scanner(tmp_path):
    # given
    src_path = tmp_path / "test_src"
    output_path = tmp_path / "output"
    dep_arguments = ""
    output_file = ['test_output']
    output_extension = [".yaml"]

    # Create necessary directories and files for the test
    src_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create a dummy source file in `src_path` to be scanned
    test_file = src_path / "test_file.py"
    test_file.write_text("# This is a test file\nprint('Hello, World!')")

    # when
    run_scanner(
        src_path=str(src_path),
        dep_arguments=dep_arguments,
        output_path=str(output_path),
        keep_raw_data=True,
        run_src=True,
        run_bin=False,
        run_dep=False,
        remove_src_data=False,
        result_log={},
        output_files=output_file,
        output_extensions=output_extension,
        num_cores=1,
        path_to_exclude=[]
    )

    # then
    # Check if `src_path` and `output_path` still exist
    assert src_path.is_dir(), "Source path should still exist."
    assert output_path.is_dir(), "Output path should still exist."


@pytest.mark.parametrize("format_name, extension", [
    ("spdx-json", ".json"), ("spdx-yaml", ".yaml"), ("spdx-xml", ".xml"), ("spdx-tag", ".tag"),
])
@pytest.mark.parametrize("output_order", ["spdx-only", "excel-first", "spdx-first"])
def test_spdx_source_keeps_files_and_matched_text(tmp_path, monkeypatch, format_name, extension, output_order):
    from fosslight_source import cli as source_cli
    from fosslight_source._license_matched import MatchedLicense
    from fosslight_source._scan_item import SourceItem
    from spdx_tools.spdx.parser.parse_anything import parse_file
    from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    source_items = []
    for filename in ("one.c", "two.c"):
        relative_path = f"src/{filename}"
        (project / relative_path).write_text("/* Example license terms. */\n", encoding="utf-8")
        item = SourceItem(relative_path)
        item.licenses = ["Example-License"]
        item.checksum = "a" * 40
        source_items.append(item)
    matched_license = MatchedLicense("Example-License", "", "Example license terms.", "src/one.c")
    matched_license.set_files("src/two.c")
    requested_matched_text = []

    def run_scancode(*args, **kwargs):
        requested_matched_text.append(args[5])
        licenses = {"example": matched_license} if args[5] else {}
        return True, "True", source_items, licenses

    monkeypatch.setattr(source_cli, "run_scan", run_scancode)
    monkeypatch.setattr(scanner, "fosslight_source_installed", True)
    monkeypatch.setattr(scanner, "_output_dir", "fosslight_raw_data")
    formats = [format_name]
    extensions = [extension]
    if output_order == "excel-first":
        formats.insert(0, "excel")
        extensions.insert(0, ".xlsx")
    elif output_order == "spdx-first":
        formats.append("excel")
        extensions.append(".xlsx")
    reports, failed_analyses = run_scanner(
        str(project), "", str(tmp_path / "output"), run_bin=False, run_dep=False,
        remove_src_data=False, result_log={}, output_files=["report"] * len(formats),
        output_extensions=extensions, formats=formats,
        selected_source_scanner="scancode", correct_mode=False,
    )

    assert failed_analyses == []
    assert requested_matched_text == [True]
    assert len(reports) == len(formats)
    document = parse_file(next(report for report in reports if report.endswith(extension)))
    assert validate_full_spdx_document(document) == []
    assert {file.name for file in document.files} == {"./src/one.c", "./src/two.c"}
    assert document.extracted_licensing_info[0].extracted_text == "Example license terms."
    assert {creator.name.split(" - ", 1)[0] for creator in document.creation_info.creators} == {
        "FOSSLIGHT_SCANNER", "FOSSLIGHT_Source", "spdx-tools",
    }


def test_excel_source_keeps_default_folder_merge(tmp_path, monkeypatch):
    from fosslight_source import cli as source_cli
    from fosslight_source._scan_item import SourceItem

    project = tmp_path / "project"
    (project / "src").mkdir(parents=True)
    source_items = []
    for filename in ("one.c", "two.c"):
        (project / "src" / filename).write_text("/* MIT */\n", encoding="utf-8")
        item = SourceItem(f"src/{filename}")
        item.licenses = ["MIT"]
        item.checksum = "a" * 40
        source_items.append(item)
    requested_matched_text = []

    def run_scancode(*args, **kwargs):
        requested_matched_text.append(args[5])
        return True, "True", source_items, {}

    monkeypatch.setattr(source_cli, "run_scan", run_scancode)
    monkeypatch.setattr(scanner, "fosslight_source_installed", True)
    monkeypatch.setattr(scanner, "_output_dir", "fosslight_raw_data")
    reports, failed_analyses = run_scanner(
        str(project), "", str(tmp_path / "output"), run_bin=False, run_dep=False,
        remove_src_data=False, result_log={}, output_files=["report"],
        output_extensions=[".xlsx"], formats=["excel"],
        selected_source_scanner="scancode", correct_mode=False,
    )

    assert failed_analyses == []
    assert requested_matched_text == [False]
    workbook = openpyxl.load_workbook(reports[0], read_only=True, data_only=True)
    try:
        assert workbook[_SRC].max_row == 2
    finally:
        workbook.close()


@pytest.fixture
def spdx_scanner_project(tmp_path, monkeypatch):
    import json
    import subprocess
    from random import Random
    from fosslight_dependency.package_manager.Npm import Npm
    from fosslight_source import cli as source_cli
    from fosslight_source._license_matched import MatchedLicense
    from fosslight_source._scan_item import SourceItem
    from fosslight_util.oss_item import OssItem

    project = tmp_path / "project"
    project.mkdir()
    (project / "main.c").write_text("/* Example license terms. */\n", encoding="utf-8")
    binary = project / "artifact.bin"
    binary.write_bytes(Random(4519).randbytes(8192))
    manifest = {"name": "project", "version": "1.0.0", "dependencies": {"parent": "1.0.0"}}
    (project / "package.json").write_text(json.dumps(manifest), encoding="utf-8")
    source_item = SourceItem("main.c")
    source_item.licenses = ["Example-License"]
    source_items = [source_item]
    matched_license = MatchedLicense("Example-License", "", "Example license terms.", "main.c")
    npm_reports = [{
        f"{name}@1.0.0": {
            "name": name, "version": "1.0.0", "licenses": "MIT",
            "path": str(project / "node_modules" / name), "repository": f"https://example.com/{name}",
        }
        for name in ("project", "parent", "child")
    }]

    def run_scancode(*args, **kwargs):
        licenses = {"example": matched_license} if args[5] and source_items else {}
        return True, "True", source_items, licenses

    def lookup(items, _url, _token):
        for item in items:
            item.set_oss_items([OssItem("binary-package", "1.0.0", "Apache-2.0")])
        return items, len(items), ""

    def run_plugin(manager):
        manager.manifest_file_name = ["package.json"]
        for index, report in enumerate(npm_reports):
            report_file = tmp_path / f"npm-report-{index}.json"
            report_file.write_text(json.dumps(report), encoding="utf-8")
            manager.input_package_list_file.append(str(report_file))
        return True

    original_run = subprocess.run

    def command_output(command, *args, **kwargs):
        if command == "npm ls -a --omit=dev --json -s":
            tree = {"name": "project", "version": "1.0.0", "dependencies": {
                "parent": {"version": "1.0.0", "dependencies": {"child": {"version": "1.0.0"}}},
            }}
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(tree), stderr="")
        return original_run(command, *args, **kwargs)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(scanner, "fosslight_source_installed", True)
    monkeypatch.setattr(scanner, "_output_dir", "fosslight_raw_data")
    monkeypatch.setattr(source_cli, "run_scan", run_scancode)
    monkeypatch.setattr(scanner.binary_analysis, "get_oss_info_from_db", lookup)
    monkeypatch.setattr(Npm, "_check_network_available", lambda self: False)
    monkeypatch.setattr(Npm, "_network_available", False)
    monkeypatch.setattr(Npm, "run_plugin", run_plugin)
    monkeypatch.setattr(subprocess, "run", command_output)
    return project, tmp_path / "output", source_items, npm_reports, binary


@pytest.mark.parametrize("format_name, extension", [
    ("spdx-json", ".json"), ("spdx-yaml", ".yaml"), ("spdx-xml", ".xml"), ("spdx-tag", ".tag"),
])
@pytest.mark.parametrize("mode, expected_scanners", [
    ("all", {"Source", "Binary", "Dependency"}),
    ("source", {"Source"}), ("binary", {"Binary"}), ("dependency", {"Dependency"}),
])
@pytest.mark.parametrize("empty", [False, True])
def test_spdx_all_and_partial_runs(spdx_scanner_project, format_name, extension, mode, expected_scanners, empty):
    import hashlib
    from spdx_tools.spdx.model import FileType, RelationshipType
    from spdx_tools.spdx.parser.parse_anything import parse_file
    from spdx_tools.spdx.validation.document_validator import validate_full_spdx_document

    project, output, source_items, npm_reports, binary = spdx_scanner_project
    if empty:
        source_items.clear()
        npm_reports.clear()
        binary.unlink()

    success = run_main(
        mode_list=[mode], path_arg=[str(project)], dep_arguments="-m npm",
        output_file_or_dir=str(output), file_format=[format_name], url_to_analyze="",
        hide_progressbar=True, num_cores=0, selected_source_scanner="scancode", correct_mode=False,
    )

    assert success
    filename, = output.glob(f"*{extension}")
    assert filename.name.startswith("fosslight_spdx_all_")
    document = parse_file(str(filename))
    assert validate_full_spdx_document(document) == []
    assert document.creation_info.name == "project"
    assert {creator.name.split(" - ", 1)[0] for creator in document.creation_info.creators} == {
        "FOSSLIGHT_SCANNER", "spdx-tools", *(f"FOSSLIGHT_{name}" for name in expected_scanners),
    }
    root = next(package for package in document.packages if package.spdx_id == "SPDXRef-ROOT-PACKAGE")
    assert root.name == "project"
    assert root.files_analyzed is False
    expected_files = set()
    if not empty and "Source" in expected_scanners:
        expected_files.add("./main.c")
        source_file = next(file for file in document.files if file.name == "./main.c")
        assert source_file.file_types == [FileType.SOURCE]
        assert source_file.checksums[0].value == hashlib.sha1((project / "main.c").read_bytes()).hexdigest()
        assert document.extracted_licensing_info[0].extracted_text == "Example license terms."
    if not empty and "Binary" in expected_scanners:
        expected_files.add("./artifact.bin")
        binary_file = next(file for file in document.files if file.name == "./artifact.bin")
        assert binary_file.file_types == [FileType.BINARY]
        assert binary_file.checksums[0].value == hashlib.sha1(binary.read_bytes()).hexdigest()
        assert binary_file.comment.startswith("fosslight:tlsh=T")
        package = next(package for package in document.packages if package.name == "binary-package")
        assert any(
            relation.spdx_element_id == package.spdx_id
            and relation.relationship_type == RelationshipType.CONTAINS
            and relation.related_spdx_element_id == binary_file.spdx_id
            for relation in document.relationships
        )
    if not empty and "Dependency" in expected_scanners:
        parent = next(package for package in document.packages if package.name == "npm:parent")
        child = next(package for package in document.packages if package.name == "npm:child")
        assert [reference.locator for reference in parent.external_references] == ["pkg:npm/parent@1.0.0"]
        assert str(parent.license_declared) == "MIT"
        assert parent.files_analyzed is False
        assert {
            (relation.spdx_element_id, relation.related_spdx_element_id)
            for relation in document.relationships if relation.relationship_type == RelationshipType.DEPENDS_ON
        } == {(root.spdx_id, parent.spdx_id), (parent.spdx_id, child.spdx_id)}
    assert {file.name for file in document.files} == expected_files
    if empty:
        assert len(document.packages) == 1
        assert not document.extracted_licensing_info


@pytest.mark.parametrize("formats", [["spdx-json"], ["excel", "spdx-json"]])
@pytest.mark.parametrize("ui_mode", [False, True])
def test_spdx_write_failure_is_not_reported_as_success(spdx_scanner_project, monkeypatch, formats, ui_mode):
    project, output, _source_items, _npm_reports, _binary = spdx_scanner_project
    original_writer = scanner.write_output_file

    def fail_spdx_output(*args, **kwargs):
        if args[5].startswith("spdx"):
            return False, "SPDX output failed", args[0] + args[1]
        return original_writer(*args, **kwargs)

    monkeypatch.setattr(scanner, "write_output_file", fail_spdx_output)
    success = run_main(
        mode_list=["source"], path_arg=[str(project)], dep_arguments="",
        output_file_or_dir=str(output), file_format=formats, url_to_analyze="",
        hide_progressbar=True, num_cores=0, selected_source_scanner="scancode", correct_mode=False,
        ui_mode=ui_mode,
    )

    assert bool(list(output.glob("*.json"))) is ui_mode
    assert success is False


SRC_OK = (True, "True", ScannerItem(FOSSLIGHT_SOURCE, ""), [], [])
BIN_OK = (True, ScannerItem(FOSSLIGHT_BINARY, ""))
DEP_OK = (True, ScannerItem(FOSSLIGHT_DEPENDENCY, ""))


def _returns(value):
    def fake(*args, **kwargs):
        if isinstance(value, Exception):
            raise value
        return value
    return fake


def _run_scanner_with(tmp_path, monkeypatch, source=SRC_OK, binary=BIN_OK, dependency=DEP_OK):
    """Run run_scanner with faked sub-scanners; return failed analyses and the merged scan items written."""
    src_path = tmp_path / "src"
    src_path.mkdir()
    (src_path / "main.py").write_text("print('hello')")
    written = []

    def fake_write_output_file(path, extension, scan_item, *args, **kwargs):
        written.append(scan_item)
        return True, "", path

    monkeypatch.setattr(scanner, "fosslight_source_installed", True)
    monkeypatch.setattr(scanner, "source_analysis_wrapper", _returns(source))
    monkeypatch.setattr(scanner.binary_analysis, "find_binaries", _returns(binary))
    monkeypatch.setattr(scanner, "run_dependency", _returns(dependency))
    monkeypatch.setattr(scanner, "write_output_file", fake_write_output_file)

    _, failed_analyses = run_scanner(
        src_path=str(src_path), dep_arguments="", output_path=str(tmp_path / "output"),
        run_src=True, run_bin=True, run_dep=True, remove_src_data=False, result_log={},
        output_files=["out"], output_extensions=[".xlsx"], formats=["excel"],
        num_cores=1, correct_mode=False, path_to_exclude=[]
    )
    return failed_analyses, written


@pytest.mark.parametrize("override,expected", [
    pytest.param({}, [], id="all-succeed"),
    pytest.param({"source": (False, "False, Source code analysis failed.", ScannerItem(FOSSLIGHT_SOURCE, ""), [], [])},
                 ["Source"], id="source-returns-false"),
    pytest.param({"source": RuntimeError("source crashed")}, ["Source"], id="source-raises"),
    pytest.param({"binary": (False, ScannerItem(FOSSLIGHT_BINARY, ""))}, ["Binary"], id="binary-returns-false"),
    pytest.param({"dependency": (False, ScannerItem(FOSSLIGHT_DEPENDENCY, ""))}, ["Dependency"],
                 id="dependency-returns-false"),
    pytest.param({"source": RuntimeError("source crashed"), "binary": RuntimeError("binary crashed"),
                  "dependency": (False, ScannerItem(FOSSLIGHT_DEPENDENCY, ""))},
                 ["Source", "Binary", "Dependency"], id="all-fail"),
])
def test_run_scanner_reports_failed_analyses(tmp_path, monkeypatch, override, expected):
    failed_analyses, _ = _run_scanner_with(tmp_path, monkeypatch, **override)

    assert failed_analyses == expected


def test_run_scanner_logs_failed_analyses_marker(tmp_path, monkeypatch, caplog):
    caplog.set_level("INFO", logger=scanner.logger.name)

    _run_scanner_with(tmp_path, monkeypatch, dependency=(False, ScannerItem(FOSSLIGHT_DEPENDENCY, "")))

    # The logger adapter prefixes messages with "[FOSSLIGHT_SCANNER] ".
    assert any(message.endswith("Analysis failed: Dependency") for message in caplog.messages)


def test_run_scanner_logs_no_marker_when_all_succeed(tmp_path, monkeypatch, caplog):
    caplog.set_level("INFO", logger=scanner.logger.name)

    _run_scanner_with(tmp_path, monkeypatch)

    assert not any("Analysis failed:" in message for message in caplog.messages)


def test_dependency_items_are_merged_even_when_dependency_fails(tmp_path, monkeypatch):
    dep_item = ScannerItem(FOSSLIGHT_DEPENDENCY, "")
    dep_item.file_items[FOSSLIGHT_DEPENDENCY] = [FileItem("pom.xml")]

    _, written = _run_scanner_with(tmp_path, monkeypatch, dependency=(False, dep_item))

    assert written[0].file_items[FOSSLIGHT_DEPENDENCY] == dep_item.file_items[FOSSLIGHT_DEPENDENCY]


def test_dependency_without_result_adds_no_cover_comment(tmp_path, monkeypatch):
    # run_dependency returns an empty fosslight_scanner item when the dependency scanner crashed.
    _, written = _run_scanner_with(tmp_path, monkeypatch, dependency=(False, ScannerItem(scanner.PKG_NAME, "")))

    assert f"[{scanner.PKG_NAME}]" not in written[0].cover.comment


def test_unexpected_error_marks_remaining_analyses_failed(tmp_path, monkeypatch):
    # A binary result without a scan item breaks the merge and jumps to run_scanner's outer except.
    failed_analyses, _ = _run_scanner_with(tmp_path, monkeypatch, binary=(True, None))

    assert failed_analyses == ["Binary", "Dependency"]


def test_download_source(tmp_path):
    # given
    link = "https://example.com/test_repo.git"
    out_dir = tmp_path / "output"

    # Create the necessary output directory
    out_dir.mkdir(parents=True, exist_ok=True)

    # when
    success, temp_src_dir, oss_name, oss_version = download_source(str(link), str(out_dir))

    # then
    # Ensure the function completes successfully
    assert isinstance(success, bool), "Function should return a boolean for success."

    # If the function fails, ensure temp_src_dir is empty
    if not success:
        assert temp_src_dir == "", "temp_src_dir should be an empty string if download fails."
    else:
        # If the function succeeds, check temp_src_dir is a valid path
        assert isinstance(temp_src_dir, str), "Temporary source directory should be a string."
        assert str(temp_src_dir).startswith(str(out_dir)), "Temporary source directory should be within the output directory."

    # Ensure oss_name and oss_version are strings
    assert isinstance(oss_name, str), "OSS name should be a string."
    assert isinstance(oss_version, str), "OSS version should be a string."


def test_init(tmp_path):
    # given
    output_path = tmp_path / "output"

    # Initialize global variables if necessary
    global _output_dir, _log_file
    _output_dir = "test_output"  # Set to a default or test-specific value
    _log_file = "test_log"       # Set the name of the log file

    # when
    dir_created, output_root_dir, result_log = init(str(output_path))

    # then
    # Ensure that the output directory was created
    assert dir_created is True, "The output directory should be created."

    # Check if the output_root_dir is correct
    assert output_root_dir == str(output_path), "Output root directory should match the given path."

    # Check that the result_log is not None and is a dictionary
    assert result_log is not None, "Result log should not be None."
    assert isinstance(result_log, dict), "Result log should be a dictionary."


def test_run_main(tmp_path):
    # given
    mode_list = ["source"]
    path_arg = [str(tmp_path / "test_src")]
    dep_arguments = []
    output_file_or_dir = str(tmp_path / "output")
    file_format = ['yaml']
    url_to_analyze = ""

    # Create necessary directories and files for the test
    (tmp_path / "test_src").mkdir(parents=True, exist_ok=True)

    # when
    result = run_main(
        mode_list=mode_list,
        path_arg=path_arg,
        dep_arguments=dep_arguments,
        output_file_or_dir=output_file_or_dir,
        file_format=file_format,
        url_to_analyze=url_to_analyze,
        hide_progressbar=True,  # Disable progress bar for testing
        keep_raw_data=True,     # Keep raw data to avoid cleanup during test
        num_cores=1,
        correct_mode=True,
        correct_fpath="",
        ui_mode=False,
        path_to_exclude=[]
    )

    # then
    assert result is True


def test_run_main_returns_false_when_an_analysis_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(scanner, "run_scanner", lambda *args, **kwargs: ([], ["Dependency"]))
    monkeypatch.setattr(scanner, "move_log_file", lambda *args: None)

    result = run_main(
        mode_list=["dependency"],
        path_arg=[str(tmp_path)],
        dep_arguments=[],
        output_file_or_dir=str(tmp_path / "output"),
        file_format=["excel"],
        url_to_analyze="",
        hide_progressbar=True,
    )

    assert result is False


@pytest.mark.parametrize("nested", [False, True], ids=["file", "merged-directory"])
@pytest.mark.parametrize("move_fails", [False, True], ids=["move-succeeds", "move-fails"])
def test_run_main_reports_only_successfully_moved_paths(tmp_path, monkeypatch, caplog, nested, move_fails):
    output_dir = tmp_path / "output"
    relative_report = Path("reports/report.yaml") if nested else Path("report.yaml")
    destination = output_dir / relative_report
    destination.parent.mkdir(parents=True)
    destination.write_text("old report")
    reports = []

    def fake_run_scanner(src_path, dep_arguments, output_path, *args, report_results):
        report = Path(output_path) / relative_report
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("current report")
        delivered = Path(output_path) / "delivered.yaml"
        delivered.write_text("another report")
        reports.extend([report, delivered])
        report_results.append((True, "", str(report)))
        return [str(report), str(delivered)], []

    real_move = shutil.move

    def move(src, dst):
        if move_fails and Path(src) == reports[0]:
            raise PermissionError("report is locked")
        return real_move(src, dst)

    monkeypatch.setattr(scanner, "run_scanner", fake_run_scanner)
    monkeypatch.setattr(scanner, "move_log_file", lambda *args: None)
    monkeypatch.setattr(shutil, "move", move)
    caplog.set_level("INFO", logger=scanner.logger.name)

    result = run_main(
        mode_list=["source"],
        path_arg=[str(tmp_path)],
        dep_arguments=[],
        output_file_or_dir=str(output_dir),
        file_format=["yaml"],
        url_to_analyze="",
        hide_progressbar=True,
    )

    assert result is True
    expected_report = reports[0] if move_fails else destination
    delivered = output_dir / "delivered.yaml"
    assert any(message.endswith(f"Output File: {expected_report}, {delivered}") for message in caplog.messages)
    assert delivered.read_text() == "another report"
    assert destination.read_text() == ("old report" if move_fails else "current report")
    assert reports[0].exists() is move_fails
    assert reports[1].parent.exists() is move_fails


@pytest.mark.parametrize("mode_list,expected_sheets", SHEET_CHECK_PARAMS)
def test_output_excel_contains_required_sheets(tmp_path, mode_list, expected_sheets):
    # given
    output_dir = tmp_path / "output"
    scan_path = _prepare_scan_fixture(tmp_path)

    # when
    result = run_main(
        mode_list=mode_list,
        path_arg=[str(scan_path)],
        dep_arguments=[],
        output_file_or_dir=str(output_dir),
        file_format=["excel"],
        url_to_analyze="",
        hide_progressbar=True,
        keep_raw_data=False,
        num_cores=0,
        correct_mode=False,
        correct_fpath="",
        ui_mode=False,
        path_to_exclude=[]
    )

    # then
    assert result is True, "run_main should return True on success."

    xlsx_files = list(output_dir.glob("*.xlsx"))
    assert len(xlsx_files) == 1, (
        f"Expected exactly one Excel report in {output_dir}, got {len(xlsx_files)}: {xlsx_files}"
    )

    xlsx_file = str(xlsx_files[0])

    actual_sheets = _get_sheet_names(xlsx_file)
    for sheet in expected_sheets:
        assert sheet in actual_sheets, (
            f"[mode={mode_list}] Sheet '{sheet}' not found. "
            f"Actual sheets: {actual_sheets}. "
            "One of the scanners may have failed silently."
        )

    for sheet in expected_sheets:
        row_count = _get_sheet_row_count(xlsx_file, sheet)
        assert row_count >= _MIN_DATA_ROWS, (
            f"[mode={mode_list}] Sheet '{sheet}' has {row_count} row(s), "
            f"expected at least {_MIN_DATA_ROWS}."
        )


def _make_read_only(target: Path) -> None:
    target.chmod(target.stat().st_mode & ~0o222)


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="Root bypasses the read-only directory permission precondition.",
)
def test_remove_tree_removes_nested_read_only_tree(tmp_path: Path):
    """remove_tree must remove a tree that shutil.rmtree alone cannot.

    A cloned git repository leaves read-only pack files behind, which Windows refuses
    to delete, and on POSIX an entry of a read-only directory cannot be removed.
    """
    # given: a read-only file inside read-only directories, under a read-only root
    root = tmp_path / "raw_data"
    nested = root / "objects" / "pack"
    nested.mkdir(parents=True)
    (nested / "locked.pack").write_bytes(b"x")
    _make_read_only(nested / "locked.pack")
    for directory in (nested, nested.parent, root):
        _make_read_only(directory)

    with pytest.raises(PermissionError):
        shutil.rmtree(root)

    # when
    removed = remove_tree(root)

    # then
    assert removed is True, "remove_tree should report the tree as gone."
    assert not root.exists(), f"{root} should have been removed."


def test_remove_tree_reports_failure_without_raising(tmp_path: Path, monkeypatch):
    """A directory that cannot be removed is reported, not raised, so callers continue."""
    # given
    target = tmp_path / "stuck"
    target.mkdir()

    def always_fail(*args, **kwargs):
        raise PermissionError("locked")

    monkeypatch.setattr(shutil, "rmtree", always_fail)

    # when / then
    assert remove_tree(target) is False
    assert target.exists()
