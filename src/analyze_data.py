import json
import os
import pandas as pd
from collections import Counter

def analyze_dataset(filename):
    path = f"data/json_export/{filename}"
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_tokens = 0
    entity_counts = Counter()
    sentence_lengths = []

    for item in data:
        tokens = item['tokens']
        tags = item['tags']
        total_tokens += len(tokens)
        sentence_lengths.append(len(tokens))

        # Only count entities (ignore 'O')
        for tag in tags:
            if tag != 'O':
                # Simplified tag (e.g., B-PER -> PER)
                main_tag = tag.split("-")[-1]
                entity_counts[main_tag] += 1

    return {
        "filename": filename,
        "sentences": len(data),
        "tokens": total_tokens,
        "avg_sent_len": round(total_tokens / len(data), 2) if data else 0,
        "entities": dict(entity_counts)
    }

def main():
    files = [
        "gold_extended_final.json",
        "wikiann_final.json",
        "wikiner_final.json",
        "synthetic_final.json"
    ]

    all_stats = []
    for f in files:
        stats = analyze_dataset(f)
        if stats:
            all_stats.append(stats)

    # Print as Markdown Table
    print("# Dataset Statistics\n")
    print("| Dataset | Sentences | Tokens | Entities (Count) | Avg. Length |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    for s in all_stats:
        ent_str = ", ".join([f"{k}: {v}" for k, v in s['entities'].items()])
        print(f"| {s['filename']} | {s['sentences']} | {s['tokens']} | {ent_str} | {s['avg_sent_len']} |")

def get_all_dataset_stats():
    files = [
        "wikiann_final.json",
        "wikiner_final.json",
        "synthetic_final.json",
        "gold_extended_final.json"
    ]
    summary = []
    for f in files:
        stats = analyze_dataset(f)
        if stats:
            row = {
                "Dataset": f.replace("_final.json", "").replace("_", " ").title(),
                "Sentences": stats["sentences"],
                "Tokens": stats["tokens"],
                "Avg Length": stats["avg_sent_len"]
            }
            # Add entity columns dynamically
            for k, v in stats["entities"].items():
                row[k] = v

            summary.append(row)
    return summary

def get_token_distribution_stats():
    files = [
        "wikiann_final.json",
        "wikiner_final.json",
        "synthetic_final.json",
        "gold_extended_final.json"
    ]
    total_counts = Counter()

    for filename in files:
        path = f"data/json_export/{filename}"
        if not os.path.exists(path): continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                total_counts.update(item['tags'])

    return dict(total_counts)

if __name__ == "__main__":
    main()
