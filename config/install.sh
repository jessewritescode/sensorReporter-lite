#!/bin/sh

# Assumes we are running it from the install directory

#echo "Installing paho"
#pip install paho-mqtt

#echo "Installing bluetooth"
#sudo apt-get install bluez python-bluez

#echo "Creating soft link in /opt"
#cd ..
#sudo ln -s `pwd` /opt/sensorReporter
#chmod a+x /opt/sensorReporter/sensorReporter.py

#echo "Setting config"
#ln -s $HOSTNAME.ini /opt/sensorReporter/sensorReporter.ini

echo "Installing start script"
# Upstart
#sudo cp ./config/sensorReporter /etc/init.d
#sudo update-rc.d sensorReporter defaults

# systemd
sudo cp ./config/sensorReporter.service /etc/systemd/system
sudo systemctl enable sensorReporter.service
