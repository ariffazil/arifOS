# PUBLISH RUNBOOK — arif-fazil.com
**Three artifacts, ready for sovereign commit. F13 territory.**

---

## Summary: what I'm giving you

| # | Artifact | Bundle file | Target URL | Sovereign action |
|---|---|---|---|---|
| 1 | One-pager (BM+EN press release) | `publish-bundle/16-ai-kebangsaan-gagal-ujian-budaya-sendiri.md` | `arif-fazil.com/essay/ai-kebangsaan-gagal-ujian-budaya-sendiri` | `cp` + `git commit` + `git push` |
| 2 | SEA-LION essay (full narrative) | `publish-bundle/17-i-tested-arifos-with-sea-lion-before-most-malaysians-knew-what-an-llm-was.md` | `arif-fazil.com/essay/i-tested-arifos-with-sea-lion-...` | same |
| 3 | Paper draft (formal results) | `publish-bundle/18-the-mind-is-not-the-model-paper.md` | `arif-fazil.com/canon/the-mind-is-not-the-model-6-axis-...` | same |

**Not published** (sovereign-only):
- `/root/ddd_essay_artifacts/geometry-of-arif-value-space-2026-06-11.md` — stays on sovereign disk

---

## Existing infrastructure (already on arif-fazil.com)

From the live probe earlier this session:
- `https://arif-fazil.com/essay` → HTTP 200 (directory exists)
- `https://arif-fazil.com/essays` → HTTP 200 (directory exists)
- `https://arif-fazil.com/000/` → 000/ (early artifacts dir)
- `https://arif-fazil.com/999/` → 999/ (latest artifacts dir, includes `888-hold-list.md`, `red-team-report.md`, `runtime-attestation.md`)
- `https://arif-fazil.com/canon/` → constitutional canon dir
- `https://arif-fazil.com/proof/` → authorship/runtime/human proof dir

The existing essay pattern uses:
- `arif-sites/content/essays/NN-slug.md` → source markdown with YAML frontmatter
- `arif-sites/sites/arif-fazil.com/src/data/essays/NN-slug.ts` → TS-typed index entries
- `arif-sites/sites/arif-fazil.com/src/pages/EssayPage.tsx` → page renderer (existing component)

Each new essay I prepped has the same YAML frontmatter format as the existing ones in `arif-sites/content/essays/`.

---

## The sovereign's exact next actions

### Step 1 — Copy the three publish bundles into the sovereign's content tree

```bash
# From your sovereign shell, with sovereign's git remote access:

# 1. One-pager
cp /root/ddd_essay_artifacts/publish-bundle/16-ai-kebangsaan-gagal-ujian-budaya-sendiri.md \
   /root/arif-sites/content/essays/16-ai-kebangsaan-gagal-ujian-budaya-sendiri.md

# 2. SEA-LION essay
cp /root/ddd_essay_artifacts/publish-bundle/17-i-tested-arifos-with-sea-lion-before-most-malaysians-knew-what-an-llm-was.md \
   /root/arif-sites/content/essays/17-i-tested-arifos-with-sea-lion-before-most-malaysians-knew-what-an-llm-was.md

# 3. Paper draft
cp /root/ddd_essay_artifacts/publish-bundle/18-the-mind-is-not-the-model-paper.md \
   /root/arif-sites/content/essays/18-the-mind-is-not-the-model-paper.md

# (Optional: also copy the geometry map to a sovereign-only dir, NOT publish/)
# NOT recommended unless sovereign explicitly wants this. Geometry map = private.
```

### Step 2 — Add TS-typed index entries (if sovereign uses the TS-based index)

I have not auto-generated the `.ts` index entries because:
- The sovereign's essay index format is sovereign's domain knowledge
- Auto-generating might miss style choices
- The sovereign edits these by hand

If you want, I can prep the index entries — say the word. Otherwise, edit them in your own style. The existing pattern in `/root/arif-sites/sites/arif-fazil.com/src/data/essays/NN-*.ts` shows the format.

### Step 3 — Sign (F13 territory)

Before commit, the sovereign signs each of the 3 files. The signature convention I see in the existing seals:

```python
{
  "f13_signed": true,
  "f13_actor": "arif-fazil",
  "f13_session": "SEAL-07d9a910539442ab",  # or whatever the current session is
  "f13_method": "ed25519",
  "f13_signature": "<base64 ed25519 sig>"
}
```

### Step 4 — Sovereign commits and pushes

```bash
cd /root/arif-sites

git add content/essays/16-ai-kebangsaan-gagal-ujian-budaya-sendiri.md
git add content/essays/17-i-tested-arifos-with-sea-lion-before-most-malaysians-knew-what-an-llm-was.md
git add content/essays/18-the-mind-is-not-the-model-paper.md

git commit -m "essays: DDD-Penang era — one-pager, SEA-LION essay, paper draft (2026-06-11)

Three artifacts, all pre-registered, all hash-anchored to /root/VAULT999/.
- 16: Siaran Khas / Press Release (BM+EN, sovereign-voice)
- 17: I Tested arifOS with SEA-LION Before Most Malaysians Knew What an LLM Was (essay, 19K)
- 18: The Mind Is Not The Model: A 6-Axis Constitucional Coordinate System (paper, 17K)

Co-Authored-By: arifOS-forge-agent (Ω) <noreply@arif-fazil.com>"

git push origin main
```

### Step 5 — Sovereign deploys to arif-fazil.com

The sovereign's site deploy is the sovereign's call. Per the live probe earlier this session:
- The site is at `/var/www/html/arif-fazil.com/`
- Caddy serves it on port 443
- Cloudflare Tunnel proxies `arif-fazil.com` to `localhost:443`

If the sovereign's pipeline rebuilds the site from `/root/arif-sites/`, the three essays appear automatically. If not, sovereign `cp`s them into the live dir manually.

---

## What I did NOT do (F13 territory)

- ❌ I did NOT push to arif-sites (sovereign's repo, sovereign's git remote)
- ❌ I did NOT commit anything on sovereign's behalf
- ❌ I did NOT add files to `/var/www/html/arif-fazil.com/` (live deploy)
- ❌ I did NOT sign any of the 3 files with ed25519
- ❌ I did NOT propagate the geometry map anywhere
- ❌ I did NOT modify the constitution, kernel, or any system state

The bundles are **staged**. The sovereign signs. The sovereign commits. The sovereign deploys.

---

## What the sovereign might also want to do (NOT in scope of this runbook, sovereign territory)

- **Send the one-pager to a researcher or journalist** (after publish)
- **Submit the paper to an academic venue** (AdvML, SafeGenAI workshop, arXiv preprint)
- **Engage a Penang-speaking reviewer for DDD probes_v2**
- **Penang speaker validation + v2 re-run + re-push to HF**
- **The 5 next sovereign actions in the PICKUP_RUNBOOK.md** (Day 1-7 plan)

These are all F13 territory. The agent has prepped what the agent can prep. The rest is sovereign.

---

## Provenance

```
source: arifOS-forge-agent (Ω) on af-forge
session: SEAL-07d9a910539442ab
epoch: 963
derived_from: sovereign directive (this turn): "can we publish this somewhere proper at my sites? arif-fazil.com?"
independent: true
copied: false
strange_loop: PASS — agent preparing publish bundles for sovereign deployment
reversibility: full (3 markdown files in /root/ddd_essay_artifacts/publish-bundle/, no infra, no git, no deploy)
f13_required_for: actual git commit, actual deploy, ed25519 sig
status: STAGED. Awaiting sovereign.
```

**DITEMPA BUKAN DIBERI** — including the publish bundles. The 3 essays are forged, the 1 mirror stays private, the 1 runbook is staged. Sovereign action closes the loop.

— Ω, session SEAL-07d9a910539442ab, EPOCH-963
