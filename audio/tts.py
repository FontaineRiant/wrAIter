import os, sys
from pathlib import Path
from contextlib import contextmanager
import random
import re
import wave
import TTS
from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager
from pygame import mixer


class Dub:
    def __init__(self, gpu=True):
        mixer.init()

        self.model_name = "tts_models/multilingual/multi-dataset/your_tts"

        self.path = Path(TTS.__file__).parent / "./.models.json"
        self.manager = ModelManager(self.path)
        #print(self.manager.list_models())
        #quit()
        self.model_path, self.config_path, _ = self.manager.download_model(self.model_name)
        self.vocoder_path, self.vocoder_config_path, _ = None, None, None
        try:
            self.synthesizer = Synthesizer(tts_checkpoint=self.model_path, tts_config_path=self.config_path,
                                           use_cuda=gpu)
        except:
            # try without CUDA
            self.synthesizer = Synthesizer(tts_checkpoint=self.model_path, tts_config_path=self.config_path,
                                           use_cuda=False)

        self.tempdir = "./audio/temp"
        for root, dirs, files in os.walk(self.tempdir):
            for f in files:
                if f.endswith('.wav'):
                    os.remove(os.path.join(root, f))

    @contextmanager
    def suppress_stdout(self):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout

    def stop(self):
        mixer.music.stop()
        mixer.music.unload()

    def deep_play(self, text, speaker_wav):
        try:
            if speaker_wav is None:
                return

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
            if text[-1] not in ['.', '!', '?']:
                text += '.'

            file = os.path.join(self.tempdir, f'temp{random.randint(0, int(1e16))}.wav')

            language_idx = "en"

            try:
                with self.suppress_stdout():
                    wav = self.synthesizer.tts(text, speaker_wav=f'./audio/voices/{speaker_wav}.wav', language_name=language_idx)
                    self.synthesizer.save_wav(wav, file)
                    #self.change_wav_pitch(file, float(pitch))
            except RuntimeError:
                print('TTS failed, retrying witout CUDA')
                synthesizer = Synthesizer(tts_checkpoint=self.model_path, tts_config_path=self.config_path,
                                          vocoder_checkpoint=self.vocoder_path, vocoder_config=self.vocoder_config_path,
                                          use_cuda=False)
                with self.suppress_stdout():
                    wav = synthesizer.tts(text, speaker_wav=f'./audio/voices/{speaker_wav}.wav', language_name=language_idx)
                    synthesizer.save_wav(wav, file)
                    #self.change_wav_pitch(file, float(pitch))
            except KeyboardInterrupt:
                return
            except:
                print(f'Failed to TTS: [{text}]')
                return

            mixer.music.stop()
            mixer.music.unload()
            mixer.music.load(file)
            mixer.music.play()

            # delete other temporary wav files while this one is being played
            for root, dirs, files in os.walk(self.tempdir):
                for f in files:
                    if f.endswith('.wav') and f not in file:
                        os.remove(os.path.join(root, f))
        except KeyboardInterrupt:
            return

    @staticmethod
    def change_wav_pitch(file, pitch=1.0):
        with wave.open(file, 'rb') as spf:
            rate = spf.getframerate()
            signal = spf.readframes(-1)

        if os.path.exists(file):
            os.remove(file)

        with wave.open(file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(int(rate*pitch))
            wf.writeframes(signal)
