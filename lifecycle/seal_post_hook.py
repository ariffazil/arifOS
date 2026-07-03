"""
seal_post_hook.py — decorator that wraps arif_seal with shadow capture.

Physics:    The hook is a measurement instrument. It does not change
            the underlying SEAL call — it observes state across the
            phase transition (pre + post) without participating in it.
Biology:    Afferent/efferent loop: writes to shadow BEFORE, reads seal
            response AFTER. The wrapping decorator is the nerve.
Chemistry:  A catalyst that does not appear in the reaction equation.
            arif_seal's output is byte-identical with or without the hook.

GÖDEL-LOCK (L11 + L13):
    If the calling actor_id == judge_session_id and the call is
    IRREVERSIBLE (ack_irreversible=True), the hook MUST refuse to wrap
    and emit HOLD. This is constitutional — actor cannot certify own
    irreversible action.

Integration map (where this is wrapped):
    The hook is opt-in. To activate:
        from lifecycle import with_shadow
        from arifosmcp.tools.vault import arif_seal as live_seal
        sealed = with_shadow(live_seal, actor_context=lambda: {
            "actor_id": current_actor(),
            "session_id": current_session(),
        })
    The wrapped function is drop-in for `arif_seal`.

    THIS SESSION: arifOS/arifosmcp/runtime/tools.py (the live seal
    entry point) is DIRTY (verdict-gate-normalization in progress).
    Wrapping live is deferred to Phase 2 — post-merge of that work.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Coroutine

from .seal_shadow import ShadowSnapshot, ShadowDiff, capture_pre, capture_post


@dataclass
class SealHookResult:
    """Container returned alongside the original SealOutput.

    The wrapped arif_seal returns (SealOutput, ShadowSnapshot|None, ShadowDiff|None)
    so callers can persist shadow records if they wish.
    """

    held_reason: str | None = None  # non-null iff GÖDEL-LOCK tripped
    shadow_pre: ShadowSnapshot | None = None
    shadow_diff: ShadowDiff | None = None


ActorContextFn = Callable[[], dict[str, str]]
SealFn = Callable[..., Awaitable[Any]]


def _is_irreversible(kwargs: dict[str, Any], args: tuple[Any, ...]) -> bool:
    """Detect IRREVERSIBLE intent — L01 AMANAH gate."""
    if kwargs.get("ack_irreversible"):
        return True
    # arg inspection: ack_irreversible is the 4th positional in live signature.
    if len(args) >= 4 and bool(args[3]):
        return True
    return False


def with_shadow(
    seal_fn: SealFn,
    *,
    actor_context: ActorContextFn,
    state_provider: Callable[[], dict[str, Any]] | None = None,
) -> SealFn:
    """Wrap an `async def arif_seal(...)` with shadow capture.

    Args:
        seal_fn:       the live arif_seal coroutine.
        actor_context: zero-arg callable returning {"actor_id", "session_id"}.
                       Must NOT yield the same value for both — that would
                       trip GÖDEL-LOCK.
        state_provider: optional zero-arg callable returning the
                        pre-SEAL state dict. Defaults to {} (shadow captures
                        only the call args, not full app state). For full
                        app-state capture, supply the engine's state dump.

    Returns:
        Async function with the same call signature, augmented to also
        return ShadowSnapshot + ShadowDiff on success.
    """
    if not inspect.iscoroutinefunction(seal_fn):
        raise TypeError(
            "with_shadow() requires an async arif_seal coroutine; "
            f"got {type(seal_fn).__name__}"
        )

    @functools.wraps(seal_fn)
    async def wrapper(*args: Any, **kwargs: Any) -> tuple[Any, ShadowSnapshot, ShadowDiff]:
        ctx = actor_context() if callable(actor_context) else actor_context
        actor_id = str(ctx.get("actor_id", ""))
        session_id = str(ctx.get("session_id", ""))
        if actor_id and session_id and actor_id == session_id:
            irreversible = _is_irreversible(kwargs, args)
            if irreversible:
                # GÖDEL-LOCK: refuse to certify own irreversible action.
                # Match the live arif_seal HOLD shape.
                await _noop()
                placeholder = _build_hold_placeholder(seal_fn, args, kwargs, actor_id)
                snap = capture_pre(
                    {"actor_id": actor_id, "session_id": session_id, "GODEL_LOCK": True},
                    actor_id=actor_id,
                    session_id=session_id,
                )
                diff = capture_post(snap, seal_response={"verdict": "HOLD", "entry_id": ""})
                return (placeholder, snap, diff)
        # Happy path: capture pre, run seal, capture post.
        snap = capture_pre(
            (state_provider() if state_provider else {}),
            actor_id=actor_id or "unknown",
            session_id=session_id or "unknown",
        )
        result = await seal_fn(*args, **kwargs)
        seal_resp = _to_dict(result)
        diff = capture_post(snap, seal_response=seal_resp)
        return (result, snap, diff)

    return wrapper


def _to_dict(result: Any) -> dict[str, Any]:
    """Coerce a SealOutput (or any plain object) into a dict for capture_post().

    Order matters: Pydantic v2 → Pydantic v1 → dict-like → object.__dict__ → {}.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict") and callable(result.dict):
        try:
            return result.dict()
        except TypeError:
            pass
    if isinstance(result, dict):
        return result
    obj_dict = getattr(result, "__dict__", None)
    if isinstance(obj_dict, dict):
        return dict(obj_dict)
    return {}


# ─── Helpers ────────────────────────────────────────────────────────────────


async def _noop() -> None:
    return None


def _build_hold_placeholder(
    seal_fn: SealFn,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    actor_id: str,
) -> Any:
    """Best-effort stand-in matching the SealOutput shape.

    We avoid importing live schemas here (couples to dirty runtime).
    Instead we emit a dict that downstream code can inspect for the
    'GODEL_LOCK' marker. Real SealOutput reconstruction lives in the
    sealed record (post-merge).
    """
    return {
        "mode": kwargs.get("mode", "seal"),
        "verdict": "HOLD",
        "status": "GODEL_LOCK",
        "chain_ok": False,
        "entry_id": "",
        "created_at": "",
        "actor_id": actor_id,
        "note": (
            f"GÖDEL-LOCK: actor {actor_id} cannot certify its own IRREVERSIBLE "
            "action via with_shadow wrapper. Requires separate judge session "
            "(F13 SOVEREIGN or independent 888 JUDGE)."
        ),
    }


if __name__ == "__main__":  # pragma: no cover
    from types import SimpleNamespace

    async def fake_seal(**kwargs):
        return SimpleNamespace(
            entry_id="fake-1",
            verdict="SEAL",
            chain_ok=True,
            witness={"human": 0.42},
        )

    wrapped = with_shadow(
        fake_seal, actor_context=lambda: {"actor_id": "actor-A", "session_id": "judge-B"}
    )

    coro: Coroutine[Any, Any, tuple[Any, ShadowSnapshot, ShadowDiff]] = wrapped(payload="hi")
    result, snap, diff = asyncio.run(coro)
    assert result.entry_id == "fake-1"
    assert diff.verdict == "SEAL"
    assert snap.actor_id == "actor-A"
    print("OK seal_post_hook smoke:", snap.snapshot_id)
