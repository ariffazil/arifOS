from .labels import StateDomain


FORBIDDEN_CLAIMS = {
    StateDomain.BODY: [
        "The user is tired.",
        "The user slept badly.",
        "The user's nervous system is in a specific state.",
        "The user has a medical condition.",
    ],
    StateDomain.PEACE: [
        "The user is spiritually peaceful.",
        "The user's soul is calm.",
        "The user's inner state is known.",
    ],
    StateDomain.ENERGY: [
        "The user's real physical energy is known.",
        "The user is biologically depleted.",
    ],
    StateDomain.AKAL: [
        "The user's intellect is objectively superior or impaired.",
        "The user's judgment can be overridden.",
    ],
    StateDomain.PRESENCE: [
        "The user's consciousness state is known.",
        "The user is fully present as a biological fact.",
    ],
    StateDomain.AMANAH: [
        "The user is morally pure.",
        "The user's niat is known.",
        "The system can certify the user's Amanah.",
    ],
}


def forbidden_claims_for(domain: StateDomain) -> list[str]:
    return FORBIDDEN_CLAIMS[domain]
