#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os


def parse_setting_json(data):
    # check type, if invalid = init value
    mode = data.get('mode', [])
    path = data.get('path', [])
    dep_argument = data.get('dep_argument', '')
    outputDir = data.get('outputDir', '')
    outputFile = data.get('outputFile', '')
    format = data.get('format', '')
    link = data.get('link', [])
    db_url = data.get('db_url', '')
    timer = data.get('timer', False)
    raw = data.get('raw', False)
    core = data.get('core', -1)
    no_correction = data.get('no_correction', False)
    correct_fpath = data.get('correct_fpath', '')
    ui = data.get('ui', False)
    exclude_path = data.get('exclude_path', [])

    str_lists = [mode, path, link, exclude_path]
    strings = [dep_argument, outputDir, outputFile, format, db_url, correct_fpath]
    booleans = [timer, raw, no_correction, ui]
    is_incorrect = False

    # check if json file is incorrect format
    for i, target in enumerate(str_lists):
        if not (isinstance(target, list) and all(isinstance(item, str) for item in target)):
            is_incorrect = True
            str_lists[i] = []

    for i, target in enumerate(strings):
        if not isinstance(target, str):
            is_incorrect = True
            str_lists[i] = ''

    for i, target in enumerate(booleans):
        if not isinstance(target, bool):
            is_incorrect = True
            str_lists[i] = False

    if not isinstance(core, int):
        is_incorrect = True
        core = -1

    if (is_incorrect):
        print('Ignoring some values with incorrect format in the setting file.')

    if not mode:
        mode = ['all']
    final_mode = mode[0].split()
    if (not ("compare" in final_mode) and (len(path) > 0)):
        path = [path[0]]
    link = link[0] if (link and not path) else ''
    output = os.path.join(outputDir, outputFile)

    return final_mode, path, dep_argument, output, format, link, db_url, timer, \
        raw, core, no_correction, correct_fpath, ui, exclude_path
