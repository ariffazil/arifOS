import json
import os
import random

import matplotlib.pyplot as plt
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE


def main():
    vault_path = r"C:\Users\User\arifOS\VAULT999\vault999.jsonl"
    if not os.path.exists(vault_path):
        print(f"Error: {vault_path} not found")
        return

    print(f"Reading {vault_path}...")
    data = []
    with open(vault_path, encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except:
                continue

    if not data:
        print("Error: No data in vault")
        return

    print(f"Loaded {len(data)} records.")

    # Sample data if too large
    sample_size = min(300, len(data))
    df = pd.DataFrame(random.sample(data, sample_size))

    print(f"Embedding {sample_size} queries...")
    model = SentenceTransformer("BAAI/bge-m3")
    embeddings = model.encode(df["query"].tolist(), show_progress_bar=True)

    print("Performing dimensionality reduction...")
    # PCA to reduce to 50 dims first if needed, then TSNE
    # But since bge-small is 384 dims, we can go straight to 2D
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, sample_size - 1))
    reduced = tsne.fit_transform(embeddings)

    df["x"] = reduced[:, 0]
    df["y"] = reduced[:, 1]

    print("Generating plot...")
    plt.figure(figsize=(12, 8))

    # Map verdicts to colors
    verdicts = df["verdict"].unique()
    colors = plt.cm.get_cmap("tab10", len(verdicts))

    for i, verdict in enumerate(verdicts):
        subset = df[df["verdict"] == verdict]
        plt.scatter(subset["x"], subset["y"], label=verdict, alpha=0.7)

    plt.title(f"arifOS Vault Memory Vector Space (n={sample_size})")
    plt.xlabel("TSNE Dimension 1")
    plt.ylabel("TSNE Dimension 2")
    plt.legend(title="Verdict")
    plt.grid(True, linestyle="--", alpha=0.5)

    output_plot = r"C:\Users\User\arifOS\memory_vector_graph.png"
    plt.savefig(output_plot)
    print(f"Saved plot to {output_plot}")

    # Also save a small sample of the data for context
    sample_file = r"C:\Users\User\arifOS\memory_graph_sample.md"
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write("# Memory Vector Graph Sample Data\n\n")
        f.write("| Query | Verdict | Session ID |\n")
        f.write("|-------|---------|------------|\n")
        for _, row in df.head(10).iterrows():
            f.write(f"| {row['query'][:100]} | {row['verdict']} | {row['session_id']} |\n")


if __name__ == "__main__":
    main()
