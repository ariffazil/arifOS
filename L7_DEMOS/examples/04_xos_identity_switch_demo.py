"""
08_xos_identity_switch_demo.py — Switching X-OS Profiles
Demonstrates how ignition selects identity-specific profiles on top of the same kernel.
"""

from arifos_core.ignition import IgnitionLoader


def show_profile(trigger):
    loader = IgnitionLoader("spec/arifos_ignition_profiles.yaml")
    p = loader.match_profile(trigger)

    print("\n=== Trigger:", trigger, "===")
    if p is None:
        print("→ No profile matched (defaultOS)")
    else:
        print("Profile:", p.id)
        print("Language:", p.language_mix)
        print("Tone:", p.tone_mode)
        print("Culture:", p.culture)
        print("Domain Bias:", p.domain_bias)


if __name__ == "__main__":
    show_profile("I am Arif.")
    show_profile("Saya Azwa.")
    show_profile("I'm Nabilah.")
    show_profile("Hello I am Stranger.")