#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - config

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

###############################################################################
# Import
#
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


###############################################################################
# ini config
#
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(BASE_PATH, INI_FILE)))

dev_mode = config['APP']['dev_mode'].lower() in ['true', '1', 'y', 'yes']
capture_interval = int(config['APP']['capture_interval'])
static_images = config['APP']['static_images'].lower() in ['true', '1', 'y', 'yes']
save_images = config['APP']['save_images'].lower() in ['true', '1', 'y', 'yes']
show_images = config['APP']['show_images'].lower() in ['true', '1', 'y', 'yes']
use_yolo_hw = config['APP']['yolo_hw'].lower() in ['true', '1', 'y', 'yes']

config['PYTHON']['python_path'] = os.path.realpath(config['PYTHON']['python_path'])
config['DARKNET_HW']['darknet_path'] = os.path.realpath(config['DARKNET_HW']['darknet_path'])
config['DARKNET_HW']['darknet_path_python'] = os.path.realpath(config['DARKNET_HW']['darknet_path_python'])
config['DARKNET_SW']['darknet_path'] = os.path.realpath(config['DARKNET_SW']['darknet_path'])
config['DARKNET_SW']['darknet_cfg_path'] = os.path.realpath(config['DARKNET_SW']['darknet_cfg_path'])
config['DARKNET_SW']['darknet_weights_path'] = os.path.realpath(config['DARKNET_SW']['darknet_weights_path'])

config['PATH']['log_path'] = os.path.realpath(config['PATH']['log_path'])
config['PATH']['timelog_path'] = os.path.realpath(config['PATH']['timelog_path'])
config['PATH']['output_path'] = os.path.realpath(config['PATH']['output_path'])
config['PATH']['raw_image_path'] = os.path.realpath(config['PATH']['raw_image_path'])
config['PATH']['input_image_path'] = os.path.realpath(config['PATH']['input_image_path'])
config['PATH']['detection_image_path'] = os.path.realpath(config['PATH']['detection_image_path'])

###############################################################################
# create folders
#
if not os.path.isdir(config['PATH']['output_path']):
  os.makedirs(config['PATH']['output_path'])
if not os.path.isdir(config['PATH']['raw_image_path']):
  os.makedirs(config['PATH']['raw_image_path'])
if not os.path.isdir(config['PATH']['detection_image_path']):
  os.makedirs(config['PATH']['detection_image_path'])
if not os.path.isdir(config['PATH']['timelog_path']):
  os.makedirs(config['PATH']['timelog_path'])
