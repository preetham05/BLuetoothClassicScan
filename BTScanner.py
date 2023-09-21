#!/usr/bin/env python3

import time
import select
import requests
import json
import logging
import bluetooth
import uuid
import re
import sys
import os
import socket


BT_Device = {}
retry_count = 0

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

class MyDiscoverer(bluetooth.DeviceDiscoverer):

    def pre_inquiry(self):
        self.done = False

    def device_discovered(self, address, device_class, rssi, name):
        # print("{} - {}".format(address, name))
        address = address.replace(":", "")

        BT_Device[address]=rssi
        # Compute distance using Proxmity API later

    def inquiry_complete(self):
        logging.warning("Scanning completed")

        self.done = True
        BT_Device.clear()



d = MyDiscoverer()

d.find_devices(lookup_names=True)

readfiles = [d, ]
rfds = select.select(readfiles, [], [])[0]

while True:

    if d in rfds:
        d.process_event()
    if d.done:
        time.sleep(0.02)
        try:
            d.find_devices(lookup_names=True)
        except:
            pass
    # Create a small sleep to flush cache in dBus
    time.sleep(1)
