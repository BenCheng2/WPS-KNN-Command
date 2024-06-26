import json
import os
from tkinter import filedialog

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI


def singleton(cls):
    # Decorator to enable singleton pattern

    _instance = {}

    def inner(*args, **kwargs):
        if cls in _instance:
            return _instance[cls]
        obj = cls(*args, **kwargs)
        _instance[cls] = obj

        return obj

    return inner

@singleton
class GPTClass:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode

        if self.debug_mode:
            self._messages = []

        else:
            api_key = os.environ.get('OPENAI_API_KEY')
            model_version = os.environ.get('OPENAI_MODEL_VERSION')

            self.client = OpenAI(api_key=api_key)
            self.model_version = model_version

            self._messages = []


            self._load_message_system_start_message()
            self.send_message_to_gpt_with_save("Start conversation")

    def get_messages_all(self):
        return self._messages

    def get_messages_by_index(self, index):
        return self._messages[index]["content"]

    def _load_message_system_start_message(self):
        with open('../../start_prompt', 'r') as f:
            self._messages.append({"role": "system", "content": f.read()})

    def send_message_to_gpt_with_save(self, message):
        self._messages.append({"role": "user", "content": message})
        if self.debug_mode:
            reply = "This is a response to your message"
            self._messages.append({"role": "system", "content": reply})
        else:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=self._messages
            )
            reply = response.choices[0].message.content
            self._messages.append({"role": "system", "content": reply})
        return reply

    def save_message_to_gpt_without_save(self, message):
        self._messages.append({"role": "user", "content": message})
        if self.debug_mode:
            reply = "This is a response to your message"
            self._messages.append({"role": "system", "content": reply})
        else:
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=self._messages
            )
            reply = response.choices[0].message.content
        return reply

    def get_current_position(self):
        reply = self.save_message_to_gpt_without_save("Current position?")

    def get_relative_position(self):
        reply = self.save_message_to_gpt_without_save("Give all relative coordinates")

    def get_room_size(self):
        reply = self.save_message_to_gpt_without_save("Give all room sizes")

    def save_message_to_json_file(self, filename=None):
        if not filename:
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not filename:
                return

        with open(filename, "w") as f:
            json.dump(self._messages, f, indent=4)

    def load_message_from_json_file(self, filename=None):
        if not filename:
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not filename:
                return None

        with open(filename, "r") as f:
            self._messages = json.load(f)
        return self._messages





        

