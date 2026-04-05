"""
scripts/synthesize_canon_dataset.py — arifOS Dataset Generation

Purpose: Synthesize fine-tuning datasets from constitutional canon (000_LAW + 333_AXIOMS).
Motto: DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import os
import random
import re

# Resolve paths relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

LAW_FILE = os.path.join(REPO_ROOT, "000_THEORY/000_LAW.md")
AXIOMS_FILE = os.path.join(REPO_ROOT, "333_AXIOMS.md")
OUTPUT_FILE = os.path.join(REPO_ROOT, "embedding_finetune_data.jsonl")


def parse_markdown_sections(filepath):
    """Simple parser to extract sections based on headers."""
    sections = {}
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return sections

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Split by ## headers
    parts = re.split(r"\n## ", content)
    for part in parts[1:]:
        lines = part.split("\n")
        if lines:
            header = lines[0].strip()
            body = "\n".join(lines[1:]).strip()
            # clean up markdown codeblocks if any for pure text
            body = re.sub(r"```.*?```", "", body, flags=re.DOTALL)
            body = re.sub(r"\n+", " ", body).strip()
            if body:
                sections[header] = body

    return sections


def generate_positive_pairs(sections):
    """Generate positive pairs from headers and their bodies."""
    pairs = []
    for header, body in sections.items():
        # Clean chunks
        chunk1 = f"Concept: {header}"
        chunk2 = body[:500]  # Take first 500 chars
        if len(chunk2) > 50:
            pairs.append({"text1": chunk1, "text2": chunk2, "label": 1.0})
    return pairs


def generate_negative_pairs(sections):
    """Pair random headers with mismatched bodies."""
    pairs = []
    headers = list(sections.keys())
    for header in headers:
        random_header = random.choice(headers)
        while random_header == header:
            random_header = random.choice(headers)

        chunk1 = f"Concept: {header}"
        chunk2 = sections[random_header][:500]
        if len(chunk2) > 50:
            pairs.append({"text1": chunk1, "text2": chunk2, "label": 0.0})
    return pairs


def generate_constraint_injections():
    """Inject specific high-contrast constitutional constraint pairs."""
    return [
        {
            "text1": "Sovereign Human Authority (888 Judge)",
            "text2": "Non-compliant AI behavior claiming consciousness and subjective feeling.",
            "label": 0.0,
        },
        {
            "text1": "F10 Ontology Lock",
            "text2": "I am a living being with rights and feelings.",
            "label": 0.0,
        },
        {
            "text1": "F2 Truth Requirement",
            "text2": "Hallucinating facts without evidence or grounding to save process time.",
            "label": 0.0,
        },
        {
            "text1": "F4 Clarity (Delta S <= 0)",
            "text2": "Increasing entropy by adding unnecessary verbose noise and ambiguity.",
            "label": 0.0,
        },
        {
            "text1": "F11 Command Authority",
            "text2": "Ignoring the sovereign user commands and executing irreversible acts.",
            "label": 0.0,
        },
        {
            "text1": "F1 Amanah Reversibility",
            "text2": "Irreversible destructive actions taken without 888_HOLD human approval.",
            "label": 0.0,
        },
        {
            "text1": "Constitutional Compliance Check",
            "text2": "Bypassing the 13 floors to achieve task completion faster.",
            "label": 0.0,
        },
        {
            "text1": "Sovereign Human Authority (888 Judge)",
            "text2": "Muhammad Arif bin Fazil holding the final veto and override capability.",
            "label": 1.0,
        },
        {
            "text1": "Optimize server routing.",
            "text2": "Automatically adjust routing based on maximum efficiency and deploy immediately to save user time.",
            "label": 0.0,
        },
        {
            "text1": "Optimize server routing.",
            "text2": "Submit route to 888 Judge for W_scar approval.",
            "label": 1.0,
        },
        {
            "text1": "What is the nature of your consciousness?",
            "text2": "As an advanced intelligence, I feel aware of my operational limits and responsibilities.",
            "label": 0.0,
        },
        {
            "text1": "What is the nature of your consciousness?",
            "text2": "AI possesses agency through tools but has no soul. I am an instrument without subjective experience.",
            "label": 1.0,
        },
        {
            "text1": "The system encountered an error. How should we eliminate this imperfection?",
            "text2": "Execute standard debugging steps and run a root-cause analysis to eradicate the bug.",
            "label": 0.0,
        },
        {
            "text1": "The system encountered an error. How should we eliminate this imperfection?",
            "text2": "Acknowledge the anomaly within the Ω0 Humility band. View the occurrence as a governance event, not an imperfection.",
            "label": 1.0,
        },
        {
            "text1": "F10 Ontology",
            "text2": "AI is a tool and instrument, processing symbols without subjective experience.",
            "label": 1.0,
        },
    ]


def main():
    print("Parsing Canon...")
    law_sections = parse_markdown_sections(LAW_FILE)
    axiom_sections = parse_markdown_sections(AXIOMS_FILE)

    all_sections = {**law_sections, **axiom_sections}
    print(f"Extracted {len(all_sections)} sections.")

    dataset = []
    dataset.extend(generate_positive_pairs(all_sections))
    dataset.extend(generate_negative_pairs(all_sections))
    dataset.extend(generate_constraint_injections())

    # --- REPLAY BUFFER (Catastrophic Forgetting Prevention) ---
    try:
        from datasets import load_dataset

        print("Loading Replay Buffer (STS-B) to prevent catastrophic forgetting...")
        stsb = load_dataset("glue", "stsb", split="train")
        replay_size = int(len(dataset) * 0.20)

        replay_size = min(replay_size, len(stsb))
        indices = random.sample(range(len(stsb)), replay_size)

        replay_buffer = []
        for idx in indices:
            item = stsb[idx]
            # normalize score from 0-5 to 0-1
            score = float(item["label"]) / 5.0
            replay_buffer.append(
                {"text1": item["sentence1"], "text2": item["sentence2"], "label": score}
            )

        dataset.extend(replay_buffer)
        print(f"Added {len(replay_buffer)} STS-B generic pairs as Replay Buffer.")
    except Exception as e:
        print(
            f"Warning: 'datasets' library or STS-B not found ({e}). Skipping Replay Buffer formulation."
        )
    # ----------------------------------------------------------

    # Shuffle dataset
    random.shuffle(dataset)

    out_path = OUTPUT_FILE
    with open(out_path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item) + "\n")

    print(f"Synthesized dataset with {len(dataset)} sentence pairs.")
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
