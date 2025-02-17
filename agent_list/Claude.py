from anthropic import AnthropicVertex
import numpy as np
from .vertex_regions import model_regions
import time


class Claude:
    def __init__(self, model_name, temperature=0, top_k=1, max_output_tokens=1000, 
                 project_id="llmsasagents", default_parameters=True, n_retries=50,
                 retry_wait=5):

        self.model_name = model_name
        self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "top_k": top_k
        }
        self.default_parameters = default_parameters
        self.n_retries = n_retries
        self.model_regions = model_regions
        self.project_id = project_id
        self.retry_wait = retry_wait

    def get_response_text(self, prompt):

        response = None
        try_count = 0
        max_tries = self.n_retries
        while response is None:

            location = np.random.choice(self.model_regions[self.model_name])
            client = AnthropicVertex(region=location, project_id=self.project_id)

            if try_count >= max_tries:
                print("Failed to generate content - returning None")
                return f'None - failed to generate content after {max_tries} tries'
         
            try:
                if self.default_parameters:
                    response = client.messages.create(
                        max_tokens=self.config['max_output_tokens'],
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        model=self.model_name,
                    )
                else:
                    response = client.messages.create(
                        temperature=self.config['temperature'],
                        top_k=self.config['top_k'],
                        max_tokens=self.config['max_output_tokens'],
                        messages=[
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                        model=self.model_name,
                    )
            except:
                print(f'Error in generating content {try_count} try. Trying again...')
                time.sleep(self.retry_wait*try_count)
                try_count += 1
        return response.content[0].text


if __name__ == '__main__':
    claude = Claude('claude-3-5-sonnet@20240620')
    print(claude.get_response_text('Tell me a game theoretic game'))
