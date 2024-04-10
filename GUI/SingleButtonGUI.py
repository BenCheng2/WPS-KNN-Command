import tkinter as tk

from GlobalVariable import get_all_data
from Position.Redis import store_network_info, get_network_info
from Prediction.KNN_Predict import predict_knn
from Prediction.LoadFromRedis import load_from_redis_into_X_y, load_from_redis_all_bssid, load_into_X_y, \
    load_from_redis_all_names_and_data


def on_record_button_click():  # Record the position information
    area_name = entry.get()
    store_network_info(area_name)

    print(get_all_data())


def on_predict_button_click():  # Predict the current position
    bssids = load_from_redis_all_bssid()
    row = get_network_info(bssids)
    # X, y = load_from_redis_into_X_y(bssids)
    X, y = load_into_X_y(bssids)

    result = predict_knn(X, y, row)
    print(result)


load_from_redis_all_names_and_data()
print(get_all_data())

root = tk.Tk()
root.title("Simple GUI")

root.geometry("300x100")

entry = tk.Entry(root)
entry.pack(pady=10)

button = tk.Button(root, text="Click", command=on_record_button_click)
button.pack(expand=True)

predict_button = tk.Button(root, text="Predict", command=on_predict_button_click)
predict_button.pack(expand=True)

root.mainloop()
