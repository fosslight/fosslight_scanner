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
    if status == ADD or status == DELETE:
        oi_ver = '' if oi['version'] == '' else f"({oi['version']})"
        oss_info = f"{oi['name']}{oi_ver}"
        license_info = f"{', '.join(oi['license'])}"
        if status == ADD:
            compared_row = [status, '', '', oss_info, license_info]
        elif status == DELETE:
            compared_row = [status, oss_info, license_info, '', '']
    elif status == CHANGE:
        oss_before, oss_after, license_before, license_after = [], [], [], []
        for prev_i in oi['prev']:
            prev_i_ver = '' if prev_i['version'] == '' else f"({prev_i['version']})"
            oss_before.append(f"{oi['name']}{prev_i_ver}")
            license_before.append(f"{', '.join(prev_i['license'])}")
        for now_i in oi['now']:
            now_i_ver = '' if now_i['version'] == '' else f"({now_i['version']})"
            oss_after.append(f"{oi['name']}{now_i_ver}")
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
    html_f = ''

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
    html_f = get_sample_html()
    if html_f != '':
        try:
            f = BeautifulSoup(html_f.read(), 'html.parser')
            f.find("li", {"class": "before_f"}).append(before_yaml)
            f.find("li", {"class": "after_f"}).append(after_yaml)

            table_html = f.find("table", {"id": "comp_result"})

            status = [ADD, DELETE, CHANGE]
            row = 2
            MIN_ROW_NUM = 100
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
                    if row >= MIN_ROW_NUM + 2:
                        p = f.new_tag('p')
                        p.string = "(!) There are so many different oss.\
                                    See the attached excel file for the full comparison result."
                        p.attrs = {"style": "font-weight:bold; color:red; font-size:15px"}
                        table_html.insert_before(p)
                        break
                else:
                    continue
                break

            if row == 2:
                tr = f.new_tag('tr')
                td = f.new_tag('td')
                td.string = 'Same'
                td.attrs = {"style": "padding:5px;"}
                tr.insert(0, td)
                for i in range(1, 5):
                    td = f.new_tag('td')
                    td.string = ''
                    td.attrs = {"style": "padding:5px;"}
                    tr.insert(i, td)
                table_html.insert(row, tr)

            with open(output_file, "wb") as f_out:
                f_out.write(f.prettify("utf-8"))
        except Exception as e:
            logger.error(f'Fail to write html file: {e}')
            ret = False
    else:
        ret = False
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
        if row == 1:
            worksheet.write_row(row, 0, ['Same', '', '', '', ''])
        workbook.close()
    except Exception as e:
        logger.error(f'Fail to write xlsx file: {e}')
        ret = False

    return ret


def write_compared_result(output_file, compared_result, file_ext, before_yaml='', after_yaml=''):
    success = False
    if file_ext == "" or file_ext == ".xlsx":
        success = write_result_xlsx(output_file, compared_result)
    elif file_ext == ".html":
        output_xlsx_file = os.path.splitext(output_file)[0] + ".xlsx"
        success_xlsx = write_result_xlsx(output_xlsx_file, compared_result)
        success = write_result_html(output_file, compared_result, before_yaml, after_yaml)
        if not success_xlsx:
            logger.error("Fail to write comparison excel file.")
        else:
            logger.info(f"In html format, {output_xlsx_file} is generated by default.")
            output_file = f"{output_xlsx_file}, {output_file}"
    elif file_ext == ".json":
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    elif file_ext == ".yaml":
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    else:
        logger.info("Not supported file extension")

    return success, output_file


def get_comparison_result_filename(output_path, output_file, output_extension, _start_time):
    result_file = ""
    if output_file != "":
        result_file = f"{output_file}{output_extension}"
    else:
        if output_extension == '.xlsx' or output_extension == "":
            result_file = f"FOSSLight_Compare_{_start_time}.xlsx"
        elif output_extension == '.html':
            result_file = f"FOSSLight_Compare_{_start_time}.html"
        elif output_extension == '.yaml':
            result_file = f"FOSSLight_Compare_{_start_time}.yaml"
        elif output_extension == '.json':
            result_file = f"FOSSLight_Compare_{_start_time}.json"
        else:
            logger.error("Not supported file extension")

    result_file = os.path.join(output_path, result_file)

    return result_file


def run_compare(before_yaml, after_yaml, output_path, output_file, file_ext, _start_time):
    ret = False
    logger.info("Start compare mode")
    logger.info(f"before file: {before_yaml}")
    logger.info(f"after file: {after_yaml}")

    result_file = get_comparison_result_filename(output_path, output_file, file_ext, _start_time)
    compared_result = compare_yaml(before_yaml, after_yaml)
    if compared_result != '':
        ret, result_file = write_compared_result(result_file, compared_result, file_ext, before_yaml, after_yaml)
        if ret:
            logger.info(f"Success to write compared result: {result_file}")
        else:
            logger.error("Fail to write compared result file.")

    return ret
