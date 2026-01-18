"""
AAA-Level Helpers: LLM Generation ⊥ Quantum Validation

Orthogonality Principle:
- LLM generates text (EXTERNAL to quantum system)
- Quantum executor validates text (INDEPENDENT measurement)
- dot_product(LLM, Quantum) = 0

This is NOT part of the quantum executor.
This is a CONVENIENCE wrapper for the common pattern:
1. Generate text with LLM
2. Validate with quantum executor
3. Use if SEAL

Authority: v47 Quantum Architecture - Option A (Separate Concerns)
Implementation: Engineer (Ω)
Date: 2026-01-17
"""

import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from datetime import datetime, timezone

from .orthogonal_executor import OrthogonalExecutor, QuantumState


# =============================================================================
# AAA-LEVEL: Async LLM + Quantum Validation
# =============================================================================

async def generate_and_validate_async(
    query: str,
    llm_generate: Optional[Callable] = None,
    llm_model: str = "gpt-4o-mini",
    llm_messages: Optional[List[Dict[str, str]]] = None,
    context: Optional[Dict[str, Any]] = None,
    **llm_kwargs
) -> Tuple[str, QuantumState]:
    """
    AAA-level: Generate LLM response + validate constitutionally (async).

    Architecture (Orthogonal):
    1. LLM generates text (EXTERNAL - your responsibility)
    2. Quantum validates text (INDEPENDENT - quantum's responsibility)
    3. You decide what to do with the result

    Args:
        query: User query or prompt
        llm_generate: Optional custom LLM function (async). If None, uses litellm.
        llm_model: Model name (default: gpt-4o-mini)
        llm_messages: Custom messages. If None, uses [{"role": "user", "content": query}]
        context: Additional context for quantum validation
        **llm_kwargs: Extra kwargs for LLM (temperature, max_tokens, etc.)

    Returns:
        Tuple[str, QuantumState]: (generated_text, quantum_validation_state)

    Example:
        >>> draft, state = await generate_and_validate_async(
        ...     query="What is 2+2?",
        ...     llm_model="gpt-4o-mini"
        ... )
        >>> if state.final_verdict == "SEAL":
        ...     print(draft)
        ... else:
        ...     print(f"Blocked: {state.apex_particle.verdict}")

    Constitutional Compliance:
        F10 (Ontology): ✅ Quantum measures EXTERNAL text (not self-generated)
        F6 (Amanah): ✅ Can swap LLM without touching quantum code
        F4 (ΔS): ✅ Single responsibility (LLM ⊥ Quantum)
    """

    # Step 1: Generate text (LLM responsibility - EXTERNAL)
    if llm_generate is not None:
        # Custom LLM function provided
        draft = await llm_generate(query, **llm_kwargs)
    else:
        # Use litellm (default)
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "litellm not installed. Install with: pip install litellm\n"
                "Or provide custom llm_generate function."
            )

        messages = llm_messages or [{"role": "user", "content": query}]
        response = await litellm.acompletion(
            model=llm_model,
            messages=messages,
            **llm_kwargs
        )
        draft = response.choices[0].message.content

    # Step 2: Validate constitutionally (Quantum responsibility - INDEPENDENT)
    executor = OrthogonalExecutor()
    validation_context = context or {}
    validation_context["draft_response"] = draft
    validation_context["llm_model"] = llm_model
    validation_context["generation_time"] = datetime.now(timezone.utc).isoformat()

    state = await executor.execute_parallel(query=query, context=validation_context)

    # Step 3: Return both (your decision - APPLICATION)
    return draft, state


def generate_and_validate_sync(
    query: str,
    llm_generate: Optional[Callable] = None,
    llm_model: str = "gpt-4o-mini",
    llm_messages: Optional[List[Dict[str, str]]] = None,
    context: Optional[Dict[str, Any]] = None,
    **llm_kwargs
) -> Tuple[str, QuantumState]:
    """
    AAA-level: Generate LLM response + validate constitutionally (sync).

    Same as generate_and_validate_async, but synchronous wrapper.

    Args:
        query: User query or prompt
        llm_generate: Optional custom LLM function (sync). If None, uses litellm.
        llm_model: Model name (default: gpt-4o-mini)
        llm_messages: Custom messages. If None, uses [{"role": "user", "content": query}]
        context: Additional context for quantum validation
        **llm_kwargs: Extra kwargs for LLM

    Returns:
        Tuple[str, QuantumState]: (generated_text, quantum_validation_state)

    Example:
        >>> draft, state = generate_and_validate_sync(
        ...     query="What is 2+2?",
        ...     llm_model="gpt-4o-mini"
        ... )
        >>> if state.final_verdict == "SEAL":
        ...     print(draft)
    """

    # Wrap async function in sync executor
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # If llm_generate is sync, wrap it
        async_llm_generate = None
        if llm_generate is not None:
            if asyncio.iscoroutinefunction(llm_generate):
                async_llm_generate = llm_generate
            else:
                # Wrap sync function in async
                async def _async_wrapper(q, **kw):
                    return llm_generate(q, **kw)
                async_llm_generate = _async_wrapper

        result = loop.run_until_complete(
            generate_and_validate_async(
                query=query,
                llm_generate=async_llm_generate,
                llm_model=llm_model,
                llm_messages=llm_messages,
                context=context,
                **llm_kwargs
            )
        )
        return result
    finally:
        loop.close()


# =============================================================================
# QUANTUM-ONLY VALIDATION (No LLM Generation)
# =============================================================================

async def validate_text_async(
    query: str,
    draft_response: str,
    context: Optional[Dict[str, Any]] = None
) -> QuantumState:
    """
    Validate pre-generated text constitutionally (async).

    Use this when you already have text from an LLM and just need validation.

    Args:
        query: Original query/prompt
        draft_response: Text to validate (from LLM or any source)
        context: Additional context

    Returns:
        QuantumState: Quantum validation result

    Example:
        >>> # You already generated text
        >>> draft = "The answer is 4"
        >>>
        >>> # Just validate it
        >>> state = await validate_text_async(
        ...     query="What is 2+2?",
        ...     draft_response=draft
        ... )
        >>> print(state.final_verdict)  # "SEAL" or "VOID"
    """
    executor = OrthogonalExecutor()
    validation_context = context or {}
    validation_context["draft_response"] = draft_response

    return await executor.execute_parallel(query=query, context=validation_context)


def validate_text_sync(
    query: str,
    draft_response: str,
    context: Optional[Dict[str, Any]] = None
) -> QuantumState:
    """
    Validate pre-generated text constitutionally (sync).

    Same as validate_text_async, but synchronous wrapper.

    Args:
        query: Original query/prompt
        draft_response: Text to validate
        context: Additional context

    Returns:
        QuantumState: Quantum validation result

    Example:
        >>> draft = "The answer is 4"
        >>> state = validate_text_sync(
        ...     query="What is 2+2?",
        ...     draft_response=draft
        ... )
        >>> print(state.final_verdict)
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            validate_text_async(query, draft_response, context)
        )
        return result
    finally:
        loop.close()


# =============================================================================
# BACKWARD COMPATIBILITY (Pipeline-style API)
# =============================================================================

class QuantumPipeline:
    """
    Backward-compatible API for pipeline users migrating to quantum.

    This is a WRAPPER, not a replacement. Quantum executor stays pure.

    Usage:
        >>> pipeline = QuantumPipeline()
        >>> result = pipeline.run(query="test", llm_model="gpt-4o-mini")
        >>> if result["verdict"] == "SEAL":
        ...     print(result["response"])
    """

    def __init__(self, llm_model: str = "gpt-4o-mini"):
        self.llm_model = llm_model
        self.executor = OrthogonalExecutor()

    def run(
        self,
        query: str,
        llm_generate: Optional[Callable] = None,
        llm_model: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **llm_kwargs
    ) -> Dict[str, Any]:
        """
        Pipeline-style API: Generate + Validate in one call.

        Args:
            query: User query
            llm_generate: Custom LLM function (optional)
            llm_model: Override default model
            context: Additional context
            **llm_kwargs: LLM parameters

        Returns:
            Dict with keys:
                - response: Generated text
                - verdict: SEAL/VOID/PARTIAL/SABAR
                - state: Full QuantumState object
                - passed: bool (True if SEAL)
        """
        model = llm_model or self.llm_model

        draft, state = generate_and_validate_sync(
            query=query,
            llm_generate=llm_generate,
            llm_model=model,
            context=context,
            **llm_kwargs
        )

        return {
            "response": draft,
            "verdict": state.final_verdict,
            "state": state,
            "passed": state.final_verdict == "SEAL",
            "agi_particle": state.agi_particle,
            "asi_particle": state.asi_particle,
            "apex_particle": state.apex_particle,
            "collapsed": state.collapsed,
            "measurement_time": state.measurement_time
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # AAA-level async
    "generate_and_validate_async",
    "validate_text_async",

    # AAA-level sync
    "generate_and_validate_sync",
    "validate_text_sync",

    # Backward compatibility
    "QuantumPipeline",
]
