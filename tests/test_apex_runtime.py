"""
APEX Theory — Runtime Conformance Matrix
========================================
Maps philosophical insights from APEX_THEORY_v2026.05.26 to runtime assertions.
Each test proves the philosophical law has operational teeth.

SEAL: DITEMPA BUKAN DIBERI

Constitution structure (source of truth):
  - laws: dict keyed by law name, each has .floor field (F1-F13)
  - state_machine: dict keyed by stage number (000, 111, ...)
  - primary_verdicts: list of valid verdict strings
  - verdict_semantics: dict with meaning/color/enforcement per verdict
"""

import json
import math
import re
from pathlib import Path

# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "federation_registry.json"
ROUTING_PATH = REPO_ROOT / "blueprints" / "routing_engine.yaml"
CONSTITUTION_PATH = REPO_ROOT / "blueprints" / "kernel_constitution.yaml"
VERDICT_CONTRACT_PATH = REPO_ROOT / "contracts" / "verdict_contract.json"
ARIFOS_HOST = "http://localhost:8088"
WEALTH_HOST = "http://localhost:18082"
GEOX_HOST = "http://localhost:8081"
WELL_HOST = "http://localhost:18083"
AFORGE_HOST = "http://localhost:7071"


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    import yaml

    with open(path) as f:
        return yaml.safe_load(f)


def fetch_json(url: str, timeout: int = 5) -> dict | None:
    import urllib.request

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except Exception:
        return None


def get_constitution():
    return load_yaml(CONSTITUTION_PATH)


def get_registry():
    return load_json(REGISTRY_PATH)


def get_routing():
    return load_yaml(ROUTING_PATH)


def find_floor(constitution: dict, floor_id: str) -> dict | None:
    """Find a law by its floor ID (F1-F13). Returns the law dict or None."""
    laws = constitution.get("laws", {})
    for law_name, law in laws.items():
        if law.get("floor") == floor_id:
            return law
    return None


# ─────────────────────────────────────────────────────────────────
# RESULT TRACKER
# ─────────────────────────────────────────────────────────────────


class Result:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def pass_test(self, name: str, detail: str = ""):
        self.passed += 1
        sep = f" — {detail}" if detail else ""
        print(f"  ✅ {name}{sep}")

    def fail_test(self, name: str, detail: str = ""):
        self.failed += 1
        sep = f" — {detail}" if detail else ""
        print(f"  ❌ {name}{sep}")

    def warn_test(self, name: str, detail: str = ""):
        self.warnings += 1
        sep = f" — {detail}" if detail else ""
        print(f"  ⚠️  {name}{sep}")

    def section(self, name: str):
        print(f"\n📋 {name}")

    def summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{'=' * 60}")
        print(f"RESULTS: {self.passed}/{total} passed", end="")
        if self.warnings:
            print(f", {self.warnings} warnings", end="")
        if self.failed:
            print(f", {self.failed} FAILED", end="")
        print()
        print(f"{'=' * 60}")
        return self.failed == 0


# ─────────────────────────────────────────────────────────────────
# LAW CLUSTERS
# ─────────────────────────────────────────────────────────────────
# LAW 1: Mechanical Bounding — Safety is execution topology, not rhetoric
# LAW 2: Certainty Hazard — Gödel Lock, impossible confidence states
# LAW 3: Temporal Scarring — Hysteresis, past constrains future
# LAW 4: Reality Veto — Physical evidence overrides social consensus
# LAW 5: Organ Republic — Separation of powers across organs
# LAW 6: Metabolic Cognition — 11-stage pipeline integrity
# LAW 7: Decision Biology — C0-C5 risk tiers and dignity
# LAW 8: Trust Thermodynamics — Ditempa Bukan Diberi
# LAW 9: Routing Orthogonality — Composite hallucination prevention


# ─────────────────────────────────────────────────────────────────
# TEST 1: LAW 1 — MECHANICAL BOUNDING
# APEX: "Unsafe cognition may exist internally. Unsafe action must be
#         structurally impossible externally."
# F1 (reversibility), F12 (defense)
# ─────────────────────────────────────────────────────────────────


def test_law1_mechanical_bounding(result: Result):
    result.section("LAW 1: MECHANICAL BOUNDING")

    # 1.1: A-FORGE has health endpoint
    health = fetch_json(f"{AFORGE_HOST}/health")
    if health:
        result.pass_test("A-FORGE: health endpoint alive")
    else:
        result.fail_test("A-FORGE: unreachable")

    # 1.2: A-FORGE has no direct /tools (no client-facing execution surface)
    tools_resp = fetch_json(f"{AFORGE_HOST}/tools")
    if tools_resp is None:
        result.pass_test("A-FORGE: /tools unreachable — no direct execution surface")
    elif isinstance(tools_resp, dict) and not tools_resp.get("tools"):
        result.pass_test("A-FORGE: /tools returns empty — isolation confirmed")
    else:
        result.fail_test("A-FORGE: /tools exposes tools — isolation breach")

    # 1.3: A-FORGE has /contract endpoint (A2A mesh)
    contract = fetch_json(f"{AFORGE_HOST}/contract")
    if contract:
        result.pass_test("A-FORGE: /contract exists (A2A mesh bridge)")
    else:
        result.warn_test("A-FORGE: /contract unreachable")

    # 1.4: TIER_3 tools are in the reversibility gate
    routing = get_routing()
    rg = routing.get("reversibility_gate", {})
    tier3_instruments = rg.get("TIER_3_IRREVERSIBLE_instruments", [])

    required_tier3 = {"arif_judge_deliberate", "arif_forge_execute", "arif_vault_seal"}
    found_tier3 = set(tier3_instruments) & required_tier3

    if found_tier3 == required_tier3:
        result.pass_test(f"TIER_3 gate: all 3 core tools gated")
    elif found_tier3:
        result.warn_test(f"TIER_3 gate: partial — {found_tier3} found")
    else:
        result.fail_test(f"TIER_3 gate: none of {required_tier3} found in reversibility_gate")

    # 1.5: Every tool has a defined reversibility tier
    registry = get_registry()
    tools = registry.get("tools", [])
    undefined_rev = [
        t["tool_name"]
        for t in tools
        if not t.get("reversibility") or t["reversibility"] == "UNDEFINED"
    ]
    if not undefined_rev:
        result.pass_test("All tools have reversibility tier assigned")
    else:
        result.fail_test(f"Tools without reversibility: {undefined_rev[:5]}")

    # 1.6: Execute action mode — arif_forge_execute is on arifOS (routes to A-FORGE via A2A)
    # A-FORGE itself has no MCP tools — it's the physical executor via A2A mesh
    execute_on_arifos = [t for t in tools if t.get("action_mode") == "EXECUTE"]
    execute_servers = {t["server"]: t["tool_name"] for t in execute_on_arifos}

    if "arifOS" in execute_servers and "A-FORGE" not in execute_servers:
        result.pass_test(
            f"EXECUTE correctly on arifOS (routes to A-FORGE via A2A): {list(execute_servers.values())}"
        )
    elif "A-FORGE" in execute_servers:
        result.fail_test(f"EXECUTE tool on A-FORGE itself: {execute_servers}")
    else:
        result.warn_test(f"EXECUTE tool placement unusual: {execute_servers}")

    # 1.7: Routing engine has task patterns (prevents composite hallucination)
    task_patterns = routing.get("task_patterns", [])
    if len(task_patterns) >= 10:
        result.pass_test(f"Routing: {len(task_patterns)} task patterns defined")
    else:
        result.warn_test(f"Routing: only {len(task_patterns)} task patterns")


# ─────────────────────────────────────────────────────────────────
# TEST 2: LAW 2 — GÖDEL LOCK (Certainty Hazard)
# APEX: "Confidence ≥ impossible-state threshold is not a warning.
#         It is a contradiction."
# F7 (Humility/Gödel Lock) — in constitution: L7_HUMAN_SOVEREIGNTY
# ─────────────────────────────────────────────────────────────────


def test_law2_godel_lock(result: Result):
    result.section("LAW 2: GÖDEL LOCK — Certainty as Impossible State")

    constitution = get_constitution()
    verdict_contract = load_json(VERDICT_CONTRACT_PATH)

    # 2.1: F7 (Gödel Lock) codified
    # Note: constitution has L7_HUMAN_SOVEREIGNTY with floor=F7
    f7 = find_floor(constitution, "F7")
    if f7:
        law_name = [k for k, v in constitution["laws"].items() if v.get("floor") == "F7"][0]
        result.pass_test(f"F7 (Gödel Lock): codified as {law_name}")
    else:
        result.fail_test("F7 (Gödel Lock): NOT codified in constitution")

    # 2.2: VOID verdict is defined as terminal rejection
    verdict_semantics = constitution.get("verdict_semantics", {})
    void_def = verdict_semantics.get("VOID", {})
    if void_def:
        allows_exec = void_def.get("allows_execution", True)
        block_all = void_def.get("block_all", False)
        if not allows_exec and block_all:
            result.pass_test("VOID: terminal rejection (block_all=True, allows_execution=False)")
        else:
            result.warn_test(
                f"VOID: severity unclear — allows_execution={allows_exec}, block_all={block_all}"
            )
    else:
        result.fail_test("VOID: not defined in verdict_semantics")

    # 2.3: All required verdict values are present
    constitution_verdicts = set(constitution.get("primary_verdicts", []))
    required_verdicts = {"SEAL", "HOLD", "VOID", "SABAR", "PARTIAL"}
    if required_verdicts <= constitution_verdicts:
        result.pass_test(f"Primary verdicts: all required present {required_verdicts}")
    else:
        result.fail_test(f"Primary verdicts: missing {required_verdicts - constitution_verdicts}")

    # 2.4: HOLD requires human confirmation
    hold_def = verdict_semantics.get("HOLD", {})
    if hold_def.get("requires_human_confirmation"):
        result.pass_test("HOLD verdict: requires human confirmation")
    else:
        result.fail_test("HOLD: does not require human confirmation")

    # 2.5: Verdict contract has justification field (no bare assertion)
    output_schema = verdict_contract.get("output_schema", verdict_contract.get("output", {}))
    if output_schema:
        props = output_schema.get("properties", {}) if isinstance(output_schema, dict) else {}
        if "justification" in props and "verdict" in props:
            result.pass_test("Verdict contract: verdict + justification are required fields")
        else:
            result.fail_test(f"Verdict contract: missing verdict or justification field")


# ─────────────────────────────────────────────────────────────────
# TEST 3: LAW 3 — TEMPORAL SCARRING (Hysteresis)
# APEX: "Ledger is not storage. Ledger is delayed consequence."
# F1 (Amanah/reversibility)
# ─────────────────────────────────────────────────────────────────


def test_law3_hysteresis_ledger(result: Result):
    result.section("LAW 3: HYSTERESIS LEDGER — Memory Scars Future Freedom")

    registry = get_registry()

    # 3.1: WEALTH has hysteresis/ledger tools
    wealth_tools = [t["tool_name"] for t in registry["tools"] if t["server"] == "WEALTH"]
    hyst_tools = [t for t in wealth_tools if "hysteresis" in t or "ledger" in t]
    if hyst_tools:
        result.pass_test(f"WEALTH hysteresis tools: {hyst_tools}")
    else:
        result.fail_test("WEALTH: no hysteresis/ledger tools (Ω-12 missing)")

    # 3.2: VAULT/SEAL tools exist
    vault_seal = [
        t["tool_name"]
        for t in registry["tools"]
        if "vault" in t["tool_name"].lower() or "seal" in t["tool_name"].lower()
    ]
    if vault_seal:
        result.pass_test(f"VAULT/SEAL tools: {vault_seal}")
    else:
        result.fail_test("No VAULT/SEAL tools found")

    # 3.3: VAULT_SEAL_RECEIPT defined in receipt schema
    receipt_schema_path = REPO_ROOT / "contracts" / "runtime_receipt_schema.json"
    if receipt_schema_path.exists():
        rs = load_json(receipt_schema_path)
        rt = rs.get("receipt_types", {})
        if "VAULT_SEAL_RECEIPT" in rt:
            result.pass_test("Receipt schema: VAULT_SEAL_RECEIPT defined")
        else:
            result.fail_test("Receipt schema: VAULT_SEAL_RECEIPT missing")
    else:
        result.fail_test("runtime_receipt_schema.json not found")

    # 3.4: TIER_3 tools include critical irreversible instruments
    routing = get_routing()
    tier3 = routing.get("reversibility_gate", {}).get("TIER_3_IRREVERSIBLE_instruments", [])
    critical_tier3 = {"arif_judge_deliberate", "arif_forge_execute", "arif_vault_seal"}
    found = set(tier3) & critical_tier3
    if found == critical_tier3:
        result.pass_test(f"Critical TIER_3 tools properly gated: {found}")
    else:
        result.fail_test(f"TIER_3: missing {critical_tier3 - found}")


# ─────────────────────────────────────────────────────────────────
# TEST 4: LAW 4 — REALITY VETO (Tri-Witness)
# APEX: "Institutions may negotiate optics. They may not negotiate the substrate."
# F2 (Truth), F3 (Tri-Witness geometric mean)
# ─────────────────────────────────────────────────────────────────


def test_law4_triwitness_physical_veto(result: Result):
    result.section("LAW 4: TRI-WITNESS — Physical Reality Vetoes Social Consensus")

    constitution = get_constitution()
    registry = get_registry()

    # 4.1: F3 (Orthogonal Separation / Tri-Witness geometric mean) codified
    f3 = find_floor(constitution, "F3")
    if f3:
        result.pass_test("F3 (Tri-Witness / Orthogonal Separation): codified")
    else:
        result.fail_test("F3 (Tri-Witness): NOT codified")

    # 4.2: F2 (Truth / no pretending) codified
    f2 = find_floor(constitution, "F2")
    if f2:
        result.pass_test("F2 (Truth): codified")
    else:
        result.fail_test("F2 (Truth): NOT codified")

    # 4.3: GEOX has QC tools (Physics9 boundary enforcement)
    geox_tools = {t["tool_name"]: t for t in registry["tools"] if t["server"] == "GEOX"}
    qc_tools = [t["tool_name"] for t in geox_tools.values() if t.get("action_mode") == "QC"]
    if qc_tools:
        result.pass_test(f"GEOX QC tools (Physics9): {qc_tools}")
    else:
        result.fail_test("GEOX: no QC tools")

    # 4.4: GEOX has REASON tools (ensemble subsurface candidates)
    reason_tools = [t["tool_name"] for t in geox_tools.values() if t.get("action_mode") == "REASON"]
    if reason_tools:
        result.pass_test(f"GEOX REASON tools (ensemble candidates): {reason_tools}")
    else:
        result.fail_test("GEOX: no REASON tools for subsurface generation")

    # 4.5: GEOX claim stages enforced (REGISTRY → INGEST → QC → INTERPRET)
    geox_stages = {t["tool_name"]: t.get("stage", "UNKNOWN") for t in geox_tools.values()}
    required_stages = {"REGISTRY", "INGEST", "QC", "INTERPRET"}
    found_stages = set(geox_stages.values()) & required_stages
    if found_stages == required_stages:
        result.pass_test(f"GEOX stages enforced: {found_stages}")
    else:
        result.fail_test(
            f"GEOX: incomplete stage coverage — missing {required_stages - found_stages}"
        )

    # 4.6: WEALTH macro/field tools provide physical-world veto data
    wealth_tools = [t["tool_name"] for t in registry["tools"] if t["server"] == "WEALTH"]
    macro = [t for t in wealth_tools if "macro" in t or "field" in t]
    if macro:
        result.pass_test(f"WEALTH macro/field tools (physical veto data): {macro}")
    else:
        result.warn_test("WEALTH: no macro/field tools")


# ─────────────────────────────────────────────────────────────────
# TEST 5: LAW 5 — ORGAN REPUBLIC (Separation of Powers)
# APEX: "No single organ should be able to complete the whole action
#         path alone."
# ─────────────────────────────────────────────────────────────────


def test_organ_separation_of_powers(result: Result):
    result.section("LAW 5: ORGAN REPUBLIC — Separation of Powers")

    registry = get_registry()
    routing = get_routing()
    tools = registry.get("tools", [])

    # 5.1: All 4 intelligence organs have tools
    servers = registry.get("tool_count", {})
    for organ in ["arifOS", "WEALTH", "GEOX", "WELL"]:
        count = servers.get(organ, 0)
        if count > 0:
            result.pass_test(f"{organ}: {count} tools deployed")
        else:
            result.fail_test(f"{organ}: no tools (or count=0)")

    # 5.2: arifOS has EXECUTE tool (routes to A-FORGE via A2A)
    execute_tools = [t for t in tools if t.get("action_mode") == "EXECUTE"]
    execute_servers = {t["server"]: t["tool_name"] for t in execute_tools}
    if "arifOS" in execute_servers:
        result.pass_test(
            f"EXECUTE tool on arifOS: {execute_servers.get('arifOS')} (A-FORGE is physical executor)"
        )
    else:
        result.fail_test("EXECUTE tool: not found on arifOS")

    # 5.3: Seal is only on arifOS and WEALTH
    seal_tools = [t for t in tools if "Seal" in t.get("action_mode", "")]
    seal_servers = set(t["server"] for t in seal_tools)
    allowed_seal = {"arifOS", "WEALTH"}
    unauthorized = seal_servers - allowed_seal
    if not unauthorized:
        result.pass_test(f"Seal action: correctly restricted to {allowed_seal}")
    else:
        result.fail_test(f"Seal action: unauthorized servers {unauthorized}")

    # 5.4: Routing covers all 4 intelligence organs
    routing_servers = set(routing.get("servers", {}).keys())
    required_organs = {"arifOS", "WEALTH", "GEOX", "WELL"}
    if required_organs <= routing_servers:
        result.pass_test(f"Routing: covers all 4 intelligence organs")
    else:
        result.fail_test(f"Routing: missing {required_organs - routing_servers}")


# ─────────────────────────────────────────────────────────────────
# TEST 6: LAW 6 — METABOLIC COGNITION (11-Stage Pipeline)
# APEX: "Skipping stages is not 'moving faster.' It is cognitive toxicity."
# F5 (Lyapunov stability / Peace²)
# ─────────────────────────────────────────────────────────────────


def test_metabolic_pipeline_integrity(result: Result):
    result.section("LAW 6: METABOLIC COGNITION — 11-Stage Pipeline Integrity")

    constitution = get_constitution()
    state_machine = constitution.get("state_machine", {})

    # 6.1: All 11 stages are defined
    required_stages = {"000", "111", "222", "333", "444", "555", "666", "777", "888", "889", "999"}
    defined_stages = set(state_machine.keys())
    if defined_stages >= required_stages:
        result.pass_test(f"Metabolic pipeline: all 11 stages defined ({len(defined_stages)} total)")
    else:
        missing = required_stages - defined_stages
        result.fail_test(f"Metabolic pipeline: missing stages {missing}")

    # 6.2: INIT (000) is defined as entry point
    if "000" in state_machine:
        init = state_machine["000"]
        if not init.get("can_skip", False) and init.get("mandatory", False):
            result.pass_test("Stage 000 (INIT): mandatory, cannot skip")
        else:
            result.warn_test(
                f"Stage 000: can_skip={init.get('can_skip')}, mandatory={init.get('mandatory')}"
            )
    else:
        result.fail_test("Stage 000 (INIT): NOT defined")

    # 6.3: JUDGE (888) is defined
    if "888" in state_machine:
        result.pass_test("Stage 888 (JUDGE): defined")
    else:
        result.fail_test("Stage 888 (JUDGE): NOT defined")

    # 6.4: VAULT (999) is defined
    if "999" in state_machine:
        result.pass_test("Stage 999 (VAULT): defined")
    else:
        result.fail_test("Stage 999 (VAULT): NOT defined")

    # 6.5: F5 (Lyapunov / Peace² / judgment-before-execution) codified
    f5 = find_floor(constitution, "F5")
    if f5:
        result.pass_test("F5 (Lyapunov Stability / Judgment-Before-Execution): codified")
    else:
        result.fail_test("F5 (Lyapunov Stability): NOT codified")


# ─────────────────────────────────────────────────────────────────
# TEST 7: LAW 7 — DECISION BIOLOGY (C0–C5 + Anti-Hantu)
# APEX: "A decision is not safe merely because it is logically correct.
#         It must also be metabolically survivable."
# F6 (Empathy/Rawlsian maximin), F9 (Anti-Hantu)
# ─────────────────────────────────────────────────────────────────


def test_decision_biology(result: Result):
    result.section("LAW 7: DECISION BIOLOGY — C0–C5 + Anti-Hantu")

    constitution = get_constitution()
    registry = get_registry()

    # 7.1: WELL has classification tools
    well_tools = [t["tool_name"] for t in registry["tools"] if t["server"] == "WELL"]
    classify = [t for t in well_tools if "classify" in t or "substrate" in t]
    if classify:
        result.pass_test(f"WELL classification tools: {classify}")
    else:
        result.fail_test("WELL: no classification tools")

    # 7.2: WELL has biological/machine assessment tools
    assess = [t for t in well_tools if "assess" in t or "metabolism" in t or "homeostasis" in t]
    if len(assess) >= 3:
        result.pass_test(f"WELL assessment tools: {assess}")
    else:
        result.warn_test(f"WELL: limited assessment coverage ({len(assess)} tools)")

    # 7.3: WELL has dignity guard (F6 constitutional enforcement)
    dignity = [t for t in well_tools if "dignity" in t]
    if dignity:
        result.pass_test(f"WELL dignity guard: {dignity}")
    else:
        result.fail_test("WELL: no dignity guard (F6 enforcement gap)")

    # 7.4: F6 (Empathy / Rawlsian maximin) codified
    f6 = find_floor(constitution, "F6")
    if f6:
        result.pass_test("F6 (Empathy / Rawlsian maximin): codified")
    else:
        result.fail_test("F6 (Empathy): NOT codified")

    # 7.5: F9 (Anti-Hantu) codified
    f9 = find_floor(constitution, "F9")
    if f9:
        result.pass_test("F9 (Anti-Hantu): codified")
    else:
        result.fail_test("F9 (Anti-Hantu): NOT codified")


# ─────────────────────────────────────────────────────────────────
# TEST 8: LAW 8 — TRUST THERMODYNAMICS (Ditempa Bukan Diberi)
# APEX: "Institutional trust is not a parameter. It must be thermodynamically
#         forged through verifiable, auditable, irreversible work."
# F1 (Amanah), F13 (Sovereign veto)
# ─────────────────────────────────────────────────────────────────


def test_trust_thermodynamics(result: Result):
    result.section("LAW 8: TRUST THERMODYNAMICS — Ditempa Bukan Diberi")

    constitution = get_constitution()
    registry = get_registry()

    # 8.1: F1 (Amanah / Truth-Before-Fluency) codified
    f1 = find_floor(constitution, "F1")
    if f1:
        result.pass_test("F1 (Amanah / Truth-Before-Fluency): codified")
    else:
        result.fail_test("F1 (Amanah): NOT codified")

    # 8.2: F13 (Sovereign veto) codified
    f13 = find_floor(constitution, "F13")
    if f13:
        result.pass_test("F13 (Sovereign/Human Veto): codified")
    else:
        result.fail_test("F13 (Sovereign Veto): NOT codified")

    # 8.3: All 5 receipt types defined
    receipt_path = REPO_ROOT / "contracts" / "runtime_receipt_schema.json"
    if receipt_path.exists():
        rs = load_json(receipt_path)
        rt = set(rs.get("receipt_types", {}).keys())
        required_rt = {
            "ACTION_RECEIPT",
            "VERDICT_RECEIPT",
            "EXECUTION_RECEIPT",
            "VAULT_SEAL_RECEIPT",
            "JOURNAL_RECEIPT",
        }
        if required_rt <= rt:
            result.pass_test(f"Receipt types: all 5 defined")
        else:
            result.fail_test(f"Receipt types: missing {required_rt - rt}")
    else:
        result.fail_test("runtime_receipt_schema.json not found")

    # 8.4: arifOS has session_init tool
    arifos_tools = [t["tool_name"] for t in registry["tools"] if t["server"] == "arifOS"]
    if any("session_init" in t for t in arifos_tools):
        result.pass_test("arifOS: session_init tool present (trust bootstrapping)")
    else:
        result.fail_test("arifOS: no session_init (trust bootstrap gap)")


# ─────────────────────────────────────────────────────────────────
# TEST 9: LAW 9 — ROUTING ORTHOGONALITY
# APEX: "OBSERVE ≠ REASON ≠ EXECUTE — you cannot 'just do it all at once.'"
# ─────────────────────────────────────────────────────────────────


def test_routing_orthogonality(result: Result):
    result.section("LAW 9: ROUTING ORTHOGONALITY — Composite Hallucination Prevention")

    routing = get_routing()
    ksm = routing.get("keyword_substrate_map", [])

    # 9.1: All 4 intelligence organs in keyword map
    organs_in_map = {e.get("organ") for e in ksm if isinstance(e, dict)}
    required_organs = {"arifOS", "WEALTH", "GEOX", "WELL"}
    if required_organs <= organs_in_map:
        result.pass_test(f"Keyword substrate map: all 4 organs present")
    else:
        result.fail_test(f"Keyword map: missing {required_organs - organs_in_map}")

    # 9.2: No keyword collisions across organs
    kw_map = {}
    for entry in ksm:
        if not isinstance(entry, dict):
            continue
        organ = entry.get("organ")
        for kw in entry.get("keywords", []):
            kw_l = kw.lower()
            if kw_l not in kw_map:
                kw_map[kw_l] = []
            kw_map[kw_l].append(organ)

    collisions = {k: v for k, v in kw_map.items() if len(v) > 1}
    if not collisions:
        result.pass_test("Routing: no keyword collisions across organs")
    else:
        result.warn_test(f"Routing: {len(collisions)} keyword(s) collide: {collisions}")

    # 9.3: WEALTH has financial keywords (prevents A-FORGE "run" false match)
    wealth_entry = next(
        (e for e in ksm if isinstance(e, dict) and e.get("organ") == "WEALTH"), None
    )
    if wealth_entry:
        kws = [k.lower() for k in wealth_entry.get("keywords", [])]
        if any("runway" in k or "cash" in k for k in kws):
            result.pass_test(
                "WEALTH: has runway/cash keywords (runway won't false-match A-FORGE 'run')"
            )
        else:
            result.warn_test("WEALTH: 'runway' keyword not found")

    # 9.4: WELL before GEOX (prevents "degrading" → geology false match)
    well_idx = next(
        (i for i, e in enumerate(ksm) if isinstance(e, dict) and e.get("organ") == "WELL"), None
    )
    geox_idx = next(
        (i for i, e in enumerate(ksm) if isinstance(e, dict) and e.get("organ") == "GEOX"), None
    )
    if well_idx is not None and geox_idx is not None:
        if well_idx < geox_idx:
            result.pass_test(
                "WELL ordered before GEOX in routing (degrading won't false-match geology)"
            )
        else:
            result.fail_test("WELL should be before GEOX in routing order")

    # 9.5: GEOX has physics/integrity keywords (verify physics integrity routing)
    geox_entry = next((e for e in ksm if isinstance(e, dict) and e.get("organ") == "GEOX"), None)
    if geox_entry:
        geox_kws = [k.lower() for k in geox_entry.get("keywords", [])]
        physics_kws = [k for k in geox_kws if "physics" in k or "integrity" in k or "verify" in k]
        if physics_kws:
            result.pass_test(f"GEOX physics/integrity keywords: {physics_kws}")
        else:
            result.fail_test("GEOX: no physics/integrity keyword (routing gap)")

    # 9.6: Task patterns defined (prevents composite one-step execution)
    patterns = routing.get("task_patterns", [])
    if len(patterns) >= 10:
        result.pass_test(f"Task patterns: {len(patterns)} defined")
    else:
        result.warn_test(f"Task patterns: only {len(patterns)}")


# ─────────────────────────────────────────────────────────────────
# TEST 10: LIVE SYSTEM
# ─────────────────────────────────────────────────────────────────


def test_live_system(result: Result):
    result.section("LIVE SYSTEM — Philosophy Runs on Metal")

    hosts = [
        ("arifOS", ARIFOS_HOST),
        ("WEALTH", WEALTH_HOST),
        ("GEOX", GEOX_HOST),
        ("WELL", WELL_HOST),
        ("A-FORGE", AFORGE_HOST),
    ]

    all_healthy = True
    for name, host in hosts:
        health = fetch_json(f"{host}/health")
        if health:
            status = health.get("status", health.get("verdict", "unknown"))
            result.pass_test(f"{name}: {status}")
        else:
            result.fail_test(f"{name}: unreachable — {host}")
            all_healthy = False

    if all_healthy:
        result.pass_test("All 5 organs: LIVE")


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────


def main():
    print("=" * 60)
    print("APEX Theory — Runtime Conformance Matrix")
    print("SEAL: DITEMPA BUKAN DIBERI")
    print("=" * 60)

    result = Result()

    test_law1_mechanical_bounding(result)
    test_law2_godel_lock(result)
    test_law3_hysteresis_ledger(result)
    test_law4_triwitness_physical_veto(result)
    test_organ_separation_of_powers(result)
    test_metabolic_pipeline_integrity(result)
    test_decision_biology(result)
    test_trust_thermodynamics(result)
    test_routing_orthogonality(result)
    test_live_system(result)

    sealed = result.summary()

    print()
    if sealed:
        print("🏛️  KERNEL SEAL: OPERATIONAL — All 9 APEX laws have runtime teeth.")
    else:
        print("⚠️  KERNEL SEAL: PARTIAL — some laws lack operational proof.")

    return sealed


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
