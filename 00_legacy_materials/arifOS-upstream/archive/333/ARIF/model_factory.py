import os
from smolagents import LiteLLMModel


def get_arif_model():
    """
    Returns the canonical arifOS model (The Mind's Engine).
    Defaults to LiteLLMModel pointing to local Ollama if ARIFOS_ENV is local,
    otherwise uses the configured backend.
    """

    # Use environment variables if set, otherwise default to local ollama llama3.2
    model_id = os.getenv("ARIFOS_MODEL_ID", "ollama/llama3.2")
    api_base = os.getenv("OLLAMA_URL", "http://localhost:11434")

    # Append /v1 for OpenAI compatibility if using litellm with ollama
    if "ollama" in model_id and not api_base.endswith("/v1"):
        api_base = f"{api_base}/v1"

    return LiteLLMModel(
        model_id=model_id,
        api_base=api_base,
        api_key="none",  # Ollama doesn't require keys for local use
    )
