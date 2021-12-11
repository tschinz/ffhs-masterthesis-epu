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
import sys, os
import numpy as np
import ctypes
from config import *

import qnn
from qnn import TinierYolo
from qnn import utils
sys.path.append(DARKNET_PATH_PYTHON)
from darknet import *


###############################################################################
# c type functions
#
def loadImg(fname):
  """ load saves image

  Args:
      fname (str): file path of image to load
  """
  fname = ctypes.c_char_p(fname.encode())
  img = load_image(fname,0,0)
  img = letterbox_image(img,416,416)
  npimg = np.copy(np.ctypeslib.as_array(img.data, (3,416,416)))
  npimg = np.swapaxes(npimg, 0,2)
  return (img, npimg)

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
# 1. Instantiate a Classifier
#
# Creating a classifier will automatically download the bitstream onto the device. All other initializations are currently performed in the Darknet framework.
def setup_yolo_hw(python_path):
  """ Setup Yolo Deep Neural Network in Hardware and Software
      It instantiates the classifier and performs a partial repogram of the FPGA

  Args:
      python_path (str): path to python distribution

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
  ## 1. Instantiate a Classifier
  print("1. Instantiate a Classifier")
  classifier = TinierYolo()
  classifier.init_accelerator()
  net = classifier.load_network(json_layer=python_path + os.sep + "dist-packages/qnn/params/tinier-yolo-layers.json")

  conv0_weights = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv0-W.npy', encoding="latin1", allow_pickle=True)
  conv0_weights_correct = np.transpose(conv0_weights, axes=(3, 2, 1, 0))
  conv8_weights = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv8-W.npy', encoding="latin1", allow_pickle=True)
  conv8_weights_correct = np.transpose(conv8_weights, axes=(3, 2, 1, 0))
  conv0_bias = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv0-bias.npy', encoding="latin1", allow_pickle=True)
  conv0_bias_broadcast = np.broadcast_to(conv0_bias[:,np.newaxis], (net['conv1']['input'][0],net['conv1']['input'][1]*net['conv1']['input'][1]))
  conv8_bias = np.load(python_path + os.sep + 'dist-packages/qnn/params/tinier-yolo-conv8-bias.npy', encoding="latin1", allow_pickle=True)
  conv8_bias_broadcast = np.broadcast_to(conv8_bias[:,np.newaxis], (125,13*13))
  file_name_cfg = c_encode_char(python_path + os.sep + "dist-packages/qnn/params/tinier-yolo-bwn-3bit-relu-nomaxpool.cfg")

  net_darknet = lib.parse_network_cfg(file_name_cfg)

  return (classifier, net, conv0_weights_correct, conv0_bias_broadcast, conv8_weights_correct, conv8_bias_broadcast, net_darknet)


###############################################################################
# Get file
#
def getFile(fname, in_folder, verbose=True):
  """ 2. Get image as numpy object

  Args:
      fname (str): filename to load
      in_folder (str): input folder of the file
      out_folder (str): output folder
      verbose (bool): more output

  Returns:
      (tuple): tuple containing:

          fpath (str): path of input file
          npimg (obj): image as numpy array
  """
  fpath = os.path.abspath(in_folder + os.sep + fname)

  if verbose:
    print("2. Get image")
    print("  * " + fpath)
  (img, npimg) = loadImg(fpath)
  free_image(img)
  return (fpath, npimg)


def execute_yolo_sw_firstlayer(npimg, weights, bias_broadcast, verbose=True):
  """ 3. Execute the first convolutional layer in Python

  Args:
      npimg (obj): image as numpy array
      weights (obj): neural net weights of conv layer 0 as numpy array
      bias_broadcast (obj):  neural net bias of conv layer 0 as numpy array
      verbose (bool): more output

  Returns:
      (obj): quantized output of convolutional layer 0 conv0_output_quant
  """
  if verbose:
    print("3. Execute the first convolutional layer in Python")
  npimg = npimg[np.newaxis, :, :, :]

  conv0_ouput = utils.conv_layer(npimg, weights, b=bias_broadcast, stride=2, padding=1)
  conv0_output_quant = conv0_ouput.clip(0.0,4.0)
  conv0_output_quant = utils.quantize(conv0_output_quant/4, 3)

  return conv0_output_quant


def execute_yolo_hw(classifier, net, conv0_output_quant, verbose=True):
  """ 4. HW Offload of the quantized layers

  Args:
      classifier (obj): tiniyolo classifier hw implemented
      net (obj): hw implemented quantized neural net layer
      conv0_output_quant (obj): quantized output of first sw convolutional layer
      verbose (bool): more output

  Returns:
     (obj): ouput of the 7th conv layer conv7_out
  """
  ## 4. HW Offload of the quantized layers
  if verbose:
    print("4. HW Offload of the quantized layers")
  out_dim = net['conv7']['output'][1]
  out_ch = net['conv7']['output'][0]

  conv_output = classifier.get_accel_buffer(out_ch, out_dim)
  conv_input = classifier.prepare_buffer(conv0_output_quant*7);

  classifier.inference(conv_input, conv_output)

  conv7_out = classifier.postprocess_buffer(conv_output)

  return conv7_out


def execute_yolo_sw_lastlayer(net, conv7_out, weights, bias_broadcast, verbose=True):
  """ 5. Execute the last convolutional layer in Python

  Args:
     net (obj): hw implemented quantized neural net layer
     conv7_out (obj): output of 7th convolutional layer
     weights (obj): neural net weights of conv layer 8 as numpy array
     bias_broadcast (obj):  neural net bias of conv layer 8 as numpy array
     verbose (bool): more output

  Returns:
     (obj): output of last convolutional layer conv8_out
  """
  if verbose:
    print("5. Execute the last convolutional layer in Python")
  out_dim = net['conv7']['output'][1]
  out_ch = net['conv7']['output'][0]

  conv7_out_reshaped = conv7_out.reshape(out_dim, out_dim, out_ch)
  conv7_out_swapped = np.swapaxes(conv7_out_reshaped, 0, 1) # exp 1
  conv7_out_swapped = conv7_out_swapped[np.newaxis, :, :, :]

  conv8_output = utils.conv_layer(conv7_out_swapped, weights, b=bias_broadcast, stride=1)
  conv8_out = conv8_output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

  return conv8_out


def darknet_detection(fpath, out_folder, conv8_out, darknet_folder, net_darknet, verbose=True):
  """ Execute the darknet detection

      * draw detection box with class name over image

  Args:
      fpath (str): base filename for all output files
      out_folder (str): folder for outut files
      conv8_out (obj): output of last convolutional layer
      net_darknet (obj): darknet network for object detection
      verbose (bool): more output

  Returns:
      (tuple): tuple containing

         fpath_out (str): filepath for output image file
         fpath_probs (str): filepath for output probability file
  """
  ## 6. Draw detection boxes using Darknet
  if verbose:
    print("6. Draw detection boxes using Darknet")

  fpath_out = os.path.abspath(out_folder + os.sep + os.path.splitext(os.path.split(fpath)[1])[0] + "_detection")
  fpath_probs = os.path.abspath(out_folder + os.sep + os.path.splitext(os.path.split(fpath)[1])[0] + "_probabilities.txt")

  lib.forward_region_layer_pointer_nolayer(net_darknet, conv8_out)
  tresh_c = c_encode_float(0.3)
  tresh_hier_c = c_encode_float(0.5)
  fpath_c = c_encode_char(fpath)
  fpath_out_c = c_encode_char(fpath_out)

  open(fpath_probs, 'w').close()
  fpath_names_voc = darknet_folder + os.sep + "data/voc.names"
  darknet_path = darknet_folder + os.sep

  fpath_probs_c = c_encode_char(fpath_probs)
  fpath_names_voc_c = c_encode_char(fpath_names_voc)
  darknet_path_c = c_encode_char(darknet_path)

  lib.draw_detection_python(net_darknet, fpath_c, tresh_c, tresh_hier_c, fpath_names_voc_c, darknet_path_c, fpath_out_c, fpath_probs_c);

  # Print probabilities
  if verbose:
    print("7. Show Probabilities")
  file_content = open(fpath_probs, "r").read().splitlines()
  detections = []
  for line in file_content[0:]:
    name, probability = line.split(": ")
    detections.append((probability, name))
  for det in sorted(detections, key=lambda tup: tup[0], reverse=True):
    print("class: {}\tprobability: {}".format(det[1], det[0]))

  return (fpath_out, fpath_probs)

###############################################################################
# Old all in one function
#

def execute_yolo_hw_old(fname, in_folder, out_folder, verbose=True):
  """ Execute the YOLO ml deep neural net model on an image

      * executes all neural net layers sw and hw
      * ensure we have some reasonable confidence

  Args:
      fname (str): name of inputfile to be loaded into the neural net
      in_folder (str): path for input images
      out_folder (str): path for output image folder
      verbose (bool): display more informations

  Returns:
      (tuple): tuple containing:

          fpath (str): path of inputfile
          fpath_out (str): path of output file
          class_id (list): id of classes found
          fpath, fpath_out, fpath_probs, conv8_out
  """
  ## 2. Get image
  if verbose:
    print("2. Get image")
  fpath = os.path.abspath(in_folder + os.sep + fname)
  fpath_out = os.path.abspath(out_folder + os.sep + os.path.splitext(os.path.split(fpath)[1])[0] + "_detection")
  fpath_probs = os.path.abspath(out_folder + os.sep + os.path.splitext(os.path.split(fpath)[1])[0] + "_probabilities.txt")
  print("  * " + fpath)
  if verbose:
    print(fpath)
    print(fpath_out)
    print(fpath_probs)
  timer.trigger("load image begin")
  (img, npimg) = loadImg(fpath)
  timer.end("load image end", "Image Loading")

  ## 3. Execute the first convolutional layer in Python
  if verbose:
    print("3. Execute the first convolutional layer in Python")
  timer.trigger()
  npimg = npimg[np.newaxis, :, :, :]

  conv0_ouput = utils.conv_layer(npimg, conv0_weights_correct, b=conv0_bias_broadcast, stride=2, padding=1)
  conv0_output_quant = conv0_ouput.clip(0.0,4.0)
  conv0_output_quant = utils.quantize(conv0_output_quant/4, 3)
  free_image(img)
  timer.end("First Conv Layer (SW)")

  ## 4. HW Offload of the quantized layers
  if verbose:
    print("4. HW Offload of the quantized layers")
  out_dim = net['conv7']['output'][1]
  out_ch = net['conv7']['output'][0]

  conv_output = classifier.get_accel_buffer(out_ch, out_dim)
  conv_input = classifier.prepare_buffer(conv0_output_quant*7);

  timer.trigger()
  classifier.inference(conv_input, conv_output)
  timer.end("Conv Layer Hardware Offloaded")

  conv7_out = classifier.postprocess_buffer(conv_output)

  ## 5. Execute the last convolutional layer in Python
  if verbose:
    print("5. Execute the last convolutional layer in Python")
  timer.trigger()
  conv7_out_reshaped = conv7_out.reshape(out_dim, out_dim, out_ch)
  conv7_out_swapped = np.swapaxes(conv7_out_reshaped, 0, 1) # exp 1
  conv7_out_swapped = conv7_out_swapped[np.newaxis, :, :, :]

  conv8_output = utils.conv_layer(conv7_out_swapped, conv8_weights_correct, b=conv8_bias_broadcast, stride=1)
  conv8_out = conv8_output.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

  timer.end("Last Conv Layer (SW)")
  return (fpath, fpath_out, fpath_probs, conv8_out)