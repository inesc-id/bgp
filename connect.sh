#!/bin/bash

# Script to connect to a router's shell.
as=${1:-AS1}
daemon=${3:-bgpd}
echo "Connecting to $ass shell"

sudo python run.py --node $as --cmd "telnet localhost " $daemon