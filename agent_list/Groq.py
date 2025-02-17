import os
from groq import Groq
import time
import random
import keys



class Groq4Game:
    def __init__(self, model_name, api_key):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def get_response_text(self, prompt):
        for i in range(10):
            try:
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model=self.model_name,
                    temperature=0.7,
                    # max_tokens=2000
                )
                break
            except Exception as e:
                random_num = random.randint(0, len(keys.groq_api_key_list) - 1)
                self.client = Groq(api_key=keys.groq_api_key_list[random_num])
                print(
                    '!!! An error occur during access Groq API, try for the {} time, use key from {}. '.format(i + 1,
                                                                                                                 random_num),
                    e)
                time.sleep(10 * (i + 1))
        try:
            return response.choices[0].message.content
        except:
            print("Failed to generate content - returning None")
            return f'None - failed to generate content after 10 tries'
