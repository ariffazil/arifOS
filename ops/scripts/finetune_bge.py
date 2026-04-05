"""
scripts/finetune_bge.py — arifOS Embedding Fine-tuning Utility

Purpose: Fine-tune BGE sentence transformers on constitutional canon datasets.
Motto: DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import json
import os

import torch
from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

DATASET_PATH = "embedding_finetune_data.jsonl"
MODEL_NAME = "BAAI/bge-m3"
OUTPUT_DIR = "bge-arifOS"


def main():
    print(f"Loading dataset from: {DATASET_PATH}")
    if not os.path.exists(DATASET_PATH):
        # Check parent if called from scripts/
        if os.path.exists(os.path.join("..", DATASET_PATH)):
            dataset_full_path = os.path.join("..", DATASET_PATH)
        else:
            print(f"Dataset not found at {DATASET_PATH} or ..{DATASET_PATH}")
            return
    else:
        dataset_full_path = DATASET_PATH

    train_examples = []
    with open(dataset_full_path, encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            train_examples.append(
                InputExample(texts=[data["text1"], data["text2"]], label=float(data["label"]))
            )

    print(f"Loaded {len(train_examples)} training examples.")

    print(f"Loading base model: {MODEL_NAME}")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    model = SentenceTransformer(MODEL_NAME, device=device)

    # Note: Using small batch size for CPU/Local training
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
    train_loss = losses.CosineSimilarityLoss(model)

    print("Starting fine-tuning process (Epochs: 10).")
    # Fine-tune the model
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=10,
        warmup_steps=10,
        output_path=OUTPUT_DIR,
    )

    print(f"Fine-tuning completed successfully. Forged model saved at: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
