#!/usr/bin/env python3
import json
import os

from generator.gptgenerator import GPTGenerator


class Generator:
    def __init__(self,
                 model_name='gpt-neo-2.7B',
                 seed=None,
                 length=80,
                 temperature=0.85,
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

        self.model_name = model_name
        self.models_dir = models_dir
        self.length = length
        self.top_k = top_k
        self.top_p = top_p
        self.temperature = temperature
        self.rep_penalty = 1.2
        self.rep_penalty_range = 512
        self.rep_penalty_slope = 3.33
        self.max_history = 1024  # max 2048 for gpt neo, 1024 for gpt-2, lower history to reduce (V)RAM usage

        self.generator = GPTGenerator(
                model_path=os.path.join(self.models_dir, self.model_name),
                generate_num=self.length,
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                repetition_penalty=self.rep_penalty,
                repetition_penalty_range=self.rep_penalty_range,
                repetition_penalty_slope=self.rep_penalty_slope,
                max_history=self.max_history,
                gpu=gpu
            )

        self.enc = self.generator.tokenizer

    def __del__(self):
        pass

    def generate(self, prompt: str):
        prompt = '<|endoftext|>' + prompt
        result = self.generator.generate(
            prompt,
            '',
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            repetition_penalty=self.rep_penalty,
            repetition_penalty_range=self.rep_penalty_range,
            repetition_penalty_slope=self.rep_penalty_slope
        )
        return result
