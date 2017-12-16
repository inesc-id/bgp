iface=${1:-vnic1}

ifconfig $iface 11.0.4.1 netmask 255.255.255.0

sudo route -n add 11.0.0.0/8 11.0.4.254
sudo route -n add 11.0.0.0/8 12.0.4.254
sudo route -n add 11.0.0.0/8 13.0.4.254