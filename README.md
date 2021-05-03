![](https://i.imgur.com/GkFedT1.png)

# Model coming soon

wrAIter is an AI that writes stories while letting the user interact and add to the story.
You can write a paragraph, making the AI write the next one, you add another, etc.
Or you can enable "choice mode" and make the AI give you a list of propositions you can chose
from for each paragraph.

The AI writer is powered by OpenAI's GPT-2 model. The included model has 355M parameters
due to hardware constraints (trainable on Colab and runs on a GTX 980),
and was fine-tuned to write fiction.

## Features
* State-of-the-art Artificial Intelligence fine-tuned for a specific purpose.
* A narrator AI that reads the story out loud (TTS).**
* Two modes to build a story: alternating AI-human writing or chosing from AI generated options.
* Save, load, continue and revert functions.
* Randomly generated or custom prompts to start new stories.

** wrAIter's voice feature only works on Windows for now.

## Installation
0. (Optional) Set up CUDA 10.1 to enable hardware acceleration if your GPU can take it (4 GB VRAM).
1. Install python 3.7
2. Download this repository.
3. Run install.ps1 (windows powershell) or install.sh (bash).
4. Download the model [scify-335M](...) (COMING SOON) and place it in `models/`
5. Play by running play.ps1 (windows powershell) or play.sh (bash).


## Credits
* [Latitude](https://github.com/Latitude-Archives/AIDungeon) for AIDungeon that I used as a prototype
* [OpenAI](https://github.com/openai/gpt-2) for GPT-2
* [Mozilla](https://github.com/mozilla) for the TTS models
* [Robin Sloan](https://www.kaggle.com/jannesklaas/scifi-stories-text-corpus) for the fiction dataset