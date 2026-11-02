"""P1-5 acceptance — one canonical identity source + widened drift (repair-2026-11-01).

Audit (D1) saw six identity strings that never agree:
  registry 1!2026.10.11 · server.json 1!2026.10.17 · serverInfo kanon-<WALLCLOCK>+024ff90
  · canon.version 2026.10.30-024ff90 · deployed 024ff90 vs repo HEAD (moving) ·
  PyPI healthy/13-13/8 tools @2026-10-16 — and drift=false only because
  drift_scope=binary_build_stamps.

The measured HEAD-vs-deployed gap (OBS 2026-11-01): deployed stamp 024ff9005 is an
ORPHANED commit (on no branch; identical author/time/subject to main's 2ba6627eb) —
the stamp captured a pre-rewrite history line; divergence from merge-base
63cf8e46c (2026-04-23) is 4666 commits repo-side / 4660 deploy-side.

Fix contract under test:
  (1) arifosmcp.runtime.deployment_identity.canonical_identity() is THE source — deployed
      stamp, canonical repo HEAD, gap counts, reachability, stable build date.
  (2) serverInfo version renders from it with a STABLE stamp date (today the
      generator used datetime.now(), so the version string mutates daily).
  (3) build attestation widens drift to repo_head_vs_deployed + reachability.
  (4) identity drift is observable on THIS box (repo != deployed, orphan stamp).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("ARIFOS_PUBLIC_TOOL_PROFILE", "full")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")

import pytest  # noqa: E402  (after env defaults, before path insert)

# Box-coupling guard (replay 2026-11-02): t2/t4/t5/t6 assert facts that only
# exist on the deploy box — the /opt/arifos stamp chain and a non-empty git
# branch set. On a CI runner those paths are absent, so the assertions would
# red the suite for reasons unrelated to the code under test. The guard is
# env-overridable (ARIFOS_TEST_FORCE_CI=1) so both branches stay testable.
_STAMP_CHAIN = (
    "/opt/arifos/releases/deployed-commit",
    "/opt/arifos/app/.git_commit",
    "/root/arifOS/.git_commit",
)
_HAS_BOX_FACTS = (
    any(Path(p).exists() for p in _STAMP_CHAIN)
    and os.getenv("ARIFOS_TEST_FORCE_CI") != "1"
)
requires_box_facts = pytest.mark.skipif(
    not _HAS_BOX_FACTS,
    reason="box-coupled: deployed stamp chain absent (CI runner has no /opt/arifos)",
)

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_t1_identity_module_shape_and_widened_scope():
    from arifosmcp.runtime.deployment_identity import canonical_identity

    ident = canonical_identity()
    for key in ("deployed_commit", "repo_head_commit", "build_date", "version", "drift"):
        assert key in ident, f"t1 canonical_identity missing {key!r}: {list(ident)}"
    drift = ident["drift"]
    assert "repo_head_vs_deployed" in str(drift.get("scope", "")), (
        f"t1 drift scope must include repo_head_vs_deployed: {drift.get('scope')!r}"
    )
    for key in ("identity_drift", "in_sync"):
        assert key in drift, f"t1 drift missing {key!r}: {list(drift)}"
    gap = ident.get("repo_gap") or {}
    for key in ("repo_ahead_of_deployed", "deployed_ahead_of_repo"):
        assert key in gap, f"t1 repo_gap missing {key!r}: {list(gap)}"
    assert ident.get("deployed_reachable") in (True, False, None)


@requires_box_facts
def test_t2_version_uses_stable_stamp_date_not_wall_clock():
    from arifosmcp.runtime.deployment_identity import canonical_identity

    ident = canonical_identity()
    stamp = ident.get("stamp_path")
    assert stamp and Path(stamp).exists(), f"t2 no stamp file resolved: {stamp!r}"
    import datetime as _dt

    stamp_date = _dt.datetime.fromtimestamp(Path(stamp).stat().st_mtime, _dt.UTC).strftime(
        "%Y-%m-%d"
    )
    assert ident["build_date"] == stamp_date, (
        f"t2 build_date must come from the STABLE stamp mtime, not the clock: "
        f"{ident['build_date']} != {stamp_date}"
    )
    deployed7 = (ident["deployed_commit"] or "")[:7]
    expect = f"kanon-{stamp_date.replace('-', '.')}+{deployed7}"
    assert ident["version"] == expect, (
        f"t2 version must render kanon-<stamp-date>+<deployed>: got {ident['version']!r} want {expect!r}"
    )


def test_t3_serverinfo_rendered_from_canonical():
    from arifosmcp.runtime.deployment_identity import canonical_identity
    from arifosmcp.server import _DEPLOY_VERSION as server_version

    ident = canonical_identity()
    assert server_version == ident["version"], (
        f"t3 serverInfo version must render from canonical identity: "
        f"server={server_version!r} canonical={ident['version']!r}"
    )


@requires_box_facts
def test_t4_build_attestation_drift_widened():
    from arifosmcp.runtime.build import get_runtime_attestation
    from arifosmcp.runtime.deployment_identity import canonical_identity

    att = get_runtime_attestation()
    ident = canonical_identity()
    scope = str(att.get("drift_scope") or "")
    assert "repo_head_vs_deployed" in scope, (
        f"t4 drift_scope must widen to repo_head_vs_deployed: {scope!r}"
    )
    for key in ("repo_gap", "deployed_reachable", "identity_drift"):
        assert key in att, f"t4 attestation missing widened field {key!r}"
    # attestation must render repo_head from the canonical identity source
    assert att.get("repo_head_commit") == ident.get("repo_head_commit"), (
        f"t4 repo_head must come from canonical identity: "
        f"att={att.get('repo_head_commit')!r} ident={ident.get('repo_head_commit')!r}"
    )
    # widened semantics: whenever identity drift exists, the drift bool is True
    if ident["drift"].get("identity_drift"):
        assert att.get("drift") is True, (
            "t4 drift bool must be True when identity_drift (repo vs deployed / orphan stamp)"
        )


@requires_box_facts
def test_t5_identity_drift_observable_on_this_box():
    from arifosmcp.runtime.deployment_identity import canonical_identity

    ident = canonical_identity()
    # Invariant: both axes (deployed stamp vs repo HEAD) must be OBSERVED, not
    # hidden behind binary build stamps. Orphan-ness of a SPECIFIC stamp is a
    # dated observation, not an invariant — deploys re-point the stamp
    # (7371c84fb @ 2026-11-01 15:41 is reachable from main) and remote refs
    # make reachability a moving fact, so the orphan claim is asserted only
    # when the observation still holds.
    assert ident["deployed_commit"], "t5 deployed stamp must resolve"
    assert ident["repo_head_commit"], "t5 canonical repo HEAD must resolve"
    assert ident["drift"]["identity_drift"] is True, (
        f"t5 this box must show identity drift: {ident}"
    )
    assert ident["deployed_reachable"] in (True, False), (
        f"t5 reachability must be OBSERVED as a bool, not hidden: "
        f"reachable={ident['deployed_reachable']!r}"
    )
    if ident["deployed_reachable"] is False:
        assert "stamp_reachability" in (ident["drift"].get("reasons") or []), (
            f"t5 an unreachable stamp must surface as a drift reason: {ident['drift']}"
        )


@requires_box_facts
def test_t6_server_json_renders_from_canonical():
    """D1: registry manifest version must track the canonical stamp date."""
    import json as _json

    from arifosmcp.runtime.deployment_identity import canonical_identity

    ident = canonical_identity()
    manifest = _json.load(open(str(Path(__file__).parent.parent / "server.json")))
    expect = "1!" + ident["build_date"].replace("-", ".")
    assert manifest.get("version") == expect, (
        f"t6 server.json version must render from canonical identity: "
        f"{manifest.get('version')!r} != {expect!r}"
    )
    # README must claim the live 9-tool surface (stale 8-tool claim removed)
    readme = (Path(__file__).parent.parent / "README.md").read_text()
    assert "9 tools: arif_init" in readme, "t6 README must claim the live 9-tool surface"
    assert "# → 8 tools:" not in readme, "t6 README stale 8-tool claim must be gone"
