#!/usr/bin/env python3
import os
import sys
from difflib import SequenceMatcher

from PyInquirer import style_from_dict, Token, prompt

from audio import tts
from story import grammars
from story.story import Story
from story.story import SAVE_PATH
from generator.generator import Generator
import argparse

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"


class Game:
    def __init__(self):
        self.gen = Generator(model_name=args.model[0])
        self.style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })
        self.story = Story(self.gen)
        self.voice = 1.05
        self.loop = self.loop_text

        print("""
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
███████████████████████████░███░█░▄▄▀█░▄▄▀█▄░▄█▄░▄█░▄▄█░▄▄▀███████████████████████████
███████████████████████████▄▀░▀▄█░▀▀▄█░▀▀░██░███░██░▄▄█░▀▀▄███████████████████████████
████████████████████████████▄█▄██▄█▄▄█░██░█▀░▀██▄██▄▄▄█▄█▄▄███████████████████████████
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀""")

    def play(self):
        while True:
            choices = ['continue', 'load', 'new', 'voice', 'model'] + \
                      ['switch to choice mode' if self.loop == self.loop_text else 'switch to text mode']
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
            'message': 'Choose a character',
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
                'message': "Type a context. The AI won't forget it, so preferably describe aspects of the setting"
                           "\nthat you expect to remain true as the story develops. Who are you? What world do you "
                           "live in?\n",
                'name': 'context'
            }, {
                'type': 'input',
                'message': 'Type a prompt. This is the start of your story.\n',
                'name': 'prompt'
            }]
            custom_input = prompt(questions, style=self.style)
            context = custom_input['context'].strip()
            custom_prompt = custom_input['prompt'].strip()
        elif action == 'ai-generated':
            custom_prompt = ''
            context = ''
        else:
            context = grammars.generate(action, "character", "context").strip()
            custom_prompt = grammars.generate(action, "character", "prompt").strip()

        print("Generating story ...")
        result = self.story.new(context, custom_prompt)
        # tts.deep_play('\n'.join(result.split("\n")[1:]), self.voice)
        tts.deep_play(result, self.voice)

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
            self.story = Story(self.gen)
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
        print(self.story)
        while True:
            user_input = input('> ').strip()

            if user_input == '/menu':
                return
            elif user_input == '/revert':
                if len(self.story.events) < 4:
                    result = self.story.new(self.story.events[0], self.story.events[1])
                    print(result)
                    # tts.deep_play('\n'.join(result.split("\n")[1:]), self.voice)
                    tts.deep_play(result, self.voice)
                else:
                    self.story.events = self.story.events[:-2]
                    print("Last action reverted.")
                    print(self.story.events[-1])

            elif user_input.startswith('/'):
                print('Known commands:\n'
                      '/menu    go to main menu (it has a save option)\n'
                      '/revert  revert last action and response (if there are none, regenerate an intro)\n\n'
                      'Tip:     Start or finish your input with a dash ("-") to complete the last response '
                      '         or let the AI complete your input. Example:\n'
                      'AI:      This sentence is probably not finished so\n'
                      'User:    -this will complete the sentence without inserting a newline. Also this-\n'
                      'AI:      will be interpreted by the AI a as sentence to complete.')
            else:
                action = user_input.strip()

                if action != '':
                    # clean end of string
                    if action[-1] == "-":
                        pass
                    elif action[-1] in [".", "?", "!"] or action.endswith('."') or action.endswith(
                            '?"') or action.endswith('!"'):
                        action = action
                    else:
                        action = action + "."

                result = self.story.act(action)
                if result is None:
                    print("--- The model failed to produce an no-repeating output. Try something else.")
                else:
                    print(result)
                    similarity = SequenceMatcher(None, action, result).ratio()
                    if similarity > 0.5:
                        # don't repeat action if the model repeated it in result
                        tts.deep_play(result, self.voice)
                    else:
                        tts.deep_play(action + " " + result, self.voice)

    def loop_choice(self):
        print(self.story)
        while True:
            choices = ['< more >'] + self.story.gen_n_results(3) + ['< revert >', '< menu >']
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
                    print(result)
                    tts.deep_play('\n'.join(result.split("\n")[1:]), self.voice)
                else:
                    self.story.events = self.story.events[:-1]
                    print("Last action reverted.")
                    print(self.story.events[-1])
            elif user_input == '< more >':
                continue
            else:
                user_input = user_input.strip()
                self.story.events.append(user_input)
                print(user_input)
                tts.deep_play(user_input, self.voice)

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
        # dirty fix: can't use GPU unless I find a way to free its memory, otherwise it just crashes
        self.gen = Generator(model_name, models_dir, gpu=False)
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
                        help='jupyter compatibility mode (replaces arrow key selection)')
    parser.add_argument('-m', '--model', action='store',
                        default=['scifi-355M'], nargs=1, type=str,
                        help='model name')

    args = parser.parse_args()

    list_input_type = 'rawlist' if args.jupyter else 'list'

    if not os.path.exists('./saved_stories'):
        os.mkdir('./saved_stories')

    g = Game()
    g.play()
