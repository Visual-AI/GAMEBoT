from beartype import beartype
from ai21 import AI21VertexClient
from ai21.models.chat import ChatMessage
import numpy as np
from .vertex_regions import model_regions
from google.auth import default
from google.auth.transport.requests import Request
import os
import time


class Jamba:

    @beartype
    def __init__(self, model_name: str, temperature: float=0.0, max_output_tokens: int=1000,
                 project_id: str="llmsasagents", default_parameters: bool=True, n_retries: int=50,
                 retry_wait: int=5) -> None:

        region = np.random.choice(model_regions[model_name])
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        credentials, _ = default()
        credentials.refresh(Request())

        self.client = AI21VertexClient(region=region, project_id=project_id, credentials=credentials)
        self.model_name = model_name
        # self.model_version = "001"
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
        }
        self.default_parameters = default_parameters
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    @beartype
    def get_response_text(self, prompt: str) -> str:

        response = None
        try_count = 0
        max_tries = 10
        while response is None:

            if try_count >= max_tries:
                print("Failed to generate content - returning None")
                return f'None - failed to generate content after {max_tries} tries'

            try:
                messages = ChatMessage(content=prompt, role="user")
                if self.default_parameters:
                    response = self.client.chat.completions.create(
                        model = f"{self.model_name}",#-{self.model_version}",
                        messages=[messages],
                        max_tokens=self.config['max_output_tokens'],
                    )
                else:
                    response = self.client.chat.completions.create(
                        model = f"{self.model_name}",#-{self.model_version}",
                        messages=[messages],
                        max_tokens=self.config['max_output_tokens'],
                        temperature=self.config['temperature'],
                        #stream=True
                    )
            except:
                print(f'Error in generating content {try_count} try. Trying again...')
                time.sleep(self.retry_wait*try_count)
                try_count += 1

        return response.choices[0].message.content


if __name__ == '__main__':
    jamba = Jamba('jamba-1.5-large')
    print(jamba.get_response_text('Tell me about the history of the Roman Empire'))
