#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2020 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import logging
from shutil import copy
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
            logger.info("|--- Path to analyze :" + path_to_run)
            os.chdir(output)
            sys.argv = params
            return_value = func()
            os.chdir(exe_path)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        pass
    except Exception as ex:
        logger.error(str_run_start + ":" + str(ex))
    return return_value


def call_analysis_api(path_to_run, str_run_start, return_idx, func, *args):
    # return_idx == -1 : Raw return value itself
    logger.info("## Start to run " + str_run_start)
    success = True
    result = []
    try:
        if path_to_run != "":
            logger.info("|--- Path to analyze :"+path_to_run)
            result = func(*args)
        else:
            logger.info("Analyzing path is missing...")
    except SystemExit:
        success = False
    except Exception as ex:
        success = False
        logger.error(str_run_start + ":" + str(ex))
    try:
        if success:
            if result and return_idx >= 0:
                if len(result) > return_idx:
                    result = result[return_idx]
                else:
                    success = False
    except Exception as ex:
        logger.debug("Get return value:" + str(ex))
        success = False
    if not result:
        result = []
    return success, result
