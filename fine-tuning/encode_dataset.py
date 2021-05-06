import gpt_2_simple as gpt2
"""
filenames = ['./data/r_shortstories_submissions.txt', './data/r_HFY_submissions.txt']
with open('./data/r_HFY_shortstories.txt', 'w', encoding='utf-8') as outfile:
    for fname in filenames:
        with open(fname, encoding='utf-8') as infile:
            for line in infile:
                outfile.write(line)
"""
gpt2.encode_dataset(file_path='./data/r_WritingPrompts_comments.txt', model_dir='../models',
                    model_name='355M', out_path='data/r_WritingPrompts.npz')