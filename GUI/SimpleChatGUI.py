import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from GPT import start_conversation, send_to_gpt, load_gpt_chat, save_gpt_chat, get_current_position

DEBUG_MODE = False

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
    def __init__(self, send_message):
        super().__init__()

        self.send_message = send_message


        self.msg_input = tk.Text(self, height=3, width=44, font=("Arial", 12))
        self.msg_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.send_button = tk.Button(self, text="Send", command=lambda: self.send_message(None))
        self.send_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.save_button = tk.Button(self, text="Save", command=self.save_chat)
        self.save_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.load_button = tk.Button(self, text="Load", command=self.load_chat)
        self.load_button.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # bind enter to send message
        self.msg_input.bind("<Return>", self.send_message)
        # # bind shift+enter to new line
        self.msg_input.bind("<Shift-Return>", self.__new_line)

    def save_chat(self):
        save_gpt_chat()
    def load_chat(self):
        load_gpt_chat()

    def __new_line(self, event):
        # Used to add a new line when shift+enter is pressed
        self.msg_input.insert(tk.INSERT, "\n")
        return "break"


class LeftFrame(tk.Frame):
    def __init__(self, updatePosition):
        super().__init__()

        self.updatePosition = updatePosition

        self.chat_window = ChatWindow(self)
        self.chat_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.message_input = MessageInput(send_message=self.send_message)
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
        return "break"

    def respond_message(self, message=None):
        # This function should be called after send_message
        # In real event, it should call gpt to get response,
        # In debug mode, it should it should return a random response
        chat_window = self.chat_window

        if (DEBUG_MODE):
            response = "This is a response to your message"
            chat_window.display_message(response, "left", "blue", "yours")
            return
        else:
            response = send_to_gpt(message)
            chat_window.display_message(response, "left", "blue", "yours")

            self.updatePosition()

class RightFrame(tk.Frame):
    def __init__(self):
        super().__init__()

        # Create two text displayer that can be updated
        self.space_displayer = tk.Text(self, height=32, width=20, font=("Arial", 12))
        self.space_displayer.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class SimpleChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Chat with Enter to Send")

        # Create a Frame for the left side
        self.left_frame = LeftFrame(updatePosition=self.updateCurrentPosition)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = RightFrame()
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def updateCurrentPosition(self):
        # Get the current position from gpt
        position = get_current_position()
        # Add the current position to the right frame
        # Add to a new line
        self.right_frame.space_displayer.insert(tk.END, position + '\n')



if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatGUI(root)
    root.mainloop()
