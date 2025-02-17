import sys
# sys.path.append("/home/wylin/LLM4Game")

# import keys
import time
from volcenginesdkarkruntime import Ark
import httpx


class DeepSeekR1:
    def __init__(self, api_key):
        self.client = Ark(
            api_key=api_key,
            timeout=httpx.Timeout(timeout=1800)
        )

    def get_response_text(self, prompt):
        for i in range(3):
            try:
                response = self.client.chat.completions.create(
                    model="ep-20250215152119-h9lfv",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    stream=True  # Using streaming by default as in the original code
                )

                # Accumulate the streamed response
                reason_response = ""
                answer_response = ""
                for chunk in response:
                    if not chunk.choices:
                        continue
                    if chunk.choices[0].delta.reasoning_content:
                        reason_response += chunk.choices[0].delta.reasoning_content
                    else:
                        answer_response += chunk.choices[0].delta.content

                return reason_response+'\n'+answer_response

            except Exception as e:
                print(
                    f'!!! An error for bytedance API, try for the {i + 1} time',
                    e
                )
                time.sleep(5)

        return f'None - failed to generate content after 3 tries'
