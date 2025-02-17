# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import vertexai
from vertexai.generative_models import GenerativeModel
import vertexai.preview.generative_models as generative_models
import time
import numpy as np
from .vertex_regions import model_regions


class Vertex:

    def __init__(self, model_name, temperature=0, top_k=1, max_output_tokens=1000,
                 project_id = "llmsasagents", default_parameters=True, n_retries=50,
                 retry_wait=5):
      
        self.model_name = model_name
        self.project_id = project_id
        self.model_regions = model_regions
        if default_parameters:
            self.config = {
            "max_output_tokens": max_output_tokens}
        else:
            self.config = {
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "top_k": top_k
            }
        self.model = GenerativeModel(model_name)
        self.default_parameters = default_parameters
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    def get_response_text(self, prompt):

        response = None
        # overcome false positive safety blocks
        safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        try_count = 0
        max_tries = self.n_retries
        while response is None:

            region = np.random.choice(self.model_regions[self.model_name])
            vertexai.init(project=self.project_id, location=region)

            if try_count >= max_tries:
                print("Failed to generate content - returning None")
                return f'None - failed to generate content after {max_tries} tries'
            
            try:
                response = self.model.generate_content(contents=[prompt],
                                        generation_config=self.config,
                                        safety_settings=safety_settings)
                # catch recitation error bug
                if response.candidates[0].finish_reason == '<FinishReason.RECITATION: 4>':
                    print('Caught recitation error')
                    return 'None - recitation error'
                try:
                    response.text
                except Exception as e:
                    # Print the type of exception and the error message
                    print(f"An exception occurred: {type(e).__name__}")
                    print(f"Error message: {e}")
                    # print error message
                    print(f"Error in generating content Inner loop. Trying again up to {max_tries - try_count} times ")
                    print(f'Response: {response}')
                    #time.sleep(5)
                    try_count += 1
                    response = None  # reset response
            except Exception as e:
                # Print the type of exception and the error message
                print(f"An exception occurred: {type(e).__name__}")
                print(f"Error message: {e}")
                # print error message
                print(f"Error in generating content Outer loop. Trying again up to {max_tries - try_count} times - returning None")
                # Sleep for 5 seconds before trying again
                time.sleep(self.retry_wait)
                try_count += 1

        # extra check for response.text
        try:
            try:
                return response.text
            except:
                return ' '.join([part.text for part in response.candidates[0].content.parts])
        except Exception as e:
            print(f"An exception occurred before return: {type(e).__name__}")
            print(f"Error message: {e}")
            return 'None - failed to generate content'


if __name__ == '__main__':
    PROJECT_ID = "llmsasagents"
    vertexai.init(project=PROJECT_ID)

    model = "gemini-pro-experimental"
    generative_model = GenerativeModel("gemini-1.5-pro-preview-0514")
    response = generative_model.generate_content(["What is mostly funny"])

    print(response.text)

    agent = Vertex(model_name="gemini-1.5-pro-preview-0514", PROJECT_ID=PROJECT_ID)
    prompt = "What is mostly funny"
    response = agent.get_response_text(prompt)
    print(response)
