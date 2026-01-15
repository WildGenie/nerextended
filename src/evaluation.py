import json
import os
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

def calculate_detailed_metrics(results_path):
    """
    Loads experiment results and prints a detailed per-class report.
    """
    if not os.path.exists(results_path):
        print(f"Error: {results_path} not found.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Assuming results JSON stores metrics/report
    if "metrics" in data and "report" in data["metrics"]:
        # The experiments_runner already saves a report string.
        # But we can reconstruct it from structured data if needed or just print.
        print(f"\nDetailed Metrics for: {data['experiment_id']}")
        print("-" * 50)

        report = data["metrics"]["report"]
        if isinstance(report, dict):
            df = pd.DataFrame(report).transpose()
            print(df)
        else:
            print(report)

def main():
    # Example: Analyze the latest Gold result
    latest_gold = "results/experiments/train_Gold__feat_use_gazetteers_use_morphology.json"
    calculate_detailed_metrics(latest_gold)

if __name__ == "__main__":
    main()
