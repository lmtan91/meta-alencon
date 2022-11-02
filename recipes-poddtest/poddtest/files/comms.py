import Adafruit_BBIO.GPIO as GPIO

from pyconnman.manager import ConnManager
from pyconnman.technology import ConnTechnology
from pyconnman.service import ConnService
from functools import partial
from collections import namedtuple

import os
import subprocess
import time
import logging
import urllib.request
import threading
import tempfile
import dbus
import json

# This module uses pyconnman (a python module for connman) to control the beaglebones network interface
# The API for pyconnman can be found at pythonhosted.org/pyconnman/apidoc.html
# TODO: Setup signal receivers from the API to call callback functions

# Communication GPIO #
WIFI_PWR_N = "P8_10"
LAN9514_nRST = "P8_8"

# Wifi Information #
wifi_ssid = 'Alencon'
wifi_password = 'Nocnela@WLAN4u'

max_connection_attempts = 10


class CommsThread(threading.Thread):

    def __init__(self):

        self.logger = logging.getLogger('PODD.Comms_Monitor')

        # Import settings to check static IP configuration and if wifi is enabled
        settings = {"general":{}}
        try:
            with open('./config/hub_settings.json', 'r') as json_file:
                settings = json.load(json_file)
        except IOError:
            print("warning: hub_settings.json not found, using default Network Configuration Values")

        # Make default config or add parameters if not in last version of HUB settings
        new_settings = False
        if "wifi_enabled" not in settings["general"]:
            settings["general"]["wifi_enabled"] = {"value": False,
                                                   "reset_required": True,
                                                   "description": "Enabled if wifi version of the PODD"}
            new_settings = True

        if "static_ip_address" not in settings["general"]:
            settings["general"]["static_ip_address"] = {"value": "0.0.0.0",
                                                        "reset_required": True,
                                                        "description": "Static IP Address for PODD"}
            new_settings = True

        if "static_gateway" not in settings["general"]:
            settings["general"]["static_gateway"] = {"value": "0.0.0.0",
                                                     "reset_required": True,
                                                     "description": "Gateway for static IP for PODD"}
            new_settings = True

        if "static_netmask" not in settings["general"]:
            settings["general"]["static_netmask"] = {"value": "0.0.0.0",
                                                     "reset_required": True,
                                                     "description": "Netmask for static IP for PODD"}
            new_settings = True

        # Rewrite settings if settings changes
        if new_settings:
            try:
                with open('./config/hub_settings.json', 'w') as json_file:
                    json.dump(settings, json_file)
            except IOError:
                print("warning: hub_settings.json not found, cannot write new settings")

        self.wifi_enabled = settings["general"]["wifi_enabled"]["value"]
        self.wifi_enabled = True 
        self.monitoring_wifi = False
        self.ip_address = 'null'
        self.connection_attempts = 1

        # Initialize USB, ETH1 and WiFi (if available)
        GPIO.setup(LAN9514_nRST, GPIO.OUT)
        GPIO.output(LAN9514_nRST, GPIO.HIGH)
#        if self.wifi_enabled:
#            self.turn_on_wifi()
#        else:
#            self.turn_off_wifi()

        # Give some time for the wifi module and ethernet hub to boot
        time.sleep(5.0)

        # Setup network connection dictionary
        self.network_connections = {}
        self.network_manager = ConnManager()
        self.get_network_connections()

        self.logger.info('Found network technologies: %s', str(self.network_connections.keys()))

        # If wifi is enabled and not connected to a network, connect to a network
        if self.wifi_enabled and not ("wlan0" in self.network_connections.keys()):
            self.setup_wifi()

        # If static ip address setting is 0.0.0.0, configure for dhcp
        if settings["general"]["static_ip_address"]["value"] != "0.0.0.0":
            self.set_static_ip(ip=settings["general"]["static_ip_address"]["value"],
                               gateway=settings["general"]["static_gateway"]["value"],
                               netmask=settings["general"]["static_netmask"]["value"])
        else:
            self.set_dhcp()

        super(CommsThread, self).__init__()
        self.start()

    def run(self):
        self.logger.info("Comms Thread Started")

        self.monitoring_wifi = True                      # Monitoring wifi

        self.start_wifi_monitoring()

        self.logger.info("Wifi Monitoring Thread Stopped")

    def stop(self):
        self.monitoring_wifi = False                             # break out of run loop

    def get_network_connections(self):
        services = self.network_manager.get_services()
        for service in services:
            (path, params) = service
            try:
                if params["Ethernet"]["Interface"] == "eth0":
                    eth0_instance = ConnService(path)
                    self.network_connections["eth0"] = {"path": self.convert_dbus_to_py(path),
                                                        "properties": self.convert_dbus_to_py(
                                                            eth0_instance.get_property())}
                if params["Ethernet"]["Interface"] == "eth1":
                    eth1_instance = ConnService(path)
                    self.network_connections["eth1"] = {"path": self.convert_dbus_to_py(path),
                                                        "properties": self.convert_dbus_to_py(
                                                            eth1_instance.get_property())}
                if params["Ethernet"]["Interface"] == "wlan0" and params["Name"] == wifi_ssid:
                    wlan0_instance = ConnService(path)
                    self.network_connections["wlan0"] = {"path": self.convert_dbus_to_py(path),
                                                         "properties": self.convert_dbus_to_py(
                                                             wlan0_instance.get_property())}
            except Exception as e:
                pass

    def setup_wifi(self):
        # Get wifi technology
        wifi_path = None
        technologies = self.network_manager.get_technologies()

        for technology in technologies:
            (path, params) = technology
            if params['Name'] == 'WiFi':
                wifi_path = path

        wifi_technology = ConnTechnology(wifi_path)

        # Enable technology
        try:
            wifi_technology.Powered = True
        except Exception as e:
            self.logger.info("Wifi already enabled")

        # Scan for services and try and refind wifi
        wifi_technology.scan()
        self.get_network_connections()

        # If not found, retry
        if "wlan0" in self.network_connections.keys():
            # Connect Service to network
            try:
                wifi_service = ConnService(self.network_connections["wlan0"]["path"])
                wifi_service.connect()
            except Exception as e:
                self.logger.info("Already connected")
        else:
            self.setup_wifi()

        return True

    def get_ip(self):
        self.logger.info('Getting IP')
        self.get_network_connections()
        try:
            if self.wifi_enabled:
                self.ip_address = self.network_connections["wlan0"]["properties"]["IPv4"]["Address"]
            else:
                self.ip_address = self.network_connections["eth0"]["properties"]["IPv4"]["Address"]
        except Exception as e:
            self.ip_address == 'null'

        if self.ip_address == 'null':
            self.logger.info('Valid IP not found')
        else:
            self.logger.info('Found valid IP: %s', self.ip_address)

    def hub_connected(self):
        if self.ip_address != 'null':
            try:
                hub_url = 'http://' + self.ip_address + ':8888'
                urllib.request.urlopen(hub_url, timeout=5)
                return True
            except:
                return False
        else:
            return False

    def pause_wifi_monitoring(self, sec):
        for i in range(sec):
            time.sleep(1.0)
            if not self.monitoring_wifi:
                break

    def start_wifi_monitoring(self):
        need_to_reboot = False
        self.monitoring_wifi = True
        while self.monitoring_wifi:
            self.get_ip()
            if self.hub_connected():
                hub_url = 'http://' + self.ip_address + ':8888'
                self.logger.info('Pinging hub at %s', hub_url)
                self.pause_wifi_monitoring(60)
                continue
            else:
                self.logger.info('HUB not found, resetting comms')
                reconnect_successful = False
                while not reconnect_successful and self.monitoring_wifi:
                    # Refresh network connections
                    self.get_ip()
                    if self.connection_attempts > max_connection_attempts:
                        # self.logger.info('Max reconnection attempts reached, restarting PODD')
                        # reconnect_successful = True 											# break out of first loop
                        # need_to_reboot = True
                        # self.stop_wifi_monitoring()												# break out of loop and reboot
                        self.pause_wifi_monitoring(30)
                        pass
                    else:
                        self.logger.info('Attempting reconnect %d', self.connection_attempts)
                        if self.wifi_enabled:
                            success1 = self.setup_wifi()
                        else:
                            success1 = True
                        success2 = self.hub_connected()
                        success = success1 and success2
                        if success:
                            self.logger.info('Reconnection successful')
                            reconnect_successful = True
                            self.connection_attempts = 1
                        else:
                            self.logger.info('Reconnection failed')
                            self.connection_attempts += 1
                        self.pause_wifi_monitoring(10)
        return need_to_reboot

    def stop_wifi_monitoring(self):
        self.monitoring_wifi = False

    def turn_off_wifi(self):
        GPIO.setup(WIFI_PWR_N, GPIO.OUT)
        GPIO.output(WIFI_PWR_N, GPIO.HIGH)
        self.logger.info('Wifi turned off')

    def turn_on_wifi(self):
        GPIO.setup(WIFI_PWR_N, GPIO.OUT)
        GPIO.output(WIFI_PWR_N, GPIO.LOW)
        self.logger.info('Wifi turned on')

    def convert_dbus_to_py(self, dbus_obj):
        """Converts dbus_obj from dbus type to python type.
		:param dbus_obj: dbus object.
		:returns: dbus_obj in python type.
		"""
        _isinstance = partial(isinstance, dbus_obj)
        ConvertType = namedtuple('ConvertType', 'pytype dbustypes')

        pyint = ConvertType(int, (dbus.Byte, dbus.Int16, dbus.Int32, dbus.Int64,
                                  dbus.UInt16, dbus.UInt32, dbus.UInt64))
        pybool = ConvertType(bool, (dbus.Boolean,))
        pyfloat = ConvertType(float, (dbus.Double,))
        pylist = ConvertType(lambda _obj: list(map(self.convert_dbus_to_py, dbus_obj)),
                             (dbus.Array,))
        pytuple = ConvertType(lambda _obj: tuple(map(self.convert_dbus_to_py, dbus_obj)),
                              (dbus.Struct,))
        types_str = (dbus.ObjectPath, dbus.Signature, dbus.String)
        pystr = ConvertType(str, types_str)

        pydict = ConvertType(
            lambda _obj: dict(list(zip(list(map(self.convert_dbus_to_py, dbus_obj.keys())),
                                       list(map(self.convert_dbus_to_py, dbus_obj.values()))
                                       ))
                              ),
            (dbus.Dictionary,)
        )

        for conv in (pyint, pybool, pyfloat, pylist, pytuple, pystr, pydict):
            if any(map(_isinstance, conv.dbustypes)):
                return conv.pytype(dbus_obj)
        else:
            return dbus_obj

    def set_static_ip(self, ip, netmask, gateway):
        ipv4_settings = {}
        ipv4_settings["Method"] = dbus.String("manual", variant_level=1)
        ipv4_settings["Address"] = dbus.String(ip, variant_level=1)
        ipv4_settings["Netmask"] = dbus.String(netmask, variant_level=1)
        ipv4_settings["Gateway"] = dbus.String(gateway, variant_level=1)

        if self.wifi_enabled:
            wlan0_service = ConnService(self.network_connections["wlan0"]["path"])
            wlan0_service.set_property("IPv4.Configuration", ipv4_settings)
        else:
            eth0_service = ConnService(self.network_connections["eth0"]["path"])
            eth0_service.set_property("IPv4.Configuration", ipv4_settings)

    def set_dhcp(self):
        ipv4_settings = {}
        ipv4_settings["Method"] = dbus.String("dhcp", variant_level=1)

        if self.wifi_enabled:
            wlan0_service = ConnService(self.network_connections["wlan0"]["path"])
            wlan0_service.set_property("IPv4.Configuration", ipv4_settings)
        else:
            eth0_service = ConnService(self.network_connections["eth0"]["path"])
            eth0_service.set_property("IPv4.Configuration", ipv4_settings)


if __name__ == "__main__":

    comm = CommsThread()

    start_time = 10
    for t in range(start_time):
        print('Starting in ', (start_time - t))
        time.sleep(1.0)

    comm.set_static_ip('10.1.10.234', '255.255.255.0', '10.1.10.1')

    comm.start_wifi_monitoring()
