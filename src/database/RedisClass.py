import json
import os
import subprocess
import uuid
from tkinter import filedialog

import redis

from dotenv import load_dotenv
load_dotenv()


def singleton(cls):
    # Decorator to enable singleton pattern

    _instance = {}

    def inner(*args, **kwargs):
        if cls in _instance:
            return _instance[cls]
        obj = cls(*args, **kwargs)
        _instance[cls] = obj

        return obj

    return inner


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
class RedisClass:
    def __init__(self, port=6379, with_redis=True):
        self.with_redis = with_redis

        if (self.with_redis):
            self.r0 = redis.Redis(host='localhost', port=port, db=0, decode_responses=True)  # r0 stores all information
            self.r1 = redis.Redis(host='localhost', port=port, db=1, decode_responses=True)  # r1 stores all all bssids

            self.local_memory = self.load_from_redis_all_names_and_data()
            self.bssids = self.load_from_redis_all_bssid()

        else:
            self.local_memory = {}
            self.bssids = set()

    def store_network_info(self, area_name):
        # if the system is windows
        if os.name == 'nt':
            networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = parse_win_network_info_into_dictionary(networks_info)
        else:
            # the system is linux/ubuntu
            interface = get_interface_name()
            networks_info = subprocess.check_output(['iwlist', interface, 'scan'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = parse_linux_network_info_into_dictionary(networks_info)
            print(networks_dict)

            # return networks_dict

        processed_area_name = area_name + " " + str(uuid.uuid4())

        for ssid, ssid_info in networks_dict.items():
            for bssid, bssid_info in ssid_info['BSSIDs'].items():
                self.r0.hset(processed_area_name, bssid, bssid_info['Signal'])
                # add_into_all_data(processed_area_name, bssid, bssid_info['Signal'])

    def get_network_info(self):
        networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

        networks_info = networks_info.decode('utf-8', errors='ignore')

        networks_dict = parse_win_network_info_into_dictionary(networks_info)

        dict_bssid_signal = {}
        for ssid, ssid_info in networks_dict.items():
            for bssid, bssid_info in ssid_info['BSSIDs'].items():
                dict_bssid_signal[bssid] = bssid_info['Signal']

        row = []
        for bssid in self.bssids:
            if bssid in dict_bssid_signal:
                row.append(float(dict_bssid_signal[bssid].strip('%')) / 100)
            else:
                row.append(0)

        return row

    def load_from_redis_all_bssid(self):

        # Iterate first to get all the BSSID
        bssid = set()
        for key in self.r0.scan_iter():
            # Iterate over the hash structure keys
            for bssid_key in self.r0.hkeys(key):
                bssid.add(bssid_key)
        return bssid

    # def load_from_redis_into_X_y(self, bssids):
    #     X = []
    #     y = []
    #
    #     redis_all_names = set()
    #     for key in self.r0.scan_iter():
    #         redis_all_names.add(key.rsplit(maxsplit=1)[0])
    #
    #     for area_name in redis_all_names:
    #         for key in self.r0.scan_iter(area_name + ' *'):
    #             row = []
    #             for bssid_key in bssids:
    #                 signal = self.r0.hget(key, bssid_key)
    #                 if signal:
    #                     row.append(float(signal.strip('%')) / 100)
    #                 else:
    #                     row.append(0)
    #             X.append(row)
    #             y.append(area_name)
    #
    #     return X, y

    def load_from_redis_all_names_and_data(self):
        all_data = {}
        count = 0
        for key in self.r0.scan_iter():
            count += 1
            name = key.rsplit(maxsplit=1)[0]
            if name not in all_data:
                all_data[name] = {}
            all_data[name][key] = self.r0.hgetall(key)

        print("Finish loading from redis")
        return all_data

    def load_into_X_y(self):
        X = []
        y = []

        for area_name in self.local_memory:
            vals = self.local_memory[area_name]
            for val in vals:
                row = []

                one_record = vals[val]
                for bssid_key in self.bssids:
                    signal = one_record.get(bssid_key)
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
        return self.local_memory
