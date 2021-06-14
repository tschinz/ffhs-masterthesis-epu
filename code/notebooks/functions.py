#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - functions

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""
###############################################################################
# Import
#
# Import required sub-modules
import sys
import os, platform
import json
import numpy as np
import cv2
import ctypes
import time

from rich import print
from rich.logging import RichHandler
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

import logging

import csv
import pandas as pd
import plotly.express as px

from PIL import Image
from datetime import datetime, timedelta

from matplotlib import pyplot as plt

import re

# import config
from config import *

###############################################################################
# Common Functions
#
def getListOfFiles(dirName, recursive=True, abspath=False):
  """For the given path, get the List of all files in the directory tree

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

def saveWebcamImage(path = '', name='webcam', ext='.jpg', camera=0, show=False, verbose=False):
  """Launch webcam and save one image to disk

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
  fpath = path + os.sep + name+ '-' + datetime.now().strftime("%Y%m%d-%H%M%S-%f") + ext
  webcam = cv2.VideoCapture(camera)
  ret, frame = webcam.read()
  if show:
    cv2.imshow('frame', frame)
  if verbose:
    print("save webcam image")
    print(fpath)
  cv2.imwrite(fpath, frame)
  return fpath

def getWebcamImage(camera=0, show=False):
  """Launch webcam and return image

  Args:
      camera (int, optional):Identifier for camera to use (only if multiple cameras available). Defaults to 0.
      show (bool, optional): Show image with cv2. Defaults to False.

  Returns:
      image: captures frame object
  """
  webcam = cv2.VideoCapture(camera)
  ret, frame = webcam.read()
  if show:
    cv2.imshow('frame', frame)
  return frame

###############################################################################
# Rich logger
#
###############################################################################
# Logging Functions
#
rich_config = {
    # 'level': logging.DEBUG,
    'show_time': True,
    'show_level': True,
    'show_path': False,
    'markup': True,
    'rich_tracebacks': True
}
#rich_format = "%Y-%m-%d %H:%M:%S"
rich_format = "%H:%M:%S"


def createHandler(dev_mode, base_path, name):
  """ Create log handler

  Args:
      dev_mode (bool): developer mode or not
      base_path ([type]): path for logfile

  Returns:
      [obj]: handler object
  """
  if not dev_mode:
    FORMAT = '%(asctime)s - %(name)s - %(message)s'
    handler = logging.FileHandler(os.path.abspath(os.path.join(base_path, datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + name + '.log')),
                                  mode="a", encoding="utf-8", delay=False)
  else:
    FORMAT = '%(message)s'
    handler = RichHandler(**rich_config)

  # setting the level parameter with basicConfig will set the level for all python modules
  logging.basicConfig(
      format=FORMAT, datefmt=rich_format, handlers=[handler])

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

def createConsole(name, level=None):
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
# Image functions
#
def displayFile(fname):
  """Launch webcam and return image

  Args:
      fname (str): Filepath to display

  Returns:
      None
  """
  im = Image.open(fname)
  display(im)

###############################################################################
# Timer Class
#
class Timer:
  """ Class to save and export measured timing down to a ms precision
  """
  def __init__(self, title=None, verbose=False, report=False, filewrite=True, file=None):
    """Constructor for timer class

    Args:
        title (str, optional): title of timing measurements. Defaults to None.
        verbose (bool, optional): more output. Defaults to False.
        report (bool, optional): console output of timings. Defaults to False.
        filewrite (bool, optional): write to csv file. Defaults to True.
        file (str, optional): filepath for csv file. Defaults to None.
    """
    self.times = []
    self.verbose = verbose
    self.report = report
    self.title = title
    self.timetype = 0
    self.durationtype = 1
    self.fields = ["type", "time", "text"]
    self.filewrite = filewrite
    if file is not None:
      self.file = file
    else:
      if self.title is not None:
        self.file = self.title + ".csv"
      else:
        self.file = "times.csv"
    if os.path.splitext(self.file)[1] != ".csv":
      self.file += ".csv"
    self.file = os.path.split(self.file)[0] + os.sep + time.strftime("%Y%m%d%H%M", time.localtime()) + "-" + platform.node() + "-" + os.path.split(self.file)[1]


  def trigger(self, text=None):
    """trigger for capture the current timestamp (start of beginning)

    Args:
        text (str, optional): Additional text to add to timestamp. Defaults to None.
    """
    self.times.append([self.timetype, datetime.now(), text])

  def calc(self, text=None):
    """calculate the time delta from the two previous timestamps

    Args:
        text (str, optional): Additional text to add to time delta. Defaults to None.

    Returns:
        datetime: datetime timedelta object
    """
    duration = self.times[-1][1] - self.times[-2][1]
    self.times.append([self.durationtype, duration, text])
    return duration

  def verbose(self, verbose=False):
    """Changing verbosity

    Args:
        verbose (bool, optional): value verbose to change to. Defaults to False.
    """
    self.verbose = verbose

  def reporting(self):
    """Generate report from the last entry. Timestamp or timedelta.

    Returns:
        str: report string from last entry
    """
    if self.times[-1][0] == self.durationtype:
      desc="Duration"
    elif self.times[-1][0] == self.timetype:
      desc="Timestamp"

    out = ""
    if self.times[-1][2] is not None:
      out = "{} of {} is {}".format(desc, self.times[-1][2], self.times[-1][1])
    else:
        out = "{} is {}".format(str(desc, self.times[-1][1]))
    return out

  def end(self, triggertext=None, durationtext=None):
    """Method to end a measurement. It will trigger the end, generate a reporting and saving it to file if neccessary

    Args:
        triggertext (str, optional): text for the trigger entry. Defaults to None.
        durationtext (str, optional): text for the timedelta entry. Defaults to None.
    """
    if triggertext is not None:
      self.trigger(triggertext)
    elif durationtext is not None:
      self.trigger(durationtext)
    else:
      self.trigger(self.title)

    if durationtext is not None:
      self.calc(durationtext)
    elif triggertext is not None:
      self.calc(triggertext)
    else:
      self.calc(self.title)

    if self.report:
      print(self.reporting())
    if self.filewrite:
      self.writeCsv(self.times[-1], append=True)
      del self.times[-1]

  def dumpToCsv(self):
    """dump timeentries to csv file
    """
    with open(self.file, 'w+', newline='') as f:
        write = csv.writer(f)
        write.writerow(self.fields)
        write.writerows(self.times)

  def writeCsv(self, rows, append=True):
    """Create or append to csv file the last timeentry recorded

    Args:
        rows (list): timeentry list [type, time, text]
        append (bool, optional): append to existing file or start fresh. Defaults to True.
    """
    if append:
      with open(self.file, 'a+', newline='') as f:
        write = csv.writer(f)
        write.writerows(rows)
    else:
      with open(self.file, 'w+', newline='') as f:
        write = csv.writer(f)
        write.writerow(self.fields)
        write.writerows(rows)

  def getTimes():
    """Getter method for all recorded time entries
       [type, time, text]
    Returns:
        list: time entries
    """
    return self.times

###############################################################################
# Timing Compare
#
def scatterPlot():
  fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species", marginal_y="violin",
           marginal_x="box", trendline="ols", template="simple_white")
  fig.show()