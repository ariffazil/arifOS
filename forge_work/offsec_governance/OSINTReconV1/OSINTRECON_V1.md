# OSINTRECON_V1.md — Passive OSINT Recon Skill
# Forged: 2026-06-29 — EHT Repo Audit (Arif + Hermes ASI)
# Authority: F13 SOVEREIGN directive
# Source:  hhhrrrttt222111/Ethical-Hacking-Tools → 14. Google Dorking/
# Corpus:  dorks1.txt (793), dorks2.txt (3,982), dorks3.txt (1,637)
#          sql_injection.txt (623), cctv.txt (25) = 7,060 total signatures
# Category: Kali Taxonomy Cell 14 — Google Dorking (OBSERVE_ONLY)
#
# DITEMPA BUKAN DIBERI — OSINT is passive; governance is active.

_meta:
  skill_id: OSINTRECON_V1
  forged: 2026-06-29
  category: 14_Google_Dorking
  default_verdict: OBSERVE_ONLY
  reversibility: FULL
  blast_radius: LOW
  agents_allowed: [hermes, geox]
  requires_human: false
  status: SEALED
  sealed_by: F13 SOVEREIGN (888 — Muhammad Arif bin Fazil)
  sealed_at: 2026-06-29T19:55:00Z
  seal_receipt: arifos://seal/EHT-2026-06-29/OSINTRECON_V1

# ─── WHAT THIS SKILL IS ───────────────────────────────────────
# Passive reconnaissance via Google Dorking — using advanced search
# operators to discover exposed assets, configuration files, login
# portals, database dumps, and misconfigured services.
#
# CONSTITUTIONAL BOUNDARY:
#   • Read-only search syntax — NO active exploitation
#   • Google/Bing/DuckDuckGo operators only — no custom scanners
#   • Results are URLs, not payloads
#   • F2 TRUTH: dorks are public search syntax, not exploits
#   • F5 PEACE: never use dorks for harassment or targeting individuals
#   • F10 ONTOLOGY: dorks reveal what is already public; they create nothing
#
# BLAST RADIUS: LOW — dork = search query. The operator (human) is
# responsible for what they do with the URLs discovered.

# ─── CORPUS ───────────────────────────────────────────────────
# 7,060 pre-curated Google dork signatures organized by target type:

corpus:
  - file: corpus/dorks1.txt
    count: 793
    focus: parameterized URLs (php?id=, page=, cat=, etc.)
    use: discovering injection points, admin panels, config leaks

  - file: corpus/dorks2.txt
    count: 3982
    focus: broad exposure discovery (filetype:, inurl:, intitle:, site:)
    use: finding exposed documents, spreadsheets, backups, logs

  - file: corpus/dorks3.txt
    count: 1637
    focus: mixed — login portals, directory listings, error messages
    use: discovering authentication surfaces, debug endpoints

  - file: corpus/sql_injection.txt
    count: 623
    focus: SQL injection probe patterns (parameterized queries, error-based)
    use: PASSIVE DETECTION ONLY — identify potential injection surfaces
    warning: "NEVER execute injection payloads. This is OBSERVE class only."

  - file: corpus/cctv.txt
    count: 25
    focus: exposed camera interfaces (Axis, EvoCam, NetSnap)
    use: discovering publicly accessible surveillance feeds
    warning: "Accessing unauthorized cameras may violate local laws (CMA 1998 in Malaysia)."

# ─── USAGE PATTERN ────────────────────────────────────────────
#
# Agent invocation (Hermes / GEOX):
#
#   1. Load corpus subset relevant to task
#   2. Marshal dork → search engine query
#   3. Return URL results ONLY — no crawling, no exploitation
#   4. Tag results with: [dork_source, search_engine, timestamp]
#
# Example:
#
#   task: "Find exposed .env files on target.com"
#   dork: "site:target.com ext:env"
#   source: corpus/dorks2.txt
#   result: [list of URLs]
#   tag: OSINT | OBSERVE_ONLY | dorks2.txt | 2026-06-29
#
# GOVERNANCE: Results are passed to arifOS for classification.
# The skill does NOT decide what is sensitive — it only discovers
# what is already public.

# ─── DO NOT USE THIS SKILL FOR ────────────────────────────────
#
#   ✗ Active exploitation of discovered vulnerabilities
#   ✗ Credential harvesting from exposed config files
#   ✗ Unauthorized camera access
#   ✗ Targeting individuals or personal information
#   ✗ Automated scanning without rate limiting
#   ✗ Bypassing robots.txt or terms of service
#   ✗ Using Dorkify (hhhrrrttt222111/Dorkify) — untrusted dependency
#
#   If you need dork automation, write your own. 20 lines of Python
#   against the Google Custom Search API is safer than pulling an
#   unaudited single-contributor repo.

# ─── DORKIFY WARNING ──────────────────────────────────────────
#
# The EHT repo maintainer (hhhrrrttt222111) ships Dorkify as their
# only original tool. DO NOT USE IT AS A DEPENDENCY. Reasons:
#
#   • Single contributor, no audit trail
#   • Could embed prompt-injection payloads into generated dorks
#   • Low maintenance signal (EHT repo mostly dead)
#
# The corpus in this skill is a SAFE EXTRACT — raw dork strings only,
# no executable code, no dependency chain, no network calls.

# ─── INTEGRATION ──────────────────────────────────────────────
#
# This skill is classified under arifOS Kali Taxonomy Cell 14:
# Google Dorking. Default verdict: OBSERVE_ONLY. Any agent that
# loads this skill inherits the cell's governance posture.
#
# See: forge_work/offsec_governance/ToolHazardV1/kali_taxonomy.yaml
#      forge_work/offsec_governance/ToolHazardV1/forbidden_patterns.yaml
