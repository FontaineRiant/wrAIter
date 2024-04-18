import os
import sys
from contextlib import contextmanager
from whisper_mic import WhisperMic, get_logger

# Hide error output from ALSA, JACK... (pyaudio)
@contextmanager
def ignoreStderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)

# custom WhisperMic for various fixes
class CustomMic(WhisperMic):
    def __init__(self, *args, **kwargs):
        with ignoreStderr():
            super().__init__(*args, **kwargs)
        self.logger = get_logger('whisper_mic', level='warning')
        self.inference_device = self.audio_model.inference_device
        self.audio_model.to('cpu')

    def listen(self, timeout=None, phrase_time_limit=None):
        self.logger.info("Listening...")
        while self.result_queue.empty():
            self._WhisperMic__listen_handler(timeout, phrase_time_limit)
            if self.result_queue.empty():
                print('Too quiet, please repeat')
        while True:
            if not self.result_queue.empty():
                return self.result_queue.get()

    def custom_listen(self):
        print('\n> Listening (ctrl+c for menu)')
        with ignoreStderr():
            if 'cuda' in str(self.inference_device):
                self.audio_model.to('cuda')
            result = self.listen()
            self.audio_model.to('cpu')
        return result

