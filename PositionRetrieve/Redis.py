import subprocess
import uuid

import redis


def parse_network_info_into_dictionary(networks_output):
    network_info = {}
    current_ssid = None
    current_bssid = None  # Ensure current_bssid is initialized

    for line in networks_output.split('\n'):
        line = line.strip()
        if line.startswith('SSID'):
            ssid_info = line.split(':', 1)
            if len(ssid_info) == 2:
                current_ssid = ssid_info[1].strip()
                network_info[current_ssid] = {'BSSIDs': {}}
                current_bssid = None  # Reset current_bssid when a new SSID starts
        elif line.startswith('BSSID'):
            bssid_key = line.split(':', 1)[1].strip()
            if current_ssid is not None:
                # Initialize the BSSID key in the dictionary to avoid KeyError
                network_info[current_ssid]['BSSIDs'][bssid_key] = {}
                current_bssid = bssid_key
        elif current_ssid is not None:
            if current_bssid and ':' in line:  # Check current_bssid is not None and line has key:value format
                key, value = line.split(':', 1)
                network_info[current_ssid]['BSSIDs'][current_bssid][key.strip()] = value.strip()
            elif ':' in line:  # Handle SSID-level information
                key, value = line.split(':', 1)
                network_info[current_ssid][key.strip()] = value.strip()

    return network_info


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def store_network_info():
    networks_info = subprocess.check_output(['netsh', 'wlan', 'show', 'network', 'mode=Bssid'])

    # decode it to strings using UTF-8 instead of ASCII
    networks_info = networks_info.decode('utf-8', errors='ignore')

    # Parse the network information into a dictionary
    networks_dict = parse_network_info_into_dictionary(networks_info)

    hash_name = str(uuid.uuid4())
    for ssid, ssid_info in networks_dict.items():
        for bssid, bssid_info in ssid_info['BSSIDs'].items():
            r.hset(hash_name, bssid, bssid_info['Signal'])


store_network_info()
