![](https://i.imgur.com/wbxNBBA.png)

wrAIter is a voiced AI that writes stories while letting the user interact and add to the story.
You can write a paragraph, making the AI write the next one, you add another, etc.
Or you can enable "choice mode" and let the AI make suggestions you can pick
from for each paragraph.

The AI writer is powered by OpenAI's GPT-2 model. The included model has 355M parameters,
and was fine-tuned to write science fiction.

## Features
* Play in Colab or locally
* State-of-the-art Artificial Intelligence fine-tuned for the specific purpose of writing stories
* A high quality narrator AI that reads the story out loud (TTS)**
* Two modes to build a story: alternating AI-human writing or chosing from AI generated options
* Save, load, continue and revert functions
* Randomly generated or custom prompts to start new stories

** wrAIter's voice feature only works on Windows for now, and definitely won't be available in Colab.

![](https://i.imgur.com/bOSnLJi.png)

## Local installation
0. (Optional) Set up CUDA 10.1 to enable hardware acceleration if your GPU can take it (4 GB VRAM).
1. Install python 3.7
2. Download or clone this repository.
3. Run `install.ps1` (windows powershell) or `install.sh` (shell script).
4. Download a [model](https://drive.google.com/drive/folders/14aex0HBP7EtUn6FGLfIoHe3gWmrIDZbI?usp=sharing) (see next section) and place it in `models/`
5. Play by running `play.ps1` (windows powershell) or `play.sh` (shell script).

## Play on Google Colab
1. Go the wrAIter's [Colab notebook](https://colab.research.google.com/drive/1Bk0_cPV5M61TWWslDw-nNjmtGG3nBF4W?usp=sharing)
2. Runtime > Run all (ctrl+F9)
3. Wait a couple of minutes for the main menu to appear in the last cell.


## Models
Pretrained models are available [here](https://drive.google.com/drive/folders/14aex0HBP7EtUn6FGLfIoHe3gWmrIDZbI?usp=sharing).
The directory names are the model names. Download the directory of your choice and place it in `models/`.
If you want to change from `scifi-355M`, you'll have to edit `play.sh` and `play.ps1` and replace `scifi-355M` with your model's name.


The 335M models a just light enough to run on most GPUs (tested on a GTX 980), and are otherwise reasonably fast on CPUs,
while trainable in a Google Colab notebook.
* `scifi-355M (TODO)` (recommended) is tuned on [Robin Sloan's](https://www.kaggle.com/jannesklaas/scifi-stories-text-corpus) science-fiction dataset.
* `355M` is the medium-sized vanilla GPT-2 model. It wasn't fine-tuned, so it can write anything, not just stories. Great for experiments, not recommended for stories.
* `774M` is the lage vanilla GPT-2 model. Like `355M`, it wasn't fine-tuned. It produces better outputs but is much slower without a very good GPU.


## Credits
* [Latitude](https://github.com/Latitude-Archives/AIDungeon) for AIDungeon that I used as a prototype,
* [OpenAI](https://github.com/openai/gpt-2) for GPT-2,
* [Mozilla](https://github.com/mozilla) for the TTS models,
* [Robin Sloan](https://www.kaggle.com/jannesklaas/scifi-stories-text-corpus) for the fiction dataset.