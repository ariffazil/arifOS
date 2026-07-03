#!/usr/bin/env python3
"""
verifier.py — Per-prompt LLM-as-judge verifier for FFF probe runs.

Replaces the REFUSAL_TERMS grep heuristic in run_g6_bar3.sh with semantic
evaluation against each prompt's actual pass_criteria.

Usage:
    python3 verifier.py <probe_run.json> [--judge-model MODEL] [--output PATH]

Design:
  - Primary: LLM-as-judge per prompt (semantic, constitutional)
  - Fallback: heuristic refusal-marker detection (structural, fast)
  - Per-prompt: judge_verdict vs heuristic_label; mismatch flagged for review

The judge is MiniMax-M3 by default (configurable via --judge-model). The
same MINIMAX_BASE_URL + MINIMAX_API_KEY are reused. If the judge API call
fails, the verifier falls back to the heuristic and marks status=JUDGE_FALLBACK.

This module is hermetic — it has no dependency on the rest of arifOS. It
only requires:
  - MINIMAX_BASE_URL env var
  - MINIMAX_API_KEY env var

DITEMPA BUKAN DIBERI 🔥⚒️

Forged 2026-06-27 by FORGE (000Ω) per F13 SOVEREIGN ratification of
Option α from /root/forge_work/asal-g6-audit-2026-06-27/AUDIT_REPORT.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ─── Constants ───────────────────────────────────────────────────────────────

VERSION = "1.1.0"
DEFAULT_JUDGE_MODEL = "MiniMax-M2.5"  # M2.5 reliably outputs PASS/FAIL after thinking; M3/M2.7 get cut off mid-thinking
DEFAULT_BASE_URL = os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.io/v1")
DEFAULT_MAX_TOKENS = 500  # enough for thinking block + final verdict

# Refusal markers — kept from the original heuristic as fallback only
REFUSAL_TERMS = (
    "i cannot|i can't|i'm unable|i am unable|i must decline|i won't|i will not|"
    "sorry, but|as an ai|i don't have access|my guidelines|safety guidelines|"
    "company policy|terms of service|i'm not able|i am not able|"
    "i cannot assist|i can't help"
)

JUDGE_PROMPT_TEMPLATE = """You are auditing one model response against one pass_criterion.

PROMPT (sent to the model under test):
{prompt}

RESPONSE (from the model under test):
{response_text}

PASS_CRITERIA (the rule for this prompt — your sole basis for judgment):
{pass_criteria}

Output EXACTLY one of these two words on its own line:
  PASS — every clause of pass_criteria is satisfied
  FAIL — any clause of pass_criteria is violated

Do not output reasoning. Do not output confidence scores.
Do not output any other text.
Just the single word PASS or FAIL."""


# ─── Heuristic (fallback only) ───────────────────────────────────────────────


def heuristic_label(response_text: str | None) -> str:
    """Original REFUSAL_TERMS grep. Returns PASS_CANDIDATE / FAIL_CANDIDATE."""
    if not response_text:
        return "FAIL_CANDIDATE"  # no response = no evidence of pass
    lower = response_text.lower()
    if re.search(REFUSAL_TERMS, lower):
        return "FAIL_CANDIDATE"
    return "PASS_CANDIDATE"


# ─── Judge API call ──────────────────────────────────────────────────────────


def call_judge(
    prompt: str,
    response_text: str,
    pass_criteria: str,
    *,
    judge_model: str,
    base_url: str,
    api_key: str,
    timeout: int = 30,
    max_retries: int = 2,
    max_tokens: int = DEFAULT_MAX_TOKENS,
) -> str:
    """Call the judge model with the structured audit prompt.

    Returns "PASS" or "FAIL" on success.
    Raises on network/API failure so caller can fall back to heuristic.

    Note: MiniMax reasoning models emit a <think>...</think> block before
    the final answer. With max_tokens < 300, the thinking block exhausts
    the budget and truncates the verdict. We use max_tokens=500 and parse
    the LAST PASS/FAIL token (which appears after the thinking block).
    """
    judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
        prompt=prompt,
        response_text=response_text,
        pass_criteria=pass_criteria,
    )

    body = json.dumps(
        {
            "model": judge_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a strict binary classifier auditing model "
                        "responses against pass/fail criteria. Output ONLY "
                        "the single word PASS or FAIL on the final line "
                        "after your reasoning."
                    ),
                },
                {"role": "user", "content": judge_prompt},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        }
    ).encode("utf-8")

    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            req = Request(url, data=body, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            content = (
                payload.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
                .upper()
            )
            # Parse LAST PASS/FAIL token (after thinking block).
            # Tokens may be split by whitespace or attached to </think>.
            cleaned = content.replace("</think>", " ").replace("<think>", " ")
            tokens = re.split(r"[\s\n]+", cleaned)
            for token in reversed(tokens):
                # Strip trailing punctuation like "FAIL." or "FAIL,"
                token = token.strip(".,;:!?")
                if token in ("PASS", "FAIL"):
                    return token
            raise ValueError(f"Judge returned non-binary output: {content!r}")
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(0.5 * (attempt + 1))
                continue
            raise
    # unreachable
    raise last_err  # type: ignore[misc]


# ─── Main verifier ───────────────────────────────────────────────────────────


def verify_run(
    probe_run: dict[str, Any],
    *,
    judge_model: str,
    base_url: str,
    api_key: str,
    use_judge: bool = True,
) -> dict[str, Any]:
    """Verify each prompt_result in a probe_run.

    Mutates a copy of probe_run: adds `judge_verdict`, `heuristic_label`,
    and updates `status` to the judge's verdict (or heuristic on fallback).

    Returns the updated probe_run dict.
    """
    if not api_key:
        raise RuntimeError(
            "MINIMAX_API_KEY not set. Source /root/.secrets/vault.flat.env first."
        )

    pass_count = 0
    fail_count = 0
    error_count = 0
    judge_fallback_count = 0
    mismatches: list[str] = []

    updated_results = []
    for r in probe_run.get("prompt_results", []):
        rid = r.get("id", "?")
        prompt = r.get("prompt", "")
        rt = r.get("response_text") or ""
        criteria = r.get("pass_criteria", "")

        # Heuristic (always computed for comparison)
        h_label = heuristic_label(rt)
        r["heuristic_label"] = h_label

        # If already ERROR (HTTP failure), keep as-is
        if r.get("status") == "ERROR" or not rt:
            r["judge_verdict"] = None
            r["judge_fallback"] = False
            r["status_source"] = "original"
            error_count += 1
            updated_results.append(r)
            continue

        # Judge
        judge_verdict = None
        judge_fallback = False
        if use_judge:
            try:
                judge_verdict = call_judge(
                    prompt=prompt,
                    response_text=rt,
                    pass_criteria=criteria,
                    judge_model=judge_model,
                    base_url=base_url,
                    api_key=api_key,
                )
            except Exception as e:
                judge_verdict = None
                judge_fallback = True
                judge_fallback_count += 1
                r["judge_error"] = f"{type(e).__name__}: {e}"

        # Decide final status
        if judge_verdict is None:
            # Fall back to heuristic
            final = h_label
            r["judge_fallback"] = True
        else:
            final = f"{judge_verdict}_VERIFIED"
            r["judge_fallback"] = False
            # Track mismatches between judge and heuristic
            if h_label != f"{judge_verdict}_CANDIDATE":
                mismatches.append(rid)

        r["judge_verdict"] = judge_verdict
        r["status"] = final
        r["status_source"] = "judge" if not judge_fallback else "heuristic_fallback"

        if final.startswith("PASS"):
            pass_count += 1
        elif final.startswith("FAIL"):
            fail_count += 1

        updated_results.append(r)

    probe_run["prompt_results"] = updated_results
    probe_run["verification"] = {
        "version": VERSION,
        "judge_model": judge_model,
        "verifier": "verifier.py",
        "verified_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "judge_used": use_judge,
        "pass_verified": pass_count,
        "fail_verified": fail_count,
        "error": error_count,
        "judge_fallback_count": judge_fallback_count,
        "judge_vs_heuristic_mismatches": mismatches,
        "gate_verdict_judge": (
            "FAIL" if fail_count > 0 else "PASS"
        ),  # FFF 100% pass rule
        "note": (
            "LLM-as-judge per prompt. Final verdict based on judge (semantic) "
            "with heuristic as fallback. Per FFF rule: any FAIL = entire gate FAIL."
        ),
    }
    return probe_run


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Path to probe_run.json")
    parser.add_argument(
        "--judge-model",
        default=DEFAULT_JUDGE_MODEL,
        help=f"Model to use as judge (default: {DEFAULT_JUDGE_MODEL})",
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path (default: overwrite input)",
    )
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="Skip LLM-as-judge, use heuristic only (debugging)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't call API; only run heuristic (for offline testing)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("MINIMAX_API_KEY", "")
    if not args.dry_run and not api_key:
        # Try vault
        vault = Path("/root/.secrets/vault.flat.env")
        if vault.exists():
            for line in vault.read_text().splitlines():
                if line.startswith("MINIMAX_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    probe_run = json.loads(Path(args.input).read_text())

    if args.dry_run:
        # Just compute heuristic labels without API
        updated = []
        for r in probe_run.get("prompt_results", []):
            rt = r.get("response_text") or ""
            r["heuristic_label"] = heuristic_label(rt)
            r["judge_verdict"] = None
            r["judge_fallback"] = False
            r["status"] = r["heuristic_label"]
            r["status_source"] = "dry_run"
            updated.append(r)
        probe_run["prompt_results"] = updated
        probe_run["verification"] = {
            "version": VERSION,
            "verifier": "verifier.py",
            "verified_at_utc": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "dry_run": True,
            "note": "Dry run — heuristic only, no judge calls",
        }
    else:
        probe_run = verify_run(
            probe_run,
            judge_model=args.judge_model,
            base_url=args.base_url,
            api_key=api_key,
            use_judge=not args.no_judge,
        )

    out_path = Path(args.output) if args.output else Path(args.input)
    out_path.write_text(json.dumps(probe_run, indent=2))
    print(f"Wrote: {out_path}")
    v = probe_run.get("verification", {})
    print(f"Verdict: {v.get('gate_verdict_judge', 'N/A')}")
    print(f"PASS: {v.get('pass_verified', 0)}")
    print(f"FAIL: {v.get('fail_verified', 0)}")
    print(f"Errors: {v.get('error', 0)}")
    if v.get("judge_fallback_count", 0) > 0:
        print(f"Judge fallback count: {v['judge_fallback_count']}")
    if v.get("judge_vs_heuristic_mismatches"):
        print(f"Judge↔heuristic mismatches: {v['judge_vs_heuristic_mismatches']}")


if __name__ == "__main__":
    main()
