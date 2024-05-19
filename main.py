#!/usr/bin/env python3
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from audio.stt import CustomMic
from InquirerPy import prompt
from story import grammars
from story.story import Story
from story.story import SAVE_PATH as SAVE_PATH
from story.conversation import Conversation
from generator.generator import Generator
import argparse
import re
import readline  # actually necessary for pyinquirer to work consistently


class Game:
    def __init__(self):
        self.gen = Generator(model_name=args.model[0], gpu=not args.cputext, precision=args.precision)
        self.tts = None if args.jupyter or args.silent else Dub(gpu=not args.cputts, lang=args.lang[0])
        self.stt = CustomMic(english=(args.lang[0]=='en'), model='medium')
        self.style = {
            "questionmark": "#e5c07b",
            "answermark": "#e5c07b",
            "answer": "#61afef",
            "input": "#98c379",
            "question": "",
            "answered_question": "",
            "instruction": "#abb2bf",
            "long_instruction": "#abb2bf",
            "pointer": "#61afef",
            "checkbox": "#98c379",
            "separator": "",
            "skipped": "#5c6370",
            "validator": "",
            "marker": "#e5c07b",
            "fuzzy_prompt": "#c678dd",
            "fuzzy_info": "#abb2bf",
            "fuzzy_border": "#4b5263",
            "fuzzy_match": "#c678dd",
            "spinner_pattern": "#e5c07b",
            "spinner_text": "",
        }
        self.story = Story(self.gen, censor=args.censor)
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
            if (len([f for f in os.listdir(SAVE_PATH) if f.endswith('.json')]) > 0
                    or len(self.story.events) > 0):
                choices.append('continue')
            if len([f for f in os.listdir(SAVE_PATH) if f.endswith('.json')]) > 0:
                choices.append('load')

            choices.append('new story')
            choices.append('new conversation')

            if self.loop != self.loop_text:
                choices += ['switch to text input']
            if self.loop != self.loop_choice and not isinstance(self.story, Conversation):
                choices += ['switch to choice mode']
            if self.loop != self.loop_voice:
                choices += ['switch to voice input']

            if len(self.story.events) > 1:
                choices.insert(1, 'save')

            main_menu = [{
                'type': list_input_type,
                'message': 'Choose an option',
                'name': 'action',
                'choices': choices
            }]

            action = {}
            while not action:
                action = prompt(main_menu, style=self.style)
            action = action['action']

            if action == 'new story':
                self.new_prompt()
            if action == 'new conversation':
                self.new_prompt(conv=True)
            elif action == 'continue':
                if len(self.story.events) == 0:
                    for path, subdirs, files in os.walk(SAVE_PATH):
                        for name in reversed(
                                sorted(files, key=lambda name: os.path.getmtime(os.path.join(path, name)))):
                            if name.endswith(' (conversation).json'):
                                self.story = Conversation(self.gen, censor=args.censor)
                                self.story.load(name[:-5])
                                break
                            elif name.endswith('.json'):
                                self.story = Story(self.gen, censor=args.censor)
                                self.story.load(name[:-5])
                                break
            elif action == 'save':
                self.save_prompt()
            elif action == 'load':
                self.load_prompt()
            elif action == 'switch to choice mode':
                self.loop = self.loop_choice
            elif action == 'switch to text input':
                self.loop = self.loop_text
            elif action == 'switch to voice input':
                self.loop = self.loop_voice
            else:
                print('invalid input')

            if len(self.story.events) != 0:
                self.loop()

    def new_prompt(self, conv=False):
        if not conv:
            menu = [{
                'type': list_input_type,
                'message': 'Choose a starting prompt',
                'name': 'action',
                'choices': ['< Back', 'custom'] + sorted([
                    f[:-11] for f in os.listdir('./story/grammars') if f.endswith('_rules''.json')
                ])
            }]

            action = {}
            while not action:
                action = prompt(menu, style=self.style)
            action = action['action']

            if action == '< Back':
                return
            elif action == 'custom':
                questions = [{
                    'type': 'input',
                    'message': "Type a short context that the AI won't forget, so preferably describe aspects of the setting"
                               "\nthat you expect to remain true as the story develops. Who are your characters? What "
                               "world do they live in? (Optional)\n",
                    'name': 'context'
                }]

                custom_input = {}
                while not custom_input:
                    custom_input = prompt(questions, style=self.style)

                context = custom_input['context'].strip()
            else:
                context = grammars.generate(action, "context").strip()

            print("Generating story ...")
            print("Type /help or /h to get a list of commands.")
            self.story = Story(self.gen, censor=args.censor)
            self.story.new(context)
            self.voice_on_next_loop = True
        else:
            questions = [{
                'type': 'input',
                'message': "Enter your tag. It can be 'You', 'A', 'B', 'C', 'Me', your name, ...\n>",
                'name': 'player',
                'default': 'Me'
            }, {
                'type': 'input',
                'message': "Enter the AI's tag. It can be 'Them', 'Him', 'Her', 'Bot', their name, ...\n>",
                'name': 'bot',
                'default': 'Bot'
            }, {
                'type': 'input',
                'message': "Type a short context about who you're talking to (or don't and it will be random).\n"
                           'For example: "The following conversation happens after a car crash."\n'
                           ">",
                'name': 'context'
            }]

            custom_input = {}
            while not custom_input:
                custom_input = prompt(questions, style=self.style)
            context = custom_input['context'].strip()
            player = custom_input['player'].strip()
            bot = custom_input['bot'].strip()

            print("Generating story ...")
            print("Type /help or /h to get a list of commands.")
            self.story = Conversation(self.gen, censor=args.censor)
            self.story.new(context, player=player, bot=bot)
            self.voice_on_next_loop = False

    def load_prompt(self):
        menu = [{
            'type': list_input_type,
            'message': 'Choose a file to load',
            'name': 'action',
            'choices': ['< Back'] + sorted([f[:-5] for f in os.listdir(SAVE_PATH) if f.endswith('.json')],
                                           key=lambda name: os.path.getmtime(os.path.join(SAVE_PATH, name + '.json')),
                                           reverse=True)
        }]

        action = {}
        while not action:
            action = prompt(menu, style=self.style)
        action = action['action']

        if action != '< Back':
            if action.endswith(' (conversation)'):
                self.story = Conversation(self.gen, censor=args.censor)
            else:
                self.story = Story(self.gen, censor=args.censor)
            self.story.load(action)

    def save_prompt(self):
        questions = [{
            'type': 'input',
            'message': "Type a name for your save file.",
            'name': 'user_input',
            'default': self.story.title
        }]

        user_input = {}
        while not user_input or not user_input['user_input']:
            user_input = prompt(questions, style=self.style)
        user_input = user_input['user_input']

        try:
            self.story.save(user_input)
            print(f'Successfully saved {user_input}')
        except:
            print(f'Failed to save the game as {user_input}')

    def loop_text(self):
        self.pprint()
        if self.voice_on_next_loop and not args.jupyter and not args.silent:
            self.tts.deep_play(str(self.story))
            self.voice_on_next_loop = False

        while True:
            self.pprint()
            user_input = input('\n> ').strip()

            if user_input in ['/menu', '/m']:
                return

            if user_input in ['/debug', '/d']:
                print(f"""
story title:      "{self.story.title}"
number of events: {len(self.story.events)}
number of tokens: {len(self.story.gen.enc.encode(str(self.story)))}/{self.story.gen.max_history} (trimmed to {
                len(self.story.gen.enc.encode(self.story.clean_input()))})
wordcloud:        {self.story.wordcloud()}
fanciest words:   {', '.join(sorted(set(re.sub(r'[^A-Za-z0-9_]+', ' ', str(self.story).lower()).split()),
                                    key=lambda x: len(x), reverse=True)[:5])}
""")
                input('Press enter to continue.')

            elif user_input in ['/e', '/edit']:
                if self.tts is not None:
                    self.tts.stop()

                question = {
                    'type': 'input',
                    'name': 'edit',
                    'message': '',
                    'default': self.story.events[-1]
                }
                self.story.events[-1] = prompt(question, style=self.style)['edit']

            elif user_input in ['/s', '/save']:
                self.save_prompt()

            elif user_input in ['/revert', '/r']:
                if self.tts is not None:
                    self.tts.stop()
                if len(self.story.events) <= 1:
                    pass
                elif len(self.story.events) == 2:
                    self.story.events = self.story.events[:-1]
                else:
                    self.story.events = self.story.events[:-2]

            elif user_input in ['/redo', '/R']:
                if self.tts is not None:
                    self.tts.stop()
                if len(self.story.events) <= 1:
                    pass
                else:
                    self.story.events = self.story.events[:-1]
                self.pprint()
                result = self.story.act()
                if not args.jupyter and not args.silent:
                    self.tts.deep_play(result)

            elif user_input.startswith('/'):
                print('Known commands:\n'
                      '/h   /help     display this help\n'
                      '/m   /menu     go to main menu (it has a save option)\n'
                      '/r   /revert   revert last action and response (if there are none, regenerate an intro)\n'
                      '/R   /redo     cancel and redo last response response\n'
                      '/e   /edit     edit last story event\n'
                      '/s   /save     save story\n'
                      '/d   /debug    show current story state\n'
                      'Tips:          Press Enter without typing anything to let the AI continue for you.'
                      '               Use "~" or "§" in your inputs to insert a line break.')
                input('Press enter to continue.')
            else:
                action = user_input.strip()
                if len(action) > 0:
                    action = ' ' + action

                # capitalize
                action = re.sub(r'\bi\b', 'I', action)  # capitalize lone 'I'
                action = re.sub(r'[.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)',
                                lambda matchobj: matchobj.group(0).upper(), action)  # capitalize start of sentences
                action = re.sub(r' *[§|~] *', '\n', action)

                if isinstance(self.story, Conversation):
                    if args.lang[0] == 'fr':
                        action = f'\n[{self.story.player}:] {action.strip()}\n[{self.story.bot}:] '
                    else:
                        action = f'\n{self.story.player}: "{action.strip()}"\n{self.story.bot}: "'

                self.pprint(action)

                result = self.story.act(action)
                self.pprint()
                if result is None:
                    print("--- The model failed to produce an decent output after multiple tries. Try something else.")
                else:
                    if not args.jupyter and not args.silent:
                        if isinstance(self.story, Conversation):
                            self.tts.deep_play(result)
                        else:
                            self.tts.deep_play(action + result)
    def loop_voice(self):
        self.pprint()
        if self.voice_on_next_loop and not args.jupyter and not args.silent:
            self.tts.deep_play(str(self.story))
            self.voice_on_next_loop = False

        while True:
            self.pprint()
            try:
                user_input = self.stt.custom_listen()
            except KeyboardInterrupt:
                return

            action = user_input.strip()

            if len(action) > 0:
                action = ' ' + action

            # capitalize
            action = re.sub(r'\bi\b', 'I', action)  # capitalize lone 'I'
            action = re.sub(r'^([a-z])|[\.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)',
                            lambda matchobj: matchobj.group(0).upper(), action)  # capitalize start of sentences

            if isinstance(self.story, Conversation):
                if args.lang[0] == 'fr':
                    action = f'\n[{self.story.player}:] {action.strip()}\n[{self.story.bot}:] '
                else:
                    action = f'\n{self.story.player}: "{action.strip()}"\n{self.story.bot}: "'

            self.pprint(action)

            result = self.story.act(action)
            self.pprint()
            if result is None:
                print("--- The model failed to produce an decent output after multiple tries. Try something else.")
            else:
                if not args.jupyter:
                    self.tts.deep_play(result)

    def loop_choice(self):
        self.pprint()
        if self.voice_on_next_loop and not args.jupyter and not args.silent:
            self.tts.deep_play(str(self.story))
            self.voice_on_next_loop = False

        while True:
            if isinstance(self.story, Conversation):
                self.loop = self.loop_text
                return

            self.pprint()
            results = self.story.gen_n_results(3)
            results = {r.strip('\n').split('\n')[0]: r for r in results}
            choices = ['< more >'] + list(results.keys()) + ['< revert >', '< menu >']
            print()
            question = [
                {
                    'type': list_input_type,
                    'name': 'choice',
                    'message': f'choice:',
                    'choices': choices
                }
            ]

            user_input = {}
            while not user_input:
                user_input = prompt(question, style=self.style)
            user_input = user_input['choice']

            if user_input == '< menu >':
                return
            elif user_input == '< revert >':
                if self.tts is not None:
                    self.tts.stop()
                if len(self.story.events) < 4:
                    self.story.new(self.story.events[0])
                    self.pprint()
                    if not args.jupyter and not args.silent:
                        self.tts.deep_play('\n'.join(filter(None, self.story.events[2:])))
                else:
                    self.story.events = self.story.events[:-1]
                    self.pprint()
            elif user_input == '< more >':
                continue
            else:
                user_input = results[user_input]
                self.story.events.append(user_input)
                self.pprint()
                if not args.jupyter and not args.silent:
                    self.tts.deep_play(user_input)

    def pprint(self, highlighted=None):
        os.system('cls' if os.name == 'nt' else 'clear')
        if args.jupyter:
            print('\n' * 25)  # dirty output clear for jupyter

        if highlighted is None:
            highlighted = self.story.events[-1]
            body = ''.join(filter(None, self.story.events[:-1])).lstrip()
        else:
            body = str(self.story)

        print(f'{body}\033[96m{highlighted}\033[00m', end='', flush=True)


if __name__ == "__main__":
    # declare command line arguments
    parser = argparse.ArgumentParser(description='wrAIter: AI writing assistant with a voice')
    parser.add_argument('-j', '--jupyter', action='store_true',
                        default=False,
                        help='jupyter compatibility mode (replaces arrow key selection, disables audio)')
    parser.add_argument('-c', '--censor', action='store_true',
                        default=False,
                        help='adds a censor to the generator')
    parser.add_argument('-s', '--silent', action='store_true',
                        default=False,
                        help='silence the voices, freeing compute resources')
    parser.add_argument('-m', '--model', action='store',
                        default=['KoboldAI/OPT-2.7B-Nerys-v2'], nargs=1, type=str,
                        help='model name')
    parser.add_argument('-t', '--cputts', action='store_true',
                        default=False,
                        help='force TTS to run on CPU')
    parser.add_argument('-x', '--cputext', action='store_true',
                        default=False,
                        help='force text generation to run on CPU')
    parser.add_argument('-p', "--precision", type=int, default=16, help='float precision, only available'
                                                                        'with GPU enabled for text generation,'
                                                                        'possible values are 4, 8, 16 (default 16),'
                                                                        'lower values reduce VRAM usage')
    parser.add_argument('-l', '--lang', action='store',
                        default=['en'], nargs=1, type=str,
                        help='generative models language (en, fr, de, it, es, ...)')

    args = parser.parse_args()

    list_input_type = 'rawlist' if args.jupyter else 'list'

    if not args.jupyter and not args.silent:
        from audio.tts import Dub

    if not os.path.exists('./saved_stories'):
        os.mkdir('./saved_stories')

    g = Game()
    try:
        g.play()
    except:
        if g.story.events:
            g.story.save(g.story.title + '_crash_recovery')
        raise
