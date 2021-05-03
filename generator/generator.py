#!/usr/bin/env python3
import json
import os

import numpy as np
import tensorflow as tf

from generator import model
from generator import sample
from generator import encoder


class Generator:
    def __init__(self,
                 model_name='sf-355M',
                 seed=None,
                 nsamples=1,
                 batch_size=1,
                 length=60,
                 temperature=0.4,
                 top_k=40,
                 top_p=0.9,
                 models_dir='models',
                 gpu=True):
        """
        :model_name=355M : String, which model to use
        :seed=None : Integer seed for random number generators, fix seed to reproduce
         results
        :nsamples=1 : Number of samples to return total
        :batch_size=1 : Number of batches (only affects speed/memory).  Must divide nsamples.
        :length=None : Number of tokens in generated text, if None (default), is
         determined by model hyperparameters
        :temperature=1 : Float value controlling randomness in boltzmann
         distribution. Lower temperature results in less random completions. As the
         temperature approaches zero, the model will become deterministic and
         repetitive. Higher temperature results in more random completions.
        :top_k=0 : Integer value controlling diversity. 1 means only 1 word is
         considered for each step (token), resulting in deterministic completions,
         while 40 means 40 words are considered at each step. 0 (default) is a
         special setting meaning no restrictions. 40 generally is a good value.
         :models_dir : path to parent folder containing model subfolders
         (i.e. contains the <model_name> folder)
        """

        assert nsamples % batch_size == 0

        self.model_name = model_name
        self.models_dir = models_dir
        self.nsamples = nsamples
        self.batch_size = batch_size
        self.length = length
        self.enc = encoder.get_encoder(self.model_name, self.models_dir)

        hparams = model.default_hparams()
        with open(os.path.join(models_dir, model_name, 'hparams.json')) as f:
            hparams.override_from_dict(json.load(f))

        if length is None:
            length = hparams.n_ctx // 2
        elif length > hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

        config = tf.compat.v1.ConfigProto()
        if not gpu:
            # disable GPU cause it isn't fat enough
            config = tf.compat.v1.ConfigProto(
                device_count={'CPU': 1, 'GPU': 0},
                allow_soft_placement=True,
                log_device_placement=False)

        self.sess = tf.compat.v1.Session(config=config)
        self.context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
        self.output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=self.context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join(models_dir, model_name))
        saver.restore(self.sess, ckpt)

    def __del__(self):
        self.sess.close()

    def generate(self, prompt: str):
        context_tokens = self.enc.encode(prompt)
        generated = 0
        for _ in range(self.nsamples // self.batch_size):
            out = self.sess.run(self.output, feed_dict={
                self.context: [context_tokens for _ in range(self.batch_size)]
            })[:, len(context_tokens):]
            for i in range(self.batch_size):
                generated += 1
                text = self.enc.decode(out[i])
                return text
