import subprocess
import uuid
import os
import redis

from GlobalVariable import Area_Name


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


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_interface_name():
    network_info = subprocess.check_output(['iw', 'dev'])
    network_info = network_info.decode('utf-8', errors='ignore')
    # iterate over each lines, and find the line that contains the interface name
    for line in network_info.split('\n'):
        if 'Interface' in line:
            return line.split(' ')[1]

def store_network_info(area_name):
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


    Area_Name.add(area_name)

    processed_area_name = area_name + " " + str(uuid.uuid4())

    for ssid, ssid_info in networks_dict.items():
        for bssid, bssid_info in ssid_info['BSSIDs'].items():
            r.hset(processed_area_name, bssid, bssid_info['Signal'])


def get_network_info(bssids):
    networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

    networks_info = networks_info.decode('utf-8', errors='ignore')

    networks_dict = parse_win_network_info_into_dictionary(networks_info)

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
