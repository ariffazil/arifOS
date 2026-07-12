import json

from arifosmcp.runtime import model_shadow_loader


def test_compiled_profiles_preserve_legacy_routing(monkeypatch, tmp_path):
    compiled = tmp_path / "compiled.json"
    compiled.write_text(json.dumps({"models": [{"model_key": "test-model"}]}))
    federation = tmp_path / "federation.json"
    federation.write_text(json.dumps({
        "censorship_registry": {
            "TEST_MODEL": {"status": "HARNESS_MONITORED"}
        }
    }))
    monkeypatch.setattr(model_shadow_loader, "_COMPILED_FEDERATION", compiled)
    monkeypatch.setattr(model_shadow_loader, "_FEDERATION_MODEL", federation)

    loader = model_shadow_loader.ModelShadowLoader()
    loader.load_all()

    assert loader.get_routing_constraints("test-model").status == "HARNESS_MONITORED"
