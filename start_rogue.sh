#!/bin/bash

echo "Killing any existing rogue AS"
./stop_rogue.sh

echo "Starting rogue AS"
sudo python run.py --node AS4 --cmd "/usr/lib/quagga/zebra -f conf/zebra-AS4.conf -d -i /tmp/zebra-AS4.pid > logs/AS4-zebra-stdout"
sudo python run.py --node AS4 --cmd "/usr/lib/quagga/bgpd -f conf/bgpd-AS4.conf -d -i /tmp/bgpd-AS4.pid > logs/AS4-bgpd-stdout"
