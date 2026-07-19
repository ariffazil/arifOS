"""SLSA v1.0 provenance tests."""
from arifosmcp.core.protocols.slsa import generate_provenance, ci_provenance, material_digest


def test_generate_provenance_minimal():
    p = generate_provenance(
        builder_id="https://github.com/ariffazil/arifOS/.github/workflows/ci.yml@refs/heads/main",
        build_type="https://slsa.dev/provenance/v1",
        materials=[],
    )
    assert p["_type"] == "https://in-toto.io/Statement/v1"
    assert p["predicateType"] == "https://slsa.dev/provenance/v1"
    assert "buildDefinition" in p["predicate"]
    assert "runDetails" in p["predicate"]

def test_ci_provenance():
    p = ci_provenance(
        repo="ariffazil/arifOS",
        workflow=".github/workflows/01-unified-ci.yml",
        ref="refs/heads/main",
        sha="abc123def456",
        materials=[{"uri": "git+https://github.com/ariffazil/arifOS", "digest": {"sha1": "abc123"}}],
    )
    assert "buildInvocationId" in p["predicate"]["runDetails"]["buildMetadata"]
    assert p["predicate"]["runDetails"]["builder"]["id"].startswith("https://github.com")

def test_material_digest():
    d = material_digest("git+https://github.com/ariffazil/arifOS", b"test")
    assert d.startswith("sha256:")
    assert len(d) == 71  # "sha256:" + 64 hex chars

def test_provenance_reproducible_flag():
    p = ci_provenance("ariffazil/test", "ci.yml", "refs/heads/main", "abc123")
    assert p["predicate"]["runDetails"]["buildMetadata"]["reproducible"] is False  # not in CI env
