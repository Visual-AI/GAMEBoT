import vertexai
from google.auth import default, transport
import openai
from beartype import beartype
from .vertex_regions import model_regions
import numpy as np
import time


class LLaMA3_1:

    @beartype
    def __init__(self, model_name: str, temperature: float=0.0, max_output_tokens: int=1000,
                 project_id: str="llmsasagents", default_parameters: bool=True, n_retries=50,
                 retry_wait=5) -> None:
        
        region = np.random.choice(model_regions[model_name])

        # fix name: replace meta-llama3 with meta/llama3
        model_name = model_name.replace('meta-llama3', 'meta/llama3')
        # region = "us-central1"
        vertexai.init(project=project_id, location=region)

        credentials, _ = default()
        auth_request = transport.requests.Request()
        credentials.refresh(auth_request)
        client = openai.OpenAI(
            base_url=f"https://{region}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{region}/endpoints/openapi/chat/completions?",
            api_key=credentials.token,
        )
        self.client = client
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        self.model_name = model_name
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
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                        #temperature=0.0,
                        max_tokens=self.config['max_output_tokens'],
                        stream=False
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "user", "content": prompt},
                        ],
                        temperature=self.config['temperature'],
                        max_tokens=self.config['max_output_tokens'],
                        stream=False
                    )
            except:
                print(f'Error in generating content {try_count} try. Trying again...')
                time.sleep(self.retry_wait*try_count)
                try_count += 1

        return response.choices[0].message.content


if __name__ == '__main__':
    # models = ["meta/llama3-405b-instruct-maas", ]

    llama3_1 = LLaMA3_1('meta/llama3-405b-instruct-maas')
    print(llama3_1.get_response_text('Tell me about the history of the Roman Empire'))
