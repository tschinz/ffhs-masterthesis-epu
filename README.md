<h1 align="center">
  <br>
  <img src="./img/edge-jump.png" alt="EPU Logo" width="400">
  <br>
  FFHS MAS Industry 4.0 Masterthesis
  <br>
</h1>

[![Read Thesis](https://img.shields.io/badge/Read-Thesis-blue)](https://github.com/tschinz/ffhs-masterthesis-epu/blob/master/doc/ffhs-mas-ind4_0-silvan_zahno-thesis.pdf) [![Download Thesis](https://img.shields.io/badge/Download-Thesis-brightgreen)](https://github.com/tschinz/ffhs-masterthesis-epu/raw/master/doc/ffhs-mas-ind4_0-silvan_zahno-thesis-print.pdf)

## Table of contents

<p align="center">
  <a href="#abstract">Abstract</a> •
  <a href="#content">Content</a> •
  <a href="#cite">Cite</a>
</p>

This repository contains all thesis, documentation, code and data for the [Masterthesis Hardware Accelerated Edge Computing](https://github.com/tschinz/ffhs-masterthesis-epu).
The main goal is to identify people at a certain location in order to stop industrial machinery for security reasons.

## Abstract

Edge computing has proven to be very valuable and is often needed in addition to cloud computing. Especially in areas such as image and video processing, where large amount of data is generated that cannot be transferred in their entirety to the cloud for processing, or in areas where security and real-time behavior are essential.

In the just mentioned cases, it is not practical to transfer the data to the cloud for processing and return the result to the device. Edge computers can be very powerful, but also high maintenance and power hungry, depending on the algorithm and hardware. In this work, a Proof of concept (POC) is presented to combine low-cost and low-power Central Processing Unit (CPU) with Field Programmable Gate Array (FPGA) to run an algorithm as optimized as possible. The simplicity of the CPU programming and the modular and parallel nature of the FPGA creates very powerful hardware, that can handle many different problems.

A prototype system was presented in an industrial use case, where an automated industrial ma- chine is allowed to run, only when no human is nearby. We present an Edge Processing Unit (EPU) that monitors a selected region using a camera. The images are preprocessed in CPU and an object detection is performed in real time using a tiny You only look once (YOLO) v3 Machine Learning (ML) implemented in FPGA. A Convolutional Neural Network (CNN) hardware accelerator, performs the person detection. A MQTT broker, which also runs on the edge device, sends the results to the cloud and local Programmable Logic Controller (PLC). The entire sys- tem runs on a Xilinx PYNQ-Z1 board with a ZYNQ XC7Z020 System on Chip (SoC) that houses a dual core Arm A9 CPU and programmable Artix-7 logic. It achieves a higher frame rate and consumed less power than a comparable non-hardware accelerated edge device. The amount of data transferred was drastically reduced, compared to a cloud application.

## Content

```
├───code              # all program files
│   ├───config        # platform configuration files
│   │   ├───pc        # pc version configuration files
│   │   └───pynq      # pynq version configuration files
│   ├───docs          # documentation, poster and presentation
│   ├───notebooks     # jupyter notebooks used for result analysis an test
│   ├───output        # jupyter notebooks output files
│   │   ├───plot      # 
│   │   └───timelogs  #
│   ├───scripts       # bash scripts for installation purposes
│   └───src           # program source files
│       ├───streamlit # files for streamlit client application
│       └───yolo      # files for epu application
├───doc               # Thesis pdf
└───img               # project images
```

## Keywords
![EPU](https://img.shields.io/badge/-EPU-red) ![Edge_Computing](https://img.shields.io/badge/-Edge_Computing-red) ![Industrial_Edge_Computing](https://img.shields.io/badge/-Industrial_Edge_Computing-red) ![Cloud_Computing](https://img.shields.io/badge/-Cloud_Computing-red) ![ML](https://img.shields.io/badge/-ML-red) ![Image_Analysis](https://img.shields.io/badge/-Image_Analysis-red) ![Hardware_Accelerator](https://img.shields.io/badge/-Hardware_Accelerator-red) ![FPGA](https://img.shields.io/badge/-FPGA-red) ![Python_for_Zynq_(PYNQ)](https://img.shields.io/badge/-Python_for_Zynq_(PYNQ)-red) ![MQTT](https://img.shields.io/badge/-MQTT-red) ![SoC](https://img.shields.io/badge/-SoC-red)

## Cite

```latex
@thesis{EPU,
    title = {{EPU}: Edge Processing Unit},
    author = {Zahno, Silvan},
    date = {2021},
    school = {Fernfachhochschule Schweiz (FFHS)},
}
```

