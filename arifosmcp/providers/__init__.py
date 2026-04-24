"""
arifOS Providers
════════════════

Dynamic component providers for the canonical surface.
"""
from __future__ import annotations

from arifosmcp.providers.aggregate import ArifAggregateProvider
from arifosmcp.providers.canonical import CanonicalProvider
from arifosmcp.providers.constitutional import ConstitutionalProvider
from arifosmcp.providers.meta_skills import MetaSkillsProvider, get_meta_skills_provider
from arifosmcp.providers.proxy import ProxyProvider
from arifosmcp.providers.skills import SkillsDirectoryProvider

__all__ = [
    "ArifAggregateProvider",
    "CanonicalProvider",
    "ConstitutionalProvider",
    "MetaSkillsProvider",
    "get_meta_skills_provider",
    "ProxyProvider",
    "SkillsDirectoryProvider",
]
