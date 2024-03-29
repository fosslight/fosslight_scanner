# Changelog

## v1.7.23 (12/03/2024)
## Changes
## 🔧 Maintenance

- Remove FL Prechecker mode @bjk7119 (#88)

---

## v1.7.22 (29/01/2024)
## Changes
## 🚀 Features

- Download the latest version of package url @dd-jy (#86)
- Supports multiple input modes @soimkim (#85)

## 🔧 Maintenance

- Normalize pypi package name (PEP 0503) @dd-jy (#83)
- Support oss name with files.pythonhosted.org url @dd-jy (#82)
- Optimize Dockerfile to reduce image size @cookienc (#68)

---

## v1.7.21 (06/11/2023)
## Changes
## 🐛 Hotfixes

- Fix the fs output path @dd-jy (#81)

---

## v1.7.20 (30/10/2023)
## Changes
## 🔧 Maintenance

- Update supported python version @dd-jy (#80)
- Fetch base-check-commit-message.yml from fosslight/.github @cookienc (#78)
- Upgrade Python minimum version to 3.8 @JustinWonjaePark (#79)

---

## v1.7.19 (15/09/2023)
## Changes
## 🔧 Maintenance

- Fix importing from  fl source @JustinWonjaePark (#76)

---

## v1.7.18 (05/09/2023)
## Changes
## 🐛 Hotfixes

- Fix absolute path related bugs @soimkim (#75)

---

## v1.7.17 (01/09/2023)
## Changes
## 🔧 Maintenance

- Print even files that were not detected @soimkim (#72)

---

## v1.7.16 (31/08/2023)
## Changes
## 🔧 Maintenance

- Include the parent directory for ScanCode @soimkim (#71)
- Fix the vulnerability @dd-jy (#69)

---

## v1.7.15 (14/08/2023)
## Changes
## 🚀 Features

- Generate ui mode result file @dd-jy (#66)

---

## v1.7.14 (26/07/2023)
## Changes
## 🐛 Hotfixes

- Fix the source analysis fail issue @dd-jy (#65)

---

## v1.7.13 (14/07/2023)
## Changes
## 🚀 Features

- Correct the source/bin scanner result @dd-jy (#62)

## 🐛 Hotfixes

- Fix the correct mode bug for yaml format @dd-jy (#63)
- Update the git config for gh action @dd-jy (#61)
- Update the ubuntu version for deploy action @dd-jy (#60)

## 🔧 Maintenance

- Modify exclude item not to compare for correct mode @dd-jy (#64)

---

## v1.7.12 (02/06/2023)
## Changes
## 🚀 Features

- Correct the source/bin scanner result @dd-jy (#62)

## 🐛 Hotfixes

- Fix the correct mode bug for yaml format @dd-jy (#63)
- Update the git config for gh action @dd-jy (#61)
- Update the ubuntu version for deploy action @dd-jy (#60)

---

## v1.7.11 (23/02/2023)
## Changes
## 🔧 Maintenance

- Add the package name to result file and log @dd-jy (#58)

---

## v1.7.10 (10/02/2023)
## Changes
## 🔧 Maintenance

- Apply additional return val of 'parsing_yml' @bjk7119 (#57)

---

## v1.7.9 (30/01/2023)
## Changes
## 🔧 Maintenance

- Change package to get release package @bjk7119 (#56)
- Add the cron job to check daily build @dd-jy (#55)

---

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
