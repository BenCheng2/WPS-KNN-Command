import threading
import tkinter as tk
from ttkbootstrap.constants import *

from src.backend.KNN_Predict import predict_knn

from src.database.RedisClass import RedisClass

RedisClass = RedisClass()
load_from_redis_all_bssid = RedisClass.load_from_redis_all_bssid
load_into_X_y = RedisClass.load_into_X_y
load_from_redis_all_names_and_data = RedisClass.load_from_redis_all_names_and_data
store_network_info = RedisClass.store_network_info
get_network_info = RedisClass.get_network_info
load_from_redis_into_X_y = RedisClass.load_from_redis_into_X_y


def on_record_button_click():  # Record the position information
    area_name = entry.get()
    store_network_info(area_name)

def on_predict_button_click_subprocess_helper():
    bssids = load_from_redis_all_bssid()
    row = get_network_info(bssids)
    X, y = load_from_redis_into_X_y(bssids)
    result = predict_knn(X, y, row)

    # Pump a window showing the result
    window = tk.Toplevel()
    window.title("Result")
    window.geometry("300x100")
    label = tk.Label(window, text="The predicted area is: " + result)
    label.pack(pady=10)
    button = tk.Button(window, text="OK", command=window.destroy)
    button.pack(pady=10)


def on_predict_button_click():  # Predict the current position
    threading.Thread(target=on_predict_button_click_subprocess_helper).start()


def on_load_button_click():
    print("Load button clicked")


load_from_redis_all_names_and_data()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Simple Button GUI")

    root.geometry("600x160")
    default_font = ('Arial', 16)
    root.option_add("*Font", default_font)

    entry = tk.Entry(root, width=30)
    entry.pack(padx=5, ipady=10, expand=True)

    button_frame = tk.Frame(root)
    button_frame.pack(expand=True, fill=tk.X)

    button = tk.Button(button_frame, text="Click", width=16, command=on_record_button_click)
    button.pack(side=LEFT, expand=True)

    load_button = tk.Button(button_frame, text="Load", width=10, command=on_load_button_click)
    load_button.pack(side=tk.LEFT, expand=True)

    predict_button = tk.Button(button_frame, text="Predict", width=16, command=on_predict_button_click)
    predict_button.pack(side=RIGHT, expand=True)

    root.mainloop()
