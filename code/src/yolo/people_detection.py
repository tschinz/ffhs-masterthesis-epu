#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - main scripts

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

###############################################################################
# Import
#
from config import *
import helpers
import mqtt_client
import timer
import time
import os
import sys
import platform
from datetime import datetime
if use_yolo_hw:
  import yolo_hw
else:
  import yolo_sw

# Create log modules
handler = helpers.createHandler(dev_mode, config['PATH']['log_path'])
log = helpers.createLogger(__name__)

log.debug("Base dir: %s" % BASE_PATH)


if __name__ == "__main__":

  log.info("[blue]---------------- People Detection started ----------------[/]")

  # Create MQTT Client
  mqttClient = mqtt_client.MqttClient(address=config['MQTT']['address'],
                                      port=int(config['MQTT']['port']),
                                      username=config['MQTT']['username'],
                                      password=config['MQTT']['password'],
                                      keepAlive=int(config['MQTT']['keepalive']),
                                      topic_detection=config['MQTT']['topic_detection'],
                                      lastWill=config['MQTT']['topic_lastwill'],
                                      location=config['APP']['location'])

  # Create timer module
  if use_yolo_hw:
    title = "hw-yolo_test"
  else:
    title = "sw-yolo_test"
  log.debug(config['PATH']['timelog_path']+os.sep+title+".csv")
  timer = timer.Timer(title=title, verbose=False, report=True, filewrite=dev_mode, file=config['PATH']['timelog_path']+os.sep+title+".csv")

  # Connect MQTT
  try:
    mqttClient.createConnection()
  except Exception:
    log.exception("Unable to connect to MQTT broker!")
    raise SystemExit

  # Setup Yolo
  if use_yolo_hw:
    # This will reprogram the FPGA partially
    timer.trigger("setup yolo begin")
    yolo_hw_nn = yolo_hw.YoloHW(config['PYTHON']['python_path'], config['DARKNET_HW']['darknet_path'])
    timer.end("setup yolo end", "Setup YOLO")
  else:
    timer.trigger("setup yolo begin")
    yolo_sw_nn = yolo_sw.YoloSW(config['DARKNET_SW']['darknet_path'],
                                config['DARKNET_SW']['darknet_cfg_path'],
                                config['DARKNET_SW']['darknet_weights_path'])
    timer.end("setup yolo end", "Setup YOLO")

  # Get static images
  if static_images:
    input_files = sorted(helpers.getListOfFiles(config['PATH']['input_image_path'], False, True))
    current_file = 0
    log.debug("Static image folder: {}".format(config['PATH']['input_image_path']))
    log.debug("Number of image files found: {}".format(len(input_files)))

  ###############################################################################
  # Main Loop
  #
  running = False
  while True:
    while running is True:
      if not static_images:
        # Get Webcam Image
        if save_images:
          fpath = helpers.saveWebcamImage(path=config['PATH']['raw_image_path'], ext=config['PATH']['extension'], camera=int(config['APP']['camera']), yolo_hw=use_yolo_hw)
          if dev_mode and not use_yolo_hw:
            helpers.displayFileCv2(fpath, False)
        else:
          fpath = os.path.abspath(os.path.join(config['PATH']['raw_image_path'], datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + "webcam" + config['PATH']['extension']))
          image = helpers.getWebcamImage(int(config['APP']['camera']))
          if show_images:
            helpers.displayImageCv2(image, waitKey=False)
      else:
        if save_images:
          fpath = os.path.abspath(os.path.join(config['PATH']['raw_image_path'], datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + "webcam" + config['PATH']['extension']))
          #fpath = helpers.saveWebcamImage(path=config['PATH']['raw_image_path'], ext=config['PATH']['extension'], camera=int(config['APP']['camera']), yolo_hw=use_yolo_hw)
        else:
          fpath = os.path.abspath(os.path.join(config['PATH']['raw_image_path'], datetime.now().strftime("%Y%m%d%H%M%S") + "-" + platform.node() + "-" + "webcam" + config['PATH']['extension']))
      # Yolo Test
      if use_yolo_hw:
        timer.trigger("load image begin")
        if static_images:
          if current_file >= len(input_files):
            running = False
            pass
          log.debug("Image {} of {} analysed".format(current_file,len(input_files)))
          yolo_hw_nn.getFile(input_files[current_file])
          current_file += 1
        else:
          if save_images:
            yolo_hw_nn.getFile(fpath)
          else:
            yolo_hw_nn.getImage(image)

        timer.end("load image end", "Image Loading")

        timer.trigger("yolo sw conv layer 0 begin")
        yolo_hw_nn.execute_yolo_sw_firstlayer()
        timer.end("yolo sw conv layer 0 end", "Apply YOLO SW Conv Layer 0")

        timer.trigger("yolo hw conv layers 1-7 begin")
        yolo_hw_nn.execute_yolo_hw()
        timer.end("yolo hw conv layers 1-7 end", "Apply YOLO HW Conv Layer 1-7")

        timer.trigger("yolo sw conv layer 8 begin")
        yolo_hw_nn.execute_yolo_sw_lastlayer()
        timer.end("yolo sw conv layer 8 end", "Apply YOLO SW Conv Layer 8")

        timer.trigger("darknet detection begin")
        (fpath_out, fpath_probs) = yolo_hw_nn.darknet_detection(fpath, config['PATH']['detection_image_path'])
        timer.end("darknet detection begin", "Draw Detection Boxes")
        #image_out = helpers.getImage(fpath_out)

        # Publish detection yolo hw
        if len(yolo_hw_nn.classes) > 0:
          mqttClient.publishDetection(yolo_hw_nn.classes, yolo_hw_nn.confidences, None, fpath_out)

      else:
        fpath_out = config['PATH']['detection_image_path'] + os.sep + os.path.basename(os.path.splitext(fpath)[0]) + '_sw_detection' + os.path.splitext(fpath)[1]
        timer.trigger("load image begin")
        if static_images:
          (image, layer_outputs) = yolo_sw_nn.loadFile(input_files[current_file])
          current_file += 1
        else:
          if save_images:
            (image, layer_outputs) = yolo_sw_nn.loadFile(fpath)
          else:
            layer_outputs = yolo_sw_nn.loadImg(image)

        timer.end("load image end", "Image Loading")

        timer.trigger("yolo sw conv layers begin")
        yolo_sw_nn.execute_yolo_sw(image)
        timer.end("yolo sw conv layers end", "Apply YOLO SW Conv Layers")

        timer.trigger("darknet detection begin")
        image_out = yolo_sw_nn.darknet_detection_sw(image, save_images, fpath_out)
        timer.end("darknet detection begin", "Draw Detection Boxes")

        # Publish detection yolo sw
        if len(yolo_sw_nn.class_ids) > 0:
          detection_labels = []
          for class_id in yolo_sw_nn.class_ids:
            detection_labels.append(yolo_sw_nn.labels[class_id])
          if save_images:
            mqttClient.publishDetection(labels=detection_labels, confidences=yolo_sw_nn.confidences, boxes=yolo_sw_nn.boxes, fpath=fpath_out)
          else:
            mqttClient.publishDetection(labels=detection_labels, confidences=yolo_sw_nn.confidences, boxes=yolo_sw_nn.boxes, image=image_out)

        # display images
        if show_images:
          if save_images:
            helpers.displayFileCv2(fpath_out)
          else:
            helpers.displayImageCv2(image_out)

      if running:
        timer.nextIndex()
        log.debug("Loop done")
        if running != mqttClient.running:
          log.info("Stopping YOLO detection")
          running = mqttClient.running
        else:
          log.debug("Waiting %d seconds before the next cycle..." % int(config['APP']['capture_interval']))
          if int(config['APP']['capture_interval']) != -1:
            time.sleep(int(config['APP']['capture_interval']))
      else:
        log.debug("Loop done, finishing")

    if running != mqttClient.running:
      log.info("Starting YOLO detection")
      running = mqttClient.running


  #if dev_mode:
  #  log.debug("Dump Timer Logs to CSV")
  #  timer.dumpToCsv()
  mqttClient.disconnect()

  # Delete objects
  if use_yolo_hw:
    del yolo_hw_nn
  else:
    del yolo_sw_nn
  log.info("[blue]---------------- People Detection ended ----------------[/]")

  sys.exit()
