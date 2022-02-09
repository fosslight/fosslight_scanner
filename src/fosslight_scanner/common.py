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
        dest = copy(source, destination)
    except Exception as ex:
        logger.debug(f"Failed to copy {source} to {destination}: {ex}")
