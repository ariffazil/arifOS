# arifOS SENSE Pipeline — Provider Registry
# Canonical provider registry for all SENSE search providers
# Providers are interchangeable sensors — QueryPlanner owns routing authority
# DITEMPA BUKAN DIBERI

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ProviderType(StrEnum):
    BRAVE = "brave"
    EXA = "exa"
    TAVILY = "tavily"
    FIRECRAWL = "firecrawl"
    JINA = "jina"
    MEYHEM = "meyhem"


class QueryMode(StrEnum):
    REALTIME = "realtime"
    SEMANTIC = "semantic"
    RESEARCH = "research"
    CODE = "code"
    DEEP_PAGE = "deep_page"
    NEWS = "news"


@dataclass
class ProviderConfig:
    name: str
    provider_type: ProviderType
    api_key_env: str
    base_url: str | None = None
    monthly_quota: int = 1_000_000
    rate_limit_rpm: int = 60
    is_default: bool = False
    supported_modes: list[QueryMode] = field(default_factory=list)
    priority_realtime: int = 0
    priority_semantic: int = 0
    priority_research: int = 0
    timeout_secs: float = 30.0

    @property
    def is_live(self) -> bool:
        # Meyhem (api_key_env="") requires no API key — always live
        if not self.api_key_env:
            return True
        return bool(os.getenv(self.api_key_env))

    @property
    def api_key(self) -> str | None:
        return os.getenv(self.api_key_env)

    def capabilities(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider_type.value,
            "live": self.is_live,
            "quota": self.monthly_quota,
            "rate_limit_rpm": self.rate_limit_rpm,
            "supported_modes": [m.value for m in self.supported_modes],
            "priorities": {
                "realtime": self.priority_realtime,
                "semantic": self.priority_semantic,
                "research": self.priority_research,
            },
        }


PROVIDER_CONFIGS: dict[ProviderType, ProviderConfig] = {
    ProviderType.BRAVE: ProviderConfig(
        name="Brave Search",
        provider_type=ProviderType.BRAVE,
        api_key_env="BRAVE_API_KEY",
        base_url="https://api.search.brave.com/res/v1/web/search",
        monthly_quota=20_000_000,
        rate_limit_rpm=20 * 60,
        is_default=True,
        supported_modes=[QueryMode.REALTIME, QueryMode.SEMANTIC],
        priority_realtime=10,
        priority_semantic=7,
        timeout_secs=20.0,
    ),
    ProviderType.EXA: ProviderConfig(
        name="Exa Search",
        provider_type=ProviderType.EXA,
        api_key_env="EXA_API_KEY",
        base_url="https://api.exa.ai",
        monthly_quota=1_000_000,
        rate_limit_rpm=60,
        supported_modes=[QueryMode.SEMANTIC, QueryMode.RESEARCH],
        priority_realtime=5,
        priority_semantic=10,
        priority_research=10,
        timeout_secs=30.0,
    ),
    ProviderType.TAVILY: ProviderConfig(
        name="Tavily AI Search",
        provider_type=ProviderType.TAVILY,
        api_key_env="TAVILY_API_KEY",
        base_url="https://api.tavily.com/search",
        monthly_quota=1_000,
        rate_limit_rpm=60,
        supported_modes=[QueryMode.REALTIME, QueryMode.SEMANTIC, QueryMode.RESEARCH],
        priority_realtime=7,
        priority_semantic=8,
        priority_research=7,
        timeout_secs=30.0,
    ),
    ProviderType.FIRECRAWL: ProviderConfig(
        name="Firecrawl",
        provider_type=ProviderType.FIRECRAWL,
        api_key_env="FIRECRAWL_API_KEY",
        base_url="https://api.firecrawl.dev/v1",
        monthly_quota=500,
        rate_limit_rpm=20,
        supported_modes=[QueryMode.DEEP_PAGE],
        priority_realtime=0,
        priority_semantic=0,
        priority_research=5,
        timeout_secs=60.0,
    ),
    ProviderType.JINA: ProviderConfig(
        name="Jina AI",
        provider_type=ProviderType.JINA,
        api_key_env="JINA_API_KEY",
        base_url="https://api.jina.ai",
        monthly_quota=500_000,
        rate_limit_rpm=100,
        supported_modes=[QueryMode.DEEP_PAGE],
        priority_realtime=0,
        priority_semantic=0,
        priority_research=3,
        timeout_secs=30.0,
    ),
    ProviderType.MEYHEM: ProviderConfig(
        name="Meyhem",
        provider_type=ProviderType.MEYHEM,
        api_key_env="",  # No API key required
        base_url="https://api.rhdxm.com",
        monthly_quota=999_999_999,  # No rate limits documented
        rate_limit_rpm=9999,
        is_default=False,
        supported_modes=[QueryMode.REALTIME, QueryMode.SEMANTIC, QueryMode.RESEARCH],
        priority_realtime=3,
        priority_semantic=4,
        priority_research=4,
        timeout_secs=20.0,
    ),
}


class ProviderRegistry:
    __slots__ = ("_providers",)

    def __init__(self) -> None:
        self._providers: dict[ProviderType, ProviderConfig] = dict(PROVIDER_CONFIGS)

    def get(self, provider_type: ProviderType) -> ProviderConfig | None:
        return self._providers.get(provider_type)

    def get_live(self) -> list[ProviderConfig]:
        return [p for p in self._providers.values() if p.is_live]

    def get_default(self) -> ProviderConfig | None:
        return next((p for p in self._providers.values() if p.is_default and p.is_live), None)

    def resolve_provider(self, name: str) -> ProviderConfig | None:
        name_lower = name.lower()
        for p in self._providers.values():
            if p.name.lower() == name_lower or p.provider_type.value == name_lower:
                return p
        return None


def get_registry() -> ProviderRegistry:
    return ProviderRegistry()


def get_live_providers() -> list[ProviderConfig]:
    return [p for p in PROVIDER_CONFIGS.values() if p.is_live]


def get_provider(provider_type: ProviderType) -> ProviderConfig | None:
    return PROVIDER_CONFIGS.get(provider_type)
