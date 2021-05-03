import json
import os
import re
from difflib import SequenceMatcher

from generator.generator import Generator

SAVE_PATH = "./saved_stories/"


class Story:
    def __init__(self, gen: Generator):
        self.gen = gen
        self.events = []

        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)

    def load(self, save_name: str):
        file_name = str(save_name) + ".json"
        exists = os.path.isfile(os.path.join(SAVE_PATH, file_name))
        if exists:
            with open(os.path.join(SAVE_PATH, file_name), "r") as fp:
                self.events = json.load(fp)
                return str(self)
        else:
            return "Error save not found."

    def cont(self):
        for path, subdirs, files in os.walk('./saved_stories'):
            for name in reversed(sorted(files, key=lambda name: os.path.getmtime(os.path.join(path, name)))):
                if name.endswith('.json'):
                    return self.load(os.path.join(path, name))

    def save(self, save_name: str):
        file_name = str(save_name) + ".json"
        with open(os.path.join(SAVE_PATH, file_name), "w") as fp:
            json.dump(self.events, fp)

    def new(self, context: str = '', prompt: str = ''):
        self.events = [context]
        self.act(prompt)
        return str(self)

    def clean_result(self, result):
        result = result.strip()

        # remove sentences that are cut in the middle
        end_of_sentence_index = next(iter([i for i, j in list(enumerate(result, 1))[::-1] if j in '.:?!']),
                                     len(result))
        result = result[:end_of_sentence_index].strip()

        # remove repeating substrings of 2+ characters at the end of result
        result = re.sub(r'([\s\S]{2,})(\1)+$', r'\1', result)

        # close open quotes
        if result.count('"') % 2 != 0:
            result += '"'

        return result

    def act(self, action: str = '', tries: int = 10):
        input_str = self.get_clipped_events(action)
        result = self.gen.generate(input_str)
        result = self.clean_result(result)

        while (len(result) < 2 or SequenceMatcher(None, self.events[-1], result).ratio() > 0.9) and tries >= 0:
            tries -= 1
            if tries == 0:
                return None
            result = self.gen.generate(input_str)
            result = self.clean_result(result)

        self.events.append(action)
        self.events.append(result)
        return result

    def gen_n_results(self, n: int = 3):
        res = []
        for i in range(0, n):
            result = self.gen.generate(str(self))
            res.append(self.clean_result(result))
        return res

    def get_clipped_events(self, action=''):

        # find the biggest memory that fits 1024 tokens
        mem_ind = 1
        while len(
                self.gen.enc.encode(action + '\n' + self.events[0] + '\n'.join(self.events[-mem_ind:])
                                    )) < 1024 - self.gen.length and len(self.events) - 1 >= mem_ind:
            mem_ind += 1
        mem_ind -= 1

        events_clipped = self.events[0]
        while mem_ind > 0:
            if len(self.events) - 1 >= mem_ind:
                events_clipped += '\n' + self.events[-mem_ind]
            mem_ind -= 1

        text = events_clipped + '\n' + action
        # parse special character "-" as a newline cancellation
        text = re.sub(r'(\n-)|(-\n)', ' ', text)
        return text

    def __str__(self):
        text = "\n".join(self.events)
        # parse special character "-" as a newline cancellation
        text = re.sub(r'(\n-)|(-\n)', ' ', text)
        return text
