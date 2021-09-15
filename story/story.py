import json
import os
import re
from difflib import SequenceMatcher
import hashlib

from generator.generator import Generator

SAVE_PATH = "./saved_stories/"


def story_hash(string: str):
    return hashlib.md5(bytes(string.lstrip()[:1000], 'utf-8')).hexdigest()


class Story:
    def __init__(self, gen: Generator, censor: bool):
        self.censor = censor
        self.gen = gen
        self.events = []

        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)

        with open("./story/censored_words.txt", "r") as f:
            self.censored_words = [l.strip(" \n\r,.") for l in f.readlines()]

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
        for path, subdirs, files in os.walk(SAVE_PATH):
            for name in reversed(sorted(files, key=lambda name: os.path.getmtime(os.path.join(path, name)))):
                if name.endswith('.json'):
                    return self.load(name[:-5])

    def save(self, save_name: str):
        file_name = str(save_name) + ".json"
        with open(os.path.join(SAVE_PATH, file_name), "w") as fp:
            json.dump(self.events, fp)

    def new(self, context: str = '', prompt: str = ''):
        self.events = [context]
        self.act(prompt)
        return str(self)

    def clean_input(self, action=''):
        max_tokens = self.gen.generator.max_history_tokens - 7  # the 7 is for the <|endoftext|> token (it's badly encoded)

        # find the biggest memory that fits 1024 tokens
        mem_ind = 1
        while len(
                self.gen.enc.encode(self.events[0] + ''.join(filter(None, self.events[-mem_ind:]))
                                    + action)) < max_tokens and len(self.events) - 1 >= mem_ind:
            mem_ind += 1
        mem_ind -= 1

        events_clipped = self.events[0]
        while mem_ind > 0:
            if len(self.events) - 1 >= mem_ind and self.events[-mem_ind]:
                events_clipped += self.events[-mem_ind]
            mem_ind -= 1

        text = events_clipped + action
        return text.strip()

    def clean_result(self, result):
        result = re.sub(r'<\|endoftext\|>[\s\S]*$', '', result)  # parse endoftext token (it happens)

        # remove sentences that are cut in the middle
        end_of_sentence_index = next(iter([i for i, j in list(enumerate(result, 1))[::-1] if j in '.:?!']),
                                     len(result))
        result = result[:end_of_sentence_index]

        # remove repeating substrings of 2+ characters at the end of result
        result = re.sub(r'([\s\S]{2,})([\s\S]?\1)+$', r'\1', result)

        # close open quotes
        if result.count('"') % 2 != 0:
            result += '"'

        result = result.replace("’", "'")
        result = result.replace("`", "'")
        result = result.replace("“", '"')
        result = result.replace("”", '"')
        result = result.replace("\n\n", '\n')

        if self.censor:
            result = re.sub(r'|'.join(rf'(\b{re.escape(s)}\b)' for s in self.censored_words), '[CENSORED]', result,
                            flags=re.IGNORECASE)

        return result.rstrip('\n')

    def act(self, action: str = '', tries: int = 10):
        max_tries = tries
        input_str = self.clean_input(action)
        result = self.gen.generate(input_str)
        result = self.clean_result(result)

        while (len(result) < 2
               or SequenceMatcher(None, self.events[-1], result).ratio() > 0.9 - 0.5 * (tries / max_tries)
               or '[CENSORED]' in result):
            # reject censored output, empty outputs and repeating outputs (tolerance to repeats increases from 0.4 to
            # 0.9 progressively with each try)
            if tries == 0:
                return None
            tries -= 1
            result = self.gen.generate(input_str)
            result = self.clean_result(result)

        self.events.append(action)
        self.events.append(result)
        return result

    def gen_n_results(self, n: int = 3, tries: int = 30):
        res = []
        max_tries = tries
        input_str = self.clean_input()

        while len(res) < n and tries > 0:
            result = self.gen.generate(input_str)
            result = self.clean_result(result)

            if not (len(result) < 2
                    or SequenceMatcher(None, self.events[-1], result).ratio() > 0.9 - 0.5 * (tries / max_tries)
                    or '[CENSORED]' in result
                    or result in res):
                res.append(result)

            tries -= 1

        return res

    def __str__(self):
        text = ''.join(filter(None, self.events)).lstrip()
        return text
