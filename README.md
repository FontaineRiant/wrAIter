![](https://i.imgur.com/wbxNBBA.png)

wrAIter is a voiced AI that writes stories while letting the user interact and add to the story.
You can write a paragraph, let the AI write the next one, you add another, etc.
Or you can enable "choice mode" and let the AI make suggestions you can pick
from for each paragraph.

The AI writer is powered by EleitherAI's GPT-NEO model, a replication of GPT-3.
The suggested model has 2.7 billion parameters
and was fine-tuned to write light novels.

## Features
* State-of-the-art Artificial Intelligence fine-tuned for the specific purpose of writing stories,
* A high quality narrator AI that reads the story out loud (TTS)**,
* Two modes to build a story: alternating AI-human writing or choosing from AI generated options,
* Save, load, continue and revert functions,
* Randomly generated or custom prompts to start new stories.


![](https://i.imgur.com/bOSnLJi.png)

## Local Installation
0. (Optional) Set up CUDA 11.1 to enable hardware acceleration if your GPU can take it.
1. Install python 3.7, [Visual C++ 14.0 (or later)](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and [eSpeak-ng](https://github.com/espeak-ng/espeak-ng).
2. Set the PHONEMIZER_ESPEAK_PATH environment variable to `C:\Program Files\eSpeak NG\espeak-ng.exe` or wherever you installed it.
3. Download or clone this repository.
4. Run `install.ps1` (windows powershell) or `install.sh` (shell script).
5. Download a GPT-NEO model and put its content in `./models/[model name]/`. Here's a link to [finetuneanon's light novel model](https://drive.google.com/file/d/1M1JY459RBIgLghtWDRDXlD4Z5DAjjMwg/view?usp=sharing). 
6. Play by running `play.ps1` (windows powershell) or `play.sh` (shell script). You can also launch `main.py` directly with your own launch options (model selection, gpu/cpu).


## FAQ
_What kind of hardware do I need?_
CPU inference is currently broken for text generation, and enabled by default for text-to-speech (launch option).
So you'll need a GPU with at least 8 GB of VRAM. If you run into video memory issues, you can lower `max_history`
in `./generator/generator.py` (maximum number of "words" that the AI can read before writing text).

_How should I write things in a way that the AI understands?_

You aren't in a dialog with an AI, you're just writing parts of a story, except there's autocompletion for the next ~60 words. Trying to talk to it will just throw it off. Write as if you were the narrator. Avoid typos, the 355M models don't react well to them (use `/revert` to cancel an input and rewrite it).

_The AI is repeating itself, help!_

With this implementation, this shouldn't happen anymore. Still, here are a few tips:
* You can switch to choice mode and hit `< more >` until the AI gives you something different.
* You can also try go along with your story with a radical change in the action, ignoring the AI until it catches up with you.
* You can `/revert` back to a point in the story before it started failing.
* If all else fails, just start a new story.

To make this happen less often, try not to be redundant or use the same word twice. GPT's whole schtick is to complete sequences, so it tends to latch onto a pattern whenever it sees one.

_Can I write in first person like in AIdungeon?_

No, AIdungeon converts first person to second person before feeding your input to its model, which was trained for second person narration. Writing in first person on wrAIter will probably result in a first person response.

_Does the AI learn from my inputs?_

While the AI remembers the last thousand words of the story, it doesn't learn from it. Playing or saving a story won't affect the way it plays another.

_Does the AI forget parts of the story?_

Yes. Because the model can only take 1024 words in the input, the oldest events can be dropped to make the story fit. However, the context of the story (first paragraph) is never "forgotten".

Until you hit 1024 words, longer stories get progressively better results.

_Can I fine-tune the AI on a corpus of my choice?_

I didn't bother with fine-tuning with GPT-NEO. The model is just too large to fit into my machine or any free cloud GPU.
So you're on your own.

_wrAIter is a terrible name._

Yes it is. Still, with a French accent it's pronounced "writer".

_Does this thing respect my privacy?_

Yes, wrAIter only needs to connect to the internet to download the TTS model and to install python packages. It doesn't upload anything, and only saves stories on your hard drive if you explicitly ask it to. To play sound, the last played wave file is also stored on your machine.

_I read an article about AIdungeon and profanity. Doesn't this have the same issues?_

No. First, wrAIter doesn't adjust based on your or other players' inputs. The model runs on your machine, so tempering with it would only affect your own experience. Second, a censor is enabled by default, trashing and regenerating entire paragraphs if the model outputs a single banned word. It can be disabled in the launch options, giving you the freedom of choice.


## Credits
* [Latitude](https://github.com/Latitude-Archives/AIDungeon) for AIDungeon that I used as a starting point,
* [EleutherAI](https://www.eleuther.ai/projects/gpt-neo/) for GPT-NEO,
* [coqui-ai](https://github.com/coqui-ai/TTS) for the TTS models.
