# Changelog

## v2.1.20 (26/03/2026)
## Changes
## 🐛 Hotfixes

- Correct incorrect timestamp in raw data output filenames @soimkim (#167)

## 🔧 Maintenance

- Add reference to the FOSSLight Scanner User Guide in the README. @soimkim (#168)

---

## v2.1.19 (23/03/2026)
## Changes
## 🔧 Maintenance

- Remove "Type of change" section from PR default template @woocheol-lge (#165)
- Update .coderabbit.yaml for auto reviewing. @soimkim (#164)
- Update test configuration format in setting.json @woocheol-lge (#162)

---

## v2.1.18 (13/02/2026)
## Changes
## 🐛 Hotfixes

- Fix incorrect timestamp in raw data output file names when running all scanners with -r option @hyesung22 (#160)

---

## v2.1.17 (05/02/2026)
## Changes
## 🔧 Maintenance

- Remove ui option in help msg @dd-jy (#159)
- Remove unnecessary description @bjk7119 (#158)

---

## v2.1.16 (02/02/2026)
## Changes
## 🔧 Maintenance

- Update help message @bjk7119 (#153)

---

## v2.1.15 (26/01/2026)
## Changes
## 🔧 Maintenance

- Add ordering scanner info sheet comment @dd-jy (#157)
- Enhance README for clarity and correctness @nickyzero (#156)
- Create intermediate files in a hidden folder @soimkim (#154)

---

## v2.1.14 (26/01/2026)
## Changes
## 🐛 Hotfixes

- Fix dependency bug for all_exclude_mode @dd-jy (#155)

---

## v2.1.13 (23/01/2026)
## Changes
- Remove duplicated exclude logic for all mode @dd-jy (#151)

## 🔧 Maintenance

- Exclude temp outputs after source analysis @bjk7119 (#152)
- Add how to use -e option @bjk7119 (#149)

---

## v2.1.12 (16/01/2026)
## Changes
## 🔧 Maintenance

- Update exclude function with fosslight_util @dd-jy (#150)

---

## v2.1.11 (24/12/2025)
## Changes
## 🔧 Maintenance

- Update supported format @dd-jy (#148)
- Add recursive_dep param in setting.json @dd-jy (#147)

---

## v2.1.10 (14/11/2025)
## Changes
## 🚀 Features

- Add dependency recursive mode @dd-jy (#146)

---

## v2.1.9 (21/08/2025)
## Changes
## 🔧 Maintenance

- Skip merge if path includes package dir @dd-jy (#145)

---

## v2.1.8 (17/07/2025)
## Changes
## 🔧 Maintenance

- Update python support ver 3.10~3.12 @dd-jy (#144)

---

## v2.1.7 (04/07/2025)
## Changes
## 🐛 Hotfixes

- Fix the compare output bug @dd-jy (#143)

---

## v2.1.6 (28/05/2025)
## Changes
## 🐛 Hotfixes

- Fix the correct mode bug @dd-jy (#142)

---

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
