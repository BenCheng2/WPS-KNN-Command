import threading
import tkinter as tk
from threading import Thread
from tkinter.scrolledtext import ScrolledText

from src.backend.GPT import start_conversation, send_to_gpt, load_gpt_chat, save_gpt_chat, get_current_position, \
    get_relative_coordinates, get_room_size
from src.frontend.RelativeMapMaxMin import RelativeMapMaxMin


from src.backend.KNN_Predict import predict_knn
from src.database.LoadFromRedis import load_from_redis_all_names_and_data, load_into_X_y, load_from_redis_all_bssid

DEBUG_MODE = False

is_recording = True


class ChatWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.chat_display = ScrolledText(self, height=32, width=75, state='disabled', font=("Arial", 12))
        self.chat_display.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def display_message(self, message, side, color, sender):
        self.chat_display.config(state='normal')
        separator = "—" * 40 if sender == "yours" else ""
        self.chat_display.insert(tk.END, separator + '\n', "separator")
        if side == "right":
            self.chat_display.tag_configure("right", justify='right', foreground=color, lmargin1=200, lmargin2=200,
                                            rmargin=10)
            self.chat_display.insert(tk.END, message + '\n', "right")
        else:
            self.chat_display.tag_configure("left", justify='left', foreground=color, lmargin1=10, lmargin2=10,
                                            rmargin=200)
            self.chat_display.insert(tk.END, message + '\n', "left")
        self.chat_display.yview(tk.END)
        self.chat_display.config(state='disabled')

class MessageInput(tk.Frame):
    def __init__(self, send_message, generate_graph, load_message):
        super().__init__()

        self.send_message = send_message
        self.generate_graph = generate_graph
        self.load_message = load_message


        self.msg_input = tk.Text(self, height=3, width=44, font=("Arial", 12))
        self.msg_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.send_button = tk.Button(self, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.save_button = tk.Button(self, text="Save", command=self.save_chat)
        self.save_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.load_button = tk.Button(self, text="Load", command=self.load_chat)
        self.load_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.generate_button = tk.Button(self, text="Generate", command=self.generate_graph)
        self.generate_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # bind enter to send message
        self.msg_input.bind("<Return>", self.send_message)
        # # bind shift+enter to new line
        self.msg_input.bind("<Shift-Return>", self.__new_line)

    def save_chat(self):
        save_gpt_chat()
    def load_chat(self):
        display_messages = load_gpt_chat()

        self.load_message(display_messages)

    def __new_line(self, event):
        # Used to add a new line when shift+enter is pressed
        self.msg_input.insert(tk.INSERT, "\n")
        return "break"


class LeftFrame(tk.Frame):
    def __init__(self, updatePosition, updatePredictedPosition, generate_graph):
        super().__init__()
        self.num_messages = 0

        self.updatePosition = updatePosition
        self.updatePredictedPosition = updatePredictedPosition
        self.generate_graph = generate_graph


        self.chat_window = ChatWindow(self)
        self.chat_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.message_input = MessageInput(send_message=self.send_message, generate_graph=self.generate_graph, load_message=self.load_message)
        self.message_input.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Start the conversation
        if (DEBUG_MODE):
            start_message = "This is a start message"
            self.chat_window.display_message(start_message, "left", "blue", "yours")
            return

        start_message = start_conversation()
        # Display the start message
        self.chat_window.display_message(start_message, "left", "blue", "yours")

    def send_message(self, event):
        chat_window = self.chat_window
        message_input = self.message_input

        message = message_input.msg_input.get("1.0", tk.END).strip()  # Get message from Text widget
        if message:
            chat_window.display_message(message, "right", "green", "mine")
            message_input.msg_input.delete("1.0", tk.END)

            # The program should respond
            self.respond_message(message)

        self.num_messages += 1
        return "break"

    def respond_message(self, message=None):
        # This function should be called after send_message
        # In real event, it should call gpt to get response,
        # In debug mode, it should it should return a random response
        chat_window = self.chat_window

        if self.num_messages > 1:
            dialog_position = self.updatePosition()
            predict_position = self.updatePredictedPosition()

            if dialog_position != predict_position:
                message += "\n" + "Different predicted position"
            print(message)

        if (DEBUG_MODE):
            response = "This is a response to your message"
            chat_window.display_message(response, "left", "blue", "yours")
            return
        else:
            response = send_to_gpt(message)
            chat_window.display_message(response, "left", "blue", "yours")



    def load_message(self, messages):
        self.chat_window.chat_display.config(state='normal')
        self.chat_window.chat_display.delete(1.0, tk.END)
        for msg in messages:
            self.chat_window.display_message(msg["content"], "left" if msg["role"] == "system" else "right",
                                             "blue" if msg["role"] == "system" else "green",
                                             "yours" if msg["role"] == "system" else "mine")
        self.chat_window.chat_display.config(state='disabled')

class RightFrame(tk.Frame):
    def __init__(self):
        super().__init__()

        # Create two text displayer that can be updated
        self.space_displayer = tk.Text(self, height=20, width=20, font=("Arial", 12))
        self.space_displayer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # A displayer to show current predicted position
        self.current_position_displayer = tk.Text(self, height=1, width=20, font=("Arial", 12))
        self.current_position_displayer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.image_drawer = RelativeMapMaxMin()
        self.image_drawer.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)


class SimpleChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Chat with Enter to Send")

        # Create a Frame for the left side
        self.left_frame = LeftFrame(updatePosition=self.updateCurrentPosition, updatePredictedPosition = self.updatePredictedPosition, generate_graph=self.generate_graph)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = RightFrame()
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.position = None

        recording_thread = Thread(target=self.record_continuously)
        recording_thread.start()

    def updateCurrentPosition(self):
        # Get the current position from gpt
        position = get_current_position()
        # Add the current position to the right frame
        # Add to a new line
        self.right_frame.space_displayer.insert(tk.END, position + '\n')

        self.position = position

        return position

    def updatePredictedPosition(self):
        bssids = load_from_redis_all_bssid()
        row = get_network_info(bssids)
        X, y = load_into_X_y(bssids)
        position = predict_knn(X, y, row)

        # Update the predicted position to the right frame
        self.right_frame.current_position_displayer.delete(1.0, tk.END)
        self.right_frame.current_position_displayer.insert(tk.END, position)

        return position

    def generate_graph(self):
        relative_coordinates = get_relative_coordinates()
        room_sizes = get_room_size()
        print(relative_coordinates)
        print(room_sizes)
        # relative_coordinates = [('Kitchen', 'LivingRoom', 'left'), ('LivingRoom', 'Kitchen', 'right'), ('LivingRoom', 'Bedroom', 'top'), ('Bedroom', 'LivingRoom', 'bottom')]
        # self.right_frame.image_drawer.update_plot([('C', 'D', 'left'), ('C', 'E', 'right')])
        self.right_frame.image_drawer.update_plot(relative_coordinates, room_sizes)


    def record_continuously(self):
        while is_recording:
            if self.position:
                store_network_info(self.position)


if __name__ == "__main__":
    data_loading_thread = threading.Thread(target=load_from_redis_all_names_and_data)
    data_loading_thread.start()

    root = tk.Tk()
    app = SimpleChatGUI(root)
    root.mainloop()
