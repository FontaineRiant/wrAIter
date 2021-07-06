"""
Use this script to encode the dataset to npz. It isn't a necessary step, but Colab
doesn't have much RAM to do it, so you might have to encode a big dataset on your
local machine before uploading it for fine-tuning. It reduces txt files to about
30% of their original size.
"""

import gpt_2_simple as gpt2
"""
# merge txt files if needed
filenames = ['./data/r_Eve_submissions.txt', './data/r_Eve_comments.txt']
with open('./data/r_Eve.txt', 'w', encoding='utf-8') as outfile:
    for fname in filenames:
        with open(fname, encoding='utf-8') as infile:
            for line in infile:
                outfile.write(line)
"""


gpt2.encode_dataset(file_path='./data/r_HFY_submissions.txt', model_dir='../models',
                    model_name='774M', out_path='data/r_HFY.npz')