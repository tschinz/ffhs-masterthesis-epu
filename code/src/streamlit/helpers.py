#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - helpers

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

###############################################################################
# Import
#
import string
import random
import os
import platform
import logging
import base64
from datetime import datetime
import cv2
from PIL import Image


from rich.logging import RichHandler
from rich.console import Console

###############################################################################
# Common Functions
#


###############################################################################
# Logging Functions
#
rich_config = {
    # 'level': logging.DEBUG,
    'show_time': True,
    'show_level': True,
    'show_path': True,
    'markup': True,
    'rich_tracebacks': True
}


def createHandler(dev_mode, base_path):
  """ Create log handler

  Args:
      dev_mode (bool): developer mode or not
      base_path ([type]): path for logfile

  Returns:
      [obj]: handler object
  """
  if not dev_mode:
    FORMAT = '%(asctime)s - %(name)s - %(message)s'
    handler = logging.FileHandler(os.path.abspath(os.path.join(base_path, datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + 'people_detection.log')),
                                  mode="a", encoding="utf-8", delay=False)
  else:
    FORMAT = '%(message)s'
    handler = RichHandler(**rich_config)

  # setting the level parameter with basicConfig will set the level for all python modules
  logging.basicConfig(
      format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S", handlers=[handler])

  # handler.setFormatter(formatter)
  return handler


def createLogger(name, level=None):
  """ Create logger module
  log levels = DEBUG < INFO < WARNING < ERROR < CRITICAL

  Args:
      name (str): name of the logging module
      level (str): logging level

  Returns:
      (obj): logger object
    """
  logger = logging.getLogger(name)
  if level is None:
    lvl_to_set = 'DEBUG'
  else:
    lvl_to_set = level
  logger.setLevel(lvl_to_set)
  return logger


###############################################################################
# Image Functions
#
def convertImageToBase64(image):
  """ Convert image to base64 for transmission

  Args:
      image (obj): opencv image  object
  Returns:
      (str): image encoded as base64
  """
  # im_arr: image in Numpy one-dim array format.
  _, im_arr = cv2.imencode('.jpg', image)
  im_bytes = im_arr.tobytes()
  return base64.b64encode(im_bytes).decode('utf-8')


def convertBase64toImage(image):
  """ Convert base64 to image from transmission

  Args:
      image (str): base 64 encoded image string
  Returns:
      (obj): image data
  """
  return base64.b64decode(image)


def convertFileToBase64(image_path):
  """ Convert image file to base64 for transmission

  Args:
      image_path (str): path to the image to be encoded
  Returns:
      (str): image encoded as base64
  """
  if os.path.isfile(image_path):
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode('utf-8')
  else:
    return -1