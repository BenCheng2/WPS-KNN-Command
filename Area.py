import random
from access_points import get_scanner

wifi_scanner = get_scanner()

from GlobalVariable import all_wifi_source


class Area:
    def __init__(self, name):
        self.name = name
        self.access_points_with_index = {}
        self.bssid_quality_with_index = {}

    def add_access_point(self, index):
        # add random number to the back of index if the index already exists
        if index in self.access_points_with_index:
            # iterate until the index is unique
            while index in self.access_points_with_index:
                index += '_'
                index += str(random.randint(0, 100))

        access_points = wifi_scanner.get_access_points()

        self.access_points_with_index[index] = access_points

        self.bssid_quality_with_index[index] = {}
        for ap in access_points:
            self.bssid_quality_with_index[index][ap["bssid"]] = ap["quality"]
            if ap["bssid"] not in all_wifi_source:
                all_wifi_source.append(ap["bssid"])

    def del_index(self, index):
        if index in self.access_points_with_index:
            # remove the index and its access points
            del self.access_points_with_index[index]
            del self.bssid_quality_with_index[index]


    def get_access_points(self, index):
        if index in self.access_points_with_index:
            return self.access_points_with_index[index]
        else:
            return None



