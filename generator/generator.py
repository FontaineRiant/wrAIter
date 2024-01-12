from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class Generator:
    def __init__(self,
                 model_name='KoboldAI/OPT-2.7B-Nerys-v2',
                 length=80,
                 gpu=True,
                 precision=16):
        """
        :model_name='KoboldAI/OPT-2.7B-Nerys-v2' : String, which model to use from huggingface
        :length=None : Number of tokens in generated text
        :gpu: use gpu (default: True)
        """
        self.device = 'cuda' if gpu else 'cpu'

        if precision == 16:
            self.model = AutoModelForCausalLM.from_pretrained(model_name,torch_dtype=torch.float16 if gpu else torch.float32)
            self.model.to(self.device)
        elif precision == 8:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, load_in_8bit=gpu)
        elif precision == 4:
            self.model = AutoModelForCausalLM.from_pretrained(model_name, load_in_4bit=gpu)
        else:
            raise ValueError(f'float precision {precision} not supported')

        self.enc = AutoTokenizer.from_pretrained(model_name)

        self.length = length
        self.max_history = self.model.config.max_position_embeddings - self.length

    def __del__(self):
        pass

    def generate(self, prompt: str):
        model_inputs = self.enc([prompt], return_tensors='pt').to(self.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=self.length,
            do_sample=True,
            use_cache=True,
        )

        return self.enc.batch_decode(generated_ids[:, model_inputs['input_ids'].shape[1]:])[0]
