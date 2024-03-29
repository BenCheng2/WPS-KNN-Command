import subprocess
import uuid

import redis

from GlobalVariable import Area_Name


def parse_network_info_into_dictionary(networks_output):
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


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def store_network_info(area_name):
    networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

    networks_info = networks_info.decode('utf-8', errors='ignore')

    networks_dict = parse_network_info_into_dictionary(networks_info)

    Area_Name.add(area_name)

    processed_area_name = area_name + " " + str(uuid.uuid4())

    for ssid, ssid_info in networks_dict.items():
        for bssid, bssid_info in ssid_info['BSSIDs'].items():
            r.hset(processed_area_name, bssid, bssid_info['Signal'])


def get_network_info(bssids):
    networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

    networks_info = networks_info.decode('utf-8', errors='ignore')

    networks_dict = parse_network_info_into_dictionary(networks_info)

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
