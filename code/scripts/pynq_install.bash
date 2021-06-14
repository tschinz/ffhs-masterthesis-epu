#!/bin/bash
#================================================================================
# pynq_install - Clone repositories
#
base_directory="$(dirname "$(readlink -f "$0")")"
pushd "$base_directory"

SEPARATOR='--------------------------------------------------------------------------------'
INDENT='  '

echo "$SEPARATOR"
echo "-- ${0##*/} Started!"
echo ""

#-------------------------------------------------------------------------------
# Clone Notbook Repo
#
cd ~/jupyter_notebooks
git clone https://github.com/tschinz/pynq_notebooks.git
git clone https://github.com/tschinz/mas_notebooks.git
git clone https://github.com/tschinz/mas_data.git
cd pynq_notebooks

#-------------------------------------------------------------------------------
# PYNQ Config
#
PYNQ_CONFIG_DIR=config/pynq
# IP Config
cp $PYNQ_CONFIG_DIR/etc/eth0 /etc/network/interfaces.d/eth0
cp $PYNQ_CONFIG_DIR/etc/wlan0 /etc/network/interfaces.d/wlan0

# Xilinx User
cp -R $PYNQ_CONFIG_DIR/xilinx/.ssh /home/xilinx/
cp $PYNQ_CONFIG_DIR/xilinx/.bashrc /home/xilinx/
cp $PYNQ_CONFIG_DIR/xilinx/.bash_aliases /home/xilinx/
cp $PYNQ_CONFIG_DIR/xilinx/.profile /home/xilinx/
cp $PYNQ_CONFIG_DIR/xilinx/.gitconfig /home/xilinx/

# Root User
sudo cp $PYNQ_CONFIG_DIR/root/.bashrc /root/
sudo cp $PYNQ_CONFIG_DIR/root/.bash_aliases /root/
sudo cp $PYNQ_CONFIG_DIR/root/.profile /root/
sudo cp $PYNQ_CONFIG_DIR/root/.gitconfig /root/

sudo cp -R $PYNQ_CONFIG_DIR/root/.jupyter /root/
sudo cp $PYNQ_CONFIG_DIR/root/jupyter_notebook_config.json /root/jupyter_notebook_config.json

# Mosquitto
sudo cp -R $PYNQ_CONFIG_DIR/etc/mosquitto /etc/

#-------------------------------------------------------------------------------
# Install Xilinx Overlays
#
# QNN
sudo pip3 install git+https://github.com/Xilinx/QNN-MO-PYNQ.git

# BNN (Binary Neural Network)
sudo pip3 install git+https://github.com/Xilinx/BNN-PYNQ.git

# LSTM (Quantized Longterm Shortterm Memory neural net for OCR
sudo pip3 install git+https://github.com/xilinx/LSTM-PYNQ.git

# Darius Deep Learning IP
sudo -H pip3 install --upgrade git+https://github.com/Xilinx/PYNQ-DL.git

# PYNQ Computer Vision
pip3 install -U Cython

sudo pip3 install --upgrade git+https://github.com/Xilinx/PYNQ-ComputerVision.git

#-------------------------------------------------------------------------------
# Other Python modules
#
sudo pip3 install rich panda numpy matplotlib pillow configparser
#sudo pip3 install opencv-python

#-------------------------------------------------------------------------------
# Install MQTT Tools
#
# Broker
sudo apt-get install mosquitto

# Client
sudo pip3 install paho-mqtt

#-------------------------------------------------------------------------------
# Exit
#
echo ""
echo "-- ${0##*/} Finished!"
echo "$SEPARATOR"
popd
