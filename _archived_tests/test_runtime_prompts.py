from __future__ import annotations

from arifosmcp.runtime.prompts import register_prompts
from arifosmcp.runtime.public_registry import PUBLIC_PROMPT_SPECS


class _PromptCollector:
    def __init__(self) -> None:
        self.prompts: dict[str, object] = {}

    def prompt(self):  # type: ignore[no-untyped-def]
        def decorator(fn):  # type: ignore[no-untyped-def]
            self.prompts[fn.__name__] = fn
            return fn

        return decorator


def test_register_prompts_matches_public_registry() -> None:
    collector = _PromptCollector()
    register_prompts(collector)  # type: ignore[arg-type]

    expected_names = {spec.name for spec in PUBLIC_PROMPT_SPECS}
    registered_names = set(collector.prompts)
    # All expected prompts must be registered (legacy aliases may also exist)
    assert expected_names.issubset(registered_names), (
        f"Missing prompts: {expected_names - registered_names}"
    )

    dashboard_prompt = collector.prompts["open_apex_dashboard"]
    assert "APEX" in dashboard_prompt()

    init_prompt = collector.prompts["init_anchor_state_prompt"]
    assert "constitutional" in init_prompt()
