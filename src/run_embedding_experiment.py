import json
import os
import logging
from src.preprocessing import Preprocessor
from src.experiments_runner import run_experiment

def main():
    # 1. Initialize Preprocessor with Nuve engine (best so far)
    print("Initializing Nuve-based Preprocessor (Deep Features)...")
    prep = Preprocessor(engine="nuve")

    # Pre-analyze all unique tokens from Gold
    print("Collecting all tokens from Gold for pre-analysis...")
    gold_data_path = "data/json_export/gold_extended_final.json"
    with open(gold_data_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    all_tokens = []
    for item in gold_data:
        all_tokens.extend(item['tokens'])

    prep.nuve.pre_analyze(all_tokens)

    # 2. Configure Experiment with Embeddings
    config = {
        "feature_config": {
            "use_gazetteers": True,
            "use_morphology": True,
            "use_embeddings": True
        }
    }

    # 3. Run Experiment
    print("Starting Hybrid Embedding-CRF Experiment (Training + Evaluation on Gold)...")
    # Note: This might be slower due to BERT feature extraction
    result = run_experiment(
        train_config={"include_gold_train": True, "dataset_name": "Gold_Embed"},
        feature_config=config["feature_config"],
        engine="nuve"
    )

    if result:
        print("\nEmbedding Experiment Complete!")
        print(f"F1 Score: {result['metrics']['f1_score']:.4f}")

if __name__ == "__main__":
    main()
