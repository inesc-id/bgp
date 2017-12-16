#!/bin/bash

node=${1:-h3-2}

sudo python run.py --node $node --cmd python CryptoPingServer.py $node 10008
