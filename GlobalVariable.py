from sklearn.neighbors import KNeighborsClassifier

# Old global variables
# all_wifi_source = []
# global_areas = {}

# Store the trained model
# KNN_Model = KNeighborsClassifier(n_neighbors=5)
KNN_Model = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)

# Store all the data from the redis server
# Fetched from the redis and the start of the program
All_Data = {}

def set_all_data(data):
    global All_Data
    All_Data = data

def get_all_data():
    global All_Data
    return All_Data

def add_into_all_data(processed_area_name, bssid, signal):
    global All_Data
    if processed_area_name not in All_Data:
        All_Data[processed_area_name] = {}
    All_Data[processed_area_name][bssid] = signal

