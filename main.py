#!/usr/bin/env python3
import os

from prompt_toolkit.filters import Condition

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from audio.stt import CustomMic
from InquirerPy import prompt
from InquirerPy import inquirer
from story.story import Story
from story.story import SAVE_PATH as SAVE_PATH
from story.conversation import Conversation
from generator.generator import Generator
import argparse
import re
import readline  # actually necessary for pyinquirer to work consistently
import shutil
from textwrap import TextWrapper


class Game:
    def __init__(self):
        self.gen = Generator(model_name=args.model[0], gpu=not args.cputext, precision=args.precision)
        self.tts = None if args.silent else Dub(gpu=not args.cputts, lang=args.lang[0])
        self.stt = CustomMic(english=(args.lang[0] == 'en'), model='medium')
        self.story = Story(self.gen, censor=args.censor)
        self.loop = self.loop_text
        self.sample_hashes = []
        self.keybind_pressed = None
        self.redo_history = []

    def play(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')

            width = shutil.get_terminal_size(fallback=(82, 40)).columns
            print("▄" * width)
            print("░███░█░▄▄▀█░▄▄▀█▄░▄█▄░▄█░▄▄█░▄▄▀".center(width, '█'))
            print("▄▀░▀▄█░▀▀▄█░▀▀░██░███░██░▄▄█░▀▀▄".center(width, '█'))
            print("█▄█▄██▄█▄▄█░██░█▀░▀██▄██▄▄▄█▄█▄▄".center(width, '█'))
            print("▀" * width)

            choices = []
            if (len([f for f in os.listdir(SAVE_PATH) if
                     f.endswith('.json') and not f.startswith('__autosave__')]) > 0 or len(self.story.events) > 0):
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

            action = inquirer.select('Choose an option',
                                        choices=choices,
                                        raise_keyboard_interrupt=False).execute()

            if action == 'new story':
                self.new_prompt()
            if action == 'new conversation':
                self.new_prompt(conv=True)
            elif action == 'continue':
                if len(self.story.events) == 0:
                    for path, subdirs, files in os.walk(SAVE_PATH):
                        for name in reversed(
                                sorted(files, key=lambda name: os.path.getmtime(os.path.join(path, name)))):
                            if name.startswith('__autosave__'):
                                continue
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

            if len(self.story.events) > 0:
                self.loop()

    def new_prompt(self, conv=False):
        if not conv:
            context = inquirer.text("Type a short context that the AI won't forget, so "
                                    "preferably describe aspects\n"
                                    "of the setting that you expect to remain true as the story develops."
                                    "\nWho are your characters? What world do they live in?"
                                    "\nYou can also use a tagging syntax like [Genre: fantasy, horror] for example"
                                    "\nor leave it empty.",
                                    qmark='', amark='', raise_keyboard_interrupt=False,
                                    multiline=True, instruction=' ', mandatory=False,
                                    long_instruction='Press Enter twice to send, Ctrl-C to cancel',
                                    keybindings={'answer': [{'key': ['enter', 'enter']}]}).execute()
            if context is None:
                return

            self.story = Story(self.gen, censor=args.censor)
            self.story.new(context)
        else:
            player = inquirer.text("Enter your tag. It can be 'You', 'A', 'B', 'C', 'Me', your name, ...\n>",
                                   qmark='', amark='', raise_keyboard_interrupt=False, default='Me', mandatory=False,
                                   long_instruction='Ctrl-C to cancel').execute()
            if player is None:
                return
            bot = inquirer.text("Enter the AI's tag. It can be 'Them', 'Him', 'Her', 'Bot', their name, ...\n>",
                                qmark='', amark='', raise_keyboard_interrupt=False, default='Bot', mandatory=False,
                                long_instruction='Ctrl-C to cancel').execute()
            if bot is None:
                return
            context = inquirer.text("Type a short context about who you're talking to "
                                    "(or don't and it will be random).\n"
                                    'For example: "The following conversation happens after a car crash."',
                                    qmark='', amark='', raise_keyboard_interrupt=False,
                                    multiline=True, instruction=' ', mandatory=False,
                                    long_instruction='Press Enter twice to send, Ctrl-C to cancel',
                                    keybindings={'answer': [{'key': ['enter', 'enter']}]}).execute()
            if context is None:
                return

            self.story = Conversation(self.gen, censor=args.censor)
            self.story.new(context, player=player.strip(), bot=bot.strip())

    def load_prompt(self):
        action = inquirer.select('Choose a file to load',
                                 choices=sorted(
                                     [f[:-5] for f in os.listdir(SAVE_PATH) if f.endswith('.json')],
                                     key=lambda name: os.path.getmtime(os.path.join(SAVE_PATH, name + '.json')),
                                     reverse=True),
                                 raise_keyboard_interrupt=False, mandatory=False,
                                 long_instruction='Ctrl-C to cancel').execute()

        if action is not None:
            if action.endswith(' (conversation)'):
                self.story = Conversation(self.gen, censor=args.censor)
            else:
                self.story = Story(self.gen, censor=args.censor)
            self.story.load(action)

    def save_prompt(self):
        user_input = inquirer.text("Type a name for your save file.\n>",
                                   default=self.story.title, mandatory=False,
                                   qmark='', amark='', raise_keyboard_interrupt=False).execute()
        if user_input is not None:
            user_input = user_input.strip()
            try:
                self.story.save(user_input)
                print(f'Successfully saved {user_input}')
            except:
                print(f'Failed to save the game as {user_input}')

    def loop_text(self):
        self.pprint()

        while True:
            try:
                self.pprint()
                default_input = self.redo_history[0] if self.redo_history else ''
                inquirer_prompt = inquirer.text(message='', qmark='', amark='', raise_keyboard_interrupt=False,
                                                mandatory=False, default=default_input, multiline=True,
                                                long_instruction='Press Enter twice to send, Ctrl-L for a list of commands',
                                                instruction=' ', keybindings={'answer': [{'key': ['enter', 'enter']}]})

                # Declare keybinds
                @inquirer_prompt.register_kb('escape')
                def menu(event):
                    self.keybind_pressed = menu
                    inquirer_prompt._handle_skip(event)

                @inquirer_prompt.register_kb('c-w')
                def wordstats(event):
                    tokens_current = len(self.story.gen.enc.encode(str(self.story)))
                    tokens_max = self.story.get_max_history()
                    tokens_trimmed = len(self.story.gen.enc.encode(self.story.clean_input()))
                    fancy_words = ", ".join(sorted(set(re.sub(
                        r"[^A-Za-z0-9_]+", " ",
                        str(self.story).lower()).split()), key=lambda x: len(x), reverse=True)[:5])
                    print(f'\n\nstory title:             "{self.story.title}"\n'
                          f'context/starting prompt:\n'
                          f'{self.story.events[0]}\n\n'
                          f'number of events:        {len(self.story.events)}\n'
                          f'number of tokens:        {tokens_current}/{tokens_max} (trimmed to {tokens_trimmed})\n'
                          f'wordcloud:               {self.story.wordcloud()}\n'
                          f'fanciest words:          {fancy_words}\n')
                    input('Press enter to continue.')
                    inquirer_prompt._handle_skip(event)

                @inquirer_prompt.register_kb('c-p')
                def edit_story_prompt(event):
                    self.keybind_pressed = edit_story_prompt
                    inquirer_prompt._handle_skip(event)

                @inquirer_prompt.register_kb('tab')
                def tab(event):
                    self.keybind_pressed = tab
                    inquirer_prompt._handle_enter(event)


                @inquirer_prompt.register_kb('c-s')
                def save(event):
                    self.keybind_pressed = save
                    inquirer_prompt._handle_skip(event)

                @inquirer_prompt.register_kb('up', filter=Condition(lambda: len(self.story.events) > 1))
                def revert(event):
                    if self.tts is not None:
                        self.tts.stop()
                    undo = 2 if isinstance(self.story, Conversation) else 1
                    self.redo_history = self.story.events[-undo:] + self.redo_history
                    self.story.events = self.story.events[:-undo]
                    inquirer_prompt._handle_skip(event)

                @inquirer_prompt.register_kb('down', filter=Condition(lambda: bool(self.redo_history)))
                def redo(event):
                    self.keybind_pressed = redo
                    inquirer_prompt._handle_enter(event)

                @inquirer_prompt.register_kb('c-l')
                def command_list(event):
                    print('\n\nKnown commands:\n'
                          'esc          go to main menu\n'
                          'tab          generate a single sentence\n'
                          'UP   arrow   undo and edit last action or response\n'
                          'DOWN arrow   redo the last undone action\n'
                          'ctrl-l       display this list\n'
                          'ctrl-p       edit context/starting prompt\n'
                          'ctrl-s       save story\n'
                          'ctrl-w       print word count and other stats\n'
                          'ctrl-c       clear current text box, interrupt generation and audio\n')
                    input('Press enter to continue.')
                    inquirer_prompt._handle_skip(event)

                # execute inquirer prompt
                self.keybind_pressed = None
                user_input = inquirer_prompt.execute()

                # Handle keybinds that require additional processing
                if self.keybind_pressed == menu:
                    return
                elif self.keybind_pressed == edit_story_prompt:
                    new_context = inquirer.text('Edit context/starting prompt:',
                                                default=self.story.events[0],
                                                qmark='', amark='', raise_keyboard_interrupt=False,
                                                mandatory=False, multiline=True, instruction=' ',
                                                long_instruction='Press Enter twice to send, Ctrl-C to cancel',
                                                keybindings={'answer': [{'key': ['enter', 'enter']}]}).execute()
                    if new_context is not None:
                        self.story.events[0] = new_context

                elif self.keybind_pressed == save:
                    self.save_prompt()
                elif user_input is None:
                    # CTRL+C case (inquirer returned None)
                    if self.tts is not None:
                        self.tts.stop()
                elif self.keybind_pressed == redo:
                    n = 2 if isinstance(self.story, Conversation) else 1
                    self.story.events.append(user_input)
                    if n > 1:
                        self.story.events += self.redo_history[1:n]
                    self.redo_history = self.redo_history[n:]
                    user_input = None  # skip generation

                # handle text input
                if user_input is not None:
                    self.story.save('__autosave__', name_is_title=False)
                    self.redo_history = []

                    action = user_input.strip(' ')

                    if len(self.story.events) <= 1:
                        action = '\n' + action
                    elif action:
                        action = ' ' + action

                    # capitalize
                    action = re.sub(r'\bi\b', 'I', action)  # capitalize lone 'I'
                    action = re.sub(r'[.|\?|\!]\s*([a-z])|\s+([a-z])(?=\.)',
                                    lambda matchobj: matchobj.group(0).upper(), action)  # capitalize start of sentences

                    if isinstance(self.story, Conversation):
                        if args.lang[0] == 'fr':
                            action = f'\n[{self.story.player}:] {action.strip()}\n[{self.story.bot}:] '
                        else:
                            action = f'\n{self.story.player}: "{action.strip()}"\n{self.story.bot}: "'

                    self.pprint(action)

                    eos_tokens = ['.', '!', '?', '\n'] if self.keybind_pressed == tab else []
                    result = self.story.act(action,eos_tokens=eos_tokens)
                    self.pprint()
                    if result is None:
                        print(
                            "--- The model failed to produce an decent output after multiple tries. Try something else.")
                    else:
                        if not args.silent:
                            if isinstance(self.story, Conversation):
                                self.tts.deep_play(result)
                            else:
                                self.tts.deep_play(action + result)
            except KeyboardInterrupt:
                if self.tts is not None:
                    self.tts.stop()

    def loop_voice(self):
        self.pprint()

        while True:
            try:
                self.story.save('__autosave__', name_is_title=False)
                self.pprint()
                try:
                    user_input = self.stt.custom_listen()
                except KeyboardInterrupt:
                    return

                action = user_input.strip()

                if len(self.story.events) <= 1:
                    action = '\n' + action
                elif action:
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
                    self.tts.deep_play(result)
            except KeyboardInterrupt:
                if self.tts is not None:
                    self.tts.stop()

    def loop_choice(self):
        self.pprint()

        while True:
            try:
                self.story.save('__autosave__', name_is_title=False)
                if isinstance(self.story, Conversation):
                    self.loop = self.loop_text
                    return

                self.pprint()
                results = self.story.gen_n_results(3)
                results = {r.strip('\n').split('\n')[0]: r for r in results}
                choices = list(results.keys()) + ['< revert >', '< more >']

                user_input = inquirer.select('\nChoice:', amark='', qmark='',
                                             choices=choices,
                                             raise_keyboard_interrupt=False, mandatory=False,
                                             long_instruction='Ctrl-C for menu').execute()
                if user_input is None:
                    return
                elif user_input == '< more >':
                    continue
                elif user_input == '< revert >':
                    if self.tts is not None:
                        self.tts.stop()
                    if len(self.story.events) < 4:
                        self.story.new(self.story.events[0])
                        self.pprint()
                        if not args.silent:
                            self.tts.deep_play('\n'.join(filter(None, self.story.events[2:])))
                    else:
                        self.story.events = self.story.events[:-1]
                        self.pprint()
                else:
                    user_input = results[user_input]
                    self.story.events.append(user_input)
                    self.pprint()
                    if not args.silent:
                        self.tts.deep_play(user_input)
            except KeyboardInterrupt:
                if self.tts is not None:
                    self.tts.stop()

    def pprint(self, highlighted=None):
        width = shutil.get_terminal_size(fallback=(82, 40)).columns
        width = min(width, 180)
        wrapper = TextWrapper(width=width, replace_whitespace=False, initial_indent='  ', subsequent_indent='  ')

        os.system('cls' if os.name == 'nt' else 'clear')

        if highlighted is None:
            highlighted = self.story.events[-1]
            body = ''.join(filter(None, self.story.events[:-1])).lstrip()
        else:
            body = str(self.story)

        body = f'{body}\033[96m{highlighted}\033[00m'

        print('\n'.join(['\n'.join(wrapper.wrap(line)) for line in body.splitlines()]),
              end='', flush=True)


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

    if not args.silent:
        from audio.tts import Dub

    if not os.path.exists('./saved_stories'):
        os.mkdir('./saved_stories')

    g = Game()
    g.play()
