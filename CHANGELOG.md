# Changelog

## v1.7.8 (02/01/2023)
## Changes
## 🔧 Maintenance

- Update version of package for actions @bjk7119 (#54)

---

## v1.7.7 (18/11/2022)
## Changes
## 🔧 Maintenance

- Fix the output file msg if nothing scanned @dd-jy (#52)

---

## v1.7.6 (04/11/2022)
## Changes
## 🐛 Hotfixes

- Fix bug about dep. arg input when not dep. running @bjk7119 (#50)

## 🔧 Maintenance

- Analyze current path if not input path @bjk7119 (#51)

---

## v1.7.5 (06/10/2022)
## Changes
## 🔧 Maintenance

- Fix the binary text copy issue @dd-jy (#49)

---

## v1.7.4 (15/09/2022)
## Changes
## 🔧 Maintenance

- Change the report file name @dd-jy (#48)
- Modify help msg if invalid input @bjk7119 (#47)

---

## v1.7.3 (01/09/2022)
## Changes
## 🚀 Features

- Support 'xlsx' report for Compare mode @dd-jy (#46)

## 🔧 Maintenance

- Change the required version of Python to 3.7 @soimkim (#45)

---

## v1.7.2 (16/08/2022)
## Changes
## 🚀 Features

- Support yaml format of FOSSLight Report @dd-jy (#42)

---

## v1.7.1 (22/07/2022)
## Changes
## 🐛 Hotfixes

- Change FL Reuse to FL Prechecker @bjk7119 (#43)

---

## v1.7.0 (22/07/2022)
## Changes
## 🚀 Features

- Add compare mode @dd-jy (#38)

## 🔧 Maintenance

- Replace 'y' option to 'p' option. @dd-jy (#41)
- Fix scanner support format and not to create csv. @dd-jy (#40)
- Print message when comparison rows are over 100. @dd-jy (#39)

---

## v1.6.15 (06/07/2022)
## Changes
## 🐛 Hotfixes

- Modify reuse input parameter @bjk7119 (#37)

---

## v1.6.14 (19/05/2022)
## Changes
## 🚀 Features

- Run fosslight_source without installing it @soimkim (#34)
- Add a Dockerfile @soimkim (#35)

## 🐛 Hotfixes

- Fix a bug where part of the output file is not created without the -o option @soimkim (#36)

---

## v1.6.13 (11/04/2022)
## Changes
## 🐛 Hotfixes

- Fix an errors when parsing with path @soimkim (#33)
- Fix an error that occur when downloading link @soimkim (#30)

## 🔧 Maintenance

- Add a commit message checker @soimkim (#31)

---

## v1.6.12 (28/03/2022)
## 🐛 Hotfixes

- Fix a bug where column names do not match when overwriting an excel @soimkim (#29)

---

## v1.6.11 (27/03/2022)
## 🚀 Features

- Print download location when analyzing as link @soimkim (#28)
- Extract the OSS name from the link @soimkim (#27)

---

## v1.6.10 (11/03/2022)
## Changes
## 🔧 Maintenance

- Apply f-string format @bjk7119 (#26)

---

## v1.6.9 (28/02/2022)
## Changes
## 🔧 Maintenance

- Change the result generation method to merging @soimkim (#25)
- Add an inputable value to mode @soimkim (#24)
- Update the README with additional Scanners @soimkim (#23)

---

## v1.6.8 (10/02/2022)
## Changes
## 🚀 Features

- Change the options when analyzing the source @soimkim (#19)
- Support analysis mode @soimkim (#17)
- Add a FOSSLight Reuse @soimkim (#16)
- Add a FOSSLight Binary @soimkim (#14)

## 🐛 Hotfixes

- Fix the bug that the raw folder is not deleted when analyzing with a link @soimkim (#21)

## 🔧 Maintenance

- Modify to print output file name @bjk7119 (#22)
- Create a result file of FOSSLight Source @soimkim (#20)
- Move the binary analysis result file to output @soimkim (#18)

---

## v1.6.7 (25/11/2021)
## Changes
## 🔧 Maintenance

- Print output file instead of path @soimkim (#13)

---

## v1.6.6 (04/11/2021)
## Changes
## 🚀 Features

- Add number of process to analyze as parameter @soimkim (#11)

---

## v1.6.5 (21/10/2021)
## Changes
## 🔧 Maintenance

- Add the -f option and change way to create output @soimkim (#10)
- Change the parameters related to the scanner path @soimkim (#9)

---

## v1.6.4 (07/10/2021)
## Changes
## 🔧 Maintenance

- Change sheet name of Dependency Scan result @soimkim (#8)

---

## v1.6.3 (06/10/2021)
## Changes
## 🚀 Features

- Add option -t  for hiding the progress bar @soimkim (#7)

---

## v1.6.2 (05/10/2021)
## Changes
## 🔧 Maintenance

- Specify the output file name @soimkim (#6)

---

## v1.6.1 (01/10/2021)
## Changes
## 🐛 Hotfixes

- Add the FOSSLight Util minimum version @soimkim (#4)

## 🔧 Maintenance

- Change the output path of log, source @soimkim (#5)

---

## v1.6.0 (24/09/2021)
## Changes
## 🔧 Maintenance

- Change the version related files @soimkim (#2)
- Add copyright, license for Reuse compliance @soimkim (#1)
