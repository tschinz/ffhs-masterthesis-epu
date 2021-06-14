#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS Machine Learning Project - yolo sw

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

###############################################################################
# Import
#
import csv
import os
import platform
from datetime import datetime
import time
import helpers


class Timer:
  """ Class to save and export measured timing down to a ms precision
  """

  def __init__(self, title=None, verbose=False, report=False, filewrite=True, file=None, index=0):
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
    self.fields = ["index", "type", "time", "text"]
    self.filewrite = filewrite
    self.index = index
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
    self.log = helpers.createLogger(__name__)
    if self.filewrite:
      self.writeCsvHeader()

  def nextIndex(self):
    """ Increment the index to indicate the next measurement series
    """
    self.index += 1

  def trigger(self, text=None):
    """trigger for capture the current timestamp (start of beginning)

    Args:
        text (str, optional): Additional text to add to timestamp. Defaults to None.
    """
    self.times.append([self.index, self.timetype, datetime.now(), text])

  def calc(self, text=None):
    """calculate the time delta from the two previous timestamps

    Args:
        text (str, optional): Additional text to add to time delta. Defaults to None.

    Returns:
        datetime: datetime timedelta object
    """
    duration = self.times[-1][2] - self.times[-2][2]
    self.times.append([self.index, self.durationtype, duration, text])
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
    if self.times[-1][1] == self.durationtype:
      desc = "Duration"
    elif self.times[-1][1] == self.timetype:
      desc = "Timestamp"

    out = ""
    if self.times[-1][3] is not None:
      out = "{} of {} is {}".format(desc, self.times[-1][3], self.times[-1][2])
    else:
      out = "{} is {}".format(str(desc, self.times[-1][2]))
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
      self.log.info(self.reporting())
    if self.filewrite:
      self.writeCsvRow(self.times[-3:], append=True)
      del self.times[-3:]

  def dumpToCsv(self):
    """dump timeentries to csv file
    """
    with open(self.file, 'w+', newline='') as f:
      write = csv.writer(f)
      write.writerow(self.fields)
      write.writerows(self.times)

  def writeCsvHeader(self):
    """Create or append to csv file the last timeentry recorded

    Args:
        rows (list): timeentry list [type, time, text]
        append (bool, optional): append to existing file or start fresh. Defaults to True.
    """
    with open(self.file, 'w+', newline='') as f:
      write = csv.writer(f)
      write.writerow(self.fields)

  def writeCsvRow(self, rows, append=True):
    """Create or append to csv file the last timeentry recorded

    Args:
        rows (list): timeentry list [type, time, text]
        append (bool, optional): append to existing file or start fresh. Defaults to True.
    """
    if append:
      with open(self.file, 'a+', newline='') as f:
        write = csv.writer(f)
        if isinstance(rows[0], int):
          write.writerow(rows)
        else:
          write.writerows(rows)
    else:
      with open(self.file, 'w+', newline='') as f:
        write = csv.writer(f)
        write.writerow(self.fields)
        if isinstance(rows[0], int):
          write.writerow(rows)
        else:
          write.writerows(rows)

  def getTimes(self):
    """Getter method for all recorded time entries
    [type, time, text]

    Returns:
        list: time entries
    """
    return self.times
