#!/usr/bin/env python3
"""verify_from_image.py — ENGINE↔POLICY bridge (F13 'ok go' 2026-09-05).

Pipeline: image → [faceid-venv] extract_edge.py (embedding+quality, air-gapped)
        → [system python] FaceVerifyService policy
          (multi-baseline max-K · band 0.25/0.42 · assertions · replay · rate-limit)
        → structured verdict (no biometric material on output).

Syed baselines seeded from identity_vault (2 conditions) with recorded
consent: test subject via Arif F13 gate 2026-09-05.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/root/arifOS")
from arifosmcp.biometric.face_verify import FaceVerifyService  # noqa: E402

VENV_PY = "/root/faceid-venv/bin/python"
EXTRACTOR = "/root/arifOS/arifosmcp/biometric/extract_edge.py"
# MEASURED band (F13 option 3): genuine cross-condition 0.47 observed →
# T_accept below it; impostor 0.0 → T_reject above noise. Middle = step-up.
BAND = {"t_accept": 0.42, "t_reject": 0.25}


def extract(image_path: str) -> dict:
    r = subprocess.run([VENV_PY, EXTRACTOR, image_path], capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"ok": False, "reason": "NO_FACE"}


def seed_service(svc: FaceVerifyService, token: str) -> dict:
    """Seed Syed's baselines from identity_vault vectors (consented test subject)."""
    seeds = json.load(open("/tmp/identity_vault_vectors.json"))
    n = 0
    for s in seeds:
        r = svc.enroll("syed_khairuddin", s["vector"],
                       "consent: test subject via Arif F13 gate 2026-09-05 (option-3 band)",
                       sovereign_token=token)
        n += 1 if r.get("ok") else 0
    return {"seeded": n}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--subject", default="syed_khairuddin")
    ap.add_argument("--nonce", required=True)
    ap.add_argument("--seed", action="store_true", help="seed baselines from identity_vault")
    args = ap.parse_args()

    token = ""  # seed via env when authorized
    import os
    token = os.environ.get("ARIFOS_BIOMETRIC_ENROLL_TOKEN", "")

    svc = FaceVerifyService(config={**BAND, "assertion_ttl_s": 240})
    if args.seed:
        if not token:
            print(json.dumps({"error": "seed requires ARIFOS_BIOMETRIC_ENROLL_TOKEN"}))
            return 1
        print(json.dumps(seed_service(svc, token)))

    ex = extract(args.image)
    if not ex.get("ok"):
        print(json.dumps({"decision": "RETRY", "assurance": "LOW", "reason_code": ex.get("reason", "NO_FACE")}))
        return 0
    r = svc.verify(
        claimed_subject_id=args.subject, purpose="session_unlock",
        session_id="bridge-cli", device_id="local", capture_nonce=args.nonce,
        embedding=ex["vector"], liveness=ex.get("liveness", "UNTESTED"),
        quality=ex.get("quality", {}), user_triggered=True,
    )
    print(json.dumps({"decision": r.decision, "assurance": r.assurance,
                      "reason_code": r.reason_code, "assertion_id": r.assertion_id,
                      "expires_at": r.expires_at}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
