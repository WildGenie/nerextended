import os
import json
import pandas as pd
from src.experiments_runner import run_experiment
from src.preprocessing import Preprocessor

def main():
    results = []

    # 1. Baseline (No Morphology)
    print("\n[1/4] Running Baseline (No Morphology)...")
    res = run_experiment(
        train_config={"include_gold_train": True, "external_sources": []},
        feature_config={"use_gazetteers": True, "use_morphology": False},
        cv=True,
        k=5
    )
    results.append(res)

    # 2. Zemberek (Deep)
    print("\n[2/4] Running Zemberek (Deep)...")
    res = run_experiment(
        train_config={"include_gold_train": True, "external_sources": []},
        feature_config={"use_gazetteers": True, "use_morphology": True},
        engine="zemberek",
        cv=True,
        k=5
    )
    results.append(res)

    # 3. Nuve (Deep)
    print("\n[3/4] Running Nuve (Deep)...")
    # Pre-analyze for Nuve performance
    prep = Preprocessor(engine="nuve")
    gold_data_path = "data/json_export/gold_extended_final.json"
    if os.path.exists(gold_data_path):
        with open(gold_data_path, "r", encoding="utf-8") as f:
            gold_data = json.load(f)
        all_tokens = []
        for item in gold_data: all_tokens.extend(item['tokens'])
        prep.nuve.pre_analyze(all_tokens)

    res = run_experiment(
        train_config={"include_gold_train": True, "external_sources": []},
        feature_config={"use_gazetteers": True, "use_morphology": True},
        engine="nuve",
        cv=True,
        k=5
    )
    results.append(res)

    # 4. Nuve (Deep) + Embeddings
    print("\n[4/4] Running Nuve (Deep) + Embeddings...")
    res = run_experiment(
        train_config={"include_gold_train": True, "external_sources": []},
        feature_config={"use_gazetteers": True, "use_morphology": True, "use_embeddings": True},
        engine="nuve",
        cv=True,
        k=5
    )
    results.append(res)

    print("\nExperiments completed. All models and detailed logs saved.")

if __name__ == "__main__":
    main()
