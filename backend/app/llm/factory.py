from .gemini_client import GeminiClient
from .nvidia_client import NvidiaNIMClient

def get_llm_client(provider: str):
    """
    Returns the appropriate LLM client based on the provider string.
    """
    provider = provider.strip().lower()
    if provider == "nvidia":
        return NvidiaNIMClient()
    
    # Default to Gemini
    return GeminiClient()