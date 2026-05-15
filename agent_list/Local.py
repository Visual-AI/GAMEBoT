import os
import time

import requests
from openai import OpenAI


class OllamaLocal:
    def __init__(
        self,
        model_name,
        base_url=None,
        temperature=0.0,
        max_output_tokens=4096,
        n_retries=6,
        retry_wait=5,
    ):
        self.model_name = model_name
        self.base_url = (base_url or os.environ.get("GAMEBOT_OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    def get_response_text(self, prompt):
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_output_tokens,
            },
        }
        last_error = None
        for i in range(self.n_retries):
            try:
                response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=600)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            except Exception as e:
                last_error = e
                print(f"Request failed for Ollama local model: {e}")
                time.sleep(self.retry_wait * (i + 1))
        return f"None - failed to generate content after {self.n_retries} tries: {last_error}"


class OpenAICompatibleLocal:
    def __init__(
        self,
        model_name,
        base_url=None,
        api_key=None,
        temperature=0.0,
        max_output_tokens=4096,
        n_retries=6,
        retry_wait=5,
    ):
        self.model_name = model_name
        self.client = OpenAI(
            base_url=base_url or os.environ.get("GAMEBOT_OPENAI_BASE_URL") or "http://127.0.0.1:8000/v1",
            api_key=api_key or os.environ.get("GAMEBOT_OPENAI_API_KEY") or "EMPTY",
        )
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.n_retries = n_retries
        self.retry_wait = retry_wait

    def get_response_text(self, prompt):
        last_error = None
        for i in range(self.n_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_output_tokens,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                print(f"Request failed for OpenAI-compatible local model: {e}")
                time.sleep(self.retry_wait * (i + 1))
        return f"None - failed to generate content after {self.n_retries} tries: {last_error}"
