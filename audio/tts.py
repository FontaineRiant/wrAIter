import io
import os, sys, datetime, argparse, time
from pathlib import Path
from contextlib import contextmanager
import random
import re
import wave
import TTS
from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager
from pygame import mixer
from pysbd import Segmenter


class Dub:
    def __init__(self, gpu=True, lang='en'):
        mixer.init()

        self.lines_spoken = 0
        self.device = 'cuda' if gpu else 'cpu'
        self.lang = lang

        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

        self.path = Path(TTS.__file__).parent / "./.models.json"
        self.manager = ModelManager(self.path)
        # print(self.manager.list_models())
        # quit()
        self.model_path, self.config_path, _ = self.manager.download_model(self.model_name)

        if self.config_path is None:
            self.config_path = self.model_path + "/config.json"

        self.vocoder_path, self.vocoder_config_path, _ = None, None, None

        self.synthesizer = Synthesizer(tts_checkpoint=self.model_path,
                                       tts_config_path=self.config_path,
                                       use_cuda=gpu)
        self.synthesizer.tts_model.to('cpu')


    @contextmanager
    def suppress_stdout(self):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def clean_input(self, text):
        text = re.sub(r'(?<=[0-9])"', ' inches', text)  # quote to inches
        text = re.sub(r"\B'\B|(?<!s)\b'\B|\B'\b", '"', text)  # replace single quotes
        text = text.replace('"', '')
        text = text.replace('\n', ' ')
        text = text.replace(':', '.')

        # double periods make empty sentences and crashes
        text = re.sub(r"[.!]\W*[.!]", ".", text)
        text = re.sub(r"[.?]\W*[.]", "?", text)
        text = re.sub(r"[.]\W*[.?]", "?", text)

        # trailing periods creates an empty sentence and crashes
        text = text.strip("\n>. ")
        # final clean dot

        if not text:
            return ''

        if text[-1] not in ['.', '!', '?']:
            text += '.'

        return text

    def stop(self):
        mixer.music.stop()
        mixer.music.unload()


    def playsound(self, file):
        self.stop()
        file.seek(0)
        mixer.music.load(file)
        mixer.music.play()


    def deep_play(self, text):
        try:
            narrator = ['./audio/voices/narrator/' + f for f in os.listdir('./audio/voices/narrator')]
            char1 = ['./audio/voices/character1/' + f for f in os.listdir('./audio/voices/character1')]
            char2 = ['./audio/voices/character2/' + f for f in os.listdir('./audio/voices/character2')]

            files = []

            for t in text.split('\n'):
                cnt = 0

                self.lines_spoken += 1

                lines = t.split('"')
                for line in lines:
                    if cnt % 2:
                        # within quotes
                        speaker = char1 if self.lines_spoken % 2 else char2
                    else:
                        # out of quotes -> narrator
                        speaker = narrator

                    cnt += 1

                    line = self.clean_input(line)

                    if not line or speaker is None:
                        continue

                    if len(line) > 1 and line[-1] == '.':
                        line = line[:-1]  # remove trailing dots, they're often pronounced "dot"

                    # split sentences manually to then regroup tiny sentences together (one-word inputs sound ugly)
                    sentences = Segmenter(language='en', clean=True).segment(line)
                    i = 0
                    while i < len(sentences) - 1:
                        if len(sentences[i]) < 25 or len(sentences[i + 1]) < 25:
                            sentences[i] += ' ' + sentences.pop(i + 1)
                        else:
                            i += 1

                    self.synthesizer.tts_model.to(self.device)

                    for sens in sentences:
                        with self.suppress_stdout():
                            try:
                                wav = self.synthesizer.tts(sens, speaker_wav=speaker, language_name=self.lang,
                                                           speaker_name=None, split_sentences=False)
                            except AssertionError:
                                try:
                                    # if input too big, try again with automatic split sentences
                                    wav = self.synthesizer.tts(sens, speaker_wav=speaker,
                                                               language_name=self.lang,
                                                               speaker_name=None, split_sentences=True)
                                except AssertionError:
                                    # if input still too big, try again with commas instead of periods
                                    wav = self.synthesizer.tts(sens.replace(',', '.'), speaker_wav=speaker,
                                                               language_name=self.lang,
                                                               speaker_name=None, split_sentences=True)

                        in_memory_wav=io.BytesIO()
                        self.synthesizer.save_wav(wav, in_memory_wav)
                        files.append(in_memory_wav)

            if files:
                file = self.postprocess(files, 1.1)
                self.playsound(file)

        except KeyboardInterrupt:
            raise
        finally:
            self.synthesizer.tts_model.to('cpu')

    def postprocess(self, files, pitch=1.0):
        processedfile = io.BytesIO()

        with wave.open(processedfile, 'wb') as wf:
            signals = []
            for file in files:
                with wave.open(file, 'rb') as spf:
                    rate = spf.getframerate()
                    signals.append(spf.readframes(-1))

            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(int(rate * pitch))

            for signal in signals:
                wf.writeframes(signal)

        return processedfile
