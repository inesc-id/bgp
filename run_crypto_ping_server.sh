#!/bin/bash

node=${1:-h3-2}
ip=${2:-13.0.2.1}

sudo python run.py --node $node --cmd python CryptoPingServer.py $ip 10008
