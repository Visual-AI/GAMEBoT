from .vertex_regions import model_regions
from beartype import beartype
import numpy as np
from mistralai_gcp import MistralGoogleCloud
import time


class Mistral:

    @beartype
    def __init__(self, model_name: str, temperature: float=0.0, max_output_tokens: int=100,
                 project_id: str="llmsasagents", seed: int=42, model_version: str="2407", 
                 default_parameters: bool=True, n_retries=50, retry_wait=5) -> None:
        region = np.random.choice(model_regions[model_name])

        self.client = MistralGoogleCloud(region=region, project_id=project_id)
        self.model_name = model_name
        self.model_version = model_version
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "random_seed": seed
        }
        self.default_parameters = default_parameters
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    @beartype
    def get_response_text(self, prompt: str) -> str:

        response = None
        try_count = 0
        max_tries = self.n_retries
        while response is None:

            if try_count >= max_tries:
                print("Failed to generate content - returning None")
                return f'None - failed to generate content after {max_tries} tries'
            
            try:

                if self.default_parameters:
                    response = self.client.chat.complete(
                        model = f"{self.model_name}-{self.model_version}",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        max_tokens=self.config['max_output_tokens'],
                        stream=False
                    )
                else:

                    response = self.client.chat.complete(
                        model = f"{self.model_name}-{self.model_version}",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        temperature=self.config['temperature'],
                        max_tokens=self.config['max_output_tokens'],
                        random_seed=self.config['random_seed'],
                        stream=True
                    )
            except:
                print(f'Error in generating content {try_count} try. Trying again...')
                time.sleep(self.retry_wait*try_count)
                try_count += 1

        return response.choices[0].message.content


if __name__ == '__main__':
    mistral = Mistral('mistral-large')
    print(mistral.get_response_text('Tell me about the history of the Roman Empire'))