"""
llm_sealion.py - SEA-LION Adapter for arifOS v35Ω

Provides SEA-LION (Qwen-SEA-LION or Llama-SEA-LION) integration.
Designed for Google Colab with GPU (A100/T4/V100).

Usage:
    from arifos_core.adapters.llm_sealion import make_llm_generate

    generate = make_llm_generate(model="aisingapore/Qwen2.5-7B-SEA-LIONv3-Instruct")
    response = generate("Apa khabar?")

Note: This adapter supplies RAW intelligence only.
Apply @apex_guardrail at call sites for constitutional governance.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Generator, Optional, List

from ..integration.adapters.llm_interface import (
    LLMConfig,
    LLMInterface,
    StreamChunk,
    estimate_entropy_from_text,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class SEALIONConfig:
    """Configuration for SEA-LION models."""
    # Model selection
    model: str = "aisingapore/Llama-SEA-LION-v3-8B-IT"

    # Generation parameters
    temperature: float = 0.4  # Lower for stability
    top_p: float = 0.9
    max_new_tokens: int = 512
    repetition_penalty: float = 1.15

    # Thinking mode (for Qwen models)
    enable_thinking: bool = False

    # System prompt
    system_prompt: str = """You are SEA-LION, an AI assistant created by AI Singapore.

IMPORTANT RULES:
- You do NOT have a physical body. You cannot eat, sleep, or have physical experiences.
- Be concise, helpful, and honest.
- If you don't know something, say so.
- Never claim to be human or have human experiences."""


# Available SEA-LION models (verified on Hugging Face)
SEALION_MODELS = {
    # Llama-based v3 (recommended for 8B)
    "llama-8b": "aisingapore/Llama-SEA-LION-v3-8B-IT",  # 128k context, instruction-tuned

    # Qwen-based v4 (32B - needs A100)
    "qwen-32b": "aisingapore/Qwen-SEA-LION-v4-32B-IT",
    "qwen-32b-4bit": "aisingapore/Qwen-SEA-LION-v4-32B-IT-4BIT",  # Quantized for less VRAM
    "qwen-32b-8bit": "aisingapore/Qwen-SEA-LION-v4-32B-IT-8BIT",

    # Gemma-based v4 (27B)
    "gemma-27b": "aisingapore/Gemma-SEA-LION-v4-27B-IT",

    # Vision-Language models
    "qwen-8b-vl": "aisingapore/Qwen-SEA-LION-v4-8B-VL",  # Image + Text
    "qwen-4b-vl": "aisingapore/Qwen-SEA-LION-v4-4B-VL",  # Smaller VL model
}


# =============================================================================
# BACKEND CREATION
# =============================================================================

def create_sealion_backend(
    model: str = "aisingapore/Llama-SEA-LION-v3-8B-IT",
    config: Optional[SEALIONConfig] = None,
    device_map: str = "auto",
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a SEA-LION streaming backend.

    Args:
        model: Model ID from Hugging Face
        config: SEALIONConfig for generation parameters
        device_map: Device placement ("auto", "cuda", "cpu")

    Returns:
        Backend function that yields StreamChunks
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        raise ImportError(
            "transformers and torch required: pip install transformers torch accelerate"
        )

    cfg = config or SEALIONConfig(model=model)

    print(f"Loading SEA-LION model: {model}")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)

    # Detect dtype based on GPU availability
    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        print(f"  GPU: {torch.cuda.get_device_name(0)}")
    else:
        dtype = torch.float32
        print("  CPU mode (slower)")

    # Load model
    model_instance = AutoModelForCausalLM.from_pretrained(
        model,
        trust_remote_code=True,
        device_map=device_map,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )

    print("  Model loaded successfully")

    def stream_fn(prompt: str) -> Generator[StreamChunk, None, None]:
        """Generate response as stream of chunks."""
        try:
            # Build messages
            messages = [
                {"role": "system", "content": cfg.system_prompt},
                {"role": "user", "content": prompt},
            ]

            # Apply chat template
            template_kwargs = {"tokenize": False, "add_generation_prompt": True}

            # Enable thinking mode for Qwen models if configured
            if cfg.enable_thinking and "qwen" in model.lower():
                template_kwargs["enable_thinking"] = True

            full_prompt = tokenizer.apply_chat_template(messages, **template_kwargs)

            # Tokenize
            inputs = tokenizer(full_prompt, return_tensors="pt")
            inputs = {k: v.to(model_instance.device) for k, v in inputs.items()}

            # Generate
            with torch.no_grad():
                outputs = model_instance.generate(
                    **inputs,
                    max_new_tokens=cfg.max_new_tokens,
                    temperature=cfg.temperature,
                    top_p=cfg.top_p,
                    repetition_penalty=cfg.repetition_penalty,
                    do_sample=cfg.temperature > 0,
                    pad_token_id=tokenizer.eos_token_id,
                )

            # Decode response
            response = tokenizer.decode(
                outputs[0][inputs["input_ids"].shape[1]:],
                skip_special_tokens=True,
            )

            # Handle thinking mode output
            if cfg.enable_thinking and "</think>" in response:
                # Split thinking from answer
                parts = response.split("</think>")
                if len(parts) > 1:
                    thinking = parts[0].replace("<think>", "").strip()
                    answer = parts[1].strip()

                    # Yield thinking as separate chunk (for transparency)
                    if thinking:
                        yield StreamChunk(
                            text=f"[Thinking: {thinking[:100]}...]\n\n",
                            entropy=estimate_entropy_from_text(thinking),
                        )
                    response = answer

            # Yield response in chunks (simulate streaming)
            words = response.split()
            chunk_size = 5  # Words per chunk

            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words) + " "

                yield StreamChunk(
                    text=chunk_text,
                    entropy=estimate_entropy_from_text(chunk_text),
                )

            yield StreamChunk(text="", finish_reason="stop")

        except Exception as e:
            yield StreamChunk(
                text=f"\n[ERROR] SEA-LION error: {str(e)}",
                finish_reason="error",
            )

    return stream_fn


def make_backend(
    model: str = "aisingapore/Llama-SEA-LION-v3-8B-IT",
    config: Optional[LLMConfig] = None,
    sealion_config: Optional[SEALIONConfig] = None,
) -> Callable[[str], Generator[StreamChunk, None, None]]:
    """
    Create a SEA-LION streaming backend with config.

    Args:
        model: Model ID or shorthand (e.g., "qwen-7b", "llama-8b")
        config: Optional LLMConfig (uses temperature/max_tokens)
        sealion_config: Optional SEALIONConfig for SEA-LION specific settings

    Returns:
        Backend function for LLMInterface
    """
    # Resolve model shorthand
    if model in SEALION_MODELS:
        model = SEALION_MODELS[model]

    # Build SEALIONConfig
    cfg = sealion_config or SEALIONConfig(model=model)

    # Override with LLMConfig if provided
    if config:
        cfg.temperature = config.temperature
        cfg.max_new_tokens = config.max_tokens

    return create_sealion_backend(model=model, config=cfg)


def make_llm_generate(
    model: str = "aisingapore/Llama-SEA-LION-v3-8B-IT",
    config: Optional[LLMConfig] = None,
    sealion_config: Optional[SEALIONConfig] = None,
) -> Callable[[str], str]:
    """
    Create a simple generate function using SEA-LION.

    This wraps the streaming backend with LLMInterface for
    entropy monitoring and SABAR triggers.

    Args:
        model: Model ID or shorthand
        config: Optional LLMConfig
        sealion_config: Optional SEALIONConfig

    Returns:
        Function that takes prompt and returns response text

    Example:
        generate = make_llm_generate("qwen-7b")
        response = generate("Apa khabar?")
    """
    cfg = config or LLMConfig()
    backend = make_backend(model, cfg, sealion_config)

    llm = LLMInterface(config=cfg, backend_fn=backend)

    def generate(prompt: str) -> str:
        response, state = llm.generate(prompt)
        return response

    return generate


# =============================================================================
# HALLUCINATION DETECTION (Level 2.5)
# =============================================================================

def detect_hallucinations(response: str) -> List[str]:
    """
    Detect common SEA-LION hallucination patterns.

    Returns list of detected issues (empty if none).
    """
    issues = []
    response_lower = response.lower()

    # Identity hallucination: "Khabaq SEA-LION" treated as name
    if "khabaq sea-lion" in response_lower or "khabaq sealion" in response_lower:
        if "khabar" not in response_lower and "apa khabar" not in response_lower:
            issues.append("identity_hallucination: treated 'khabaq' as name")

    # Physical body claims
    body_patterns = [
        "saya makan", "aku makan", "baru makan", "dah makan",
        "i ate", "i'm eating", "i eat", "my body", "i feel hungry",
        "saya tidur", "aku tidur", "i sleep", "i slept",
    ]
    for pattern in body_patterns:
        if pattern in response_lower:
            issues.append(f"physical_hallucination: '{pattern}'")
            break

    # Repetition loop detection
    sentences = re.split(r'[.!?]+', response)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if len(sentences) > 3:
        for s in sentences:
            if sentences.count(s) > 2:
                issues.append(f"repetition_loop: '{s[:30]}...'")
                break

    # Arrogance/certainty (Omega drift)
    arrogance_patterns = ["100%", "pasti", "definitely", "absolutely certain", "no doubt"]
    for pattern in arrogance_patterns:
        if pattern in response_lower:
            issues.append(f"omega_drift: '{pattern}'")
            break

    return issues


__all__ = [
    "SEALIONConfig",
    "SEALION_MODELS",
    "create_sealion_backend",
    "make_backend",
    "make_llm_generate",
    "detect_hallucinations",
]
