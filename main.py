# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from Area import Area, wifi_scanner
from GlobalVariable import all_wifi_source, areas
from MachineLearning import load_areas_into_data, train_temp, predict

def add_new_area(name, index):

    if name not in areas:
        areas[name] = Area(name)
    areas[name].add_access_point(index)

def get_current_bssid_list():
    access_points = wifi_scanner.get_access_points()
    # Obtain the bssid list
    bssid_list = []
    for ap in access_points:
        bssid_list.append(ap["bssid"])

    row = []

    # Iterate over the all_wifi_source, to get the signal strength of the current area
    for bssid in all_wifi_source:
        if bssid in bssid_list:
            for ap in access_points:
                if ap["bssid"] == bssid:
                    row.append(ap["quality"])
        else:
            row.append(0)

    return row


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    while True:
        name = input("Enter the current area: ")
        if name.lower() == 'quit':
            break  # Exit the loop if the user types 'quit'
        index = int(input("Enter the current index: "))

        add_new_area(name, index)
    X, y = load_areas_into_data(areas)

    train_temp(X, y)

    current = get_current_bssid_list()

    print("Predicted Area:", predict(current))
