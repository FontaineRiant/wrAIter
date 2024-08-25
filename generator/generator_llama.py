from llama_cpp import Llama

class Generator:
    def __init__(self,
                 model_name,
                 gpu=True):
        """
        :model_name='KoboldAI/OPT-2.7B-Nerys-v2' : String, which model to use from huggingface
        :gpu: use gpu (default: True)
        :precision: floating point precision
        :offload_to_memory: stores the model in memory when not in use (eat loads of RAM but saves vram)
        """
        self.device = 'cuda' if gpu else 'cpu'

        self.model = Llama.from_pretrained(model_name, filename='*F16.gguf',
                                           verbose=False,
                                           n_gpu_layers=-1 if gpu else 0)

        self.enc = self.model.tokenizer_

    def generate(self, prompt: str, length, stream=True, eos_tokens=[]):

        print('\033[96m', end='')
        try:
            text = []
            for c in self.model.create_completion(
                    prompt,
                    stream=True,
                    max_tokens=length,
                    repeat_penalty=1.05,
                    stop=eos_tokens
                ):
                t = c['choices'][0]['text']
                if stream:
                    print(t, end='', flush=True)
                text.append(t)
            text = ''.join(text)
        except KeyboardInterrupt:
            raise
        finally:
            print('\033[00m', end='')
        return text
