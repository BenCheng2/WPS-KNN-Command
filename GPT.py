import json
from tkinter import filedialog

from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

# Load the variables from the .env file
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)
model_version = os.getenv('OPENAI_MODEL_VERSION')

# Variables to store the conversation
local_messages = []

# Start message
# Read the message from the file 'start_prompt.txt', store into variable 'system_msg'
with open('../start_prompt', 'r') as f:
    system_msg = f.read()
def start_conversation():
    # The initial message to start the conversation
    local_messages.append({"role": "system", "content": system_msg})
    local_messages.append({"role": "user", "content": "Start conversation"})
    # Send the messages to the model
    response = client.chat.completions.create(
        model=model_version,
        messages=local_messages
    )
    # Get the reply from the model
    # As the model provides multiple choices, we will use the first choice
    reply = response.choices[0].message.content
    local_messages.append({"role": "system", "content": reply})
    return reply


def send_to_gpt(message):
    local_messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(
        model=model_version,
        messages=local_messages
    )
    # Get the reply from the model
    # As the model provides multiple choices, we will use the first choice
    reply = response.choices[0].message.content
    local_messages.append({"role": "system", "content": reply})
    return reply

def get_current_position():
    local_messages.append({"role": "user", "content": "Give me my current position"})
    response = client.chat.completions.create(
        model=model_version,
        messages=local_messages
    )
    position = response.choices[0].message.content
    local_messages.pop()
    return position

def get_relative_coordinates():
    local_messages.append({"role": "user", "content": "Give me the relative coordinates"})
    response = client.chat.completions.create(
        model=model_version,
        messages=local_messages
    )
    coordinates = response.choices[0].message.content
    local_messages.pop()
    return eval(coordinates)

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
    if not filename:
        # If no filename is provided, prompt the user to choose one
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filename:  # User canceled the dialog
            return None

    with open(filename, "r") as f:
        local_messages = json.load(f)
    return local_messages


