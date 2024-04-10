import tkinter as tk
from threading import Thread
import time

from Position.Redis import store_network_info, get_network_info
from Prediction.KNN_Predict import predict_knn
from Prediction.LoadFromRedis import load_from_redis_into_X_y, load_from_redis_all_bssid

# Flag to keep track of recording state
is_recording = False

def record_continuously(area_name):
    global is_recording
    while is_recording:
        store_network_info(area_name)
        time.sleep(0.2)  # Delay between recordings, adjust as needed

def on_record_button_click():  # Toggle the recording state
    global is_recording
    area_name = entry.get()
    if not is_recording:
        is_recording = True
        recording_thread = Thread(target=record_continuously, args=(area_name,))
        recording_thread.start()
        button.config(text="Stop Recording")
    else:
        is_recording = False
        button.config(text="Start Recording")

def on_predict_button_click():  # Predict the current position
    bssids = load_from_redis_all_bssid()
    row = get_network_info(bssids)
    X, y = load_from_redis_into_X_y(bssids)
    result = predict_knn(X, y, row)
    print(result)

root = tk.Tk()
root.title("Simple GUI")

root.geometry("300x150")

entry = tk.Entry(root)
entry.pack(pady=10)

button = tk.Button(root, text="Start Recording", command=on_record_button_click)
button.pack(expand=True)

predict_button = tk.Button(root, text="Predict", command=on_predict_button_click)
predict_button.pack(expand=True)

root.mainloop()
