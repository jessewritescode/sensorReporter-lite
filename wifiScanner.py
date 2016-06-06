from __future__ import absolute_import, division, print_function
import scapy.all
import socket
import math
import traceback
import sys
debug = 0


class wifiSensor:
    """Represents a Bluetooth device"""

    def __init__(self, address, destination, publish, logger, poll):
        """Finds whether the BT device is close and publishes its current state"""

        self.logger = logger
        self.logger.info(
            "----------Configuring WifiSensor: Address = " + address + " Destination = " + destination)
        self.address = address
        self.state = "OFF"
        self.destination = destination
        self.publish = publish
        self.poll = poll

        self.publishState()

    def long2net(self,arg):
        if arg <= 0 or arg >= 0xFFFFFFFF:
            raise ValueError("illegal netmask value", hex(arg))
        return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))

    def to_CIDR_notation(self,bytes_network, bytes_netmask):
        network = scapy.utils.ltoa(bytes_network)
        netmask = self.long2net(bytes_netmask)
        net = "%s/%s" % (network, netmask)
        if netmask < 16:
            self.logger.warn("%s is too big. skipping" % net)
            return None
        return net

    def getNetworkPresence(self, net, interface, timeout=1):
        self.logger.info("arping %s on %s" % (net, interface))
        value = "OFF"
        try:
            ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=True)
            for s, r in ans.res:
                mac = r.sprintf("%Ether.src%")
                self.logger.info("MAC: %s", mac.lower())
                self.logger.info("ADDR_MAC: %s", self.address.lower())
                self.logger.info("Equal: %s", mac.lower() == self.address.lower())

                if mac.lower() == self.address.lower():
                    self.logger.info("Found matching MAC!")
                    value = "ON"
                    break

        except socket.error as e:
            if e.errno == errno.EPERM:     # Operation not permitted
                self.logger.error("%s. Did you run as root?", e.strerror)
            else:
                raise
        self.logger.info("Returning value: %s", value)
        return value

    def checkNetwork(self):
        self.logger.info("Checking network...")
        value = self.state
        for network, netmask, _, interface, address in scapy.config.conf.route.routes:
            self.logger.info("Running trough network...")
            """ Skip loopback network and default gw """
            if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
                continue

            if netmask <= 0 or netmask == 0xFFFFFFFF:
                continue

            net = self.to_CIDR_notation(network, netmask)

            if interface != scapy.config.conf.iface:
                # see http://trac.secdev.org/scapy/ticket/537
                self.logger.warn("skipping %s because scapy currently doesn't support arping on non-primary network interfaces",
                            net)
                continue

            if net:
                value = self.getNetworkPresence(net, interface)
                self.logger.info("Value: %s", value)
                self.logger.info("State: %s", self.state)
                if value != self.state:
                    self.state = value
                    #self.publishState()
                    break

    def getPresence(self):
        self.logger.info("Getting presence")
        self.checkNetwork()
        """Detects whether the device is near by or not using lookup_name"""


    def checkState(self):
        """Detects and publishes any state change"""
        self.logger.info("Checking Wifi state for %s", self.address)
        self.getPresence()

    def publishState(self):
        """Publishes the current state"""
        traceback.print_stack(file=sys.stdout)
        self.logger.info("Publishing state: %s", self.state)
        self.publish(self.state, self.destination)