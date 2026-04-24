
"""
ARIFOS CONSTITUTIONAL MAP (v2)

Single source of truth for the 10-tool mega-surface.
This supersedes the legacy `capability_map.py`.
Ditempa Bukan Diberi.
"""
from enum import Enum


class Void000Mode(str, Enum):
    init = "init"
    epoch = "epoch"
    session_id = "session_id"
    entropy_zero = "entropy_zero"
    omega_band = "omega_band"
    anti_hantu = "anti_hantu"
    injection_guard = "injection_guard"
    sovereign_arm = "sovereign_arm"
    witness_seed = "witness_seed"
    discover = "discover"
    handover = "handover"
    revoke = "revoke"
    refresh = "refresh"
    state = "state"
    status = "status"

class Anchor111Mode(str, Enum):
    search = "search"
    ingest = "ingest"
    compass = "compass"
    atlas = "atlas"
    epoch = "epoch"
    entropy_dS = "entropy_dS"
    w3_earth = "w3_earth"

class Explore222Mode(str, Enum):
    diverge = "diverge"
    stress_test = "stress_test"
    path_map = "path_map"
    delta_s = "delta_s"
    eureka = "eureka"

class Agi333Mode(str, Enum):
    reason = "reason"
    reflect = "reflect"
    forge = "forge"
    debate = "debate"
    socratic = "socratic"

class Kernel444Mode(str, Enum):
    route = "route"
    kernel = "kernel"
    triage = "triage"
    delegate = "delegate"
    status = "status"

class Forge555Mode(str, Enum):
    engineer = "engineer"
    query = "query"
    recall = "recall"
    write = "write"
    generate = "generate"
    commit = "commit"

class Rasa666Mode(str, Enum):
    critique = "critique"
    simulate = "simulate"
    redteam = "redteam"
    maruah = "maruah"
    deescalate = "deescalate"
    empathy = "empathy"

class Math777Mode(str, Enum):
    health = "health"
    vitals = "vitals"
    cost = "cost"
    genius = "genius"
    psi_le = "psi_le"
    omega = "omega"
    landauer = "landauer"

class Apex888Mode(str, Enum):
    judge = "judge"
    validate = "validate"
    hold = "hold"
    rules = "rules"
    armor = "armor"
    probe = "probe"
    notify = "notify"

class Seal999Mode(str, Enum):
    seal = "seal"
    verify = "verify"
    ledger = "ledger"
    changelog = "changelog"
    audit = "audit"


CONSTITUTIONAL_TOOLS = {
    "void_000": {
        "name": "void_000",
        "description": "000_VOID: Salam-to-Seal metabolic loop entry. Manages session sovereignty, identity, and entropy.",
        "modes": Void000Mode,
        "floor_guards": ["F1", "F9", "F12", "F13"],
        "hold_condition": "Unverified actor on irreversible mode, or injection detected."
    },
    "anchor_111": {
        "name": "anchor_111",
        "description": "111_ANCHOR: Reality grounding and temporal intelligence.",
        "modes": Anchor111Mode,
        "floor_guards": ["F2", "F4", "F7"],
        "output_contract": "Reality-grounded payload with confidence band Omega_0 in [0.03,0.05]."
    },
    "explore_222": {
        "name": "explore_222",
        "description": "222_EXPLORE: Thermodynamic divergence engine for novelty and stress-testing.",
        "modes": Explore222Mode,
        "floor_guards": ["F3", "F4", "F7", "F8"],
        "trigger": "Psi_LE >= 1.05 OR query spans >=2 repo layers OR novel arch proposed."
    },
    "agi_333": {
        "name": "agi_333",
        "description": "333_AGI: Reasoning and synthesis engine. QTT-enabled.",
        "modes": Agi333Mode,
        "floor_guards": ["F2", "F4", "F7", "F8"],
        "output_contract": "Tagged CLAIM | PLAUSIBLE | HYPOTHESIS | ESTIMATE | UNKNOWN."
    },
    "kernel_444": {
        "name": "kernel_444",
        "description": "444_KERNEL: Primary metabolic conductor. Routes query through pipeline.",
        "modes": Kernel444Mode,
        "floor_guards": ["F1", "F4", "F11", "F13"],
        "hold_condition": "risk_tier=critical requires F11 verified ID before execution."
    },
    "forge_555": {
        "name": "forge_555",
        "description": "555_FORGE: Engineering memory and generation engine.",
        "modes": Forge555Mode,
        "floor_guards": ["F2", "F4", "F8"],
        "output_contract": "Generated artifact + delta_S reduction metric."
    },
    "rasa_666": {
        "name": "rasa_666",
        "description": "666_RASA: Heart engine. Safety, empathy, and red-team audit.",
        "modes": Rasa666Mode,
        "floor_guards": ["F5", "F6", "F9"],
        "orthogonality": "Omega_ortho >= 0.95 vs agi_333."
    },
    "math_777": {
        "name": "math_777",
        "description": "777_MATH: Thermodynamic vitals and Genius equation engine.",
        "modes": Math777Mode,
        "floor_guards": ["F2", "F7", "F8"],
        "output_contract": "JSON telemetry block compatible with seal_999 footer."
    },
    "apex_888": {
        "name": "apex_888",
        "description": "888_APEX: Constitutional verdict engine. Sovereign judgment layer.",
        "modes": Apex888Mode,
        "floor_guards": ["F1", "F2", "F8", "F11", "F12", "F13"],
        "hold_condition": "Irreversible action, injection detected, or F13 veto required."
    },
    "seal_999": {
        "name": "seal_999",
        "description": "999_SEAL: Immutable vault and Merkle commit engine.",
        "modes": Seal999Mode,
        "floor_guards": ["F1", "F2", "F13"],
        "hold_condition": "Any seal without prior apex_888 judge=SEAL verdict."
    }
}

def get_public_tool_specs() -> dict[str, str]:
    """Generates the PUBLIC_PROXY_SPECS dictionary from the constitutional map."""
    specs = {}
    for tool_key, tool_data in CONSTITUTIONAL_TOOLS.items():
        specs[tool_key] = tool_data["description"]
    return specs


# ─── Canonical Enums (v2026.04.24-KANON) ────────────────────────────────────
# Appended to unify VerdictCode, SacredStage, and FloorId across the federation.

class VerdictCode(str, Enum):
    SEAL = "SEAL"       # Approved / Committed
    SABAR = "SABAR"     # 888 HOLD / Pause
    VOID = "VOID"       # Forbidden / Intercepted
    PARTIAL = "PARTIAL" # Degraded / Caution

class SacredStage(str, Enum):
    INIT = "000_INIT"
    SENSE = "111_SENSE"
    MIND = "333_MIND"
    KERNEL = "444_KERNEL"
    MEM = "555_MEM"
    HEART = "666_HEART"
    FORGE = "777_FORGE"
    JUDGE = "888_JUDGE"
    VAULT = "999_VAULT"

class FloorId(str, Enum):
    F1 = "F1_AMANAH"
    F2 = "F2_TRUTH"
    F3 = "F3_PEACE"
    F4 = "F4_DELTAS"
    F5 = "F5_WITNESS"
    F6 = "F6_EMPATHY"
    F7 = "F7_OMEGA0"
    F8 = "F8_LEDGER"
    F9 = "F9_ANTIHANTU"
    F10 = "F10_COHERENCE"
    F11 = "F11_SABAR"
    F12 = "F12_PHOENIX"
    F13 = "F13_KHILAFAH"
