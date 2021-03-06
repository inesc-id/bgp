#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import lg, info, setLogLevel, error
from mininet.util import dumpNodeConnections, quietRun, moveIntf
from mininet.cli import CLI
from mininet.node import Switch, OVSKernelSwitch
from mininet.link import Intf, TCLink

from subprocess import Popen, PIPE, check_output
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import sys
import os
import termcolor as T
import time
import re

setLogLevel('info')

parser = ArgumentParser("Configure simple BGP network in Mininet.")
parser.add_argument('--rogue', action="store_true", default=False)
parser.add_argument('--sleep', default=3, type=int)
parser.add_argument('--iface', default=None)
args = parser.parse_args()

FLAGS_rogue_as = args.rogue
ROGUE_AS_NAME = 'AS4'

def log(s, col="green"):
    print T.colored(s, col)


class Router(Switch):
    """Defines a new router that is inside a network namespace so that the
    individual routing entries don't collide.

    """
    ID = 0
    def __init__(self, name, **kwargs):
        kwargs['inNamespace'] = True
        Switch.__init__(self, name, **kwargs)
        Router.ID += 1
        self.switch_id = Router.ID

    @staticmethod
    def setup():
        return

    def start(self, controllers):
        pass

    def stop(self):
        self.deleteIntfs()

    def log(self, s, col="magenta"):
        print T.colored(s, col)


class SimpleTopo(Topo):
    """The Autonomous System topology is a simple straight-line topology
    between AS1 -- AS2 -- AS3.  The rogue AS (AS4) connects to AS1 directly.

    """
    def __init__(self):
        # Add default members to class.
        super(SimpleTopo, self ).__init__()
        num_hosts_per_as = 3
        num_ases = 3
        num_hosts = num_hosts_per_as * num_ases
        # The topology has one router per AS
	routers = []
        for i in xrange(num_ases):
            router = self.addSwitch('AS%d' % (i+1))
	    routers.append(router)
        hosts = []
        for i in xrange(num_ases):
            router = 'AS%d' % (i+1)
            for j in xrange(num_hosts_per_as):
                hostname = 'h%d-%d' % (i+1, j+1)
                host = self.addNode(hostname)
                hosts.append(host)
                self.addLink(router, host)

        for i in xrange(num_ases-1):
            self.addLink('AS%d' % (i+1), 'AS%d' % (i+2), bw=10, delay='5ms', loss=1, use_htb=True)

        routers.append(self.addSwitch('AS4'))
        for j in xrange(num_hosts_per_as):
            hostname = 'h%d-%d' % (4, j+1)
            host = self.addNode(hostname)
            hosts.append(host)
            self.addLink('AS4', hostname)
        # This MUST be added at the end
        self.addLink('AS1', 'AS4', bw=10, delay='10ms', loss=1, use_htb=True)
        return


def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    config = quietRun( 'ifconfig %s 2>/dev/null' % intf, shell=True )
    if not config:
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', config )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )


def getIP(hostname):
    AS, idx = hostname.replace('h', '').split('-')
    AS = int(AS)
    if AS == 4:
        AS = 3
    ip = '%s.0.%s.1/24' % (10+AS, idx)
    return ip


def getGateway(hostname):
    AS, idx = hostname.replace('h', '').split('-')
    AS = int(AS)
    # This condition gives AS4 the same IP range as AS3 so it can be an
    # attacker.
    if AS == 4:
        AS = 3
    gw = '%s.0.%s.254' % (10+AS, idx)
    return gw


def startWebserver(net, hostname, text="Default web server"):
    host = net.getNodeByName(hostname)
    return host.popen("python webserver.py --text '%s'" % text, shell=True)


def startCryptoPingServer(net, hostname):
    host = net.getNodeByName(hostname)
    return host.popen("python CryptoPingServer.py %s 10008" % (hostname), shell=True)


def main():
    os.system("rm -f /tmp/AS*.log /tmp/AS*.pid logs/*")
    os.system("mn -c >/dev/null 2>&1")
    os.system("killall -9 zebra bgpd > /dev/null 2>&1")
    os.system('pgrep -f webserver.py | xargs kill -9')

    info( '*** Creating network\n' )
    net = Mininet(topo=SimpleTopo(), switch=Router, link=TCLink)

    if (args.iface is not None):
        info( '*** Checking', args.iface, '\n' )
        checkIntf( args.iface )
        
        os.system("sudo ip link set %s name AS1-external" % (args.iface));

        router = net.getNodeByName('AS1')
        info( '*** Adding hardware interface', 'AS1-external', 'to router',
              router.name, '\n' )
        Intf( 'AS1-external', node=router )
        
        info( '*** Note: you may need to reconfigure the interfaces for '
              'the Mininet hosts:\n', net.hosts, '\n' )

    net.start()
    for router in net.switches:
        router.cmd("sysctl -w net.ipv4.ip_forward=1")
        router.waitOutput()

    log("Waiting %d seconds for sysctl changes to take effect..."
        % args.sleep)
    sleep(args.sleep)

    for router in net.switches:
        if router.name == ROGUE_AS_NAME and not FLAGS_rogue_as:
            continue
        router.cmd("/usr/lib/quagga/zebra -f conf/zebra-%s.conf -d -i /tmp/zebra-%s.pid > logs/%s-zebra-stdout 2>&1" % (router.name, router.name, router.name))
        router.waitOutput()
        router.cmd("/usr/lib/quagga/bgpd -f conf/bgpd-%s.conf -d -i /tmp/bgp-%s.pid > logs/%s-bgpd-stdout 2>&1" % (router.name, router.name, router.name), shell=True)
        router.waitOutput()
        log("Starting zebra and bgpd on %s" % router.name)

    for host in net.hosts:
        host.cmd("ifconfig %s-eth0 %s" % (host.name, getIP(host.name)))
        host.cmd("route add default gw %s" % (getGateway(host.name)))

    log("Starting web servers", 'yellow')
    startWebserver(net, 'h3-1', "Default web server")
    startWebserver(net, 'h4-1', "*** Attacker web server ***")

    log("Starting crypto ping servers", 'yellow')
    startCryptoPingServer(net, "h3-2")
    startCryptoPingServer(net, "h4-2")

    CLI(net)
    net.stop()
    os.system("killall -9 zebra bgpd")
    os.system('pgrep -f webserver.py | xargs kill -9')
    if (args.iface is not None):
        log("Waiting %d seconds before renaming AS1-external"
            % args.sleep)
        sleep(args.sleep)
        os.system("sudo ip link set AS1-external name %s" % (args.iface));


if __name__ == "__main__":
    main()
