"""
Class to keep track of connected devices
"""

import time


class DeviceList:
    def __init__(self):
        self._devices = {}

    def get_devices(self):
        device_list = []
        for ip, device in list(self._devices.items()):
            if time.time() - device['last active'] > 5:
                del self._devices[ip]
            else:
                device_list.append((ip, device['name']))
        return device_list

    def add_device(self, ip, name):
        self._devices.update({ip: {
            'name': name,
            'last active': time.time(),
            'received': False
        }})

    def update_activity(self, ip):
        self._devices[ip]['last active'] = time.time()

    def get_received(self, ip):
        return self._devices[ip]['received']

    def set_received(self, ip, value):
        self._devices[ip]['received'] = value
