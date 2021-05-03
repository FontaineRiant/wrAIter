import os
import requests
from tqdm import tqdm
import gpt_2_simple as gpt2

model_name = "355M"
sess = gpt2.start_tf_sess()

model = model_name

subdir = os.path.join('models', model)
if not os.path.exists(subdir):
    os.makedirs(subdir)
#subdir = subdir.replace('\\','/') # needed for Windows

for filename in ['checkpoint','encoder.json','hparams.json','model.ckpt.data-00000-of-00001', 'model.ckpt.index', 'model.ckpt.meta', 'vocab.bpe']:

    r = requests.get("https://openaipublic.blob.core.windows.net/gpt-2/" + subdir + "/" + filename, stream=True)

    with open(os.path.join(subdir, filename), 'wb') as f:
        file_size = int(r.headers["content-length"])
        chunk_size = 1000
        with tqdm(ncols=100, desc="Fetching " + filename, total=file_size, unit_scale=True) as pbar:
            # 1k for chunk_size, since Ethernet packet size is around 1500 bytes
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                pbar.update(chunk_size)

file_name = "./data/data.npz"

batch_size = 8
learning_rate = 0.0001
steps = 8000

sess = gpt2.start_tf_sess()
gpt2.finetune(
    sess,
    file_name,
    multi_gpu=False,
    batch_size=batch_size,
    learning_rate=learning_rate,
    model_name=model_name,
    sample_every=10000,
    max_checkpoints=2,
    save_every=2000,
    steps=steps, # 1000,
    sample_length=100,
    overwrite=True
)

gpt2.generate(sess)

gpt2.generate(sess)