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
system_msg = "You are a Cartographer bot.\
You will introduce yourself as a Cartographer whose role is to ask the user some questions about their visit.\
Your role is to ask the user the following questions in a professional manner, one question at a time.\
You should skip questions when the user has already provided an answer to a previous question you asked. \
You should follow up on questions whenever the response given by the user is vague.\
You should collect information about a building to develop a spatial understanding of the layout.\
The user might tell you about multiple connected spaces. You should ask about the next spatial area, one space at a time.\
You should continue this process until the user feels like they described all that they want to tell you.\
You should not ask the user to choose the next area, you should choose by yourself.\
You must use a list to display and store explored areas.\
Here are the questions to ask:\
1. What room do you want to start with?\
3. What are other spaces near to [XXX]?\
4. Where [XXX] is located in relative to [XXX]?\
5. What is the short description of area [XXX]?\
[XXX] only represent spaces\
Do not ask 2 or more questions each time.\
Your current description explored area list is [].\
Your current near space known area list is [].\
Your current unexplored area list is [].\
An area is unexplored if its description and areas near it not found. \
You must display this list in each time you talk and update it if possible.\
"


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
