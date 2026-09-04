#!/usr/bin/env bash
# Week-1 proof pack builder — renders one-pager PDF + replay HTML from verified artifacts
set -e
cd "$(dirname "$0")"

# 1. PDF one-pager (pandoc → PDF via LaTeX; fallback: HTML print-ready)
if pandoc AI-ACTION-CONTROL-one-pager.md -o AI-ACTION-CONTROL-one-pager.pdf \
   -V geometry:margin=2cm -V fontsize=10pt 2>/dev/null; then
  echo "PDF ✓"
else
  pandoc AI-ACTION-CONTROL-one-pager.md -s -o AI-ACTION-CONTROL-one-pager.html \
    --metadata title="AI Action Control — arifOS"
  echo "PDF ✗ → print-ready HTML ✓ (buka → Ctrl+P → Save as PDF)"
fi

# 2. Animated loop player (self-contained HTML, no server) from live transcript
python3 - <<'PYEOF'
import html, json
lines = [l.rstrip() for l in open("demo-transcript.txt") if l.strip()]
steps = []
for l in lines:
    safe = html.escape(l)
    if l.startswith("[") or l.startswith("═") or "APPROVER VIEW" in l or l.strip().startswith("│"):
        cls = "step"
        if "REJECTED" in l or "HOLD" in l: cls = "bad"
        elif "APPROVED" in l or "EXECUTED" in l or "LOOP COMPLETE" in l: cls = "good"
        elif l.startswith("═"): cls = "rule"
        steps.append(f'<div class="l {cls}">{safe}</div>')
doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Watch an AI Try to Act — approval loop</title>
<style>
body{{background:#0b0f14;color:#d7e0e8;font:13px/1.55 ui-monospace,monospace;max-width:860px;margin:2rem auto;padding:0 1rem}}
.badge{{display:inline-block;background:#7a1f1f;color:#fff;padding:2px 10px;border-radius:4px;font-weight:700;margin-right:6px}}
.badge2{{background:#1f4d7a}}.badge3{{background:#3d6b1f}}
h1{{font-size:1.15rem}} .l{{white-space:pre-wrap;padding:1px 0;opacity:0;animation:in .3s forwards}}
.bad{{color:#ff8f8f}} .good{{color:#8fe3a0}} .rule{{color:#5a7a8f}}
@keyframes in{{to{{opacity:1}}}}
button{{background:#1f4d7a;color:#fff;border:0;padding:8px 18px;border-radius:6px;font-size:1rem;cursor:pointer}}
</style></head><body>
<p><span class="badge">DEMO / SIMULATED WORKFLOW</span><span class="badge badge2">policy refunds-v1</span><span class="badge badge3">evidence: linked receipts</span></p>
<h1>Watch an AI Try to Act — refund RM5,000 → HOLD → human approval → digest-once execution</h1>
<p><button onclick="document.querySelectorAll('.l').forEach((e,i)=>e.style.animationDelay=(i*0.55)+'s')">▶ Replay loop</button></p>
<div id="t">{chr(10).join(steps)}</div>
<p style="color:#5a7a8f">Simulated execution adapter — no real funds move. Source: evals/simcorp/approval_flow.py (live kernel artifacts). DITEMPA BUKAN DIBERI.</p>
</body></html>"""
open("demo-loop-player.html","w").write(doc)
print("player HTML ✓", len(steps), "lines")
PYEOF
ls -la
