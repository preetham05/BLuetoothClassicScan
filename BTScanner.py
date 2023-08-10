#!/usr/bin/env python3

import time
import select
import requests
import json
import logging
import bluetooth
import uuid
import re
import socket


baseURL='http://zigpos-gateway331/rtls_api/rest'

BT_Device = {}
ScanData = []
address_base = 0x70B3
anchor_address = hex(address_base<<48 | (uuid.getnode()))
print('HexValue:'+ anchor_address)
anchor_address = int(anchor_address,16)
print(anchor_address)
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
        # print("{} - {}".format(address, name))

        # get some information out of the device class and display it.
        # voodoo magic specified at:
        # https://www.bluetooth.org/foundry/assignnumb/document/baseband
        # major_classes = ("Miscellaneous",
        #                  "Computer",
        #                  "Phone",
        #                  "LAN/Network Access Point",
        #                  "Audio/Video",
        #                  "Peripheral",
        #                  "Imaging")
        # major_class = (device_class >> 8) & 0xf
        # if major_class < 7:
        #     print(" " + major_classes[major_class])
        # else:
        #     print("  Uncategorized")

        # print("  Services:")
        # service_classes = ((16, "positioning"),
        #                    (17, "networking"),
        #                    (18, "rendering"),
        #                    (19, "capturing"),
        #                    (20, "object transfer"),
        #                    (21, "audio"),
        #                    (22, "telephony"),
        #                    (23, "information"))

        # for bitpos, classname in service_classes:
        #     if device_class & (1 << (bitpos-1)):
        #         print("   ", classname)
        BT_Device[address]=rssi
        for bt_macAdreess, rssi in BT_Device.items():

            data = {    "macAddress": str(bt_macAdreess),
                        "uuid": "0",
                        "majorNum": 0,
                        "minorNum": 0,
                        "txPowerAt1m": 0,
                        "rssi": rssi}
            # print(json.dumps(data))
            ScanData.append(data)

            # print(baseURL + '/bluetooth/1/anchor/' + str(anchor_address) + '/scanresults/')

            r = requests.post(url=baseURL + '/bluetooth/1/anchor/' + str(anchor_address) + '/scanresults/',
                            data= json.dumps(ScanData),
                            headers={'Content-Type': 'application/json'})
            print(r.text)
            response_code = r.status_code
            logging.info(response_code)
            response_message = r.content
            if response_code == 200:
                logging.info("The address %s sent the beacon", address)

            else:
                logging.warning("The address %s failed to send the beacon", address)
    def inquiry_complete(self):
        logging.warning("Scanning completed")

        self.done = True
        BT_Device.clear()

anchor_data = {
                "address": anchor_address,
                "networkType": "BLUETOOTH",
                "appRole": "ANCHOR",
                "activated": True,
                "connected": True,
                "customName": socket.gethostname()
                }
print(json.dumps(anchor_data))

r = requests.put(url=baseURL + '/devices/',
                            data= json.dumps(anchor_data),
                            headers={'Content-Type': 'application/json'})
print(r.text)
response_code = r.status_code
logging.warning(response_code)
response_message = r.content
if response_code == 200:
    logging.warning("The address %s added to the devices ", anchor_address)

else:
    logging.warning("The address %s failed to be added to the devices ", anchor_address)


d = MyDiscoverer()
d.find_devices(lookup_names=True)

readfiles = [d, ]
rfds = select.select(readfiles, [], [])[0]

while True:

    if d in rfds:
        d.process_event()
    if d.done:
        time.sleep(0.02)
        d.find_devices(lookup_names=True)
