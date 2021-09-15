#!/usr/bin/env python3
import json
import os

import story.story

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from PyInquirer import style_from_dict, Token, prompt

from story import grammars
from story.story import Story
from story.story import SAVE_PATH
from generator.generator import Generator
import argparse
import re


class Game:
    def __init__(self):
        self.gen = Generator(model_name=args.model[0], gpu=not args.cpugpt)
        self.tts = None if args.jupyter else Dub(gpu=not args.cputts)
        self.style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })
        self.story = Story(self.gen, censor=args.censor)
        self.voice = 1.05
        self.loop = self.loop_text
        self.voice_on_next_loop = False
        self.sample_hashes = []

    def play(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            print("""
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
███████████████████████████░███░█░▄▄▀█░▄▄▀█▄░▄█▄░▄█░▄▄█░▄▄▀███████████████████████████
███████████████████████████▄▀░▀▄█░▀▀▄█░▀▀░██░███░██░▄▄█░▀▀▄███████████████████████████
████████████████████████████▄█▄██▄█▄▄█░██░█▀░▀██▄██▄▄▄█▄█▄▄███████████████████████████
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀""")

            choices = []
            if len([f for f in os.listdir(SAVE_PATH) if f.endswith('.json')]) > 0 or len(self.story.events) > 0:
                choices.append('continue')
            if len([f for f in os.listdir(SAVE_PATH) if f.endswith('.json')]) > 0:
                choices.append('load')

            choices.append('new')
            if not args.jupyter:
                choices.append('voice')

            choices += ['model'] + ['switch to choice mode' if self.loop == self.loop_text else 'switch to text mode']
            if len(self.story.events) > 1:
                choices.insert(1, 'save')

            main_menu = [{
                'type': list_input_type,
                'message': 'Choose an option',
                'name': 'action',
                'choices': choices
            }]

            action = prompt(main_menu, style=self.style)['action']

            if action == 'new':
                self.new_prompt()
            elif action == 'continue':
                if len(self.story.events) == 0:
                    self.story.cont()
            elif action == 'save':
                self.save_prompt()
            elif action == 'load':
                self.load_prompt()
            elif action == 'model':
                self.model_prompt()
            elif action == 'voice':
                self.voice_prompt()
            elif action == 'switch to choice mode':
                self.loop = self.loop_choice
            elif action == 'switch to text mode':
                self.loop = self.loop_text
            else:
                print('invalid input')

            if len(self.story.events) != 0:
                self.loop()

    def new_prompt(self):

        menu = [{
            'type': list_input_type,
            'message': 'Choose a starting prompt',
            'name': 'action',
            'choices': ['< Back', 'custom'] + [
                f[:-11] for f in os.listdir('./story/grammars') if f.endswith('_rules''.json')
            ] + ['ai-generated']
        }]

        action = prompt(menu, style=self.style)['action']
        if action == '< Back':
            return
        elif action == 'custom':
            questions = [{
                'type': 'input',
                'message': "Type a short context. The AI won't forget it, so preferably describe aspects of the setting"
                           "\nthat you expect to remain true as the story develops. Who are your characters? What "
                           "world do they live in?\n",
                'name': 'context'
            }, {
                'type': 'input',
                'message': 'Type a short prompt. This is the start of your story.\n',
                'name': 'prompt'
            }]
            custom_input = prompt(questions, style=self.style)
            context = custom_input['context'].strip()
            custom_prompt = custom_input['prompt'].strip()
        elif action == 'ai-generated':
            custom_prompt = ''
            context = ''
        else:
            context = grammars.generate(action, "context").strip()
            custom_prompt = grammars.generate(action, "prompt").strip()

        if context and custom_prompt:
            custom_prompt = ' ' + custom_prompt

        print("Generating story ...")
        print("Type /help or /h to get a list of commands.")
        self.story.new(context, custom_prompt)
        self.voice_on_next_loop = True

    def load_prompt(self):
        menu = [{
            'type': list_input_type,
            'message': 'Choose a file to load',
            'name': 'action',
            'choices': ['< Back'] + sorted([f[:-5] for f in os.listdir(SAVE_PATH) if f.endswith('.json')],
                                           key=lambda name: os.path.getmtime(os.path.join(SAVE_PATH, name + '.json')))
        }]

        action = prompt(menu, style=self.style)['action']

        if action != '< Back':
            self.story.load(action)

    def save_prompt(self):
        questions = [{
            'type': 'input',
            'message': "Type a name for your save file.",
            'name': 'user_input'
        }]
        user_input = prompt(questions, style=self.style)['user_input']
        try:
            self.story.save(user_input)
            print(f'Successfully saved {user_input}')
        except:
            print(f'Failed to save the game as {user_input}')

    def loop_text(self):
        self.pprint()
        if self.voice_on_next_loop and not args.jupyter:
            self.tts.deep_play(str(self.story), self.voice)
            self.voice_on_next_loop = False

        while True:
            self.pprint()
            user_input = input('> ').strip()

            if user_input in ['/menu', '/m']:
                return
            elif user_input in ['/revert', '/r']:
                self.tts.stop()
                if len(self.story.events) <= 2:
                    result = self.story.new(self.story.events[0], self.story.events[1])
                    self.pprint()
                    if not args.jupyter:
                        self.tts.deep_play('\n'.join(filter(None, self.story.events[2:])), self.voice)
                elif len(self.story.events) == 3:
                    self.story.events = self.story.events[:-1]
                else:
                    self.story.events = self.story.events[:-2]
            elif user_input in ['/n', '/next']:
                if not self.sample_hashes:
                    self.sample_hashes = [f[:-5] for f in os.listdir('samples') if f.endswith('.json')]

                intro_hash = story.story.story_hash(str(self.story))

                if intro_hash in self.sample_hashes:
                    with open(f'samples/{intro_hash}.json', "r") as fp:
                        text = json.load(fp)
                    index = text.find(str(self.story))
                    if index > -1:
                        index += len(str(self.story))
                        sep = '\n'
                        min_len = 300
                        action = text[index:]
                        action = action[:min_len] + sep.join(action[min_len:].split(sep)[:1])
                        self.story.events.append(action)
                        self.pprint()
                        if not args.jupyter:
                            self.tts.deep_play(action, self.voice)
                    else:
                        print("The start of the story matches the dataset, but not the rest.")
                        input('Press enter to continue.')
                else:
                    print("Couldn't find a story with an identical hash (filename) for the first 1000 characters.")
                    input('Press enter to continue.')

            elif user_input.startswith('/'):
                print('Known commands:\n'
                      '/h   /help     display this help\n'
                      '/m   /menu     go to main menu (it has a save option)\n'
                      '/r   /revert   revert last action and response (if there are none, regenerate an intro)\n'
                      '/n   /next     check ./samples for an identical story and keep reading from the dataset ('
                      'undocumented)\n '
                      'Tips:          Press Enter without typing anything to let the AI continue for you.'
                      '               Use "~" or "§" in your inputs to insert a line break.')
                input('Press enter to continue.')
            else:
                action = user_input.strip()
                if len(action) > 0:
                    action = ' ' + action
                action = re.sub(r' *[§|~] *', '\n', action)

                self.pprint(action)

                result = self.story.act(action)
                self.pprint()
                if result is None:
                    print("--- The model failed to produce an decent output after multiple tries. Try something else.")
                else:
                    if not args.jupyter:
                        self.tts.deep_play(action + result, self.voice)

    def loop_choice(self):
        self.pprint()
        if self.voice_on_next_loop and not args.jupyter:
            self.tts.deep_play(str(self.story), self.voice)
            self.voice_on_next_loop = False

        while True:
            self.pprint()
            results = self.story.gen_n_results(3)
            results = {r.strip('\n').split('\n')[0]: r for r in results}
            choices = ['< more >'] + list(results.keys()) + ['< revert >', '< menu >']
            question = [
                {
                    'type': list_input_type,
                    'name': 'model_name',
                    'message': f'choice:',
                    'choices': choices
                }
            ]

            user_input = prompt(question, style=self.style)['model_name']

            if user_input == '< menu >':
                return
            elif user_input == '< revert >':
                if len(self.story.events) < 4:
                    result = self.story.new(self.story.events[0], self.story.events[1])
                    # print(result)
                    self.pprint()
                    if not args.jupyter:
                        self.tts.deep_play('\n'.join(filter(None, self.story.events[2:])), self.voice)
                else:
                    self.story.events = self.story.events[:-1]
                    # print("Last action reverted.")
                    # print(self.story.events[-1])
                    self.pprint()
            elif user_input == '< more >':
                # print('\x1b[1A\x1b[2K\x1b[1A')
                continue
            else:
                #user_input = results[user_input].strip()
                #self.story.events.append('\n' + user_input)
                user_input = results[user_input].strip()
                self.story.events.append(' ' + user_input)
                # print('\x1b[1A\x1b[2K' + user_input)
                # print(user_input)
                self.pprint()
                if not args.jupyter:
                    self.tts.deep_play(user_input, self.voice)

    def pprint(self, highlight=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        if args.jupyter:
            print('\n' * 25)  # dirty output clear for jupyter

        if highlight is None:
            highlight = self.story.events[-1]
            body = ''.join(filter(None, self.story.events[:-1])).lstrip()
        else:
            body = str(self.story)

        print(body + f'\033[96m{highlight}\033[00m')

    def model_prompt(self):
        models_dir = './models'
        models_list = [f for f in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, f))]

        question = [
            {
                'type': list_input_type,
                'name': 'model_name',
                'message': f'Chose a model for the AI (located in {models_dir}, current is {self.gen.model_name}). '
                           f'\nThe new model won\'t be able to use the GPU while still allocating VRAM.\nChange default'
                           f' model_name in generator/generator.py instead.',
                'choices': ['< Back'] + models_list,
                'default': self.gen.model_name
            }
        ]

        model_name = prompt(question, style=self.style)['model_name']

        if model_name == '< Back':
            return

        print('Loading model ...')
        # dirty fix: disable GPU unless I find a way to free its memory, otherwise it just crashes
        self.gen = Generator(model_name, models_dir)
        self.story.gen = self.gen

    def voice_prompt(self):
        question = [
            {
                'type': 'input',
                'name': 'voice',
                'message': f'Chose a voice speed multiplier (0 to mute sound, 1 for normal speed):',
                'default': str(self.voice),
                'validate': lambda val: val.replace('.', '', 1).isdigit()
            }
        ]

        self.voice = float(prompt(question, style=self.style)['voice'])


if __name__ == "__main__":
    # declare command line arguments
    parser = argparse.ArgumentParser(description='wrAIter: AI writing assistant with a voice')
    parser.add_argument('-j', '--jupyter', action='store_true',
                        default=False,
                        help='jupyter compatibility mode (replaces arrow key selection, disables audio)')
    parser.add_argument('-c', '--censor', action='store_true',
                        default=False,
                        help='adds a censor to the generator')
    parser.add_argument('-m', '--model', action='store',
                        default=['gpt-neo-2.7B'], nargs=1, type=str,
                        help='model name')
    parser.add_argument('-t', '--cputts', action='store_true',
                        default=False,
                        help='force TTS to run on CPU')
    parser.add_argument('-g', '--cpugpt', action='store_true',
                        default=False,
                        help='(broken) force text generation to run on CPU')

    args = parser.parse_args()

    list_input_type = 'rawlist' if args.jupyter else 'list'

    if not args.jupyter:
        from audio.tts import Dub

    if not os.path.exists('./saved_stories'):
        os.mkdir('./saved_stories')

    g = Game()
    g.play()
