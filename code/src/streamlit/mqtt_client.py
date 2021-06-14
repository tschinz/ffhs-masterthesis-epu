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
from functions import *
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
    topic_detection (str): Default="yolo/detection". Topic were detection are published
    topic_state (str): Default="yolo/state". Topic were state outputs are published
    lastWill (str): Default="yolo/control/status". Topic were the last will is published
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
               lastWill="yolo/control/status"
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
    self.client = mqtt.Client()
    self.log = helpers.createLogger(__name__)

    self.image = None
    self.detection = {}
    self.location = None
    self.st_image = None
    self.st_json = None
    self.filename = "latest_detection.jpg"

  def setHandlers(self, st_image, st_json):
    self.st_image = st_image
    self.st_json = st_json

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
    self.client.subscribe(self.topic_detection)
    self.client.message_callback_add(self.topic_detection, self.detection_callback)
    thread = self.client._thread
    #thread = self.client._thread.join()
    st.report_thread.add_report_ctx(thread)
    time.sleep(MQTT_THREAD_CONNETION_WAIT)
    self.client.loop_start()
    self.client.will_set(self.lastWill, "The yolo control stopped surreptitiously", retain=True)


  def detection_callback(self, client, userdata, msg):
    """Callback used to collect the detection and displays its result

    Args:
        client ([type]): [description]
        usedata ([type]): [description]
        msg ([type]): [description]
    """
    try:
        detection = json.loads(msg.payload)
        self.location = detection['location']
        self.detection = detection['detections']
        self.image = helpers.convertBase64toImage(detection['image'])
    except:
      self.log.error("The message is not properly formatted.. Value: %s, type: %s" % (msg.payload, type(msg.payload)))

    with open(self.filename, 'wb') as f:
      f.write(self.image)

    #self.st_image.image(self.filename, caption="Detection at {}".format(self.location), use_column_width=True)
    #self.st_json.write(self.detection)

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

  def publishState(self, state=False):
    """Publish the new steate commands

    Args:
      state (bool): new state
    Returns:
      None
    """
    self.publishMessage(state, self.topic_state)

  def disconnect(self):
    self.client.disconnect()
