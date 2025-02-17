import reka
from reka import ChatMessage
from reka.client import Reka as RekaClient
from beartype import beartype
import time


class Reka:

    @beartype
    def __init__(self, model_name: str, api_key: str, temperature: float=0.0, 
                 max_output_tokens: int=1000, seed: int=42, default_parameters: bool=True,
                 n_retries: int=50, retry_wait: int=5) -> None:

        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.seed = seed
        self.api_key = api_key
        self.default_parameters = default_parameters
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    @beartype
    def get_response_text(self, prompt: str) -> str:

        if self.default_parameters:
            gen_kwargs = dict(max_tokens=self.max_output_tokens) 
        else:
            gen_kwargs = dict(temperature=self.temperature, 
                          max_tokens=self.max_output_tokens, 
                          seed=self.seed)

        client = RekaClient(api_key=self.api_key, timeout=120)

        response = None
        try_count = 0
        max_tries = self.n_retries
        while response is None:

            if try_count >= max_tries:
                print("Failed to generate content - returning None")
                return f'None - failed to generate content after {max_tries} tries'

            try:
                response = client.chat.create(
                    messages=[
                        ChatMessage(
                            role="user",
                            content=[
                                {
                                    "type": "text",
                                    "text": prompt,
                                }
                            ],
                        )
                    ],
                    model=self.model_name,
                    **gen_kwargs
                )
                return response.responses[0].message.content
            except reka.core.ApiError as e:  # Handle all errors
                print(e.status_code)
                print(e.body)
                time.sleep(self.retry_wait*try_count)
                try_count += 1

        print('Error, returning None')
        return ''


if __name__ == '__main__':
    import keys
    model_name = 'reka-flash'
    agent = Reka(model_name=model_name, api_key=keys.reka_key)
    prompt = 'What is the meaning of life?'
    response = agent.get_response_text(prompt)
    print(response)
