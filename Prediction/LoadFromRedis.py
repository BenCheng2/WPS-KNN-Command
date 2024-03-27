import redis

from GlobalVariable import Area_Name
from Prediction.KNN_Predict import predict

# Start Variable
Local_Area_Name = []
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Debug Variable
debug = True

if debug:
    Local_Area_Name = ['Room A', 'Area2', 'Area3']
else:
    Local_Area_Name = Area_Name



# Functions
def load_from_redis_all_bssid():
    # Iterate first to get all the BSSID
    bssid = set()
    for key in r.scan_iter():
        # Iterate over the hash structure keys
        for bssid_key in r.hkeys(key):
            bssid.add(bssid_key)
    return bssid

def load_from_redis_all_names():
    # Iterate first to get all the BSSID
    names = set()
    for key in r.scan_iter():
        names.add(key.rsplit(maxsplit=1)[0])
    return names


def load_from_redis_into_X_y(bssids):
    """
    Load the data from the redis server
    Return X, y, that will be used to train the KNN model
    """

    X = []
    y = []

    # iterate over global variables Area_Name
    for area_name in load_from_redis_all_names():
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


