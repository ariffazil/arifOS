import pytest

from arifosmcp.runtime.governance_enforcer import classify_and_route


@pytest.mark.asyncio
async def test_governed_queries_route_to_leaf_tool_not_kernel():
    result = await classify_and_route("seal and deploy this plan", context={"mode": "kernel"})

    assert result["requires_tool"] is True
    assert result["tool_name"] in {"arifos_forge", "arifos_judge", "arifos_vault"}
    assert result["tool_name"] != "arifos_kernel"
