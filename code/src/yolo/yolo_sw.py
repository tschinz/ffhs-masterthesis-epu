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
import os
import numpy as np
import cv2
import helpers


class YoloSW:
  """ Class for executing Yolo software machine learning recognition
  """

  def __init__(self, darknet_path, darknet_cfg, darknet_weights):
    """ Setup YoloSW Deep Neural Network
        It performs the following steps

           * Read labels that are used on object
           * Give the configuration and weight files for the model and load the network.
           * Determine the output layer, now this piece is not intuitive

    Args:
        darknet_path (str): Path to darknet library
        darknet_cfg (str): Path to darknet configuration file
        darknet_weights (str): Path to darknet neural net weights

    Returns:
        (tuple): tuple containing:

          net (obj): neural net network
          ln (lst): layer names
          colors (list): random color for labels
          labels (list): labels used on the object
    """
    self.log = helpers.createLogger(__name__)
    # Read labels that are used on object
    self.labels = open(os.path.join(darknet_path, "data", "coco.names")).read().splitlines()
    # Make random colors with a seed, such that they are the same next time
    np.random.seed(0)
    self.colors = np.random.randint(0, 255, size=(len(self.labels), 3)).tolist()

    # Give the configuration and weight files for the model and load the network.
    self.net = cv2.dnn.readNetFromDarknet(darknet_cfg, darknet_weights)
    # Determine the output layer, now this piece is not intuitive
    self.ln = self.net.getLayerNames()
    self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
    self.log.info("YoloSW Neural Net loaded")

    # instantiate variables
    self.layer_outputs = None
    self.boxes = []
    self.confidences = []
    self.class_ids = []

  def loadFile(self, file):
    """ load file into neural net

    Args:
        file (str): filepath to load into the neural net

    Returns:
        (tuple): tuple containing:

          image (obj): image object loaded
          layer_outputs (list): output of the neural net evaluation
    """
    self.log.info("YoloSW Load File")
    # Load the image
    image = cv2.imread(file)
    # Get the shape
    h, w = image.shape[:2]
    # Load it as a blob and feed it to the network
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    self.net.setInput(blob)

    # Get the output
    self.layer_outputs = self.net.forward(self.ln)

    return (image, self.layer_outputs)

  def loadImg(self, image):
    """ load image into neural net

    Args:
        image (obj): image object to load into the neural net

    Returns:
        (tuple): tuple containing:

          layer_outputs (list): output of the neural net evaluation
    """
    self.log.info("YoloSW Load Image")
    # Get the shape
    h, w = image.shape[:2]
    # Load it as a blob and feed it to the network
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    self.net.setInput(blob)

    # Get the output
    self.layer_outputs = self.net.forward(self.ln)

    return self.layer_outputs

  def execute_yolo_sw(self, image, verbose=True):
    """ Execute the YOLO ml deep neural net model on an image
        Parse the result form layer_outputs

        * executes all neural net layers
        * ensure we have some reasonable confidence

    Args:
        image (obj): image object loaded into the neural net
        verbose (bool): display more informations

    Returns:
        (tuple): tuple containing:

            boxes (list): list of box coordinates found
            confidences (list): list of confidences for each class resp. box
            class_id (list): id of classes found
    """
    self.log.info("Execute YoloSW")
    # Initialize the lists we need to interpret the results
    self.boxes = []
    self.confidences = []
    self.class_ids = []

    # Get the shape
    h, w = image.shape[:2]

    # Loop over the layers
    for output in self.layer_outputs:
      # For the layer loop over all detections
      for detection in output:
        # The detection first 4 entries contains the object position and size
        scores = detection[5:]
        # Then it has detection scores - it takes the one with maximal score
        class_id = np.argmax(scores).item()
        # The maximal score is the confidence
        confidence = scores[class_id].item()

        # Ensure we have some reasonable confidence, else ignore
        if confidence > 0.3:
          # The first four entries have the location and size (center, size)
          # It needs to be scaled up as the result is given in relative size (0.0 to 1.0)
          box = detection[0:4] * np.array([w, h, w, h])
          center_x, center_y, width, height = box.astype(int).tolist()

          # Calculate the upper corner
          x = center_x - width//2
          y = center_y - height//2

          # Add our findings to the lists
          self.boxes.append([x, y, width, height])
          self.confidences.append(confidence)
          self.class_ids.append(class_id)
    return (self.boxes, self.confidences, self.class_ids)

  def darknet_detection_sw(self, image, save_image=True, outfile=None):
    """ Execute the darknet detection

        * draw detection box with class name over image

    Args:
        image (obj): image object analzed
        outfile (str): path for the output file

    Returns:
        outfile (str): path for the file with detection boxes
    """
    self.log.info("Execute Darknet Detection")
    # Only keep the best boxes of the overlapping ones
    idxs = cv2.dnn.NMSBoxes(self.boxes, self.confidences, 0.3, 0.3)

    # Ensure at least one detection exists - needed otherwise flatten will fail
    if len(idxs) > 0:
      # Loop over the indexes we are keeping
      for i in idxs.flatten():
        # Get the box information
        x, y, w, h = self.boxes[i]

        # Make a rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), self.colors[self.class_ids[i]], 2)
        # Make and add text
        text = "{}: {:.4f}".format(self.labels[self.class_ids[i]], self.confidences[i])
        cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors[self.class_ids[i]], 2)

    # Write the image with boxes and text
    if save_image:
      cv2.imwrite(outfile, image)

    return image
