#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MAS PYNQ Machine Learning Project - yolo hw

Confidentiality
---------------
All information in this document is strictly confidential.
Copyright (C) 2021 FFHS - All Rights Reserved
"""

###############################################################################
# Import
#
import sys
import os
import numpy as np
import ctypes
import helpers

import qnn
from qnn import TinierYolo
from qnn import utils

sys.path.append("/opt/darknet/python/")
from darknet import *

from pynq import Xlnk

###############################################################################
# c type functions
#
def c_encode_char(string):
  """ ctypes char encoding

  Args:
      string (str): string to encode as c_char_p
  """
  return ctypes.c_char_p(string.encode())


def c_encode_float(float):
  """ ctypes float encoding

  Args:
      string (float): float value to encode as c_float
  """
  return ctypes.c_float(float)


###############################################################################
# YoloHW Class
#
class YoloHW:
  """ Class for executing Yolo hardware machine learning recognition
  """

  def __init__(self, python_path, darknet_path):
    """ Setup Yolo Deep Neural Network in Hardware and Software
        It instantiates the classifier and performs a partial repogram of the FPGA

        Creating a classifier will automatically download the bitstream onto the device.
        All other initializations are currently performed in the Darknet framework.

    Args:
        python_path (str): path to python distribution
        python_path (str): path to darknet distribution

    Returns:
        (tuple): tuple containing

            classifier (obj): Yolo classifier
            net (obj): Yolo network
            conv0_weights_correct (obj): numpyarray of the weight of the first convolutional layer
            conv0_bias_broadcast (obj): numpyarray of the bias of the first convolutional layer
            conv8_weights_correct (obj): numpyarray of the weight of the last convolutional layer
            conv8_bias_broadcast (obj): numpyarray of the bias of the last convolutional layer
            net_darknet (obj): darknet network configuration
    """
    self.log = helpers.createLogger(__name__)
    self.log.info("1. Instantiate a Classifier")


    self.darknet_path = darknet_path
    sys.path.append(python_path)
    #from darknet import *

    self.classifier = TinierYolo()
    self.classifier.init_accelerator()
    self.net = self.classifier.load_network(json_layer=python_path + os.sep + "dist-packages/qnn/params/tinier-yolo-layers.json")
    conv0_weights = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv0-W.npy', encoding="latin1", allow_pickle=True)
    self.conv0_weights_correct = np.transpose(conv0_weights, axes=(3, 2, 1, 0))
    conv8_weights = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv8-W.npy', encoding="latin1", allow_pickle=True)
    self.conv8_weights_correct = np.transpose(conv8_weights, axes=(3, 2, 1, 0))
    conv0_bias = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv0-bias.npy', encoding="latin1", allow_pickle=True)
    self.conv0_bias_broadcast = np.broadcast_to(conv0_bias[:, np.newaxis], (self.net['conv1']['input'][0], self.net['conv1']['input'][1]*self.net['conv1']['input'][1]))
    conv8_bias = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv8-bias.npy', encoding="latin1", allow_pickle=True)
    self.conv8_bias_broadcast = np.broadcast_to(conv8_bias[:, np.newaxis], (125, 13*13))
    file_name_cfg = c_encode_char(python_path + os.sep + "dist-packages/qnn/params/tinier-yolo-bwn-3bit-relu-nomaxpool.cfg")
    # Output of CNN created why??
    self.net_darknet = lib.parse_network_cfg(file_name_cfg)
    # Create class variables
    self.npimg = None
    self.conv0_output_quant = None
    self.conv7_out = None
    self.conv8_out = None
    self.classes = None
    self.confidences = None

  def __del__(self):
    # deinint classifier
    self.classifier.deinit_accelerator()
    # Reset the device
    xlnk = Xlnk();
    xlnk.xlnk_reset()
    
    
  def loadFile(self, fname):
    """ load saves image

    Args:
        fname (str): file path of image to load

    Returns:
        npimg (obj): image as numpy array
    """
    self.log.info("Load Image")
    fname = c_char_p(fname.encode())
    img = load_image(fname, 0, 0)
    img = letterbox_image(img, 416, 416)
    self.npimg = np.copy(np.ctypeslib.as_array(img.data, (3, 416, 416)))
    self.npimg = np.swapaxes(self.npimg, 0, 2)
    free_image(img)
    return self.npimg


  ###############################################################################
  # Get file
  #
  def getImage(self, image):
    """ 2. Get image as numpy object

    Args:
        image (obj): image to load

    Returns:
        (tuple): tuple containing:

            fpath (str): path of input file
            npimg (obj): image as numpy array
    """
    self.log.info("2. Get image")

    self.npimg = np.copy(np.ctypeslib.as_array(image.data, (3, 416, 416)))
    self.npimg = np.swapaxes(self.npimg, 0, 2)
    free_image(image)
    return self.npimg


  def getFile(self, fpath):
    """ 2. Get fileimage as numpy object

    Args:
        fpath (str): filepath to load

    Returns:
        (tuple): tuple containing:

            fpath (str): path of input file
            npimg (obj): image as numpy array
    """
    self.log.info("2. Get image")
    self.log.debug("  * " + fpath)

    self.npimg = self.loadFile(fpath)
    return (fpath, self.npimg)

  def execute_yolo_sw_firstlayer(self):
    """ 3. Execute the first convolutional layer in Python

    Args:
        None

    Returns:
        (obj): quantized output of convolutional layer 0 conv0_output_quant
    """
    self.log.info("3. Execute the first convolutional layer in Python")
    npimg = self.npimg[np.newaxis, :, :, :]

    conv0_ouput = utils.conv_layer(npimg, self.conv0_weights_correct, b=self.conv0_bias_broadcast, stride=2, padding=1)
    self.conv0_output_quant = conv0_ouput.clip(0.0, 4.0)
    self.conv0_output_quant = utils.quantize(self.conv0_output_quant/4, 3)

    return self.conv0_output_quant

  def execute_yolo_hw(self):
    """ 4. HW Offload of the quantized layers

    Args:
        None

    Returns:
      (obj): ouput of the 7th conv layer conv7_out
    """
    self.log.info("4. HW Offload of the quantized layers")
    out_dim = self.net['conv7']['output'][1]
    out_ch = self.net['conv7']['output'][0]

    conv_output = self.classifier.get_accel_buffer(out_ch, out_dim)
    conv_input = self.classifier.prepare_buffer(self.conv0_output_quant*7)

    self.classifier.inference(conv_input, conv_output)

    self.conv7_out = self.classifier.postprocess_buffer(conv_output)

    return self.conv7_out

  def execute_yolo_sw_lastlayer(self):
    """ 5. Execute the last convolutional layer in Python

    Args:
        None

    Returns:
      (obj): output of last convolutional layer conv8_out
    """
    self.log.info("5. Execute the last convolutional layer in Python")
    out_dim = self.net['conv7']['output'][1]
    out_ch = self.net['conv7']['output'][0]

    conv7_out_reshaped = self.conv7_out.reshape(out_dim, out_dim, out_ch)
    conv7_out_swapped = np.swapaxes(conv7_out_reshaped, 0, 1)  # exp 1
    conv7_out_swapped = conv7_out_swapped[np.newaxis, :, :, :]

    conv8_output = utils.conv_layer(conv7_out_swapped, self.conv8_weights_correct, b=self.conv8_bias_broadcast, stride=1)
    self.conv8_out = conv8_output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

    return self.conv8_out

  def darknet_detection(self, fpath, output_folder):
    """ Execute the darknet detection

        * draw detection box with class name over image

    Args:
        fpath (str): saved webcam file
        output_folder (str): folder for all output files

    Returns:
        (tuple): tuple containing

          fpath_out (str): filepath for output image file
          fpath_probs (str): filepath for output probability file
    """
    self.log.info("6. Draw detection boxes using Darknet")

    fpath_out = output_folder + os.sep + os.path.basename(os.path.splitext(fpath)[0]) + '_hw_detection'# + os.path.splitext(fpath)[1]
    fpath_probs = os.path.abspath(os.path.splitext(fpath_out)[0] + "_probabilities.txt")

    self.log.debug(fpath)
    self.log.debug(fpath_out)
    self.log.debug(fpath_probs)

    lib.forward_region_layer_pointer_nolayer(self.net_darknet, self.conv8_out)
    tresh_c = c_encode_float(0.3)
    tresh_hier_c = c_encode_float(0.5)
    fpath_c = c_encode_char(fpath)
    fpath_out_c = c_encode_char(fpath_out)

    open(fpath_probs, 'w').close()
    fpath_names_voc = self.darknet_path + os.sep + "data/voc.names"
    darknet_path = self.darknet_path + os.sep

    fpath_probs_c = c_encode_char(fpath_probs)
    fpath_names_voc_c = c_encode_char(fpath_names_voc)
    darknet_path_c = c_encode_char(darknet_path)

    lib.draw_detection_python(self.net_darknet, fpath_c, tresh_c, tresh_hier_c, fpath_names_voc_c, darknet_path_c, fpath_out_c, fpath_probs_c)

    # Print probabilities
    self.log.debug("7. Show Probabilities")
    file_content = open(fpath_probs, "r").read().splitlines()
    detections = []
    self.classes = []
    self.confidences = []
    for line in file_content[0:]:
      name, probability=line.split(": ")
      self.classes.append(name)
      self.confidences.append(probability)
      detections.append((probability, name))
    for det in sorted(detections, key=lambda tup: tup[0], reverse=True):
      self.log.debug("class: {}\tprobability: {}".format(det[1], det[0]))

    return (fpath_out + '.png', fpath_probs)
