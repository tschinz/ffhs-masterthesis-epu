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


def getListOfFiles(dirName, recursive=True, abspath=False):
  """ For the given path, get the List of all files in the directory tree

  Args:
      dirName (str): Path of the directory
      recursive (bool, optional): Flag for seraching recursively. Defaults to True.
      abspath (bool, optional): Return list of files as absolute path or not. Defaults to False.

  Returns:
      list: List of all found files
  """
  listOfFile = os.listdir(dirName)
  allFiles = []
  for entry in listOfFile:
    fullPath = os.path.join(dirName, entry)
    if os.path.isdir(fullPath):
      if recursive:
        allFiles = allFiles + getListOfFiles(fullPath)
    else:
      if abspath:
        allFiles.append(os.path.abspath(fullPath))
      else:
        allFiles.append(fullPath)
  return allFiles


def randomword(length):
  """ Get random word of a given length

  Args:
      length (int): character size to generate

  Returns:
      str: random word of given length
  """
  return ''.join(random.choice(string.lowercase) for i in range(length))


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
# Webcam Functions
#
def saveWebcamImage(path='', name='webcam', ext='.jpg', camera=0, show=False, yolo_hw=False, verbose=False):
  """ Launch webcam and save one image to disk

  Args:
      path (str, optional): Path to save the file. Defaults to ''.
      name (str, optional): Name, will be part of the filename. Defaults to 'webcam'.
      ext (str, optional): File extention. Defaults to '.jpg'.
      camera (int, optional): Identifier for camera to use (only if multiple cameras available). Defaults to 0.
      show (bool, optional): Show image with cv2. Defaults to False.
      verbose (bool, optional): More output. Defaults to False.

  Returns:
      str: Path of saved file
  """
  fpath = os.path.abspath(os.path.join(path, datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + name + ext))
  if yolo_hw:
    webcam = cv2.VideoCapture(camera)
  else:
    webcam = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
  ret, frame = webcam.read()
  if show:
    cv2.imshow('frame', frame)
  if verbose:
    print("save webcam image")
    print(fpath)
  cv2.imwrite(fpath, frame)
  return fpath


def getWebcamImage(camera=0, show=False):
  """ Launch webcam and return image

  Args:
      camera (int, optional):Identifier for camera to use (only if multiple cameras available). Defaults to 0.
      show (bool, optional): Show image with cv2. Defaults to False.

  Returns:
      image: captures frame object
  """
  webcam = cv2.VideoCapture(camera, cv2.CAP_DSHOW)
  ret, frame = webcam.read()
  if show:
    cv2.imshow('frame', frame)
  return frame


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


def displayFileNotebook(fname):
  """ Open image and display it in a notebook

  Args:
      fname (str): Filepath to image

  Returns:
      None
  """
  im = Image.open(fname)
  display(im)


def displayImageCv2(image, window_title=None, waitKey=True):
  """ Display image it in cv2 window

  Args:
      image (obj): image object

  Returns:
      None
  """
  if window_title is None:
    window_title =  datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "- Image"
  cv2.imshow(window_title, image)
  if waitKey:
    # to avoid python kernel from crashing
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def displayFileCv2(fname, waitKey=True):
  """ Open file and display it in cv2 window

  Args:
      fname (str): Filepath to image

  Returns:
      None
  """
  image = cv2.imread(fname)
  displayImageCv2(image, fname, waitKey)


def getImage(fname):
  """ Open file and return image

  Args:
      fname (str): filepath to open

  Retruns:
      image (obj): image object
  """
  return cv2.imread(fname)
