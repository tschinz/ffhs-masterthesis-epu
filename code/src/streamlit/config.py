#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - config

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

##############################################################################
# Import sub-modules
import sys
import os
import configparser
from config import *

###############################################################################
# Constants
#
CWD = os.getcwd()
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
INI_FILE = "app_config_pc.ini"
#INI_FILE = "app_config_pynq.ini"
# Change basepath
os.chdir(BASE_PATH)
MQTT_THREAD_CONNETION_WAIT = 0.5

###############################################################################
# ini config
#
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(BASE_PATH, INI_FILE)))

# folders
CWD = os.getcwd()

# Data Storage constants
asset_dir = 'assets'
data_dir = 'data'

###############################################################################
# app variables
#
page_title = 'Masterthesis HW Accelerated Yolo Detection'
author = 'Zahno Silvan'
author_url = 'https://github.com/tschinz'
sidebar_title = 'Controls'
repo = 'github'
repo_url = 'https://github.com/tschinz/ffhs-mas-ind4_0'

footer = "Made with :heart: by [{}]({})".format(author, author_url) + os.linesep