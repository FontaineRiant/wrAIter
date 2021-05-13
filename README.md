![](https://i.imgur.com/wbxNBBA.png)

wrAIter is a voiced AI that writes stories while letting the user interact and add to the story.
You can write a paragraph, making the AI write the next one, you add another, etc.
Or you can enable "choice mode" and let the AI make suggestions you can pick
from for each paragraph.

The AI writer is powered by OpenAI's GPT-2 model. The included model has 355M parameters
and was fine-tuned to write fiction.

## Features
* Play in [Google Colab](https://colab.research.google.com/drive/1Bk0_cPV5M61TWWslDw-nNjmtGG3nBF4W?usp=sharing) or locally,
* State-of-the-art Artificial Intelligence fine-tuned for the specific purpose of writing stories,
* A high quality narrator AI that reads the story out loud (TTS),**
* Two modes to build a story: alternating AI-human writing or chosing from AI generated options,
* Save, load, continue and revert functions,
* Randomly generated or custom prompts to start new stories.

** wrAIter's voice feature isn't available in Colab.

![](https://i.imgur.com/bOSnLJi.png)

## Local Installation
0. (Optional) Set up CUDA 10.1 to enable hardware acceleration if your GPU can take it (4 GB VRAM).
1. Install python 3.7
2. Download or clone this repository.
3. Run `install.ps1` (windows powershell) or `install.sh` (shell script).
4. Download a [model](https://drive.google.com/drive/folders/14aex0HBP7EtUn6FGLfIoHe3gWmrIDZbI?usp=sharing) (see next section) and place it in `models/`
5. Play by running `play.ps1` (windows powershell) or `play.sh` (shell script).

## Try it on Google Colab
The Colab version doesn't have a voiced narrator and has issues with displaying text without truncating some of it. Use the local version if you want the full experience.

1. Go the wrAIter's [Colab notebook](https://colab.research.google.com/drive/1Bk0_cPV5M61TWWslDw-nNjmtGG3nBF4W?usp=sharing)
2. Runtime > Run all (ctrl+F9)
3. Wait a couple of minutes for the main menu to appear in the last cell.


## Models
Pretrained models are available [here](https://drive.google.com/drive/folders/14aex0HBP7EtUn6FGLfIoHe3gWmrIDZbI?usp=sharing).
The directory names are the model names. Download the directory of your choice and place it in `models/`.
If you want to change from `wp-355M`, you'll have to edit `play.sh` and `play.ps1` and replace `wp-355M` with your model's name.


The 335M models a just light enough to run on most GPUs (tested on a GTX 980), and are otherwise reasonably fast on CPUs,
while trainable in a Google Colab notebook. I'll start training a 774M model whenever GPUs become affordable again.
* `wp-355M` (default) is best for all kinds of fictional stories. It was tuned on a dataset of 88,147,095 words from r/WritingPrompts comments (>1000 characters only, about 2 years worth of short stories).
* `hfy-355M` (coming soon) is specialized in science-fiction. It was trained on every post from r/HFY (sci-fi short stories where Humanity is the hero).
* `shortstories-355M` (coming soon?) was trained on every post from r/shortstories. It has the same kind of content as r/WritingPrompts, but with fewer stories of (maybe?) higher quality.
* `eve-355M` (coming soon) is an experiment trained on all comments from 01/2020 to 05/2021 and all posts from r/Eve.
* `355M` is the medium-sized vanilla GPT-2 model. It wasn't fine-tuned, so it can write anything, not just stories. Great for experiments, not recommended for stories.
* `774M` is the lage vanilla GPT-2 model. Like `355M`, it wasn't fine-tuned. It produces better outputs but is much slower without a very good GPU.

The reddit datasets were collected using `fine-tuning/scrape.py` which calls the [pushshift API](https://github.com/pushshift/api).

## FAQ
_Does this thing respect my privacy?_

Yes, wrAIter only needs to connect to the internet to download the TTS model and to install python packages. It doesn't upload anything, and only saves stories on your hard drive if you explicitly ask it to. To play sound, the last played wave file is also stored on your machine. Keep in mind that the Colab notebook runs on Google's server, on which they have full control, so I offer no guarantees there.

_How should I write things in a way that the AI understands?_

You aren't in a dialog with an AI, you're just writing parts of a story, except the autocompletion tries to guess the next 60 words. Trying to talk to it will just throw it off. Write as if you were the narrator. Avoid typos, the 355M models don't react well to them (use `/revert` to cancel an input and rewrite it).

_The AI is repeating itself, help!_

There are checks in place to reduce this problem, but they're sometimes unavoidable. Here are a few tips:
* You can switch to choice mode and hit `< more >` until the AI gives you something different.
* You can also try go along with your story with a radical change in the action, ignoring the AI until it catches up with you.
* You can `/revert` back to a point in the story before it started failing.
* If all else fails, just start a new story.

To make this happen less often, try not to be redundant or use the same word twice. GPT-2's whole schtick is to complete sequences, so it tends to latch onto a pattern whenever it sees one.

_Can I write in first person like in AIdungeon?_

No, AIdungeon converts first person to second person before feeding your input to its model, which was trained for second person narration. Writing in first person on wrAIter will probably result in a first person response.

_Does the AI learn from my inputs?_

While the AI remembers the last thousand words of the story, it doesn't learn from it. Playing or saving a story won't affect the way it plays another.

_Does the AI forget parts of the story?_

Yes. Because the model can only take 1024 words in the input, the oldest events can be dropped to make the story fit. However, the context of the story (first paragraph) is never "forgotten".

Until you hit 1024 words, longer stories get progressively better results.

_Can I fine-tune the AI on a corpus of my choice?_

Yes, the `fine-tuning` folder contains a few scripts that should let you do that if you know a bit of python. It's recommended you have at least 50 MB of raw text. Google Colab's servers are powerful enough to train OpenAI's 355M model.



## Credits
* [Latitude](https://github.com/Latitude-Archives/AIDungeon) for AIDungeon that I used as a prototype,
* [OpenAI](https://github.com/openai/gpt-2) for GPT-2,
* [Mozilla](https://github.com/mozilla) for the TTS models.