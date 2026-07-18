import os
from openai import OpenAI
from .base import BaseLLMClient

class NvidiaNIMClient(BaseLLMClient):
    # Updated to a live Llama 3.1 endpoint
    def __init__(self, model_name: str = "meta/llama-3.1-8b-instruct"):
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is missing.")
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        self.model_name = model_name

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=1024,
        )
        return response.choices[0].message.content