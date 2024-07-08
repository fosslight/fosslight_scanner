#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 LG Electronics
# SPDX-License-Identifier: Apache-2.0
from codecs import open
from setuptools import setup, find_packages


with open('README.md', 'r', 'utf-8') as f:
    readme = f.read()

with open('requirements.txt', 'r', 'utf-8') as f:
    required = f.read().splitlines()

if __name__ == "__main__":
    setup(
        name='fosslight_scanner',
        version='1.7.29',
        package_dir={"": "src"},
        packages=find_packages(where='src'),
        description='FOSSLight Scanner',
        long_description=readme,
        long_description_content_type='text/markdown',
        license='Apache-2.0',
        author='LG Electronics',
        url='https://github.com/fosslight/fosslight_scanner',
        download_url='https://github.com/fosslight/fosslight_scanner',
        classifiers=['License :: OSI Approved :: Apache Software License',
                     "Programming Language :: Python :: 3",
                     "Programming Language :: Python :: 3.8",
                     "Programming Language :: Python :: 3.9",
                     "Programming Language :: Python :: 3.10",
                     "Programming Language :: Python :: 3.11", ],
        python_requires=">=3.8",
        install_requires=required,
        package_data={'fosslight_scanner': ['resources/bom_compare.html']},
        entry_points={
            "console_scripts": [
                "fosslight = fosslight_scanner.cli:main",
                "fosslight_scanner = fosslight_scanner.cli:main"
            ]
        }
    )
