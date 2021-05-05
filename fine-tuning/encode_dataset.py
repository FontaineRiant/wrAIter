import gpt_2_simple as gpt2

filenames = ['./data/r_Eve_comments.txt', './data/r_Eve_submissions.txt']
with open('./data/r_Eve.txt', 'w') as outfile:
    for fname in filenames:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)

gpt2.encode_dataset(file_path='./data/r_Eve.txt', model_dir='models', model_name='355M', out_path='data/r_Eve.npz')