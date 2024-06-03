from src.database.GlobalVariable import all_wifi_source, KNN_Model


def load_areas_into_data(areas):
    """
    Load the areas into the data
    Areas is a dictionary that contains the area name and the area object

    Each area object contains the bssid_quality_with_index, which is a dictionary that contains the index and the bssid
    The bssid_quality_with_index looks like this:
    {
        1: {
            'bssid1': 10,
            'bssid2': 20,
            'bssid3': 30
        },
        2: {
            'bssid1': 20,
            'bssid2': 30,
            'bssid3': 40
        }
    }
    The return value will be the X and y, which is the input and output of the KNN model
    The X looks like this:
    [
        [10, 20, 30],
        [20, 30, 40]
    ]
    The y looks like this:
    [
        'Area 1',
        'Area 2'
    ]

    :param areas:
    :return:
    """
    X = []
    y = []

    for name, area_object in areas.items():
        # iterate over the all_wifi_source
        # if the iterated item is in the all_wifi_source, append the signal strength to the row
        # if not, add 0 to the row

        # itearate over the all the index
        for index in area_object.bssid_quality_with_index:
            row = []

            for bssid in all_wifi_source:
                if bssid in area_object.bssid_quality_with_index[index]:
                    row.append(area_object.bssid_quality_with_index[index][bssid])
                else:
                    row.append(0)

            X.append(row)
            y.append(name)

    return X, y


def train_temp(X, y):
    """
    Train the KNN classifier
    It will call the KNN_Model stored in the GlobalVariable.py to fit the model using the X and y
    :param X:
    :param y:
    :return:
    """
    KNN_Model.fit(X, y)


def predict(current):
    """
    Predict the current area based on the current signal strength
    The current variable looks like this: [72, 43, 86, 57, 43, 82, 29, 16, 72, 43, 86, 86, 57, 43, 43, 87, 86, 72]
    The return value will be the area name, looks like this: 'Area 1'

    :param current:
    :return:
    """
    y_pred = KNN_Model.predict([current])
    return y_pred[0]
