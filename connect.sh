#!/bin/bash

# Script to connect to a router's bgpd shell.
as=${1:-AS1}
echo "Connecting to $ass shell"

sudo python run.py --node $as --cmd "telnet localhost bgpd"