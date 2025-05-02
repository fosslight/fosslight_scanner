# Changelog

## v2.1.5 (02/05/2025)
## Changes
## 🚀 Features

- Add dep item in ui result @dd-jy (#141)

---

## v2.1.4 (24/04/2025)
## Changes
## 🐛 Hotfixes

- Fix ui mode error when analyzing only dependency @dd-jy (#140)

## 🔧 Maintenance

- Remove prechecker @dd-jy (#139)

---

## v2.1.3 (05/02/2025)
## Changes
## 🐛 Hotfixes

- Update platform in docker build workflow @soimkim (#138)
- Change base image to fix docker build error on macOS @soimkim (#137)

---

## v2.1.2 (09/01/2025)
## Changes
## 🐛 Hotfixes

- Fix json output error when not analyzing source @soimkim (#136)

---

## v2.1.1 (05/12/2024)
## Changes
## 🚀 Features

- Support cycloneDX format @dd-jy (#135)

## 🔧 Maintenance

- Print option name with error msg @bjk7119 (#132)

---

## v2.1.0 (08/10/2024)
## Changes
## 🚀 Features

- Support multi format and spdx (spdx only Linux) @dd-jy (#130)

## 🔧 Maintenance

- Change the test code to use pytest @cjho0316 (#124)
- ci: Add Docker build and push workflow for automated releases @soonhong99 (#122)

---

## v2.0.1 (09/09/2024)
## Changes
## 🔧 Maintenance

- Revert "Remove prechecker" @dd-jy (#120)

---

## v2.0.0 (06/09/2024)
## Changes
## 🔧 Maintenance

- Remove prechecker @dd-jy (#119)
- Refactoring OSS item @dd-jy (#118)

---

## v1.7.31 (06/09/2024)
## Changes
## 🚀 Features

- Setting.json with source_scanner selection @soonhong99 (#109)

## 🐛 Hotfixes

- Fix a bug related to path_to_exclude @soimkim (#116)

## 🔧 Maintenance

- Limit installation fosslight package @dd-jy (#117)
- Add simple_mode parameter to CoverItem constructor @YongGoose (#108)

---

## v1.7.30 (22/07/2024)
## Changes
## 🚀 Features

- Run with compressed file @bjk7119 (#105)

## 🔧 Maintenance

- Remove to create bin.txt @bjk7119 (#100)

---

## v1.7.29 (08/07/2024)
## Changes
## 🚀 Features

- Supports for applying setting from json file @SeongjunJo (#97)

## 🔧 Maintenance

- Change the json key and value format @soimkim (#99)
- Allow more than two modes to be entered @soimkim (#98)

---

## v1.7.28 (01/07/2024)
## Changes
## 🚀 Features

- Supports for excluding paths from analysis @SeongjunJo (#95)

---

## v1.7.27 (13/06/2024)
## Changes
## 🚀 Features

- Supports for multiple modes @SeongjunJo (#92)

## 🐛 Hotfixes

- When merging src to bin, remove src info instead of excluding @dd-jy (#96)

## 🔧 Maintenance

- Modify column name @bjk7119 (#94)

---

## v1.7.26 (29/05/2024)
## Changes
## 🔧 Maintenance

- Update the requirements.txt @bjk7119 (#93)
- Modify FL Binary required ver. to 4.1.29 @bjk7119 (#91)

---

## v1.7.25 (07/05/2024)
## Changes
## 🚀 Features

- Add TLSH, SHA1 column for binary analysis @bjk7119 (#90)

---

## v1.7.24 (26/04/2024)
## Changes
## 🚀 Features

- Add detection summary message (cover sheet) @dd-jy (#89)

---

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
