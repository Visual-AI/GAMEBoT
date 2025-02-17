import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from beartype import beartype


class Phi:

    @beartype
    def __init__(self, model_name: str, temperature: float=0.0, max_output_tokens: int=1000,
                 default_parameters: bool=True) -> None:
        torch.random.manual_seed(0)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype="auto",
            trust_remote_code=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
        )
        self.pipe = pipe
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        self.model_name = model_name
        self.default_parameters = default_parameters

    @beartype
    def get_response_text(self, prompt: str) -> str:
        if self.default_parameters:
            generation_args = { 
                "max_new_tokens": self.config['max_output_tokens'], 
                "return_full_text": False, 
                #"te    mperature": self.config['temperature'], 
                #"do_sample": False, 
            }
        else:
            generation_args = { 
                "max_new_tokens": self.config['max_output_tokens'], 
                "return_full_text": False, 
                #"temperature": self.config['temperature'], 
                "do_sample": False, 
            } 
        messages = [
            {"role": "user", "content": prompt},
        ]

        output = self.pipe(messages, **generation_args)

        return output[0]['generated_text']


if __name__ == '__main__':
    phi3_5 = Phi('microsoft/Phi-3.5-mini-instruct')
    print(phi3_5.get_response_text('Tell me about the history of the Roman Empire'))
