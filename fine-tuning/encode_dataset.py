import gpt_2_simple as gpt2
"""
filenames = ['./data/r_Eve_submissions.txt', './data/r_Eve_comments.txt']
with open('./data/r_Eve.txt', 'w', encoding='utf-8') as outfile:
    for fname in filenames:
        with open(fname, encoding='utf-8') as infile:
            for line in infile:
                outfile.write(line)
"""
gpt2.encode_dataset(file_path='./data/r_HFY_submissions.txt', model_dir='../models',
                    model_name='355M', out_path='data/r_HFY.npz')