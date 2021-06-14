Hardware Accelerated Edge Computing Documentation
=================================================

.. toctree::
   :maxdepth: 2

   control
   yolo

Repository folders description
------------------------------

.. code::

   +-- .vscode/                    # vscode project configuration
   +-- config/                     # PYNQ backup configuration
   +-- docs/                       # project documentation
   | +-- resources/                # documentation images, documents etc.
   +-- notebooks/                  # notebooks for testing and analysing purposes
   | +-- mqtt-test.ipynb           # mqtt test sender and receiver
   | +-- tiny-yolo-image-all.ipynb # example tiny-yolo hw implementation
   | +-- webcam-test.ipynb         # usb webcam test on PYNQ
   | +-- config.py                 # configuration for all notebooks
   | +-- functions.py              # common used functions for all notebooks
   | +-- yolo_hw.py                # custom implementation of tiny-yolo neural net in HW
   +-- outputs/                    # for storing timing and probability outputs (for verification purposes)
   +-- scripts/                    # various helpder scripts for maintenance the PYNQ installation
   | +-- backup_pynq.bash          # creates a backup in the config/ folder
   | +-- pynq_install.bash         # clean install of the PYNQ Hardware
   | +-- rabbitmq_install.bash     # installation of a rabbitmq MQTT Broker
   | +-- start_wifi.bash           # connect to wifi
   | +-- start_wifi.py             # connect to wifi
   | +-- useful_git_repos.bash     # cloning of useful git example repos
   +-- src/                        # folder for main project code used at Syrto analysing
   | +-- control/                  # app to control the system
   | +-- yolo/                     # yolo detection app for ARM with and without HW and x86
   |   +-- darknet/                # darknet yolo implementation including weights, bias etc.
   |   +-- app_config_pc.ini       # configuration for debug and development purposes on the PC
   |   +-- app_config_pynq.ini     # configuration for debug and development purposes on the PYNQ
   |   +-- app_config_prod.ini     # configuration for production purposes
   |   +-- config.py               # configuration object
   |   +-- helpers.py              # helper functions mainly for logging
   |   +-- mqtt_client.py          # mqtt client implementation
   |   +-- people_detection.py     # main scripts
   |   +-- timer.py                # timer module for measuring execution time
   |   +-- yolo_hw.py              # yolo hw module
   |   +-- yolo_sw.py              # yolo sw module
   +-- .gitignore                  # gitignore file
   +-- .pep8                       # pep8 settings file
   +-- Makefile                    # Makefile for all common commands
   +-- README.md                   # This file