import json
import os
import logging
from src.preprocessing import Preprocessor
from src.experiments_runner import run_experiment
from src.features import BERTFeatureExtractor

def run_native_test(model_name, label):
    print(f"\n--- Testing Native Model: {label} ({model_name}) ---")

    # Reset singleton to load new model
    BERTFeatureExtractor._instance = None

    config = {
        "feature_config": {
            "use_gazetteers": True,
            "use_morphology": True,
            "use_embeddings": True,
            "embedding_model": model_name
        }
    }

    # We need to modify experiments_runner or use a manual loop here
    # since FeatureExtractor init happens inside run_experiment
    # I'll modify experiments_runner to pass the model name

    result = run_experiment(
        train_config={"include_gold_train": True, "dataset_name": f"Gold_{label}"},
        feature_config=config["feature_config"],
        engine="nuve"
    )

    if result:
        print(f"[{label}] F1 Score: {result['metrics']['f1_score']:.4f}")
        return result['metrics']['f1_score']
    return 0

def main():
    # Pre-analyze for Nuve
    prep = Preprocessor(engine="nuve")
    gold_data_path = "data/json_export/gold_extended_final.json"
    with open(gold_data_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)
    all_tokens = []
    for item in gold_data: all_tokens.extend(item['tokens'])
    prep.nuve.pre_analyze(all_tokens)

    results = {}

    # 1. VBART Small (16.1M)
    results["VBART-Small"] = run_native_test("vngrs-ai/VBART-Small-Base", "VBART_Small")

    # 2. VBART Medium (0.1B)
    results["VBART-Medium"] = run_native_test("vngrs-ai/VBART-Medium-Base", "VBART_Medium")

    # 3. Kumru (If we want to try a larger one, maybe just 2B if the others finish fast)
    # results["Kumru"] = run_native_test("vngrs-ai/Kumru-2B-Base", "Kumru")

    print("\n--- Final Results Summary ---")
    for k, v in results.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    main()
