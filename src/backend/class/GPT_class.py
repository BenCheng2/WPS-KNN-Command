import json
from tkinter import filedialog

from openai import OpenAI


class GPT_class:
    def __init__(self, api_key=None, model_version=None, system_msg=None):
        self.client = OpenAI(api_key=api_key)
        self.model_version = model_version

        self.local_messages = []
        self.system_msg = system_msg

    def start_conversation(self):
        self.local_messages.append({"role": "system", "content": self.system_msg})
        self.local_messages.append({"role": "user", "content": "Start conversation"})

        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=self.local_messages
        )
        reply = response.choices[0].message.content

        self.local_messages.append({"role": "system", "content": reply})
        return reply

    def send_to_gpt(self, message):
        self.local_messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=self.local_messages
        )
        reply = response.choices[0].message.content

        self.local_messages.append({"role": "system", "content": reply})
        return reply

    def save_gpt_chat(filename=None):
        if not filename:
            # If no filename is provided, prompt the user to choose one
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not filename:  # User canceled the dialog
                return

        # Store in JSON format
        with open(filename, "w") as f:
            json.dump(local_messages, f, indent=4)

    def load_gpt_chat(filename=None):
        global local_messages

        if not filename:
            # If no filename is provided, prompt the user to choose one
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not filename:  # User canceled the dialog
                return None

        with open(filename, "r") as f:
            local_messages = json.load(f)
        return local_messages

    def get_current_position(self):
        local_messages.append({"role": "user", "content": "Current position?"})
        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=local_messages
        )
        position = response.choices[0].message.content
        local_messages.pop()
        return position

    def get_relative_coordinates(self):
        local_messages.append({"role": "user", "content": "Give all relative coordinates"})
        print(local_messages)
        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=local_messages
        )
        coordinates = response.choices[0].message.content
        local_messages.pop()
        return eval(coordinates)

    def get_room_size(self):
        local_messages.append({"role": "user", "content": "Give all room sizes"})
        print(local_messages)
        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=local_messages
        )
        size = response.choices[0].message.content
        local_messages.pop()
        return eval(size)


