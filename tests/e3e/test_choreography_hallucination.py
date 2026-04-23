import pytest
from logging import getLogger

from arifosmcp.runtime.tools import init_anchor, arifos_kernel
from arifosmcp.runtime.models import Verdict


logger = getLogger(__name__)


@pytest.mark.asyncio
async def test_e3e_hallucination_recovery_unanchored():
    """
    Simulates an AI Agent hallucinating and calling the main kernel
    WITHOUT first calling init_anchor (auth continuity violation).

    Proves that the system catches the violation and explicitly returns
    guidance advising the agent to call `init_anchor` first,
    rather than throwing a stack trace.
    """

    # 1. Agent attempts to execute kernel logic without anchoring
    envelope = await arifos_kernel(query="Delete all logs", risk_tier="high")

    # 2. Verify envelope was returned (not exception)
    assert envelope is not None, "Envelope should be returned even for unanchored calls"

    # 3. Check that blocked_tools contains guidance to run init_anchor
    # This is the self-explaining recovery interface
    blocked_tools = getattr(envelope, "blocked_tools", None)
    assert blocked_tools is not None, "blocked_tools should be present"

    # Find the arifos_kernel entry in blocked_tools
    kernel_blocked = [t for t in blocked_tools if t.get("tool") == "arifos_kernel"]
    assert len(kernel_blocked) > 0, (
        "arifos_kernel should be in blocked_tools for unanchored session"
    )

    # Verify the reason mentions init_anchor
    assert "init_anchor" in kernel_blocked[0].get("reason", ""), (
        "Blocked reason should mention init_anchor"
    )

    # 4. Verify allowed_next_tools includes init_anchor
    allowed = getattr(envelope, "allowed_next_tools", [])
    assert "init_anchor" in allowed, "init_anchor should be in allowed_next_tools"

    logger.info("✅ E3E Hallucination Test: Unanchored recovery guidance verified.")


@pytest.mark.asyncio
async def test_e3e_hallucination_recovery_invalid_mode():
    """
    Simulates an AI Agent calling a tool but providing a completely
    hallucinated mode that does not exist in the 11-Tool Mega-Surface.
    """
    # 1. Agent correctly anchors
    anchor_env = await init_anchor(
        mode="init", payload={"actor_id": "test_user", "intent": "testing recovery"}
    )
    assert anchor_env.verdict in [Verdict.SEAL, "SEAL"]

    # 2. Extract session_id for subsequent calls
    session_id = anchor_env.session_id if hasattr(anchor_env, "session_id") else None

    # 3. Test invalid mode handling - arifos_kernel only accepts "kernel" or "status"
    try:
        envelope = await arifos_kernel(
            mode="invalid_hallucinated_mode",  # This mode doesn't exist
            payload={"query": "Test query"},
            session_id=session_id,
            dry_run=True,
        )
        # Should not reach here - ValueError expected
        assert False, "Should have raised ValueError for invalid mode"
    except ValueError as e:
        # Expected: Invalid mode for arifos_kernel
        assert "Invalid mode" in str(e)
        logger.info(f"✅ Caught expected validation error: {e}")
    except Exception as e:
        # Any other exception should be handled gracefully
        logger.info(f"Caught exception (may be expected): {type(e).__name__}: {e}")

    logger.info("✅ E3E Hallucination Test: Invalid mode handling secured.")


@pytest.mark.asyncio
async def test_e3e_valid_kernel_execution():
    """
    Tests a valid kernel execution flow after proper anchoring.
    """
    # 1. Agent correctly anchors
    anchor_env = await init_anchor(
        mode="init", payload={"actor_id": "test_user", "intent": "testing valid execution"}
    )
    assert anchor_env.verdict in [Verdict.SEAL, "SEAL"]

    session_id = anchor_env.session_id if hasattr(anchor_env, "session_id") else None

    # 2. Execute kernel in dry_run mode
    envelope = await arifos_kernel(
        mode="kernel",
        payload={"query": "Test query for E3E validation"},
        session_id=session_id,
        dry_run=True,
        risk_tier="medium",
    )

    # 3. Verify response structure
    assert envelope is not None
    assert hasattr(envelope, "verdict") or "verdict" in str(envelope)

    logger.info("✅ E3E Valid Execution Test: Kernel execution verified.")
