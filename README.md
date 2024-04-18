![image](https://github.com/FontaineRiant/wrAIter/assets/25899941/d40d33ba-acc6-4f48-b1f6-9232738980f8)

wrAIter is a voiced AI that writes stories while letting the user interact and add to the story.
You can write a paragraph, let the AI write the next one, you add another, etc.
Or you can enable "choice mode" and let the AI make suggestions you can pick
from for each paragraph.

It has an option for voice input through the microphone, as well as a conversation mode to chat like you would to a home assistant without touching your keyboard.

The AI writer is powered by any LLM that can be found on [Hugging Face](https://huggingface.co/), easily swappable through a command line argument.
The default model has 2.7 billion parameters
and was fine-tuned to write fictional stories.

![image](https://github.com/FontaineRiant/wrAIter/assets/25899941/44173a2e-6cd4-4ec6-bf7a-f1028a23902c)

## Features
* State-of-the-art LLMs from huggingface fine-tuned for the specific purpose of writing stories,
* A high quality narrator AI that reads the story out loud (TTS)**,
* Customizable voice: the narrator will sound like any voice sample of your choice,
* Multiple speakers: the voice will change between the narrator and different characters,
* Three modes to build a story: alternating AI-human writing, choosing from AI generated options or **microphone input**,
* A conversation mode to chat directly with a fictional character,
* Save, load, continue and revert functions.

![image](https://github.com/FontaineRiant/wrAIter/assets/25899941/2aa0c411-c9a0-47ca-b472-6632f4d280ae)

## Local Installation
0. (Optional) Set up CUDA 11.1 to enable hardware acceleration if your GPU can take it.
1. Install python 3.7 or greater
2. Set the PHONEMIZER_ESPEAK_PATH environment variable to `C:\Program Files\eSpeak NG\espeak-ng.exe` or wherever you installed it. (windows only)
3. Download or clone this repository.
4. Run `install.ps1` (windows powershell) or `install.sh` (shell script).
5. Play by running `play.ps1` (windows powershell) or `play.sh` (shell script). You can also launch `main.py` directly with your own launch options (model selection, gpu/cpu).


## FAQ

_How can I customize the narrator's voice?_

Simply drop WAV files into the directories in `audio/voices/`. Dialogues will alternate between character1 and character2 voices,
and everything outside quotes will be read by narrator.
The files should be a clean and samples of a single person talking.
A male and a female voice samples are already included: "librispeech-f" and "librispeech-m"

_What kind of hardware do I need?_

You'll need an GPU with at least 8 GB of VRAM, or a lot of patience and 28 GB of RAM (with the --cputext flag).
With 10 GB of VRAM (RTX 3080), you can also run TTS faster by removing the --cputts flag. Feel free to try smaller and 
bigger variants of the OPT model from huggingface.

With 24GB of VRAM, Mistral models now work with enough spare memory for TTS.

AMD is also supported since version 2.2.0.

The `--precision` also allows you to reduce VRAM usage by reducing float precision to 8 or 4 bits (see `--help`, NVIDIA only for now).

_Can I write in first person like in AIdungeon?_

No, AIdungeon converts first person to second person before feeding your input to its model, which was trained for second person narration.
Writing in first person on wrAIter will probably result in a first person response.

_Does the AI learn from my inputs?_

While the AI remembers the last thousand words of the story, it doesn't learn from it. Playing or saving a story won't affect the way it plays another.

_Does the AI forget parts of the story?_

Yes. Because the model can only take 2048 words in the input (number depends on the model), the oldest events can be dropped to make the story fit. However, the context of the story (first paragraph) is never "forgotten".

Until you hit 2048 words, longer stories get progressively better results.

_Can I fine-tune the AI on a corpus of my choice?_

I didn't bother with fine-tuning LLMs larger than 355M parameters. The models are just too large to fit into my machine or any free cloud GPU.
So you're on your own if you want to try.

_Does this thing respect my privacy?_

Yes, wrAIter only needs to connect to the internet to download the models and to install python packages. It doesn't upload anything, and only saves stories on your hard drive.

_I read an article about AIdungeon and profanity. Doesn't this have the same issues?_

No. First, wrAIter doesn't adjust based on your or other players' inputs. The model runs on your machine, so tempering with it would only affect your own experience. Second, a censor is enabled by default, trashing and regenerating entire paragraphs if the model outputs a single banned word. It can be disabled in the launch options, giving you the freedom of choice.


## Credits
* [Latitude](https://github.com/Latitude-Archives/AIDungeon) for AIDungeon that I used as a starting point,
* [Hugging Face](https://huggingface.co/) for Language Models,
* [coqui-ai](https://github.com/coqui-ai/TTS) for the TTS models.
