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
from fosslight_util.convert_excel_to_yaml import convert_excel_to_yaml

logger = logging.getLogger(constant.LOGGER_NAME)
ADD = "add"
DELETE = "delete"
CHANGE = "change"
COMP_STATUS = [ADD, DELETE, CHANGE]

JSON_EXT = '.json'
YAML_EXT = '.yaml'
HTML_EXT = '.html'
XLSX_EXT = '.xlsx'


def write_result_json_yaml(output_file, compared_result, file_ext):
    ret = True
    try:
        with open(output_file, 'w') as f:
            if file_ext == JSON_EXT:
                json.dump(compared_result, f, indent=4, sort_keys=True)
            elif file_ext == YAML_EXT:
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
    SAMPLE_HTML = f'bom_compare{HTML_EXT}'
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


def write_result_html(output_file, compared_result, before_f, after_f):
    ret = True
    html_f = get_sample_html()
    if html_f != '':
        try:
            f = BeautifulSoup(html_f.read(), 'html.parser')
            f.find("li", {"class": "before_f"}).append(before_f)
            f.find("li", {"class": "after_f"}).append(after_f)

            table_html = f.find("table", {"id": "comp_result"})

            row = 2
            MIN_ROW_NUM = 100
            for st in COMP_STATUS:
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

        workbook = xlsxwriter.Workbook(output_file)
        worksheet = workbook.add_worksheet('BOM_compare')
        bold = workbook.add_format({'bold': True})
        worksheet.write_row(0, 0, HEADER, bold)

        row = 1
        for st in COMP_STATUS:
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


def write_compared_result(output_file, compared_result, file_ext, before_f='', after_f=''):
    success = False
    if file_ext == "" or file_ext == XLSX_EXT:
        success = write_result_xlsx(output_file, compared_result)
    elif file_ext == HTML_EXT:
        output_xlsx_file = f'{os.path.splitext(output_file)[0]}{XLSX_EXT}'
        success_xlsx = write_result_xlsx(output_xlsx_file, compared_result)
        success = write_result_html(output_file, compared_result, before_f, after_f)
        if not success_xlsx:
            logger.error("Fail to write comparison excel file.")
        else:
            logger.info(f"In html format, {output_xlsx_file} is generated by default.")
            output_file = f"{output_xlsx_file}, {output_file}"
    elif file_ext == JSON_EXT:
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    elif file_ext == YAML_EXT:
        success = write_result_json_yaml(output_file, compared_result, file_ext)
    else:
        logger.info("Not supported file extension")

    return success, output_file


def get_comparison_result_filename(output_path, output_file, output_extension, _start_time):
    result_file = ""
    compare_prefix = f"fosslight_compare_{_start_time}"
    if output_file != "":
        result_file = f"{output_file}{output_extension}"
    else:
        if output_extension == XLSX_EXT or output_extension == "":
            result_file = f"{compare_prefix}{XLSX_EXT}"
        elif output_extension == HTML_EXT:
            result_file = f"{compare_prefix}{HTML_EXT}"
        elif output_extension == YAML_EXT:
            result_file = f"{compare_prefix}{YAML_EXT}"
        elif output_extension == JSON_EXT:
            result_file = f"{compare_prefix}{JSON_EXT}"
        else:
            logger.error("Not supported file extension")

    result_file = os.path.join(output_path, result_file)

    return result_file


def count_compared_result(compared_result):
    comp_len = [len(compared_result[st]) for st in COMP_STATUS]
    if sum(comp_len) == 0:
        count_str = "all oss lists are the same."
    else:
        count_str = f"total {sum(comp_len)} oss updated ("
        count_str += ', '.join([f"{COMP_STATUS[x]}: {comp_len[x]}" for x in range(0, 3)]) + ")"
    logger.info(f"Comparison result: {count_str}")


def run_compare(before_f, after_f, output_path, output_file, file_ext, _start_time, _output_dir):
    ret = False
    before_yaml = ''
    after_yaml = ''
    logger.info("Start compare mode")
    logger.info(f"before file: {before_f}")
    logger.info(f"after file: {after_f}")

    before_ext = f'.{os.path.basename(before_f).split(".")[-1]}'
    after_ext = f'.{os.path.basename(after_f).split(".")[-1]}'
    if before_ext != after_ext:
        logger.error("Please enter the two FOSSLight report with the same file extension.")
        return False
    if before_ext not in [YAML_EXT, XLSX_EXT]:
        logger.error(f"Compare mode only supports 'yaml' or 'xlsx' extension. (input extension:{before_ext})")
        return False
    else:
        tmp_b_yaml = f'{os.path.basename(before_f).rstrip(XLSX_EXT)}{YAML_EXT}'
        before_yaml = before_f if before_ext == YAML_EXT else os.path.join(_output_dir, tmp_b_yaml)
        tmp_a_yaml = f'{os.path.basename(after_f).rstrip(XLSX_EXT)}{YAML_EXT}'
        after_yaml = after_f if after_ext == YAML_EXT else os.path.join(_output_dir, tmp_a_yaml)

    result_file = get_comparison_result_filename(output_path, output_file, file_ext, _start_time)

    if before_ext == XLSX_EXT:
        convert_excel_to_yaml(before_f, before_yaml)
        convert_excel_to_yaml(after_f, after_yaml)
    compared_result = compare_yaml(before_yaml, after_yaml)
    if compared_result != '':
        count_compared_result(compared_result)
        ret, result_file = write_compared_result(result_file, compared_result, file_ext, before_yaml, after_yaml)
        if ret:
            logger.info(f"Success to write compared result: {result_file}")
        else:
            logger.error("Fail to write compared result file.")

    return ret
