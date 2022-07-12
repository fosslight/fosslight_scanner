#!/usr/bin/env python
# -*- coding: utf-8 -*-
# FOSSLight Scanner
# Copyright (c) 2022 LG Electronics Inc.
# SPDX-License-Identifier: Apache-2.0
import os
import sys
import json
import yaml
import logging
import xlsxwriter
import codecs
from pathlib import Path
from bs4 import BeautifulSoup
import fosslight_util.constant as constant
from fosslight_util.compare_yaml import compare_yaml

logger = logging.getLogger(constant.LOGGER_NAME)
ADD = "add"
DELETE = "delete"
CHANGE = "change"


def write_result_json_yaml(output_file, compared_result, file_ext):
    ret = True
    try:
        with open(output_file, 'w') as f:
            if file_ext == '.json':
                json.dump(compared_result, f, indent=4, sort_keys=True)
            elif file_ext == '.yaml':
                yaml.dump(compared_result, f, sort_keys=True)
    except Exception:
        ret = False
    return ret


def parse_result_for_table(oi, status):
    compared_row = []
    if status == ADD:
        oss_after = f"{oi['name']} ({oi['version']})"
        license_after = f"{', '.join(oi['license'])}"
        compared_row = [status, '', '', oss_after, license_after]
    elif status == DELETE:
        oss_before = f"{oi['name']} ({oi['version']})"
        license_before = f"{', '.join(oi['license'])}"
        compared_row = [status, oss_before, license_before, '', '']
    elif status == CHANGE:
        oss_before, oss_after, license_before, license_after = [], [], [], []
        for prev_i in oi['prev']:
            oss_before.append(f"{oi['name']} ({prev_i['version']})")
            license_before.append(f"{', '.join(prev_i['license'])}")
        for now_i in oi['now']:
            oss_after.append(f"{oi['name']} ({now_i['version']})")
            license_after.append(f"{', '.join(now_i['license'])}")
        compared_row = [status, ' / '.join(oss_before), ' / '.join(license_before),
                                ' / '.join(oss_after), ' / '.join(license_after)]
    else:
        logger.error(f"Not supported compared status: {status}")

    return compared_row


def get_sample_html():
    RESOURCES_DIR = 'resources'
    SAMPLE_HTML = 'bom_compare.html'
    html_file = os.path.join(RESOURCES_DIR, SAMPLE_HTML)

    try:
        base_dir = sys._MEIPASS
    except Exception:
        base_dir = os.path.dirname(__file__)

    file_withpath = os.path.join(base_dir, html_file)
    try:
        html_f = codecs.open(file_withpath, 'r', 'utf-8')
    except Exception as ex:
        logger.error(f"Error to get sample html file : {ex}")

    return html_f


def write_result_html(output_file, compared_result, before_yaml, after_yaml):
    ret = True

    f = BeautifulSoup(get_sample_html().read(), 'html.parser')
    f.find("li", {"class": "before_f"}).append(before_yaml)
    f.find("li", {"class": "after_f"}).append(after_yaml)

    table_html = f.find("table", {"id": "comp_result"})

    status = [ADD, DELETE, CHANGE]
    row = 2
    for st in status:
        for oi in compared_result[st]:
            compared_row = parse_result_for_table(oi, st)
            tr = f.new_tag('tr')
            for i, ci in enumerate(compared_row):
                td = f.new_tag('td')
                td.string = ci
                td.attrs = {"style": "padding:5px;"}
                tr.insert(i, td)
            table_html.insert(row, tr)
            row += 1

    with open(output_file, "wb") as f_out:
        f_out.write(f.prettify("utf-8"))
    return ret


def write_result_xlsx(output_file, compared_result):
    HEADER = ['Status', 'OSS_Before', 'License_Before', 'OSS_After', 'License_After']
    ret = True

    try:
        output_dir = os.path.dirname(output_file)
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        workbook = xlsxwriter.Workbook(os.path.basename(output_file))
        worksheet = workbook.add_worksheet('BOM_compare')
        bold = workbook.add_format({'bold': True})
        worksheet.write_row(0, 0, HEADER, bold)

        row = 1
        status = [ADD, DELETE, CHANGE]
        for st in status:
            for oi in compared_result[st]:
                compared_row = parse_result_for_table(oi, st)
                worksheet.write_row(row, 0, compared_row)
                row += 1
        workbook.close()
    except Exception:
        ret = False

    return ret


def write_compared_result(output_file, compared_result, file_ext, before_yaml='', after_yaml=''):
    success = False
    if file_ext == "" or file_ext == ".xlsx":
        success = write_result_xlsx(output_file, compared_result)
    elif file_ext == ".html":
        success = write_result_html(output_file, compared_result, before_yaml, after_yaml)
    elif file_ext == ".json":
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    elif file_ext == ".yaml":
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    else:
        logger.info("Not supported file extension")

    return success


def run_compare(before_yaml, after_yaml, output_file, file_ext):
    ret = False
    logger.info("Start compare mode")

    compared_result = compare_yaml(before_yaml, after_yaml)
    if compared_result != '':
        ret = write_compared_result(output_file, compared_result, file_ext, before_yaml, after_yaml)
        if ret:
            logger.info(f"Success to write compared result: {output_file}")
        else:
            logger.error("Fail to write compared result file.")

    return ret