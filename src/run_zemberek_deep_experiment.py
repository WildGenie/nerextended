import json
import os
import logging
from src.preprocessing import Preprocessor
from src.experiments_runner import run_experiment

def main():
    # 1. Initialize Preprocessor with Zemberek engine
    print("Initializing Zemberek-based Preprocessor (Deep Features)...")
    prep = Preprocessor(engine="zemberek")

    # 2. Configure Experiment
    config = {
        "feature_config": {
            "use_gazetteers": True,
            "use_morphology": True
        }
    }

    # 3. Run Experiment
    print("Starting Zemberek Deep Experiment...")
    result = run_experiment(
        train_config={"include_gold_train": True},
        feature_config=config["feature_config"],
        engine="zemberek"
    )

    if result:
        print("\nZemberek Deep Experiment Complete!")
        print(f"F1 Score: {result['metrics']['f1_score']:.4f}")

if __name__ == "__main__":
    main()
