#!/bin/bash

sudo python run.py --node AS4 --cmd "pgrep -f [z]ebra-AS4 | xargs kill -9"
sudo python run.py --node AS4 --cmd "pgrep -f [b]gpd-AS4 | xargs kill -9"
