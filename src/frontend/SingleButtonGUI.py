import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


from src.backend.KNN_Predict import predict_knn

from src.database.RedisClass import RedisClass
RedisClass = RedisClass()
load_from_redis_all_bssid = RedisClass.load_from_redis_all_bssid
load_into_X_y = RedisClass.load_into_X_y
load_from_redis_all_names_and_data = RedisClass.load_from_redis_all_names_and_data
store_network_info = RedisClass.store_network_info
get_network_info = RedisClass.get_network_info

def on_record_button_click():  # Record the position information
    area_name = entry.get()
    store_network_info(area_name)



def on_predict_button_click():  # Predict the current position
    bssids = load_from_redis_all_bssid()
    row = get_network_info(bssids)
    # X, y = load_from_redis_into_X_y(bssids)
    X, y = load_into_X_y(bssids)

    result = predict_knn(X, y, row)
    print(result)


load_from_redis_all_names_and_data()

#
# root.geometry("300x100")
#
# entry = tk.Entry(root)
# entry.pack(pady=10)
#
# button = tk.Button(root, text="Click", command=on_record_button_click)
# button.pack(expand=True)
#
# predict_button = tk.Button(root, text="Predict", command=on_predict_button_click)
# predict_button.pack(expand=True)
#
# root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Simple Button GUI")

    root.geometry("400x160")
    default_font = ('Arial', 16)
    root.option_add("*Font", default_font)

    entry = tk.Entry(root, width=30)
    entry.pack(padx=5, ipady=10, expand=True)

    # Frame for buttons to help in alignment
    button_frame = tk.Frame(root)
    button_frame.pack(expand=True, fill=tk.X)

    # Button for 'Click'
    button = tk.Button(button_frame, text="Click",  width=16, command=on_record_button_click)
    button.pack(side=LEFT, padx=5, expand=True)

    # Button for 'Predict'
    predict_button = tk.Button(button_frame, text="Predict", width=16, command=on_predict_button_click)
    predict_button.pack(side=RIGHT, padx=5, expand=True)


    root.mainloop()

