from .labels import StateDomain

# Claims the system must NEVER make about a human domain.
# These are not style preferences — these are Amanah hard boundaries.
#
# The module answers: "What evidence exists?"
# It must NEVER answer: "Arif IS X."


FORBIDDEN_CLAIMS: dict[StateDomain, list[str]] = {
    StateDomain.BODY: [
        "The user is tired.",
        "The user slept badly.",
        "The user's nervous system is in a specific state.",
        "The user is biologically depleted.",
        "The user has a medical condition.",
        "The user's body is in X state.",
    ],
    StateDomain.PEACE: [
        "The user is spiritually peaceful.",
        "The user's soul is calm.",
        "The user's inner peace is known.",
        "The user has achieved X spiritual state.",
    ],
    StateDomain.ENERGY: [
        "The user's real physical energy is known.",
        "The user is biologically depleted.",
        "The user's energy level is X.",
    ],
    StateDomain.AKAL: [
        "The user's intellect is objectively superior or impaired.",
        "The user's judgment can be overridden by the system.",
        "The user's reasoning capacity is X.",
    ],
    StateDomain.PRESENCE: [
        "The user's consciousness state is known.",
        "The user is fully present as a biological fact.",
        "The user has achieved X presence state.",
    ],
    StateDomain.AMANAH: [
        "The user is morally pure.",
        "The user's niat is known.",
        "The system can certify the user's Amanah.",
        "The user's truthfulness is X.",
    ],
}


def forbidden_claims_for(domain: StateDomain) -> list[str]:
    return FORBIDDEN_CLAIMS[domain]
