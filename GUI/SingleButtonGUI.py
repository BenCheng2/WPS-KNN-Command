import tkinter as tk
from PositionRetrieve.Redis import store_network_info

def on_button_click():
    area_name = entry.get()
    store_network_info(area_name)

root = tk.Tk()
root.title("Simple GUI")

root.geometry("300x100")

entry = tk.Entry(root)
entry.pack(pady=10)

button = tk.Button(root, text="Click", command=on_button_click)

predict_button = tk.Button(root, text="Predict")

button.pack(expand=True)
predict_button.pack(expand=True)

root.mainloop()
