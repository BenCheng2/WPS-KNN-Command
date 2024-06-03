import redis

from src.database.GlobalVariable import set_all_data, get_all_data

# Start Variable
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Debug Variable
debug = True



# Functions
def load_from_redis_all_bssid():
    # Iterate first to get all the BSSID
    bssid = set()
    for key in r.scan_iter():
        # Iterate over the hash structure keys
        for bssid_key in r.hkeys(key):
            bssid.add(bssid_key)
    return bssid

def load_from_redis_into_X_y(bssids):
    """
    This version of function fetch the data redis while using
    :param bssids:
    :return:
    """

    X = []
    y = []

    redis_all_names = set()
    for key in r.scan_iter():
        redis_all_names.add(key.rsplit(maxsplit=1)[0])

    for area_name in redis_all_names:
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

def load_from_redis_all_names_and_data():
    all_data = {}
    count = 0
    for key in r.scan_iter():
        count += 1
        name = key.rsplit(maxsplit=1)[0]
        if name not in all_data:
            all_data[name] = {}
        all_data[name][key] = r.hgetall(key)
    set_all_data(all_data)

    print("Finish loading from redis")
    return all_data

def load_into_X_y(bssids):
    X = []
    y = []

    all_data = dict(get_all_data())

    for area_name in all_data.keys():
        row = []
        vals = all_data[area_name]
        for bssid_key in bssids:
            signal = vals.get(bssid_key)
            if signal:
                row.append(float(signal.strip('%')) / 100)
            else:
                row.append(0)
        X.append(row)
        y.append(area_name.rsplit(maxsplit=1)[0])

    return X, y

