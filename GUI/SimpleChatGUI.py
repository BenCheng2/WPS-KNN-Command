import tkinter as tk
from tkinter.scrolledtext import ScrolledText

from GPT import start_conversation, send_to_gpt


class SimpleChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Chat with Enter to Send")

        # Create the chat display area
        self.chat_display = ScrolledText(root, height=32, width=75, state='disabled', font=("Arial", 12))
        self.chat_display.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Create the message input area with height for multiple lines
        self.msg_input = tk.Text(root, height=3, width=44, font=("Arial", 12))
        self.msg_input.grid(row=1, column=0, padx=10, pady=10)
        self.msg_input.bind("<Return>", self.send_message)  # Bind Enter to send message
        self.msg_input.bind("<Control-Return>", self.new_line)  # Bind Ctrl+Enter to insert newline
        self.msg_input.focus_set()

        # Create the send button
        self.send_button = tk.Button(root, text="Send", command=lambda: self.send_message(None))
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        start_message = start_conversation()
        self.respond_message(start_message)

    def send_message(self, event):
        message = self.msg_input.get("1.0", tk.END).strip()  # Get message from Text widget
        if message:
            self.display_message(message, "right", "green", "mine")
            self.msg_input.delete("1.0", tk.END)  # Clear the input area

            # Once the message is sent, get the reply from the GPT model
            reply = send_to_gpt(message)
            self.respond_message(reply)

        return "break"

    def respond_message(self, message):
        self.root.after(500, lambda: self.display_message(message, "left", "blue", "yours"))

    def new_line(self, event):
        self.msg_input.insert(tk.INSERT, "\n")
        return "break"

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


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChatGUI(root)
    root.mainloop()
