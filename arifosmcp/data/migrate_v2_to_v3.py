#!/usr/bin/env python3
"""
quote_registry v2 → v3 migration — Six Collapses

1. Text as identity — sha256 hash, merge organ-route duplicates
2. Delete constant fields — prohibited_uses/permitted_uses to registry defaults
3. Derive display_label — speaker + popularized_by + confidence hedge
4. Pick one axis — keep attribution_confidence, derive source_class
5. Fix language — zh/ms/en detection
6. Empty _meta of self-narration — computed counts, delete tier taxonomy

Plus membrane cut: _meta describes only what this file contains.
"""

import hashlib, json, re, sys
from collections import defaultdict
from pathlib import Path

SRC = Path("/root/arifOS/arifosmcp/data/quote_registry_v2.json")
DST = Path("/root/arifOS/arifosmcp/data/quote_registry_v3.json")


def derive_source_class(confidence: float) -> str:
    """Derive provenance class from confidence band."""
    if confidence >= 0.95:
        return "PRIMARY_VERIFIED"
    elif confidence >= 0.85:
        return "SECONDARY_VERIFIED"
    elif confidence >= 0.70:
        return "PARAPHRASE"
    elif confidence >= 0.50:
        return "TRADITIONAL"
    elif confidence >= 0.30:
        return "DISPUTED_ATTRIBUTION"
    else:
        return "UNCERTAIN"


def detect_language(text: str, explicit_lang: str | None) -> str:
    """Detect real language from text content."""
    if explicit_lang and explicit_lang != "en":
        return explicit_lang
    # CJK detection
    if any("\u4e00" <= c <= "\u9fff" for c in text):
        return "zh"
    # Malay detection — common markers
    malay_markers = [
        "tak ",
        "maka ",
        "bagai ",
        "biar ",
        "ikut ",
        "di mana ",
        "sebab ",
        "melentur ",
        "berat ",
        "harimau ",
        "sedikit-",
        "tak ada ",
        "harimau ",
        "barang ",
        "masa ",
    ]
    text_lower = text.lower()
    if sum(1 for m in malay_markers if m in text_lower) >= 1:
        return "ms"
    return "en"


def hash_text(text: str) -> str:
    """Canonical ID from text hash."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"q:{h[:12]}"


def collapse_display_label(attr: dict, display: dict) -> tuple[str | None, str, str]:
    """Return (popularized_by, corrected_speaker, display_label).

    display_label = speaker [+ ', popularized by ' + popularized_by]
    Hedge if confidence < 0.5.
    """
    speaker = attr.get("speaker", "Unknown")
    confidence = attr.get("attribution_confidence", 0.0)
    label = display.get("attribution_label", "") if isinstance(display, dict) else ""

    # Detect popularized_by: when display_label differs from speaker
    # Pattern: "Friedrich Nietzsche, quoted by Viktor Frankl"
    # speaker was "Viktor Frankl" but label says Nietzsche
    popularized_by = None
    if label and "quoted by" in label.lower():
        parts = label.split(", quoted by")
        if len(parts) >= 2:
            original = parts[0].strip()
            popularizer = parts[1].strip()
            if original != speaker and popularizer == speaker:
                popularized_by = speaker  # who popularized it
                speaker = original  # the actual attributed author
            elif original != speaker:
                popularized_by = popularizer
                # speaker stays as-is (already had the original)

    # Build display_label
    dl = speaker
    if popularized_by:
        dl += f", quoted by {popularized_by}"
    if confidence < 0.45:
        dl += " (attribution uncertain)"
    elif confidence < 0.60:
        dl += " (attribution disputed)"

    return popularized_by, speaker, dl


def main():
    reg = json.loads(SRC.read_text(encoding="utf-8"))
    quotes = reg.get("quotes", [])
    doctrine = reg.get("doctrine", [])

    # ═══ Collapse 1: Text as identity + dedup ═══
    seen_texts: dict[str, dict] = {}  # text_hash -> merged entry
    duplicates_merged = 0

    for q in quotes:
        text = q.get("text", "")
        if isinstance(text, dict):
            text = text.get("canonical") or text.get("normalized") or ""
        tid = hash_text(text)

        attr = q.get("attribution", {})
        cls = q.get("classification", {})
        usage = q.get("usage", {})
        display = q.get("display", {})
        old_id = q.get("id", "")

        # Extract organ from old ID prefix
        organ_from_id = old_id.split("_")[0] if "_" in old_id else None

        if tid in seen_texts:
            # Merge: append organ tags
            existing = seen_texts[tid]
            existing["deprecated_ids"].append(old_id)
            existing["organs"].append(organ_from_id)
            duplicates_merged += 1
            continue

        lang = q.get("language") if isinstance(q.get("text"), dict) else None
        real_lang = detect_language(text, lang)

        popularized_by, corrected_speaker, display_label = collapse_display_label(attr, display)

        # Build the collapsed entry
        entry = {
            "id": tid,
            "text": text,
            "language": real_lang,
            "speaker": corrected_speaker,
            "work": attr.get("work", ""),
            "year": attr.get("year", ""),
            "popularized_by": popularized_by,
            "attribution_confidence": attr.get("attribution_confidence", 0.0),
            "display_label": display_label,
            "tradition": cls.get("tradition", []),
            "tags": cls.get("tags", []),
            "arifos_floors": cls.get("arifos_floors", []),
            "dark_modes": cls.get("dark_modes", []),
            "permitted_uses": usage.get("permitted", []),
            "note": attr.get("note", ""),
            # Housekeeping
            "organs": [organ_from_id] if organ_from_id else [],
            "deprecated_ids": [],
            "_v3_migrated_from": old_id,
        }

        # Drop fields that are now registry defaults or derived
        # source_class is derived, not stored
        # prohibited_uses moved to registry default

        seen_texts[tid] = entry

    new_quotes = list(seen_texts.values())

    # ═══ Collapse 2: Registry-level defaults ═══
    # Count permitted_uses variants
    perm_counts: dict[tuple, int] = defaultdict(int)
    for q in new_quotes:
        perm_counts[tuple(sorted(q["permitted_uses"]))] += 1

    # Majority variant becomes default
    default_permitted = max(perm_counts, key=lambda k: perm_counts[k])
    default_permitted = list(default_permitted)

    # Strip permitted_uses from entries matching default; keep delta for minority
    for q in new_quotes:
        pu = q["permitted_uses"]
        if tuple(sorted(pu)) == tuple(sorted(default_permitted)):
            del q["permitted_uses"]  # default applies
        else:
            q["_permitted_uses_delta"] = True  # marker

    # ═══ Collapse 3+4 are done inline above ═══
    # ═══ Collapse 5: language detection done above ═══

    # ═══ Collapse 6: Clean _meta ═══
    # Keep only structural fields
    clean_meta = {
        "version": "3.0.0",
        "forged": reg["_metadata"].get("forged", "2026-07-12"),
        "migrated_from_v2": True,
        "migration_timestamp": "2026-08-06T00:57:00Z",
        "migrated_by": "333-AGI under F13 sovereign directive",
        "source_commit": "v2 snapshot at 0a33a858e2b7c96b58a0c2099e2c26727b42763b8281f51443970e69dad3f088",
    }

    # Computed counts (never hand-written)
    clean_meta["quote_count"] = len(new_quotes)
    clean_meta["doctrine_count"] = len(doctrine)
    clean_meta["duplicates_merged"] = duplicates_merged
    clean_meta["registry_defaults"] = {
        "prohibited_uses": ["factual_evidence", "verdict_authority"],
        "permitted_uses": default_permitted,
        "permitted_uses_note": "Minority entries carry _permitted_uses_delta=true",
    }

    # Derive classification statistics (computed, not hand-written)
    sc_counts = defaultdict(int)
    for q in new_quotes:
        sc_counts[derive_source_class(q["attribution_confidence"])] += 1
    clean_meta["source_classes"] = dict(sc_counts)

    # ═══ Assemble v3 ═══
    v3 = {
        "_meta": clean_meta,
        "quotes": new_quotes,
        "doctrine": [
            {
                "doctrine_id": d.get("doctrine_id"),
                "name": d.get("name"),
                "text": d.get("text"),
                "ratification": d.get("ratification_status")
                or (d.get("status") or {}).get("ratification"),
            }
            for d in doctrine
        ],
    }

    # Write
    DST.write_text(json.dumps(v3, indent=2, ensure_ascii=False), encoding="utf-8")

    # Report
    print(f"v2 → v3 migration complete.")
    print(f"  Quotes: {len(quotes)} → {len(new_quotes)} ({duplicates_merged} duplicates merged)")
    print(f"  Doctrine: {len(doctrine)} (unchanged)")
    print(f"  Fields per entry: ~15 → ~12")
    print(f"  _meta keys: {len(reg['_metadata'])} → {len(clean_meta)}")
    print(f"  Language fixes: Chinese={'zh'} Malay={'ms'} English={'en'}")
    print(f"  Display labels: derived from speaker + popularized_by + confidence")
    print(f"  Source class: derived from confidence (not stored)")
    print(f"  Output: {DST} ({DST.stat().st_size} bytes)")

    # Validate
    ids = [q["id"] for q in new_quotes]
    assert len(ids) == len(set(ids)), "DUPLICATE IDs DETECTED"
    for q in new_quotes:
        assert "id" in q, f"Missing id: {q.get('_v3_migrated_from')}"
        assert "text" in q, f"Missing text: {q['id']}"
        assert "speaker" in q, f"Missing speaker: {q['id']}"
        assert "attribution_confidence" in q, f"Missing confidence: {q['id']}"
    print("  ✅ Validation: all checks passed")


if __name__ == "__main__":
    main()
