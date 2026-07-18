import os
from google import genai
from google.genai import types
from .base import BaseLLMClient

class GeminiClient(BaseLLMClient):
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        # The client automatically picks up GEMINI_API_KEY from the environment
        self.client = genai.Client()
        self.model_name = model_name

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
            )
        )
        return response.text