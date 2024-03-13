from sklearn.neighbors import KNeighborsClassifier

# Recording all the wifi bssid that has been scanned
all_wifi_source = []

# Record the area name and their matched area object
global_areas = {}

# Store the trained model
KNN_Model = KNeighborsClassifier(n_neighbors=5)