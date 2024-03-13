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

def command_enter_area():
    """
    When the user enters the area,
    they will be repeatedly asked to enter the area and the index of the access point.
    :return:
    """
    while True:
        name = input("Enter the current area ('quit' to stop):  ")
        if name.lower() == 'quit':
            break  # Exit the loop if the user types 'quit'
        index = input("Enter the current index: ")

        add_new_area(name, index)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # The user will be in a loop to enter the command
    while True:
        base_command = input("Enter the command ('quit' to stop):  ")
        if base_command.lower() == 'quit':
            break
        elif base_command.lower() == 'record':
            # If the user enters 'record', the user will enter another loop
            # to enter the area and index repeatedly
            command_enter_area()
        elif base_command.lower() == 'predict':
            X, y = load_areas_into_data(areas)
            train_temp(X, y)
            current = get_current_bssid_list()
            print(predict(current))


