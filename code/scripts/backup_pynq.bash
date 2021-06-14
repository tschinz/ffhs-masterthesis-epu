#!/bin/bash
#================================================================================
# backup_pynq - backup local config
#
base_directory="$(dirname "$(readlink -f "$0")")"
pushd "$base_directory"

SEPARATOR='--------------------------------------------------------------------------------'
INDENT='  '

echo "$SEPARATOR"
echo "-- ${0##*/} Started!"
echo ""

#-------------------------------------------------------------------------------
# Define Constans
#
BACKUP_DIR="/home/xilinx/jupyter_notebooks/pynq_notebooks/config/pynq"

#-------------------------------------------------------------------------------
# Backup
#

# Network interfaces

# xilinx user
mkdir -p $BACKUP_DIR/xilinx
sudo cp -R -p /home/xilinx/.ssh         $BACKUP_DIR/xilinx/
sudo cp /home/xilinx/.bashrc            $BACKUP_DIR/xilinx/
sudo cp /home/xilinx/.bash_aliases      $BACKUP_DIR/xilinx/
sudo cp /home/xilinx/.profile           $BACKUP_DIR/xilinx/
sudo cp /home/xilinx/.gitconfig         $BACKUP_DIR/xilinx/
sudo cp /home/xilinx/.git-credentials   $BACKUP_DIR/xilinx/

# root user
mkdir -p $BACKUP_DIR/root
sudo cp /root/.bashrc                   $BACKUP_DIR/root/
sudo cp /root/.bash_aliases             $BACKUP_DIR/root/
sudo cp /root/.profile                  $BACKUP_DIR/root/
sudo cp /root/.gitconfig                $BACKUP_DIR/root/
sudo cp /root/.git-credentials          $BACKUP_DIR/root/

# jupyterconfig
sudo cp -R -p /root/.jupyter            $BACKUP_DIR/root/
sudo cp -R -p /root/.ipython            $BACKUP_DIR/root/
sudo cp /root/jupyter_notebook_config.json $BACKUP_DIR/root/

# /etc config
mkdir -p $BACKUP_DIR/etc
# network
sudo cp /etc/network/interfaces.d/wlan0 $BACKUP_DIR/etc/
sudo cp /etc/network/interfaces.d/eth0  $BACKUP_DIR/etc/
# mosquitto
sudo cp -R -p /etc/mosquitto            $BACKUP_DIR/etc/

# python environment
sudo pip3 freeze > $BACKUP_DIR/pip_requirements.txt

#-------------------------------------------------------------------------------
# Exit
#
echo ""
echo "-- ${0##*/} Finished!"
echo "$SEPARATOR"
popd
