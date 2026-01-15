import os
import json
from src.experiments_runner import run_experiment

def main():
    config = {"include_gold_train": True, "external_sources": []}
    features = {"use_gazetteers": True, "use_morphology": True}

    print("\n--- K-Fold Stability Comparison (Zemberek Deep) ---")

    # K=5
    print("\n[1/2] Running 5-Fold CV...")
    res5 = run_experiment(config, features, engine="zemberek", cv=True, k=5)

    # K=10
    print("\n[2/2] Running 10-Fold CV...")
    res10 = run_experiment(config, features, engine="zemberek", cv=True, k=10)

    summary = {
        "k5": {
            "avg": res5['metrics']['cross_validation']['average_f1'],
            "std": res5['metrics']['cross_validation']['std_f1']
        },
        "k10": {
            "avg": res10['metrics']['cross_validation']['average_f1'],
            "std": res10['metrics']['cross_validation']['std_f1']
        }
    }

    print("\n--- STABILITY SUMMARY ---")
    print(f"K=5:  Avg F1 = {summary['k5']['avg']:.4f} (±{summary['k5']['std']:.4f})")
    print(f"K=10: Avg F1 = {summary['k10']['avg']:.4f} (±{summary['k10']['std']:.4f})")

    with open("results/k_stability_analysis.json", "w") as f:
        json.dump(summary, f, indent=4)

if __name__ == "__main__":
    main()
