<!--
Copyright (c) 2021 LG Electronics
SPDX-License-Identifier: Apache-2.0
 -->

# FOSSLight Scanner
<strong>Analyze at once for Open Source Compliance.</strong><br>

<img src="https://img.shields.io/pypi/l/fosslight_scanner" alt="FOSSLight Scanner is released under the Apache-2.0." /> <img src="https://img.shields.io/pypi/v/fosslight_scanner" alt="Current python package version." /> <img src="https://img.shields.io/pypi/pyversions/fosslight_scanner" /> [![REUSE status](https://api.reuse.software/badge/github.com/fosslight/fosslight_scanner)](https://api.reuse.software/info/github.com/fosslight/fosslight_scanner)


**FOSSLight Scanner** performs open source analysis after downloading the source by passing a link that can be cloned by wget or git. Instead, open source analysis can be performed for the local source path. The output result is generated in [FOSSLight Report][or] format.

- **[FOSSLight Reuse][re]** Check whether the [source code's copyright and license writing rules][rule] are complied with.
- **[FOSSLight Source Scanner][s]** Extract license and copyright in the source code using [ScanCode][sc].
- **[FOSSLight Dependency Scanner][d]** Extract dependency and OSS information from the package manager's manifest file.
- **[FOSSLight Binary Scanner][flbin]** Find binary and print OSS information.

[s]: https://github.com/fosslight/fosslight_source_scanner
[d]: https://github.com/fosslight/fosslight_dependency_scanner
[sc]: https://github.com/nexB/scancode-toolkit
[or]: https://fosslight.org/fosslight-guide-en/learn/2_fosslight_report.html
[flbin]: https://github.com/fosslight/fosslight_binary_scanner
[re]: https://github.com/fosslight/fosslight_reuse
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
  - [👏 How to report issue](#-how-to-report-issue)
  - [📄 License](#-license)


## 📋 Prerequisite

FOSSLight Scanner needs a Python 3.6+.

## 🎉 How to install


It can be installed using pip3. It is recommended to install it in the [python 3.6 + virtualenv]([etc/guide_virtualenv.md](https://fosslight.org/fosslight-guide-en/scanner/etc/guide_virtualenv.html)) environment.

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
            source            Run FOSSLight Source
            dependency        Run FOSSLight Dependency
            binary            Run FOSSLight Binary
            reuse             Run FOSSLight Reuse
            all               Run all scanners
``` 
Options:
``` 
    -h                        Print help message
    -r                        Keep raw data  
    -t                        Hide the progress bar
    -v                        Print FOSSLight Scanner version
    -p <path>                 Path to analyze source
    -w <link>                 Link to be analyzaed can be downloaded by wget or git clone
    -o <output>               Output Directory or file
    -f <format>               Output file format (excel, csv, opossum)
    -c <cores>                Number of processes to analyze source
    -d <additional_arg>       Additional arguments for running dependency analysis 
    -u <db_url>               DB Connection(format :'postgresql://username:password@host:port/database_name')
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

### Ex 2. Download Link and analyze
```
$ fosslight all -o test_result_wget -w "https://github.com/LGE-OSS/example.git"
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

## 👏 How to report issue

Please report any ideas or bugs to improve by creating an issue in [fosslight_scanner repository][cl].    
Then there will be quick bug fixes and upgrades. Ideas to improve are always welcome.

[cl]: https://github.com/fosslight/fosslight_scanner/issues

## 📄 License

FOSSLight Scanner is released under [Apache-2.0][l].

[l]: https://github.com/fosslight/fosslight_scanner/blob/main/LICENSE
