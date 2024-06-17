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
    def __init__(self, api_key=None, model_version=None):
        self.client = OpenAI(api_key=api_key)
        self.model_version = model_version

        self._messages = []

        self._load_message_system_start_message()

    def _load_message_system_start_message(self):
        with open('../../start_prompt.txt', 'r') as f:
            self._messages.append({"role": "system", "content": f.read()})
        self._messages.append({"role": "user", "content": "Start conversation"})

    def send_message_to_gpt_with_save(self, message):
        self._messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model_version,
            messages=self._messages
        )
        reply = response.choices[0].message.content
        self._messages.append({"role": "system", "content": reply})
        return reply

    def save_message_to_gpt_without_save(self, message):
        self._messages.append({"role": "user", "content": message})
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






        

