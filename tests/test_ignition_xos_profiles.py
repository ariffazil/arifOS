
from arifos_core.ignition import IgnitionLoader

def test_arif_profile():
    loader = IgnitionLoader("spec/arifos_ignition_profiles.yaml")
    p = loader.match_profile("I am Arif.")
    assert p.id == "arifOS"

def test_azwa_profile():
    loader = IgnitionLoader("spec/arifos_ignition_profiles.yaml")
    p = loader.match_profile("Saya Azwa.")
    assert p.id == "azwaOS"

def test_default_profile():
    loader = IgnitionLoader("spec/arifos_ignition_profiles.yaml")
    p = loader.match_profile("Hello, I am unknown.")
    assert p is None or p.id in ["defaultOS"]
