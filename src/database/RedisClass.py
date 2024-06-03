import os
import subprocess
import uuid

import redis


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


@singleton
class RedisClass:
    def __init__(self, port=6379, db=0):
        self.r = redis.Redis(host='localhost', port=port, db=db, decode_responses=True)

    def parse_win_network_info_into_dictionary(self, networks_output):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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

    def parse_linux_network_info_into_dictionary(self, networks_output):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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

    def get_interface_name(self):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        network_info = subprocess.check_output(['iw', 'dev'])
        network_info = network_info.decode('utf-8', errors='ignore')
        # iterate over each lines, and find the line that contains the interface name
        for line in network_info.split('\n'):
            if 'Interface' in line:
                return line.split(' ')[1]

    def store_network_info(self, area_name):

        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # if the system is windows
        if os.name == 'nt':
            networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = self.parse_win_network_info_into_dictionary(networks_info)
        else:
            # the system is linux/ubuntu
            interface = self.get_interface_name()
            networks_info = subprocess.check_output(['iwlist', interface, 'scan'])
            networks_info = networks_info.decode('utf-8', errors='ignore')
            networks_dict = self.parse_linux_network_info_into_dictionary(networks_info)
            print(networks_dict)

            # return networks_dict

        processed_area_name = area_name + " " + str(uuid.uuid4())

        for ssid, ssid_info in networks_dict.items():
            for bssid, bssid_info in ssid_info['BSSIDs'].items():
                self.r.hset(processed_area_name, bssid, bssid_info['Signal'])
                # add_into_all_data(processed_area_name, bssid, bssid_info['Signal'])

    def get_network_info(self, bssids):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

        networks_info = networks_info.decode('utf-8', errors='ignore')

        networks_dict = self.parse_win_network_info_into_dictionary(networks_info)

        dict_bssid_signal = {}
        for ssid, ssid_info in networks_dict.items():
            for bssid, bssid_info in ssid_info['BSSIDs'].items():
                dict_bssid_signal[bssid] = bssid_info['Signal']

        row = []
        for bssid in bssids:
            if bssid in dict_bssid_signal:
                row.append(float(dict_bssid_signal[bssid].strip('%')) / 100)
            else:
                row.append(0)

        return row

    def load_from_redis_all_bssid():
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        # Iterate first to get all the BSSID
        bssid = set()
        for key in r.scan_iter():
            # Iterate over the hash structure keys
            for bssid_key in r.hkeys(key):
                bssid.add(bssid_key)
        return bssid

    def load_from_redis_into_X_y(bssids):
        """
        This version of function fetch the data redis while using
        :param bssids:
        :return:
        """

        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        X = []
        y = []

        redis_all_names = set()
        for key in r.scan_iter():
            redis_all_names.add(key.rsplit(maxsplit=1)[0])

        for area_name in redis_all_names:
            for key in r.scan_iter(area_name + ' *'):
                row = []
                for bssid_key in bssids:
                    signal = r.hget(key, bssid_key)
                    if signal:
                        row.append(float(signal.strip('%')) / 100)
                    else:
                        row.append(0)
                X.append(row)
                y.append(area_name)

        return X, y

    def load_from_redis_all_names_and_data(self):

        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        all_data = {}
        count = 0
        for key in r.scan_iter():
            count += 1
            name = key.rsplit(maxsplit=1)[0]
            if name not in all_data:
                all_data[name] = {}
            all_data[name][key] = r.hgetall(key)
        # set_all_data(all_data)

        print("Finish loading from redis")
        return all_data

    def load_into_X_y(bssids):
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

        X = []
        y = []

        # all_data = dict(get_all_data())

        for area_name in all_data.keys():
            row = []
            vals = all_data[area_name]
            for bssid_key in bssids:
                signal = vals.get(bssid_key)
                if signal:
                    row.append(float(signal.strip('%')) / 100)
                else:
                    row.append(0)
            X.append(row)
            y.append(area_name.rsplit(maxsplit=1)[0])

        return X, y
