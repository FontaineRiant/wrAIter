import json
import os.path


class Settings:
    def __init__(self, file='settings.json'):
        self.file = file
        self.defaults = {
            'silent': False,  # mute audio output
            'censor': True,  # censor bad words (slurs/nsfw)
            'model': 'KoboldAI/OPT-2.7B-Nerys-v2',  # model name on huggingface
            'cputts': False,  # force TTS to run on CPU
            'cputext': False,  # force text generation to run on CPU
            'precision': 16,  # float precision, only available with GPU enabled for text generation,
            # possible values are 4, 8, 16 (default 16), lower values reduce VRAM usage
            'language': 'en'
        }

    def get(self, key):
        self._create_file_if_not_exists()

        with open(self.file, 'r') as f:
            settings = json.load(f)
            return settings[key] if key in settings else self.defaults[key]

    def set(self, key, value):
        self._create_file_if_not_exists()

        with open(self.file, 'r') as f:
            settings = json.load(f)

        settings[key] = value

        with open(self.file, 'w') as f:
            json.dump(settings, fp=f, indent=4)

    def _create_file_if_not_exists(self):
        if not os.path.isfile(self.file):
            with open(self.file, 'w') as f:
                json.dump(self.defaults, fp=f, indent=4)
