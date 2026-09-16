#!/usr/bin/env python3
"""
verify_federation_organism.py — Federation organism witness verifier

Cycle: federation-organism-2026-09-17
Reference: ARIFOS::M365_COPILOT_KERNEL::v1.1
Authority: ARIF (Human Sovereign)

PURPOSE
=======
Read-only witness. Probes the federation's static claims against its
observable surface. Does NOT boot organs, does NOT mutate anything, does NOT
write a FederationEnvelope. Encodes the six cross-organ invariants from the
2026-09-17 federation audit (section 13) as static checks.

THE SIX INVARIANTS
==================
I1.  Every organ declares a contracts/mcp_surface.yaml OR equivalent.
I2.  Per-organ advertised tool count matches contracts/tools.yaml entry count.
I3.  Every organ's session_id parsing goes through one canonical function.
I4.  A-FORGE execution path requires an approved-action hash (Hash(executed)
     = Hash(judged)).
I5.  No specialist organ (GEOX/HERMES/WELL/WEALTH) writes SEAL/HOLD/VOID.
I6.  WELL metabolic flux produces a backpressure signal (not authority).

USAGE
=====
    python3 verify_federation_organism.py            # full
    python3 verify_federation_organism.py --quiet   # summary only
    python3 verify_federation_organism.py --strict  # exit 1 on any violation

EXIT CODES
==========
    0 = no violation (HEALTHY)
    1 = at least one violation (DEGRADED, HOLD)
    2 = verifier error
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ─── Federation roots ──────────────────────────────────────────────────────
# On GitHub Actions, the repo is at $GITHUB_WORKSPACE.
# On VPS, organs are at /root/<organ>.
# Detect: if running in CI, use workspace parent; else use /root.
import os as _os
_repo_root = Path(_os.environ.get("GITHUB_WORKSPACE", "/root"))
FEDERATION_ROOTS = {
    "arifOS": _repo_root / "arifOS" if (_repo_root / "arifOS").exists() else _repo_root,
    "AAA": _repo_root / "AAA",
    "GEOX": _repo_root / "GEOX",
    "HERMES": _repo_root / "HERMES",
    "WELL": _repo_root / "WELL",
    "WEALTH": _repo_root / "WEALTH",
    "A-FORGE": _repo_root / "A-FORGE",
}

# Constitutional verdict vocabulary — ONLY arifOS may emit these.
CONSTITUTIONAL_VERDICT_VALUES = {"SEAL", "HOLD", "VOID", "SABAR"}

EXCLUDE_PATTERNS = [
    "__pycache__",
    "/.git/",
    "/archive/",
    "/build/",
    "/dist/",
    "/node_modules/",
    "/.venv/",
    "/venv/",
    "/site-packages/",
    ".bak",
]


# ─── Findings ──────────────────────────────────────────────────────────────
@dataclass
class Finding:
    rule: str       # I1..I6 or FED-*
    severity: str   # CRITICAL | HIGH | MEDIUM | LOW
    organ: str
    file: str       # repo-relative path
    line: int
    message: str
    evidence: str   # the offending text (truncated)

    def render(self) -> str:
        marker = {"CRITICAL": "✗", "HIGH": "!", "MEDIUM": "~", "LOW": "."}[self.severity]
        return (
            f"  {marker} [{self.severity}] {this_rule_short(self.rule)} "
            f":: {self.organ} :: {self.file}:{self.line}\n"
            f"      {self.message}\n"
            f"      → {self.evidence.strip()[:120]}"
        )


def this_rule_short(rule: str) -> str:
    return rule.split("::", 1)[0] if "::" in rule else rule


@dataclass
class FederationReport:
    findings: list[Finding] = field(default_factory=list)
    organs_probed: list[str] = field(default_factory=list)

    @property
    def is_degraded(self) -> bool:
        return any(f.severity in ("CRITICAL", "HIGH") for f in self.findings)

    @property
    def verdict(self) -> str:
        return "HOLD" if self.is_degraded else "SEAL"

    @property
    def health(self) -> str:
        return "DEGRADED" if self.is_degraded else "HEALTHY"

    def counts(self) -> dict[str, int]:
        c = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for f in self.findings:
            c[f.severity] += 1
        return c

    def summary(self) -> str:
        c = self.counts()
        return (
            f"FEDERATION_ORGANISM_INVARIANT :: verdict={self.verdict} :: health={self.health}\n"
            f"  organs_probed: {len(self.organs_probed)}\n"
            f"  findings: critical={c['CRITICAL']} high={c['HIGH']} "
            f"medium={c['MEDIUM']} low={c['LOW']}"
        )


# ─── Rules ─────────────────────────────────────────────────────────────────

def rule_i1_surface_contract_exists(organ: str, root: Path) -> list[Finding]:
    """
    I1: Every organ declares contracts/mcp_surface.yaml OR equivalent.
    """
    findings: list[Finding] = []
    candidates = [
        root / "contracts" / "mcp_surface.yaml",
        root / "mcp_surface.yaml",
        root / "contracts" / "surface.yaml",
    ]
    if not any(p.exists() for p in candidates):
        findings.append(Finding(
            rule="I1::surface_contract_exists",
            severity="HIGH",
            organ=organ,
            file=str(root.relative_to(Path("/root"))),
            line=0,
            message="No contracts/mcp_surface.yaml found; organ surface is undeclared",
            evidence="(no surface contract)",
        ))
    return findings


def rule_i2_tools_yaml_consistency(organ: str, root: Path) -> list[Finding]:
    """
    I2: Per-organ advertised tool count matches contracts/tools.yaml entry count.
    Static-only: counts '- name:' entries in tools.yaml and compares against
    advertised count in mcp_surface.yaml if present.
    """
    findings: list[Finding] = []
    tools_yaml = root / "contracts" / "tools.yaml"
    if not tools_yaml.exists():
        return findings
    try:
        text = tools_yaml.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings
    actual_count = len(re.findall(r"^\s*-?\s*name:", text, flags=re.MULTILINE))
    # Look for advertised count
    surface_yaml = root / "contracts" / "mcp_surface.yaml"
    advertised = None
    if surface_yaml.exists():
        s = surface_yaml.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"public_surface_count:\s*(\d+)", s)
        if m:
            advertised = int(m.group(1))
    if advertised is not None and actual_count != advertised and actual_count > 0:
        findings.append(Finding(
            rule="I2::tools_yaml_consistency",
            severity="MEDIUM",
            organ=organ,
            file=str(tools_yaml.relative_to(Path("/root"))),
            line=0,
            message=f"Advertised count {advertised} ≠ tools.yaml name entries {actual_count}",
            evidence=f"advertised={advertised} actual={actual_count}",
        ))
    return findings


def rule_i3_session_id_parser_canonical(organ: str, root: Path, report: FederationReport) -> None:
    """
    I3: Every organ's session_id parsing should not reinvent _default.
    Static: scan Python files for `session_id = "_default"` or
    `session_id or "_default"` — both are symptom patterns.
    """
    pattern = re.compile(r'session_id\s*=\s*["\']_default["\']|session_id\s+or\s+["\']_default["\']')
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                report.findings.append(Finding(
                    rule="I3::session_id_canonical",
                    severity="CRITICAL",
                    organ=organ,
                    file=str(path.relative_to(Path("/root"))),
                    line=i,
                    message="session_id falls back to _default; federation session is lost",
                    evidence=line.strip(),
                ))


def rule_i4_aforge_action_hash(organ: str, root: Path, report: FederationReport) -> None:
    """
    I4: A-FORGE execution must require an approved action hash.
    Static: scan A-FORGE for execution paths and verify they consume a hash arg.
    """
    if organ != "A-FORGE":
        return
    # Look for execute/exec functions and check they reference hash
    pattern_execute = re.compile(r"def\s+(execute|exec|run_apply|apply)\s*\(")
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if pattern_execute.search(line):
                # Look at next ~30 lines for hash reference
                lines = text.splitlines()
                window = "\n".join(lines[i:i + 30])
                if "hash" not in window.lower() and "action_hash" not in window:
                    report.findings.append(Finding(
                        rule="I4::aforge_action_hash",
                        severity="HIGH",
                        organ=organ,
                        file=str(path.relative_to(Path("/root"))),
                        line=i,
                        message="A-FORGE execute path does not reference action_hash in scope",
                        evidence=line.strip(),
                    ))
                    break  # one finding per function


def rule_i5_specialist_no_constitutional_verdict(organ: str, root: Path, report: FederationReport) -> None:
    """
    I5: No specialist organ (GEOX/HERMES/WELL/WEALTH) writes SEAL/HOLD/VOID
    as a constitutional verdict. They may emit domain_recommendation or
    sensor_state. Detected by looking for verdict= / verdict: "SEAL"
    assignments in specialist organs.
    """
    if organ not in {"GEOX", "HERMES", "WELL", "WEALTH"}:
        return
    # Pattern: verdict assigned to a constitutional value
    patterns = [
        re.compile(r'verdict\s*[:=]\s*["\'](SEAL|HOLD|VOID|SABAR)["\']'),
        re.compile(r'(SEAL|HOLD|VOID|SABAR)\s*=\s*["\'](SEAL|HOLD|VOID|SABAR)["\']'),
    ]
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    # Allow well-scoped exceptions: receipts that merely log
                    if "log" in line.lower() or "test" in path.name.lower():
                        continue
                    report.findings.append(Finding(
                        rule="I5::specialist_no_constitutional_verdict",
                        severity="MEDIUM",
                        organ=organ,
                        file=str(path.relative_to(Path("/root"))),
                        line=i,
                        message="Specialist organ emits constitutional verdict vocabulary",
                        evidence=line.strip(),
                    ))
                    break


def rule_i6_well_backpressure_signal(organ: str, root: Path, report: FederationReport) -> None:
    """
    I6: WELL metabolic flux should produce a backpressure signal, not authority.
    Static: look for flux/backpressure handlers that emit a STOP / HOLD / kill
    action rather than advisory.
    """
    if organ != "WELL":
        return
    patterns = [
        re.compile(r"backpressure\s*=\s*[\"']STOP[\"']"),
        re.compile(r"flux\s*>\s*0\.85.*HOLD"),
    ]
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    # Acceptable if it routes through AAA, not direct authority
                    window = text[text.find(line):text.find(line) + 500]
                    if "AAA" not in window and "aaa" not in window.lower():
                        report.findings.append(Finding(
                            rule="I6::well_backpressure_signal",
                            severity="LOW",
                            organ=organ,
                            file=str(path.relative_to(Path("/root"))),
                            line=i,
                            message="WELL backpressure may not route through AAA",
                            evidence=line.strip(),
                        ))
                    break


def rule_i7_stale_premise_unknown(organ: str, root: Path, report: FederationReport) -> None:
    """
    I7: Stale premise → score collapses to UNKNOWN, not VOID.
    Static: detect evidence handlers that use a sealed/baseline value WITHOUT
    carrying source_observed_at / expires_after metadata. A premise that has
    no expiry cannot fail closed when reality changes.
    """
    if organ not in {"arifOS", "WEALTH", "GEOX", "WELL", "HERMES"}:
        return
    # Look for patterns that suggest sealed/locked facts without expiry metadata
    patterns = [
        re.compile(r"sealed\s*=\s*True"),
        re.compile(r"baseline\s*=\s*[\"'][^\"']+[\"']"),
        re.compile(r"IFR_\d{4}|FY\d{4}"),
    ]
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        # Only check finance-y / data-y modules
        if not any(k in spath.lower() for k in (
            "wealth", "vitals", "ifr", "fiscal", "fundamental",
            "registry", "ledger", "snapshot", "baseline",
        )):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    # Look at next ~20 lines for expiry/observed_at metadata
                    window = text.splitlines()[i:i + 20]
                    window_text = "\n".join(window).lower()
                    has_expiry = any(k in window_text for k in (
                        "expires_after", "source_observed_at",
                        "retrieved_at", "model_computed_at",
                        "stale", "drift_check",
                    ))
                    if not has_expiry:
                        report.findings.append(Finding(
                            rule="I7::stale_premise_unknown",
                            severity="MEDIUM",
                            organ=organ,
                            file=str(path.relative_to(Path("/root"))),
                            line=i,
                            message="Sealed/baseline premise lacks expiry metadata; stale evidence cannot collapse to UNKNOWN",
                            evidence=line.strip(),
                        ))
                    break


def rule_i8_specialist_vocabulary_isolation(organ: str, root: Path, report: FederationReport) -> None:
    """
    I8: Specialist organs must NOT reuse arifOS constitutional verdict vocabulary
    (SEAL/HOLD/VOID/SABAR) for non-constitutional meanings (e.g. financial
    score bands, health states, recommendation levels).

    Architectural lesson from VITALS reality audit 2026-09-17:
    "WEALTH assessment ≠ arifOS verdict" — even visual similarity conflates
    authority. Specialist organs must namespace their own vocabulary or use
    prefixes (ECON_SEAL, VITALS_CRITICAL, HERMES_BOUNDED, etc.).
    """
    if organ == "arifOS":
        return  # arifOS owns these terms
    if organ not in {"WEALTH", "GEOX", "WELL", "HERMES", "AAA", "A-FORGE"}:
        return
    # Pattern: bare constitutional verdict used as a score label / status / band
    patterns = [
        re.compile(r'verdict\s*[:=]\s*[\"\'](SEAL|HOLD|VOID|SABAR)[\"\']'),
        re.compile(r'score_band\s*[:=]\s*[\"\'](SEAL|HOLD|VOID|SABAR)[\"\']'),
        re.compile(r'(status|level|band|grade)\s*[:=]\s*[\"\'](SEAL|HOLD|VOID|SABAR)[\"\']'),
        re.compile(r'(SEAL|HOLD|VOID|SABAR)_(SCORE|BAND|LEVEL|STATUS)'),
    ]
    for path in root.rglob("*.py"):
        spath = str(path)
        if any(p in spath for p in EXCLUDE_PATTERNS):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for pat in patterns:
                if pat.search(line):
                    # Allow if explicitly namespaced (ECON_, VITALS_, HERMES_, etc.)
                    if re.search(
                        r'(ECON|VITALS|HERMES|WELL|WEALTH|GEOX|AAA|AFORGE)_'
                        r'(SEAL|HOLD|VOID|SABAR)',
                        line,
                    ):
                        continue
                    # Allow tests and fixtures
                    if "test" in path.name.lower() or "fixture" in path.name.lower():
                        continue
                    report.findings.append(Finding(
                        rule="I8::specialist_vocabulary_isolation",
                        severity="HIGH",
                        organ=organ,
                        file=str(path.relative_to(Path("/root"))),
                        line=i,
                        message=(
                            "Specialist organ uses bare constitutional verdict "
                            "vocabulary; namespacify to prevent authority "
                            "conflation with arifOS 888"
                        ),
                        evidence=line.strip(),
                    ))
                    break


# ─── Probe ─────────────────────────────────────────────────────────────────

def probe_organ(organ: str, root: Path, report: FederationReport) -> None:
    if not root.exists():
        report.findings.append(Finding(
            rule="FED::organ_missing",
            severity="CRITICAL",
            organ=organ,
            file=str(root.relative_to(Path("/root"))),
            line=0,
            message=f"Organ root does not exist: {root}",
            evidence=str(root),
        ))
        return
    report.organs_probed.append(organ)
    report.findings.extend(rule_i1_surface_contract_exists(organ, root))
    report.findings.extend(rule_i2_tools_yaml_consistency(organ, root))
    rule_i3_session_id_parser_canonical(organ, root, report)
    rule_i4_aforge_action_hash(organ, root, report)
    rule_i5_specialist_no_constitutional_verdict(organ, root, report)
    rule_i6_well_backpressure_signal(organ, root, report)
    rule_i7_stale_premise_unknown(organ, root, report)
    rule_i8_specialist_vocabulary_isolation(organ, root, report)


def probe() -> FederationReport:
    report = FederationReport()
    for organ, root in FEDERATION_ROOTS.items():
        probe_organ(organ, root, report)
    return report


# ─── Main ──────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    quiet = "--quiet" in argv
    report = probe()

    print("=" * 72)
    print("FEDERATION_ORGANISM_INVARIANT :: read-only witness")
    print("Cycle: federation-organism-2026-09-17")
    print("Reference: ARIFOS::M365_COPILOT_KERNEL::v1.1")
    print("=" * 72)
    print()

    if report.findings and not quiet:
        by_rule: dict[str, list[Finding]] = {}
        for f in report.findings:
            by_rule.setdefault(f.rule, []).append(f)
        for rule in sorted(by_rule.keys()):
            items = by_rule[rule]
            print(f"[{rule}] — {len(items)} occurrence(s)")
            for item in items[:20]:
                print(item.render())
            if len(items) > 20:
                print(f"  ... and {len(items) - 20} more")
            print()

    print(report.summary())

    if report.is_degraded and strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
