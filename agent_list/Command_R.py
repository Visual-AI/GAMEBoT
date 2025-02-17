import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from beartype import beartype


class Command_R:

    @beartype
    def __init__(self, model_name: str, temperature: float = 0.0, max_output_tokens: int = 1000,
                 ) -> None:
        torch.random.manual_seed(0)

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        self.model_name = model_name

    @beartype
    def get_response_text(self, prompt: str) -> str:
        # Format message with the command-r-plus chat template
        messages = [{"role": "user", "content": prompt}]
        input_ids = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True,
                                                       return_tensors="pt")
        ## <BOS_TOKEN><|START_OF_TURN_TOKEN|><|USER_TOKEN|>Hello, how are you?<|END_OF_TURN_TOKEN|><|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>

        gen_tokens = self.model.generate(
            input_ids,
            max_new_tokens=self.config['max_output_tokens'],
            do_sample=False,
            temperature=self.config['temperature'],
        )

        gen_text = self.tokenizer.decode(gen_tokens[0])

        return gen_text


if __name__ == '__main__':
    # models = ["meta/llama3-405b-instruct-maas", ]

    commandr = Command_R('CohereForAI/c4ai-command-r-plus')
    print(commandr.get_response_text('Tell me about the history of the Roman Empire'))