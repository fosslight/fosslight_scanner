#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import logging
from shutil import copy
import re
import pandas as pd
import fosslight_util.constant as constant

logger = logging.getLogger(constant.LOGGER_NAME)


def copy_file(source, destination):
    try:
        copy(source, destination)
    except Exception as ex:
        logger.debug(f"Failed to copy {source} to {destination}: {ex}")


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
