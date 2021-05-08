import os, sys
from pathlib import Path
from contextlib import contextmanager
import random
import re
import wave
from playsound import playsound
import TTS
from TTS.utils.synthesizer import Synthesizer
from TTS.utils.manage import ModelManager

try:
    # Use winsound if available. Playsound works, but can't interrupt a sound if you try to play another.
    import winsound
    WINSOUND = True
except ImportError:
    WINSOUND = False


model_name = "tts_models/en/ljspeech/tacotron2-DCA"
#model_name = "tts_models/en/ljspeech/glow-tts"

vocoder_name = "vocoder_models/en/ljspeech/multiband-melgan"
#vocoder_name = "vocoder_models/universal/libri-tts/wavegrad"
#vocoder_name = "vocoder_models/universal/libri-tts/fullband-melgan"

path = Path(TTS.__file__).parent / "./.models.json"
manager = ModelManager(path)
model_path, config_path, _ = manager.download_model(model_name)
vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)
synthesizer = Synthesizer(tts_checkpoint=model_path, tts_config_path=config_path,
                          vocoder_checkpoint=vocoder_path, vocoder_config=vocoder_config_path, use_cuda=True)

tempdir = "./audio"
for root, dirs, files in os.walk(tempdir):
    for f in files:
        if f.endswith('.wav'):
            os.remove(os.path.join(root, f))


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


def deep_play(text, pitch=1):
    if pitch is None:
        pitch = 1
    if pitch == 0:
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
    
    file = os.path.join(tempdir, f'temp{random.randint(0, int(1e16))}.wav')
    
    try:
        with suppress_stdout():
            wav = synthesizer.tts(text)
            synthesizer.save_wav(wav, file)
            change_wav_pitch(file, float(pitch))
    except:
        print(f'Failed to TTS: [{text}]')
        return

    # os.system(f'tts --text "{text}" --model_name tts_models/en/ljspeech/tacotron2-DCA --vocoder_name
    # "vocoder_models/en/ljspeech/mulitband-melgan" --out_path {audio_dir} >{audio_dir}logs.txt 2>&1')

    if WINSOUND:
        winsound.PlaySound(file, winsound.SND_ASYNC)
    else:
        playsound(file, block=True)

    # delete other temporary wav files while this one is being played
    for root, dirs, files in os.walk(tempdir):
        for f in files:
            if f.endswith('.wav') and f not in file:
                os.remove(os.path.join(root, f))

    
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
