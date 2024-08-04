import json
import os
import re
from difflib import SequenceMatcher
import hashlib
from collections import Counter
from generator.generator import Generator

SAVE_PATH = "./saved_stories/"
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def story_hash(string: str):
    return hashlib.md5(bytes(string.lstrip()[:1000], 'utf-8')).hexdigest()


class Story:
    def __init__(self, gen: Generator, censor: bool, gen_length=100):
        self.gen_length=gen_length
        self.stream = True
        self.censor = censor
        self.gen = gen
        self.events = []
        self.title = ''
        self.save_path = SAVE_PATH

        with open("./story/censored_words.txt", "r") as f:
            self.censored_words = [l.strip(" \n\r,.") for l in f.readlines()]

    def load(self, save_name: str):
        self.title = save_name
        file_name = str(save_name) + ".json"
        exists = os.path.isfile(os.path.join(self.save_path, file_name))
        if exists:
            with open(os.path.join(self.save_path, file_name), "r") as fp:
                self.events = json.load(fp)
            return str(self)
        else:
            return "Error save not found."

    def save(self, save_name: str, name_is_title=True):
        if name_is_title:
            self.title = save_name
        file_name = str(save_name) + ".json"
        with open(os.path.join(self.save_path, file_name), "w") as fp:
            json.dump(self.events, fp)

    def new(self, context: str = ''):
        self.title = ''
        self.events = [context]
        return str(self)

    def get_max_history(self):
        return min(self.gen.model.config.max_position_embeddings - self.gen_length, 6000)

    def clean_input(self, action=''):
        # find the biggest memory that fits max_tokens
        mem_ind = 1
        while len(
                self.gen.enc.encode(self.events[0] + ''.join(filter(None, self.events[-mem_ind:]))
                                    + action)) < self.get_max_history() and len(self.events) - 1 >= mem_ind:
            mem_ind += 1
        mem_ind -= 1

        events_clipped = self.events[0]
        while mem_ind > 0:
            if len(self.events) - 1 >= mem_ind and self.events[-mem_ind]:
                events_clipped += self.events[-mem_ind]
            mem_ind -= 1

        text = events_clipped + action
        return text

    def clean_result(self, result):
        result = re.sub(rf'{self.gen.enc.eos_token}[\s\S]*$', '', result)  # parse endoftext token that end the text
        result = re.sub(rf'^({self.gen.enc.eos_token})+', '', result) # remove leading endoftext tokens

        result = result.replace("’", "'")
        result = result.replace("`", "'")
        result = result.replace("“", '"')
        result = result.replace("”", '"')
        result = result.replace("\n\n", '\n')

        # remove repeating substrings of 2+ characters at the end of result
        result = re.sub(r'([\s\S]{2,})([\s\S]?\1)+$', r'\1', result)

        # remove sentences that are cut in the middle
        end_of_sentence_index = next(iter([i for i, j in list(enumerate(result, 1))[::-1] if j in '".:?!']),
                                     len(result))
        result = result[:end_of_sentence_index]

        # remove trailing start of quote
        result = re.sub(r'\s"$', '', result)

        if self.censor:
            result = re.sub(r'|'.join(rf'(\b{re.escape(s)}\b)' for s in self.censored_words), '[CENSORED]', result,
                            flags=re.IGNORECASE)

        return result.rstrip('\n')

    def act(self, action: str = '', tries: int = 10, eos_tokens=[]):
        max_tries = tries
        input_str = self.clean_input(action)
        self.events.append(action)
        try:
            result = self.gen.generate(input_str, stream=self.stream, eos_tokens=eos_tokens, length=self.gen_length)
            result = self.clean_result(result)

            while (len(result) < 2
                   or SequenceMatcher(None, self.events[-1], result).ratio() > 0.9 - 0.5 * (tries / max_tries)
                   or '[CENSORED]' in result):
                # reject censored output, empty outputs and repeating outputs (tolerance to repeats increases from 0.4 to
                # 0.9 progressively with each try)
                if tries == 0:
                    return None
                tries -= 1
                result = self.gen.generate(input_str, stream=self.stream, eos_tokens=eos_tokens, length=self.gen_length)
                # print(result)
                result = self.clean_result(result)
        except KeyboardInterrupt:
            raise
        self.events.append(result)
        return result

    def gen_n_results(self, n: int = 3, tries: int = 30):
        res = []
        max_tries = tries
        input_str = self.clean_input()

        while len(res) < n and tries > 0:
            result = self.gen.generate(input_str, stream=False, length=self.gen_length, eos_tokens=['.', '!', '?', '\n'])
            result = self.clean_result(result)

            if not (len(result) < 2
                    or SequenceMatcher(None, self.events[-1], result).ratio() > 0.9 - 0.5 * (tries / max_tries)
                    or '[CENSORED]' in result
                    or result in res):
                res.append(result)

            tries -= 1

        return res

    def wordcloud(self, top_n=10, include_count=True):
        ignorelist = ['you', 'are','she',  'has', 'have', 'don', 'does', 'her', 'can', 'for', 'out', 'not', 'all',
                      'get', 'his','your', 'this', 'that', 'but', 'then', 'with', 'the', 'and', 'they', 'them', 'into',
                      'from', 'was', 'had', 'would', 'could', 'him', 'when', 'where', 'going', 'couldn', 'wouldn',
                      'its', 'their', 'were']
        words = [w for w
                 in re.sub(r'\W+',' ',  str(self).lower()).split()
                 if w not in ignorelist and len(w) > 2]
        wordcloud = Counter(words).most_common(top_n)
        if include_count:
            return ', '.join([f'{w} ({n})'for w, n in wordcloud])
        else:
            return ', '.join([w for w, _ in wordcloud])

    def __str__(self):
        text = ''.join(filter(None, self.events)).lstrip()
        return text
