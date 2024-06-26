import json
import os
import subprocess
import uuid
from tkinter import filedialog

import redis

from dotenv import load_dotenv

from src.helper.singleton import singleton

load_dotenv()

from collections import defaultdict


def parse_win_network_info_into_dictionary(networks_output):
    network_info = {}
    current_ssid = None
    current_bssid = None

    for line in networks_output.split('\n'):
        line = line.strip()
        if line.startswith('SSID'):
            ssid_info = line.split(':', 1)
            if len(ssid_info) == 2:
                current_ssid = ssid_info[1].strip()
                network_info[current_ssid] = {'BSSIDs': {}}
                current_bssid = None
        elif line.startswith('BSSID'):
            bssid_key = line.split(':', 1)[1].strip()
            if current_ssid is not None:
                network_info[current_ssid]['BSSIDs'][bssid_key] = {}
                current_bssid = bssid_key
        elif current_ssid is not None:
            if current_bssid and ':' in line:
                key, value = line.split(':', 1)
                network_info[current_ssid]['BSSIDs'][current_bssid][key.strip()] = value.strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                network_info[current_ssid][key.strip()] = value.strip()

    return network_info


def parse_linux_network_info_into_dictionary(networks_output):
    network_info = {}
    current_ssid = None
    current_bssid = None
    current_signal = None
    for line in networks_output.split('\n'):
        line = line.strip()
        if 'Address:' in line:
            current_bssid = line.split(': ')[1]
        elif 'ESSID:' in line:
            current_ssid = line.split(':')[1]
            current_ssid = current_ssid[1:-1]

            if current_ssid not in network_info:
                network_info[current_ssid] = {'BSSIDs': {}}

            if current_bssid not in network_info[current_ssid]['BSSIDs']:
                network_info[current_ssid]['BSSIDs'][current_bssid] = {}

            if current_signal:
                network_info[current_ssid]['BSSIDs'][current_bssid]['Signal'] = current_signal


        elif 'Signal level=' in line:
            current_signal = line.split('Signal level=')[1]
            current_signal = current_signal.split(' ')[0]
            current_signal = int(current_signal)

    return network_info


def get_interface_name():
    network_info = subprocess.check_output(['iw', 'dev'])
    network_info = network_info.decode('utf-8', errors='ignore')
    # iterate over each lines, and find the line that contains the interface name
    for line in network_info.split('\n'):
        if 'Interface' in line:
            return line.split(' ')[1]


@singleton
class DatabaseClass:
    def __init__(self, redis_port=6379, with_redis=True):
        self.with_redis = with_redis

        self.local_memory = defaultdict(lambda: defaultdict(dict))
        self.bssids = set()

        # The redis database is only for demonstration purposes
        # Therefore no persistence operation should be done
        self.r0 = None
        if self.with_redis:
            self.r0 = redis.Redis(host='localhost', port=redis_port, db=0, decode_responses=True)

            # Clean the Redis database
            self.r0.flushdb()

    def _get_networks_info_from_system(self):
        # Helper to get the current network information from the system at this moment
        if os.name == 'nt':
            # the system is windows
            networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = parse_win_network_info_into_dictionary(networks_info)
        else:
            # the system is linux/ubuntu
            interface = get_interface_name()
            networks_info = subprocess.check_output(['iwlist', interface, 'scan'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = parse_linux_network_info_into_dictionary(networks_info)

        return networks_dict

    def store_network_info(self, area_name):
        networks_dict = self._get_networks_info_from_system()

        processed_area_name = area_name + " " + str(uuid.uuid4())

        # The database class in the redis mode need to sync the local memory with the redis database
        # To avoid repeated computation, we do the check outside the loop
        if self.with_redis:
            for ssid, ssid_info in networks_dict.items():
                for bssid, bssid_info in ssid_info['BSSIDs'].items():
                    self.local_memory[processed_area_name][bssid] = bssid_info['Signal']
                    self.bssids.add(bssid)
        else:
            for ssid, ssid_info in networks_dict.items():
                for bssid, bssid_info in ssid_info['BSSIDs'].items():
                    self.local_memory[processed_area_name][bssid] = bssid_info['Signal']
                    self.r0.hset(processed_area_name, bssid, bssid_info['Signal'])
                    self.bssids.add(bssid)

    def get_network_info(self):
        # Function to get the current network information from the system at this moment
        # Without storing it in the database
        networks_dict = self._get_networks_info_from_system()

        bssid_dict = {}
        for ssid, ssid_info in networks_dict.items():
            for bssid, bssid_info in ssid_info['BSSIDs'].items():
                bssid_dict[bssid] = bssid_info['Signal']

        row = []
        for bssid in self.bssids:
            if bssid in bssid_dict:
                row.append(float(bssid_dict[bssid].strip('%')) / 100)
            else:
                row.append(0)

        return row

    # def load_from_redis_all_bssid(self):
    #
    #     # Iterate first to get all the BSSID
    #     bssid = set()
    #     for key in self.r0.scan_iter():
    #         # Iterate over the hash structure keys
    #         for bssid_key in self.r0.hkeys(key):
    #             bssid.add(bssid_key)
    #     return bssid
    #
    # # def load_from_redis_into_X_y(self, bssids):
    # #     X = []
    # #     y = []
    # #
    # #     redis_all_names = set()
    # #     for key in self.r0.scan_iter():
    # #         redis_all_names.add(key.rsplit(maxsplit=1)[0])
    # #
    # #     for area_name in redis_all_names:
    # #         for key in self.r0.scan_iter(area_name + ' *'):
    # #             row = []
    # #             for bssid_key in bssids:
    # #                 signal = self.r0.hget(key, bssid_key)
    # #                 if signal:
    # #                     row.append(float(signal.strip('%')) / 100)
    # #                 else:
    # #                     row.append(0)
    # #             X.append(row)
    # #             y.append(area_name)
    # #
    # #     return X, y
    #
    # def load_from_redis_all_names_and_data(self):
    #     all_data = {}
    #     count = 0
    #     for key in self.r0.scan_iter():
    #         count += 1
    #         name = key.rsplit(maxsplit=1)[0]
    #         if name not in all_data:
    #             all_data[name] = {}
    #         all_data[name][key] = self.r0.hgetall(key)
    #
    #     print("Finish loading from redis")
    #     return all_data

    def load_into_X_y(self):
        X = []
        y = []

        for area_name in self.local_memory:
            vals = self.local_memory[area_name]
            for val in vals:
                row = []
                for bssid_key in self.bssids:
                    signal = vals.get(bssid_key)
                    if signal:
                        row.append(float(signal.strip('%')) / 100)
                    else:
                        row.append(0)
                X.append(row)
                y.append(area_name.rsplit(maxsplit=1)[0])

        return X, y

    def save_location_info_to_json_file(self, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not filename:
                return

        with open(filename, "w") as f:
            json.dump(self.local_memory, f, indent=4)

    def load_location_info_from_json_file(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not filename:
                return None

        with open(filename, "r") as f:
            self.local_memory = json.load(f)
            # Need to reinitialize the set of bssids as json file does not store the set and only store the local memory
            self._set_bssids_by_local_memory()

            # Need to sync the local memory with the redis database
            if self.with_redis:
                for area_name in self.local_memory:
                    for bssid in self.local_memory[area_name]:
                        self.r0.hset(area_name, bssid, self.local_memory[area_name][bssid])
        return self.local_memory

    def _set_bssids_by_local_memory(self):
        # Helper to set the set of bssids by looking values in local memory
        self.bssids = set()
        for area_name in self.local_memory:
            for bssid in self.local_memory[area_name]:
                self.bssids.add(bssid)
