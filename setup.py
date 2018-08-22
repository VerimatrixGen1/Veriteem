#!/usr/bin/env python
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import atexit
import os
import sys
import shutil

from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install

setup(
    name="veriteem",
    version="0.1.18",
    packages=find_packages('src'),
    package_dir={'':'src'},

    package_data={
         # include any asset files found in the 'veriteem' package:
        'veriteem': ['README.md', 'assets/*', 'bin/*', 'scripts/*' ],
    },
    scripts=['src/veriteem/VeriteemConfig.py',
             'src/veriteem/Veriteem.py',
            ],

    # metadata for upload to PyPI
    author="Brad Ree",
    author_email="bree@verimatrix.com",
    description="Veriteem Blockchain DLT",
    license="GPL",
    keywords="Verimatrix Blockchain Compliance Ledger ",
    url="https://github.com/VerimatrixGen1/Veriteem",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Documentation": "https://github.com/VerimatrixGen1/Veriteem/wiki",
        "Source Code": "https://github.com/VerimatrixGen1/Veriteem",
    }

    # could also include long_description, download_url, classifiers, etc.  
)
