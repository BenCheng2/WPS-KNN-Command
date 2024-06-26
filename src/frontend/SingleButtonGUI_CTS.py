import threading
import tkinter as tk
from threading import Thread
from ttkbootstrap.constants import *

from src.backend.KNN_Predict import predict_knn

from src.database.DatabaseClass import DatabaseClass

DatabaseClass = DatabaseClass()
load_into_X_y = DatabaseClass.load_into_X_y
store_network_info = DatabaseClass.store_network_info
get_network_info = DatabaseClass.get_network_info
save_location_info_to_json_file = DatabaseClass.save_location_info_to_json_file
load_location_info_from_json_file = DatabaseClass.load_location_info_from_json_file


is_recording = False


def on_record_button_click_subprocess_helper(area_name):
    global is_recording
    while is_recording:
        store_network_info(area_name)


def on_record_button_click():
    global is_recording
    area_name = entry.get()
    if not is_recording:
        is_recording = True
        recording_thread = Thread(target=on_record_button_click_subprocess_helper, args=(area_name,))
        recording_thread.start()
        button.config(text="Stop Recording")
    else:
        is_recording = False
        button.config(text="Start Recording")


def on_predict_button_click_subprocess_helper():
    row = get_network_info()
    X, y = load_into_X_y()
    num_samples = len(X)

    if num_samples <= 5:
        result = "Insufficient data to predict"
    else:
        result = predict_knn(X, y, row)


    window = tk.Toplevel()
    window.title("Result")
    window.geometry("300x100")
    label = tk.Label(window, text="The predicted area is: " + result + " (From " + str(num_samples) + " samples)")
    label.pack(pady=10)
    button = tk.Button(window, text="OK", command=window.destroy)
    button.pack(pady=10)


def on_predict_button_click():  # Predict the current position
    threading.Thread(target=on_predict_button_click_subprocess_helper).start()


def on_json_store_button_click():
    save_location_info_to_json_file()

def on_json_load_button_click():
    load_location_info_from_json_file()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Simple Button GUI For Continuous Recording")

    root.geometry("600x160")
    default_font = ('Arial', 16)
    root.option_add("*Font", default_font)

    entry = tk.Entry(root, width=30)
    entry.pack(padx=5, ipady=10, expand=True)

    button_frame = tk.Frame(root)
    button_frame.pack(expand=True, fill=tk.X)

    button = tk.Button(button_frame, text="Start Recording", width=10, command=on_record_button_click)
    button.pack(side=LEFT, expand=True)

    store_button = tk.Button(button_frame, text="Store", width=10, command=on_json_store_button_click)
    store_button.pack(side=tk.LEFT, expand=True)

    load_button = tk.Button(button_frame, text="Load", width=10, command=on_json_load_button_click)
    load_button.pack(side=tk.LEFT, expand=True)

    predict_button = tk.Button(button_frame, text="Predict", width=10, command=on_predict_button_click)
    predict_button.pack(side=RIGHT, expand=True)

    root.mainloop()
