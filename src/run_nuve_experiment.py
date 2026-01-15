import json
import os
import logging
from src.preprocessing import Preprocessor
from src.experiments_runner import run_experiment

def main():
    # 1. Initialize Preprocessor with Nuve engine
    print("Initializing Nuve-based Preprocessor (Deep Features)...")
    nuve_preprocessor = Preprocessor(engine="nuve")

    # Pre-analyze all unique tokens from Gold to avoid subprocess overhead during training
    print("Collecting all tokens from Gold for pre-analysis...")
    gold_data_path = "data/json_export/gold_extended_final.json"
    if not os.path.exists(gold_data_path):
        print(f"Error: {gold_data_path} not found.")
        return

    with open(gold_data_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    all_tokens = []
    for item in gold_data:
        all_tokens.extend(item['tokens'])

    print(f"Total Unique tokens: {len(set(all_tokens))}")
    nuve_preprocessor.nuve.pre_analyze(all_tokens)

    # 2. Configure Experiment
    config = {
        "feature_config": {
            "use_gazetteers": True,
            "use_morphology": True
        }
    }

    # 3. Run Experiment
    print("Starting Nuve Experiment...")
    result = run_experiment(
        train_config={"include_gold_train": True},
        feature_config=config["feature_config"],
        engine="nuve"
    )

    if result:
        print("\nNuve Experiment Complete!")
        print(f"F1 Score: {result['metrics']['f1_score']:.4f}")

if __name__ == "__main__":
    main()
