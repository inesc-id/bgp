#!/bin/bash
sudo apt-get update
cd ~
git clone git://github.com/mininet/mininet.git
cd mininet/util
./install.sh -a
sudo apt-get install -y quagga curl screen
sudo apt-get install python-dev
sudo apt-get install python-setuptools
sudo easy_install termcolor
sudo easy_install PyCrypto
