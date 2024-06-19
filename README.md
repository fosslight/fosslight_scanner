<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: Apache-2.0
 -->

# FOSSLight Scanner
<strong>Analyze at once for Open Source Compliance.</strong><br>

<img src="https://img.shields.io/pypi/l/fosslight_scanner" alt="FOSSLight Scanner is released under the Apache-2.0." /> <img src="https://img.shields.io/pypi/v/fosslight_scanner" alt="Current python package version." /> <img src="https://img.shields.io/pypi/pyversions/fosslight_scanner" /> [![REUSE status](https://api.reuse.software/badge/github.com/fosslight/fosslight_scanner)](https://api.reuse.software/info/github.com/fosslight/fosslight_scanner)


**FOSSLight Scanner** performs open source analysis after downloading the source by passing a link that can be cloned by wget or git. Instead, open source analysis can be performed for the local source path. The output result is generated in [FOSSLight Report][or] format.

- **[FOSSLight Prechecker][re]** Check whether the [source code's copyright and license writing rules][rule] are complied with.
- **[FOSSLight Source Scanner][s]** Extract license and copyright in the source code using [ScanCode][sc].
- **[FOSSLight Dependency Scanner][d]** Extract dependency and OSS information from the package manager's manifest file.
- **[FOSSLight Binary Scanner][flbin]** Find binary and print OSS information.

[s]: https://github.com/fosslight/fosslight_source_scanner
[d]: https://github.com/fosslight/fosslight_dependency_scanner
[sc]: https://github.com/nexB/scancode-toolkit
[or]: https://fosslight.org/fosslight-guide-en/learn/2_fosslight_report.html
[flbin]: https://github.com/fosslight/fosslight_binary_scanner
[re]: https://github.com/fosslight/fosslight_prechecker
[rule]: https://oss.lge.com/guide/process/osc_process/1-identification/copyright_license_rule.html

## Contents

- [FOSSLight Scanner](#fosslight-scanner)
  - [Contents](#contents)
  - [📋 Prerequisite](#-prerequisite)
  - [🎉 How to install](#-how-to-install)
  - [🚀 How to run](#-how-to-run)
    - [Parameters](#parameters)
    - [Ex 1. Local Source Analysis](#ex-1-local-source-analysis)
    - [Ex 2. Download Link and analyze](#ex-2-download-link-and-analyze)
  - [📁 Result](#-result)
  - [🐳 How to run using Docker](#-how-to-run-using-docker)
  - [👏 How to report issue](#-how-to-report-issue)
  - [📄 License](#-license)


## 📋 Prerequisite

FOSSLight Scanner needs a Python 3.6+.

## 🎉 How to install


It can be installed using pip3. It is recommended to install it in the [python 3.7 + virtualenv]([etc/guide_virtualenv.md](https://fosslight.org/fosslight-guide-en/scanner/etc/guide_virtualenv.html)) environment.

```
$ pip3 install fosslight_scanner
```

## 🚀 How to run

FOSSLight Scanner is run with the **fosslight** command.
``` 
fosslight [Mode] [option1] <arg1> [option2] <arg2>...
``` 
### Parameters   
Mode
``` 
        all                     Run all scanners(Default)
        source                  Run FOSSLight Source
        dependency              Run FOSSLight Dependency
        binary                  Run FOSSLight Binary
        prechecker              Run FOSSLight Prechecker
        compare                 Compare two FOSSLight reports
``` 
Options:
``` 
        -h                      Print help message
        -p <path>               Path to analyze (ex, -p {input_path})
                                 * Compare mode input file: Two FOSSLight reports (supports excel, yaml)
                                   (ex, -p {before_name}.xlsx {after_name}.xlsx)
        -w <link>               Link to be analyzed can be downloaded by wget or git clone
        -f <format>             FOSSLight Report file format (excel, yaml)
                                 * Compare mode result file: supports excel, json, yaml, html
        -o <output>             Output directory or file
        -c <number>             Number of processes to analyze source
        -e <path>               Path to exclude from analysis (ex, -e {dir} {file})
        -r                      Keep raw data
        -t                      Hide the progress bar
        -v                      Print FOSSLight Scanner version
        -s <path>               Path to apply setting from json file (check format with 'setting.json' in this repository)
                                 * Direct cli flags have higher priority than setting file
                                   (ex, '-f yaml -s setting.json' - result file extension is .yaml)
```
- Refs. 
    - Additional arguments for running dependency analysis. See the [FOSSLight Dependency Guide][fd_guide] for instructions.
    - In the case of DB URL, it is the [DB connection information to be used in FOSSLight Binary][flbindb].

[flbindb]: https://fosslight.org/fosslight-guide-en/scanner/etc/binary_db.html
[fd_guide]: https://fosslight.org/fosslight-guide-en/scanner/2_dependency.html

### Ex 1. Local Source Analysis
```
$ fosslight all -p /home/source_path -d "-a 'source /test/Projects/venv/bin/activate' -d 'deactivate'"
```

### Ex 2. Local Source Analysis with Path to Exclude
```
$ fosslight all -p /home/source_path -e temp_dir src/temp.py
```

### Ex 3. Download Link and analyze
```
$ fosslight all -o test_result_wget -w "https://github.com/LGE-OSS/example.git"
```
If you want to analyze private repository, set your github token like below.
```
$ fosslight all -w "https://my_github_token@github.com/Foo/private_repo
```

### Ex 4. Compare the BOM of two FOSSLight reports with yaml or excel format and check the oss status (change/add/delete)
```
$ fosslight compare -p FOSSLight_before_proj.yaml FOSSLight_after_proj.yaml -f excel
```

## 📁 Result

```
$ tree
.
├── fosslight_log
│   ├── fosslight_log_20210924_022422.txt
└── FOSSLight-Report_20210924_022422.xlsx
```

- FOSSLight_Report-[datetime].xlsx : OSS Report format file that outputs source code analysis, binary analysis, and dependency analysis results.
- fosslight_raw_data_[datetime] directory: Directory in which raw data files are created as a result of analysis

## 🐳 How to run using Docker
1. Build image using Dockerfile.
```
$docker build -t fosslight .
```
2. Run with the image you built.      
ex. Output: /Users/fosslight_source_scanner/test_output, Path to be analyzed: tests/test_files
```
$docker run -it -v /Users/fosslight_source_scanner/test_output:/app/output fosslight -p tests/test_files -o output
```

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [fosslight_scanner repository][cl].    
Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[cl]: https://github.com/fosslight/fosslight_scanner/issues

## 📄 License

FOSSLight Scanner is released under [Apache-2.0][l].

[l]: https://github.com/fosslight/fosslight_scanner/blob/main/LICENSE
