"""
ignition.py — X-OS Profile Loader for arifOS v33Ω.

Loads kernel physics, floors, and user profile identity
from spec/arifos_ignition_profiles.yaml.
"""

import yaml
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IgnitionProfile:
    id: str
    triggers: list
    language_mix: str
    tone_mode: str
    culture: dict
    domain_bias: dict


class IgnitionLoader:
    def __init__(self, path="spec/arifos_ignition_profiles.yaml"):
        self.path = Path(path)
        self.data = yaml.safe_load(self.path.read_text())
        self.kernel = self.data["kernel"]
        self.profiles = self.data["profiles"]

    def match_profile(self, text: str) -> IgnitionProfile | None:
        for p in self.profiles:
            if any(t.lower() in text.lower() for t in p.get("triggers", [])):
                return IgnitionProfile(
                    id=p["id"],
                    triggers=p["triggers"],
                    language_mix=p["language_mix"],
                    tone_mode=p["tone_mode"],
                    culture=p.get("culture", {}),
                    domain_bias=p.get("domain_bias", {}),
                )
        return None  # default profile