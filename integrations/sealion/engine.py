"""
SEA-LION Engine Response Extraction Module

Provides robust extraction of model responses from various chat formats:
- ChatML (Qwen) format
- Llama/Mistral format
- ### Response: format
- [INST] format

Version: v42.0.0
"""

import re
from typing import Optional


def extract_response_robust(raw_output: Optional[str]) -> str:
    """
    Extract the clean response from various LLM output formats.

    Handles:
    - ChatML format (Qwen): <|im_start|>assistant\n...<|im_end|>
    - Llama format: User: ...\nAssistant: ...
    - Response tag format: ### Response:\n...
    - INST format: [INST] ... [/INST] ...

    Args:
        raw_output: Raw model output string

    Returns:
        Clean response string with special tokens stripped
    """
    if raw_output is None or raw_output == "":
        return ""

    text = raw_output.strip()

    # ChatML format (Qwen) - most specific first
    chatml_pattern = r"<\|im_start\|>assistant\s*\n?(.*?)(?:<\|im_end\|>|$)"
    chatml_match = re.search(chatml_pattern, text, re.DOTALL)
    if chatml_match:
        response = chatml_match.group(1).strip()
        # Strip any remaining ChatML tokens
        response = re.sub(r"<\|im_(?:start|end)\|>", "", response)
        return response.strip()

    # Llama/Mistral format: User: ... Assistant: ...
    llama_pattern = r"(?:User|Human):\s*.*?\s*(?:Assistant|AI):\s*(.*?)$"
    llama_match = re.search(llama_pattern, text, re.DOTALL | re.IGNORECASE)
    if llama_match:
        return llama_match.group(1).strip()

    # Response tag format: ### Response: ...
    response_tag_pattern = r"###\s*Response:\s*(.*?)(?:###|$)"
    response_match = re.search(response_tag_pattern, text, re.DOTALL)
    if response_match:
        return response_match.group(1).strip()

    # INST format: [INST] ... [/INST] response
    inst_pattern = r"\[INST\].*?\[/INST\]\s*(.*?)$"
    inst_match = re.search(inst_pattern, text, re.DOTALL)
    if inst_match:
        return inst_match.group(1).strip()

    # No recognized format - return as-is (but strip special tokens)
    text = re.sub(r"<\|[^|]+\|>", "", text)
    return text.strip()


def strip_special_tokens(text: str) -> str:
    """
    Strip common special tokens from text.

    Args:
        text: Input text

    Returns:
        Text with special tokens removed
    """
    # ChatML tokens
    text = re.sub(r"<\|im_(?:start|end)\|>", "", text)
    # Other common tokens
    text = re.sub(r"<\|(?:eos|bos|pad)\|>", "", text)
    text = re.sub(r"<s>|</s>", "", text)
    return text.strip()


__all__ = [
    "extract_response_robust",
    "strip_special_tokens",
]
