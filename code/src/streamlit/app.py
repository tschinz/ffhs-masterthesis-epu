#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - app

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

from functions import *
from config import *
import helpers
import mqtt_client


###############################################################################
# Setup
#
state = True
mqttClient = mqtt_client.MqttClient(address=config['MQTT']['address'],
                                    port=int(config['MQTT']['port']),
                                    username=config['MQTT']['username'],
                                    password=config['MQTT']['password'],
                                    keepAlive=int(config['MQTT']['keepalive']),
                                    topic_detection=config['MQTT']['topic_detection'],
                                    topic_state=config['MQTT']['topic_control_state'],
                                    lastWill=config['MQTT']['topic_lastwill'])


###############################################################################
# Sidebar
#
st.sidebar.title(sidebar_title)
if st.sidebar.button('Start'):
  state = True

if st.sidebar.button('Stop'):
  state = False

if st.sidebar.button('Reload'):
  state = True
  raise st.script_runner.RerunException(st.script_request_queue.RerunData(None))

###############################################################################
# Page
#
st.title(page_title)

if state:
  st.success("Detection is running")
else:
  st.error("Detection not running")

st.subheader("Image")
st_image = st.image(np.random.randint(0, 100, size=(480, 640)), caption=" No image received yet", use_column_width=True)
st.subheader("Detection")
st_json = st.json(mqttClient.detection)
mqttClient.setHandlers(st_image, st_json)
people_detected = 0
for key in mqttClient.detection:
  if mqttClient.detection[key] == "person":
    people_detected += 1

if people_detected > 0:
  st.warning("Warning {} people detected".format(people_detected))

###############################################################################
# Footer
#
st.markdown("---")
st.markdown("Made with :heart: by [{}]({})".format(author, author_url))
st.markdown("Sourcecode on [{}]({})".format(repo, repo_url))

# Connect MQTT
try:
  mqttClient.createConnection()
except Exception:
  print("Unable to connect to MQTT broker!")
  raise SystemExit

###############################################################################
# Execution
#
mqttClient.publishState(int(state))

#while True:
#  pass
st_image.image(mqttClient.filename, caption="Detection at {}".format(mqttClient.location), use_column_width=True)
st_json.write(mqttClient.detection)
