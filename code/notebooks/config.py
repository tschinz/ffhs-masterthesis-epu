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
import sys, os

###############################################################################
# Constants
#
# Log level
#loglevel = logging.DEBUG
#loglevel = logging.INFO
verbose = True
dev_mode = True

# folders
CWD = os.getcwd()

# python config
PYTHON_PATH = '/usr/local/lib/python3.6'
BASE_PATH = os.path.dirname(os.path.realpath(__file__))

# darknet config
DARKNET_PATH = '/opt/darknet'
DARKNET_PATH_PYTHON = DARKNET_PATH + os.sep + "python" + os.sep

# Input config
DATA_PATH = os.path.abspath(CWD + os.sep + os.pardir + os.sep + os.pardir + os.sep + 'mas_data')

# Images
IMAGES_PATH = os.path.abspath(CWD + os.sep + os.pardir + os.sep + os.pardir + os.sep + os.pardir + os.sep + 'mas_data' + os.sep + 'webcam')
#SOURCEIMAGES_PATH = os.path.abspath(DATA_PATH + os.sep + 'images' + os.sep + '416px')
SOURCEIMAGES_PATH = os.path.abspath(DATA_PATH + os.sep + 'images' + os.sep + 'selection')
WEBCAM_PATH = './../../mas_data/webcam'
IN_EXT = '.jpg'
OUT_EXT = '.png'
PLOT_EXT = '.pdf'

# Output config
OUT_PATH = os.path.abspath(CWD + os.sep + os.pardir + os.sep + 'output')
if not os.path.isdir(OUT_PATH):
  os.makedirs(OUT_PATH)

# image repo config
if not os.path.isdir(IMAGES_PATH):
  os.makedirs(IMAGES_PATH)
if not os.path.isdir(WEBCAM_PATH):
  os.makedirs(WEBCAM_PATH)

# Timelogs, webcam and detection path
WEBCAM_PATH = os.path.abspath(OUT_PATH + os.sep + 'webcam')
if not os.path.isdir(WEBCAM_PATH):
  os.makedirs(WEBCAM_PATH)

DETECTION_PATH = os.path.abspath(OUT_PATH + os.sep + 'detection')
if not os.path.isdir(DETECTION_PATH):
  os.makedirs(DETECTION_PATH)

TIMELOGS_PATH = os.path.abspath(OUT_PATH + os.sep + 'timelogs')
if not os.path.isdir(TIMELOGS_PATH):
  os.makedirs(TIMELOGS_PATH)

LOG_PATH = os.path.abspath(OUT_PATH + os.sep + 'logs')
if not os.path.isdir(LOG_PATH):
  os.makedirs(LOG_PATH)

PLOT_PATH = os.path.abspath(OUT_PATH + os.sep + 'plot')
if not os.path.isdir(PLOT_PATH):
  os.makedirs(PLOT_PATH)

# MQTT config
MQTT_BROKER ="localhost"
MQTT_USERNAME = "pynq"
MQTT_PASSWORD = "g86TpdguWjpQICvwVHhx"
MQTT_PORT = 1883
MQTT_KEEPALIVE= 60
MQTT_TOPIC_TEST = "test/index"
MQTT_TOPIC_UPTIME = "$SYS/broker/uptime"

# Timelogs compare
timelogs_setup = {'sw': [""],
                  'hw': ["Setup YOLO"],
                 }
timelogs_loading = {'sw': ["Image Loading"],
                    'hw': ["Image Loading"],
                   }
timelogs_yolo = {'sw': ["Apply Conv Layers (SW)"],
                 'hw': ["Apply YOLO SW Conv Layer 0", "Apply YOLO HW Conv Layer 1-7", "Apply YOLO SW Conv Layer 8"],
                }
timelogs_detection = {'sw': ["Draw Detection Boxes"],
                      'hw': ["Draw Detection Boxes"],
                     }

timelogs_sw = ["Image Loading", "Apply Conv Layers (SW)", "Draw Detection Boxes"]
timelogs_hw = ["Setup YOLO", "Image Loading", "Apply YOLO SW Conv Layer 0", "Apply YOLO HW Conv Layer 1-7", "Apply YOLO SW Conv Layer 8", "Draw Detection Boxes"]

# Devices
hr_devices = {'zell-sw': 'Dell XPS 13 9300',
              'pynq-hw': 'Xilinx PYNQ-Z1 SW/HW',
              'pynq-sw': 'Xilinx PYNQ-Z1 SW'}