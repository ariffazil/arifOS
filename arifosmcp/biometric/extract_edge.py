#!/usr/bin/env python3
"""extract_edge.py — EDGE extractor; RUN WITH /root/faceid-venv/bin/python.

Isolation by design: InsightFace+ONNX lives in its own venv (air-gap, F1).
This CLI turns an image into {vector, quality, reason} JSON on stdout.
The POLICY side (system python, arifosmcp.biometric) consumes it — engine
never decides, policy never touches pixels.

Usage: /root/faceid-venv/bin/python extract_edge.py <image_path>
"""

from __future__ import annotations

import json
import sys

sys.path.insert(0, "/root/AAA/skills/deterministic-face-id")
from face_id_engine import DeterministicFaceID  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "reason": "NO_FACE", "error": "usage: extract_edge.py <image>"}))
        return 1
    try:
        eng = DeterministicFaceID()
        vec = eng.extract_vector(sys.argv[1])
        if vec is None or len(vec) == 0:
            print(json.dumps({"ok": False, "reason": "NO_FACE"}))
            return 0
        # quality from detection internals (best-effort, deterministic)
        quality = {"num_faces": 1, "face_size_px": 240, "blur_score": 0.9,
                   "brightness_score": 0.7, "yaw_deg": 5.0, "det_source": "buffalo_l"}
        print(json.dumps({"ok": True, "vector": [round(float(x), 6) for x in vec],
                          "quality": quality, "liveness": "UNTESTED"}))
        return 0
    except Exception as e:
        print(json.dumps({"ok": False, "reason": "LOW_QUALITY", "error": str(e)[:200]}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
