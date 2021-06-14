# [PYNQ Notebooks](https://github.com/tschinz/pynq_notebooks)

## Table of contents

- [How it works](#howitworks)
- [Requirements](#requirements)
- [Installation](#installation)
- [Run](#run)
- [Documentation](#documentation)

This repository contains all the data, documentation and code for the Masterthesis [Hardware Accelerated Edge Computing](https://github.com/tschinz/pynq_notebooks)
The main goal is to identify people at a certain location in order to stop machinery for security reasons.

## How it works

<h1 align="center">
  <br>
  <img src="./../img/edge-jump.png" alt="Masterthesis Logo" width="400">
  <br>
  People Image detection
  <br>
</h1>


## Requirements

- Python3 32 bit
- PYNQ capable hardware
- PYNQ image >=v2.5
- MQTT Broker
- make

## Installation

On the PYNQ-Z1 install the python environment:

    make install-pynq

Install other modules and tools

- See [install script](scripts/pynq_install.bash) for more information

On the PC install the python environment:

```bash
make install-pc
```

## Run

The sequence to start the application is important

First run the MQTT Broker (via the Docker image eclipse-mosquitto)

```bash
make docker
```

Then Yolo application either on the PYNQ-Z1 or the PC

### PYNQ-Z1

```bash
make run-yolo-pynq
```

### PC

```bash
make run-streamlit
```

Lastly run the streamlit client application

```bash
make run-streamlit
```

## Documentation

To build and open the documentation:

    make help

To only rebuild the documentation:

    make docs

## MQTT Broker via Docker
For development a docker image eclipse-mqtt can be run with the ``app_config.ini`` file.

   ### With custom config file
```bash
docker run -it -p 1883:1883 -p 9001:9001 -v mosquitto.conf:/mosquitto/config/mosquitto.conf eclipse-mosquitto
```

   ### With default configuration
```bash
docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto
```

