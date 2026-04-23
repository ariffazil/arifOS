from __future__ import annotations

import json
import subprocess
import sys


def test_aki_contract_import_does_not_eager_load_sentence_transformers() -> None:
    code = """
import json
import sys

import core.enforcement.aki_contract

payload = {
    "sentence_transformers_loaded": "sentence_transformers" in sys.modules,
    "transformers_loaded": "transformers" in sys.modules,
    "torch_loaded": "torch" in sys.modules,
}
print(json.dumps(payload))
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    loaded = json.loads(completed.stdout.strip().splitlines()[-1])
    assert loaded == {
        "sentence_transformers_loaded": False,
        "transformers_loaded": False,
        "torch_loaded": False,
    }
