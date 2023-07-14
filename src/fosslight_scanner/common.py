#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import logging
import shutil
import re
import pandas as pd
import yaml
import copy
import fosslight_util.constant as constant
from fosslight_util.parsing_yaml import parsing_yml
from fosslight_util.write_yaml import create_yaml_with_ossitem
from fosslight_util.read_excel import read_oss_report
from fosslight_util.output_format import write_output_file

logger = logging.getLogger(constant.LOGGER_NAME)
SRC_SHEET = 'SRC_FL_Source'
BIN_SHEET = 'BIN_FL_Binary'


def copy_file(source, destination):
    copied_file = ""
    try:
        shutil.copy(source, destination)
        if os.path.isdir(destination):
            copied_file = os.path.join(destination, os.path.basename(source))
        else:
            copied_file = destination
    except Exception as ex:
        logger.debug(f"Failed to copy {source} to {destination}: {ex}")
        return False, copied_file
    else:
        return True, copied_file


def run_analysis(path_to_run, params, func, str_run_start, output, exe_path):
    # This function will be replaced by call_analysis_api().
    logger.info("## Start to run "+str_run_start)
    return_value = ""
    try:
        if path_to_run != "":
            logger.info(f"|--- Path to analyze : {path_to_run}")
            os.chdir(output)
            sys.argv = params
            return_value = func()
            os.chdir(exe_path)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(f"{str_run_start}:{ex}")
    return return_value


def call_analysis_api(path_to_run, str_run_start, return_idx, func, *args):
    # return_idx == -1 : Raw return value itself
    logger.info(f"## Start to run {str_run_start}")
    success = True
    result = []
    try:
        if path_to_run != "":
            logger.info(f"|--- Path to analyze : {path_to_run}")
            result = func(*args)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        success = False
    except Exception as ex:
        success = False
        logger.error(f"{str_run_start}:{ex}")
    try:
        if success:
            if result and return_idx >= 0:
                if len(result) > return_idx:
                    result = result[return_idx]
                else:
                    success = False
    except Exception as ex:
        logger.debug(f"Get return value:{ex}")
        success = False
    if not result:
        result = []
    return success, result


def extract_name_from_link(link):
    # Github : https://github.com/(owner)/(repo)
    # npm : www.npmjs.com/package/(package)
    # npm : https://www.npmjs.com/package/@(group)/(package)
    # pypi : https://pypi.org/project/(oss_name)
    # Maven: https://mvnrepository.com/artifact/(group)/(artifact)
    # pub: https://pub.dev/packages/(package)
    # Cocoapods: https://cocoapods.org/(package)
    pkg_pattern = {
        "github": r'https?:\/\/github.com\/([^\/]+)\/([^\/\.]+)(\.git)?',
        "pypi": r'https?:\/\/pypi\.org\/project\/([^\/]+)',
        "maven": r'https?:\/\/mvnrepository\.com\/artifact\/([^\/]+)\/([^\/]+)',
        "npm": r'https?:\/\/www\.npmjs\.com\/package\/([^\/]+)(\/[^\/]+)?',
        "pub": r'https?:\/\/pub\.dev\/packages\/([^\/]+)',
        "pods": r'https?:\/\/cocoapods\.org\/pods\/([^\/]+)'
    }
    oss_name = ""
    if link.startswith("www."):
        link = link.replace("www.", "https://www.", 1)
    for key, value in pkg_pattern.items():
        try:
            p = re.compile(value)
            match = p.match(link)
            if match:
                group = match.group(1)
                if key == "github":
                    repo = match.group(2)
                    oss_name = f"{group}-{repo}"
                    break
                elif key == "pypi":
                    oss_name = f"pypi:{group}"
                    break
                elif key == "maven":
                    artifact = match.group(2)
                    oss_name = f"{group}:{artifact}"
                    break
                elif key == "npm":
                    if group.startswith("@"):
                        pkg = match.group(2)
                        oss_name = f"npm:{group}{pkg}"
                    else:
                        oss_name = f"npm:{group}"
                    break
                elif key == "pub":
                    oss_name = f"pub:{group}"
                    break
                elif key == "pods":
                    oss_name = f"cocoapods:{group}"
                    break
        except Exception as ex:
            logger.debug(f"extract_name_from_link_{key}:{ex}")
    return oss_name


def overwrite_excel(excel_file_path, oss_name, column_name='OSS Name'):
    if oss_name != "":
        try:
            files = os.listdir(excel_file_path)
            for file in files:
                if file.endswith(".xlsx"):
                    file = os.path.join(excel_file_path, file)
                    excel_file = pd.ExcelFile(file, engine='openpyxl')

                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(file, sheet_name=sheet_name, engine='openpyxl')
                            if column_name in df.columns:
                                updated = (df[column_name] == '') | (df[column_name].isnull())
                                df.loc[updated, column_name] = oss_name
                                df.to_excel(file, sheet_name=sheet_name, index=False)
                        except Exception as ex:
                            logger.debug(f"overwrite_sheet {sheet_name}:{ex}")
        except Exception as ex:
            logger.debug(f"overwrite_excel:{ex}")


def merge_yamls(_output_dir, merge_yaml_files, final_report, remove_src_data=False, default_oss_name='', url=''):
    success = True
    err_msg = ''

    oss_total_list = []
    yaml_dict = {}
    try:
        for mf in merge_yaml_files:
            if os.path.exists(os.path.join(_output_dir, mf)):
                oss_list, license_list, err_reason = parsing_yml(os.path.join(_output_dir, mf), _output_dir)

                if remove_src_data:
                    existed_yaml = {}
                    for oi in oss_list:
                        oi.name = default_oss_name if oi.name == '-' else oi.name
                        oi.download_location = url if oi.download_location == '' else oi.download_location
                        create_yaml_with_ossitem(oi, existed_yaml)
                    with open(os.path.join(_output_dir, mf), 'w') as f:
                        yaml.dump(existed_yaml, f, default_flow_style=False, sort_keys=False)

                oss_total_list.extend(oss_list)

        if oss_total_list != []:
            for oti in oss_total_list:
                create_yaml_with_ossitem(oti, yaml_dict)
            with open(os.path.join(_output_dir, final_report), 'w') as f:
                yaml.dump(yaml_dict, f, default_flow_style=False, sort_keys=False)
        else:
            success = False
            err_msg = "Output file is not created as no oss items detected."
    except Exception as ex:
        err_msg = ex
        success = False

    return success, err_msg


def correct_scanner_result(_output_dir, output_files, output_extension, exist_src, exist_bin):
    src_oss_list = []
    bin_oss_list = []
    duplicates = False

    if exist_src:
        src_oss_list = check_exclude_dir(get_osslist(_output_dir, output_files['SRC'], output_extension, SRC_SHEET))
    if exist_bin:
        bin_oss_list = check_exclude_dir(get_osslist(_output_dir, output_files['BIN'], output_extension, BIN_SHEET))

    if exist_src and exist_bin:
        try:
            dup_bin_list = []
            exclude_list = []
            for src_item in src_oss_list:
                dup_bin = ''
                for idx, bin_item in enumerate(bin_oss_list):
                    if (not src_item.source_name_or_path) or src_item.exclude or bin_item.exclude:
                        continue
                    if src_item.source_name_or_path[0] == bin_item.source_name_or_path[0]:
                        dup_bin = copy.deepcopy(bin_item)
                        if not dup_bin.license:
                            if dup_bin.exclude:
                                src_item.exclude = dup_bin.exclude
                            dup_bin.set_sheet_item(src_item.get_print_array()[0])
                            if dup_bin.comment:
                                dup_bin.comment += '/'
                            dup_bin.comment += 'Loaded from SRC OSS info'
                            dup_bin_list.append(dup_bin)
                            exclude_list.append(idx)
                if dup_bin:
                    src_item.exclude = True
                    if src_item.comment:
                        src_item.comment += '/'
                    src_item.comment += 'Excluded by duplicated binary within BIN'
                    duplicates = True

            exclude_list = list(set(exclude_list))
            for idx in exclude_list:
                bin_oss_list[idx].exclude = True
                if bin_oss_list[idx].comment:
                    bin_oss_list[idx].comment += '/'
                bin_oss_list[idx].comment += 'Excluded by SRC OSS info'
            bin_oss_list.extend(dup_bin_list)
        except Exception as ex:
            logger.warning(f"correct the scanner result:{ex}")

    try:
        if exist_src:
            success, err_msg = write_output_with_osslist(src_oss_list, _output_dir, output_files['SRC'],
                                                         output_extension, SRC_SHEET)
            if not success:
                logger.warning(err_msg)
        if exist_bin:
            success, err_msg = write_output_with_osslist(bin_oss_list, _output_dir, output_files['BIN'],
                                                         output_extension, BIN_SHEET)
            if not success:
                logger.warning(err_msg)
        if duplicates:
            logger.info('Success to correct the src/bin scanner result')
    except Exception as ex:
        logger.warning(f"Corrected src/bin scanner result:{ex}")
    return


def write_output_with_osslist(oss_list, output_dir, output_file, output_extension, sheetname):
    new_oss_list = []
    sheet_list = {}
    sheet_list[sheetname] = []

    for src_item in oss_list:
        new_oss_list.append(src_item.get_print_array()[0])
    sheet_list[sheetname].extend(new_oss_list)
    if os.path.exists(os.path.join(output_dir, output_file)):
        os.remove(os.path.join(output_dir, output_file))
    success, err_msg, _ = write_output_file(os.path.join(output_dir, output_file).rstrip(output_extension),
                                            output_extension, sheet_list)
    return success, err_msg


def get_osslist(_output_dir, output_file, output_extension, sheet_name=''):
    err_reason = ''
    oss_list = []
    oss_file_with_fullpath = os.path.join(_output_dir, output_file)

    if os.path.exists(oss_file_with_fullpath):
        if output_extension == '.xlsx':
            oss_list = read_oss_report(oss_file_with_fullpath, sheet_name)
        elif output_extension == '.yaml':
            oss_list, _, err_reason = parsing_yml(oss_file_with_fullpath, _output_dir)
        else:
            err_reason = f'Not supported extension: {output_extension}'
    if err_reason:
        logger.info(f'get_osslist: {err_reason}')
    return oss_list


def check_exclude_dir(oss_list):
    _exclude_dirs = ["venv", "node_modules", "Pods", "Carthage"]

    for oss_item in oss_list:
        if not oss_item.source_name_or_path:
            continue
        for exclude_dir in _exclude_dirs:
            if exclude_dir in oss_item.source_name_or_path[0].split(os.path.sep):
                oss_item.exclude = True
                break
    return oss_list
