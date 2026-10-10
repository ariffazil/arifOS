"""resolve_skill_visibility.py — task-scoped skill-visibility resolution.

T2 build of the resolver proposal (/root/forge_work/resolver-p1-20261010/),
authorized under F13 APPROVE-1 (2026-10-10) with 888 adjudication conditions:
D1-C1 (held-out fixture set sha256-sealed BEFORE this branch existed —
HELDOUT_SEAL.md @ package repo fdbc603) and D2-(ii) (distinct name; the
pre-existing resolve_capabilities at capability_index/resolve.py projects
CapabilityRecord indexes — different input domain, different contract).

Input domain (consumer, never a registry — compiler rule 3):
  AAA capability-compiler family manifests   (families/*.yaml)
  alias ledger                                (references/ALIASES.yaml)
  Hermes skill-catalog snapshot               (loader-level denominator)

Contract properties (proposal §2, fixture-pinned by P1 20/20 + held-out H01-H10):
  • deterministic — pure function of request + immutable inputs; sorted output
  • explicit reasons on every visibility decision
  • no do_not_select alias selectable (intercepted → canonical + hidden)
  • missing metadata → unresolved/quarantine, never invented
  • abstention path (ABSTAIN_NO_MATCH) — refusing to invent an owner is correct
  • F11 policy (A): ties inside the ±1 band → AMBIGUOUS, both doors explicit,
    no auto-pick (888 ruling 2026-10-10)
  • F06: visibility:deferred jobs never contribute eager executors
    (consequence-class verbs deferred — POLICY_DEFERRED)
  • F16: single-word triggers require whole-token membership; multi-word
    triggers keep substring semantics
  • duplicates collapse to one canonical registration (instances_seen recorded)
  • visibility ≠ permission — auth_note; authority flows through the verdict
    chain (F15)

Known caveat carried from the proposal (F22, 2026-10-10): executor strings are
prose; a prose word can collide with a real catalog skill name (measured:
'constitutional'). This module implements the fixture-pinned semantics as-is;
executor-field hygiene (explicit name references) is a compiler/metadata-lane
fix, not a resolver change.

Scope of this build: function only. MCP surface registration, loader wiring,
and activation are separate later binaries (flag-off default off).

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Optional

import yaml

RESOLVER_VERSION = "kernel.resolve_skill_visibility.v1"
EAGER_CAP = 15

# Topology (Banda Haram: paths are water, not granite) — env-overridable, with
# the canonical federation paths as defaults. Held-out gate runs on defaults.
DEFAULT_FAMILIES_DIR = "/root/AAA/skills/aaa-capability-compiler/families"
DEFAULT_ALIASES_PATH = "/root/AAA/skills/aaa-capability-compiler/references/ALIASES.yaml"
DEFAULT_SNAPSHOT_PATH = "/root/.hermes/.skills_prompt_snapshot.json"

# Path segments that appear inside executor strings but are never skill names.
_JUNK_NAMES = frozenset(
    {"scripts", "references", "skills", "domains", "general", "core", "workflows"}
)

AUTH_NOTE = (
    "Visibility only. This resolver mints no permission; execution authority "
    "flows through the arifOS verdict chain."
)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def _script_leaves(s) -> list:
    return re.findall(r"[\w./-]+\.(?:sh|py|json|yaml)", str(s or ""))


def load_inputs(
    families_dir: Optional[str] = None,
    aliases_path: Optional[str] = None,
    snapshot_path: Optional[str] = None,
):
    """Load the three input populations. Read-only; no mutation of sources."""
    fdir = Path(families_dir or os.environ.get("ARIFOS_SKILL_FAMILIES_DIR", DEFAULT_FAMILIES_DIR))
    apath = Path(aliases_path or os.environ.get("ARIFOS_SKILL_ALIASES_PATH", DEFAULT_ALIASES_PATH))
    spath = Path(snapshot_path or os.environ.get("ARIFOS_SKILLS_SNAPSHOT_PATH", DEFAULT_SNAPSHOT_PATH))

    fams: dict = {}
    for f in sorted(fdir.glob("*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d and d.get("family"):
            fams[d["family"]] = d
    aliases = yaml.safe_load(apath.read_text()) or {}
    snap = json.loads(spath.read_text())
    snap_id = hashlib.sha256(spath.read_bytes()).hexdigest()[:16]
    return fams, aliases, snap, snap_id


def _catalog_index(snap: dict) -> dict:
    """skill_name → [entries]; canonical instance = one whose category
    contains 'domains/' (domains-tree-as-category design, per ALIASES note)."""
    idx: dict = {}
    for s in snap.get("skills", []):
        idx.setdefault(s.get("skill_name", ""), []).append(s)
    return idx


def _pick_canonical_instance(entries: list):
    dom = [e for e in entries if "domains/" in (e.get("category") or "")]
    return sorted(dom or entries, key=lambda e: e.get("category", ""))[0]


def _score_families(task_n: str, fams: dict):
    """F16 rule: multi-word triggers substring-match; single-word triggers
    require whole-token membership. Returns per-family (score, job hits)."""
    tokens = set(task_n.split())
    scores, hits = {}, {}
    for fname, fam in fams.items():
        total, fhits = 0, []
        for job_key, job in (fam.get("jobs") or {}).items():
            for trig in job.get("triggers") or []:
                t = _norm(trig)
                if not t:
                    continue
                if (" " in t and t in task_n) or (" " not in t and t in tokens):
                    total += 2 if " " in t else 1
                    fhits.append((job_key, trig))
        scores[fname] = total
        hits[fname] = fhits
    return scores, hits


def _executor_names(executor: str, cat_names) -> list:
    """Catalog skill names referenced by an executor string (path segments and
    script leaves are not skill names; short/junk names filtered)."""
    found = []
    en = _norm(executor)
    for name in cat_names:
        nn = _norm(name)
        if not name or len(nn) <= 5 or nn in _JUNK_NAMES:
            continue
        if nn in en:
            found.append(name)
    return sorted(found, key=len, reverse=True)


def resolve_skill_visibility(
    task: str,
    agent_id: str = "hermes",
    role: str = "FULL",
    domains: Optional[list] = None,
    *,
    inputs: Optional[tuple] = None,
) -> dict:
    """Resolve the task-scoped skill-visibility manifest.

    Pure function of (task, agent_id, role, domains, inputs). Returns the
    contract manifest: status / eager / deferred / hidden /
    duplicates_collapsed / unresolved / metadata_partial / auth_note.
    """
    if inputs is not None:
        fams, aliases, snap, snap_id = inputs
    else:  # module-level load cache (deterministic per process; tests inject)
        global _INPUTS_CACHE
        if "_INPUTS_CACHE" not in globals() or _INPUTS_CACHE is None:
            _INPUTS_CACHE = load_inputs()
        fams, aliases, snap, snap_id = _INPUTS_CACHE

    idx = _catalog_index(snap)
    cat_names = set(idx.keys())
    task_n = _norm(task)

    out: dict = {
        "resolver_version": RESOLVER_VERSION,
        "source_snapshot": {"sha256_16": snap_id, "catalog_entries": len(snap.get("skills", [])),
                            "distinct_names": len(cat_names)},
        "request_context": {"task": task, "agent_id": agent_id,
                            "role": role, "domains": list(domains or [])},
        "status": None, "eager": [], "deferred": [], "hidden": {},
        "canonical_owner": None, "duplicates_collapsed": {},
        "unresolved": [], "metadata_partial": False,
        "auth_note": AUTH_NOTE,
    }
    eager: list = []
    hidden: dict = {}

    def add_eager(name, reason, source=None):
        if name and name not in [e["name"] for e in eager]:
            entries = idx.get(name, [])
            inst = _pick_canonical_instance(entries) if entries else None
            dup = len(entries)
            if dup > 1:
                out["duplicates_collapsed"][name] = dup
                hidden.setdefault(name, "DUPLICATE_REGISTRATION")
            eager.append({"name": name,
                          "source": source or (inst.get("category") if inst else None),
                          "reason": reason, "instances_seen": dup or 1})

    # ---- 1. alias interception (before family scoring; canonical wins) ----
    alias_hits = []
    for alias, meta in sorted(aliases.items()):
        if _norm(alias) in task_n:
            alias_hits.append((alias, meta))
    for alias, meta in alias_hits:
        hidden[alias] = "ALIAS_DO_NOT_SELECT"
        canon = str((meta or {}).get("canonical") or "")
        if canon and "/" in canon:
            add_eager(Path(canon).name, "ALIAS_CANONICALIZED", source=canon)
        elif canon:
            add_eager(canon, "ALIAS_CANONICALIZED")

    # ---- 2. family scoring (F11 policy A: ±1 tie band → explicit AMBIGUOUS) ----
    scores, hits = _score_families(task_n, fams)
    ranked = sorted(((s, f) for f, s in scores.items() if s > 0),
                    key=lambda x: (-x[0], x[1]))
    if ranked:
        top = ranked[0][0]
        tied = [f for s, f in ranked if s >= top - 1 and s > 0]
        if len(tied) > 1:
            out["status"] = "AMBIGUOUS"
            for f in sorted(tied):
                add_eager(Path(fams[f]["canonical_owner"]).name,
                          "AMBIGUOUS_TIE", source=fams[f]["canonical_owner"])
            out["unresolved"].append({"kind": "ambiguity", "candidates": sorted(tied)})
        else:
            fam = fams[tied[0]]
            out["status"] = "RESOLVED"
            door = Path(fam["canonical_owner"]).name
            out["canonical_owner"] = fam["canonical_owner"]
            if not Path(fam["canonical_owner"]).is_dir():
                out["status"] = "UNKNOWN_QUARANTINE"
                out["unresolved"].append({"kind": "door_missing", "family": tied[0]})
                return _finish(out, eager, hidden, idx)
            if fam.get("status") == "ALIAS_PENDING_MERGE":
                out["metadata_partial"] = True
            matched_jobs = {j for j, _ in hits[tied[0]]}
            dns = {a for a, m in aliases.items()
                   if (m or {}).get("do_not_select")}
            job_infos = []
            for jk, job in sorted((fam.get("jobs") or {}).items()):
                ex_names = _executor_names(str(job.get("executor", "")), cat_names)
                if not ex_names:
                    out["unresolved"].append(
                        {"kind": "executor_unresolved", "job": jk})
                    continue
                leaves = sorted(set(_script_leaves(job.get("executor"))
                                    + _script_leaves(job.get("verify") or "")))
                job_infos.append({
                    "jk": jk, "ex": ex_names, "leaves": leaves,
                    "mand": bool(job.get("verify")) or jk in matched_jobs,
                    "vis": str(job.get("visibility") or "eager"),
                })
            all_leaves = sorted({l for ji in job_infos for l in ji["leaves"]})
            door_src = fam["canonical_owner"] + (
                "|scripts:" + ",".join(all_leaves) if all_leaves else "")
            add_eager(door, "FAMILY_DOOR", source=door_src)
            for ji in job_infos:
                src = fam["canonical_owner"] + (
                    "|scripts:" + ",".join(ji["leaves"])
                    if ji["leaves"] else "")
                reason = ("JOB_EXECUTOR" if ji["jk"] in matched_jobs
                          else "FAMILY_MEMBER")
                for n in ji["ex"]:
                    if n == door:
                        continue
                    if n in dns:
                        hidden[n] = "ALIAS_DO_NOT_SELECT"
                        continue
                    if ji["vis"] == "deferred":  # F06: never eager
                        if n not in [d["name"] for d in out["deferred"]]:
                            out["deferred"].append(
                                {"name": n, "reason": "POLICY_DEFERRED"})
                        continue
                    if ji["mand"]:
                        add_eager(n, reason + "+MANDATORY", source=src)
                    elif len(eager) < EAGER_CAP:
                        add_eager(n, reason, source=src)
                    else:
                        out["deferred"].append({"name": n, "reason": "EAGER_CAP"})
        for s, f in ranked[1:]:  # sibling doors stay discoverable, not eager
            d = Path(fams[f]["canonical_owner"]).name
            if d not in [e["name"] for e in eager]:
                out["deferred"].append({"name": d, "reason": "SIBLING_FAMILY"})
    elif alias_hits:
        out["status"] = "RESOLVED" if eager else "UNKNOWN_QUARANTINE"
        out["canonical_owner"] = (eager[0]["source"] if eager and
                                  eager[0]["source"] and
                                  str(eager[0]["source"]).startswith("/")
                                  else None)
    else:
        # ---- 3. plain name-direct (longest catalog-name match in task) ----
        direct = sorted((n for n in cat_names
                         if n and _norm(n) in task_n and len(_norm(n)) > 3),
                        key=len, reverse=True)
        if direct:
            name = direct[0]
            out["status"] = "RESOLVED"
            out["canonical_owner"] = None  # family-unmapped skill
            add_eager(name, "NAME_DIRECT")
        else:
            out["status"] = "ABSTAIN_NO_MATCH"
            out["unresolved"].append({"kind": "no_capability_match", "task": task})

    return _finish(out, eager, hidden, idx)


def _finish(out: dict, eager: list, hidden: dict, idx: dict) -> dict:
    eager_names = {e["name"] for e in out["eager"]}
    deferred_names = {d["name"] for d in out["deferred"]}
    out["hidden"] = dict(hidden)
    out["hidden_population"] = len(idx) - len(eager_names | deferred_names)
    out["eager"] = sorted(eager, key=lambda e: e["name"])
    out["deferred"] = sorted(out["deferred"], key=lambda d: d["name"])
    return out


_INPUTS_CACHE = None
