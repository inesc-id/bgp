# bgp

This tutorial extends [BGP Path Hijacking Attack Demo](https://github.com/mininet/mininet/wiki/BGP-Path-Hijacking-Attack-Demo). You can find the original [source code](https://bitbucket.org/jvimal/bgp/src/789055b95a666f0585e5eee67fbdb30876ab06ec?at=master) on Bitbucket.

It adds an additional host with the ip address *11.0.4.1* to *AS1* (gateway: *11.0.4.254*). This host is **not** running in mininet and has to be connected to a real network interface connected to the virtual machine.

Furthermore, it starts CryptoPingServers on *h3-2 (13.0.2.1:10008)* and *h4-2 (***13***.0.2.1:10008)*. Due to the fact that mininet hosts share the same directories, separate public and private keys are generated depending on the hosts.

> Tested with VirtualBx 5.2.2 on macOS 10.13.2

![](Setup.png)

## Setup

Download the latest [Ubuntu Server LTS](https://www.ubuntu.com/download/server) and make sure the system is up to date. Clone this repository and run

```
$ ./install.sh
```

This will install all necessary dependencies including mininet and quagga.

Alternatively, you can download a preconfigured virtual machine. Login credentials are the following:

username: `mininet`<br/>
password: `mininet`

Run

```
$ cd ~/bgp
$ git pull
```

to make sure the repository is up to date.

### Network configurations (VirtualBox)

NAT Networks can be created and configured in the general VirtualBox settings. Create *11.0.4.0/24* and make sure to remove the tic from *Supports DHCP*.

Connect two network adapters to your virtual machine

* NAT (for internet connection)
* NAT Network (used as an external host connected to *AS1*)

Run mininet with

`$ sudo python bgp.py --iface enp0s8`.

Replace *enp0s8* with the name of your NAT network interface. If no parameter is given, mininet will start without connecting an external controller.

Use another virtual machine connected to the same NAT network as the external host. You need to find out the corresponding name of the network interface on your **external host** (e.g. *eth0*). Set the ip address of the interface to *11.0.4.1/24* and make *11.0.4.254* the default gateway. On Debian *(DARSHANA-Client)*, this can be done with the following commands:

```
$ sudo su
$ ifconfig eth0 11.0.4.1 netmask 255.255.255.0
$ route add default gw 11.0.4.254 eth0
```