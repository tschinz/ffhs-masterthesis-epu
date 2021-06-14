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
import math
import paho.mqtt.client as mqtt
import helpers
import json
import os


class MqttClient:
  """MQTT client model.

  Args:
    address (int): Default=None. MQTT broker IP address.
    port (int): Default=1883. MQTT broker port
    username (str): Default=None. Username to connect to the broker.
    password (str): Default=None. Password to connect to the broker.
    keepAlive (int): Default=60. Keepalive in seconds.
    retain (bool): Default=True. A boolean that determines if a message is retained or not.
    packetSize (int): size of packets in case of image transmission
    topic_detection (str): Default="v/detection". Topic were detection outputs are published
    lastWill (str): Default="yolo/status". Topic were the last will is published
    location (str): Default="not defined". identification of image location
  Returns:
    None
  """

  def __init__(self,
               address=None,
               port=1883,
               username=None,
               password=None,
               keepAlive=60,
               retain=True,
               packetsize=3000,
               topic_detection="yolo/detection",
               topic_state="yolo/state",
               lastWill="yolo/status",
               location="not defined"
               ):
    # default config, no address given as we don't want to spread code everywhere
    self.address = address
    self.port = port
    self.keepAlive = keepAlive
    self.retain = retain
    self.topic_detection = str(topic_detection).replace('"', '')
    self.topic_state = str(topic_state).replace('"', '')
    self.lastWill = str(lastWill).replace('"', '')
    self.username = username
    self.password = password
    self.packetsize = packetsize
    self.location = location
    self.client = mqtt.Client()
    self.log = helpers.createLogger(__name__)
    self.running = False

  def createConnection(self):
    """Create connection to MQTT broker.
    Link callbacks on messages and connection, set credentials, subscribe to input channel and
    set a last will message which indicates optimizer status.

    Args:
      None
    Returns:
      None
    """
    self.client.on_connect = self.on_connect
    self.client.on_message = self.on_message
    self.client.username_pw_set(
        username=self.username, password=self.password)
    self.client.connect(self.address, self.port, self.keepAlive)
    self.client.subscribe(self.topic_state)
    self.client.loop_start()
    self.client.will_set(
    self.lastWill, "The people detection stopped surreptitiously", retain=True)

    self.client.message_callback_add(self.topic_state, self.changeState)


  def changeState(self, client, userdata, msg):
    """Callback used to collect state to update and trigger a new planning

    Args:
        client ([type]): [description]
        usedata ([type]): [description]
        msg ([type]): [description]
    """
    try:
        running = int(msg.payload)
    except:
      self.log.error("The message is not properly formatted.. Value: %s, type: %s" % (msg.payload, type(msg.payload)))
      running = None

    if running is not None:
      if running == 1:
        self.running = True
      else:
        self.running = False


  def on_connect(self, client, userdata, flags, rc):
    """Connection callback on connection. Used as a feedback.
    As this is a lib mandatory function, please consult paho mqtt doc.

    Args:
      None
    Returns:
      None
    """
    self.log.info("Connected with result code " + str(rc))

  def on_message(self, client, userdata, msg):
    """Message callback.
    As this is a lib mandatory function, please consult paho mqtt doc.

    Args:
      None
    Returns:
      None
    """
    self.log.debug(msg.topic + " " + str(msg.payload))
    self.log.debug("received an input...")

  def publishMessage(self, message, topicOut):
    """Send a message to the broker using predefined channel.

    Args:
        message (str): Message to publish.
    Returns:
        None
    """

    self.log.debug("Publish message on topic '%s'" % topicOut)
    msginfo = self.client.publish(topicOut, message, retain=self.retain)
    if not msginfo.is_published() and int(msginfo.rc) != 0:
      self.log.error("Fail to publish to topic: '%s'. Error code: %s" % (topicOut, msginfo.rc))

  def publishDetection(self, labels=[], confidences=[], boxes=None, fpath="", image=None):
    """Create the json object for image detection.

    Args:
      labels (list): list of confidences of the boxes
      boxes (list): list of coordinates of detection boxes
      confidences (list): list of confidences of the boxes
      fpath (str): filepath to image
    Returns:
      None
    """
    json_elements = {}
    detections = []
    if len(labels) > 0 and (os.path.exists(fpath) or image is not None):
      for i in range(len(labels)):
        if boxes is None:
          detections.append({'labels':labels[i], 'confidences': confidences[i], 'box': -1})
        else:
          detections.append({'labels':labels[i], 'confidences': confidences[i], 'box': boxes[i]})
      json_elements['location'] = self.location
      json_elements['detections'] = detections
      if image is not None:
        json_elements['image'] = helpers.convertImageToBase64(image)
      else:
        json_elements['image'] = helpers.convertFileToBase64(fpath)
      jsonString = json.dumps(json_elements, indent=4)
      self.publishMessage(jsonString, self.topic_detection)
    else:
      self.log.info("Nothing detected")

  def disconnect(self):
    self.client.disconnect()
