import os
import json
import logging
from src.experiments_runner import run_experiment
from src.preprocessing import Preprocessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("\n--- Running Hybrid Morphology Experiment (Nuve + Zemberek) ---")

    # OPTIMIZATION: Pre-analyze ALL data for Nuve to fill cache once
    # Since NuveBridge is a singleton, this cache will be shared with the inner run_experiment call
    prep = Preprocessor(engine="hybrid")
    gold_data_path = "data/json_export/gold_extended_final.json"
    if os.path.exists(gold_data_path):
        with open(gold_data_path, "r", encoding="utf-8") as f:
            gold_data = json.load(f)
        all_tokens = []
        for item in gold_data: all_tokens.extend(item['tokens'])
        logging.info(f"Pre-analyzing {len(all_tokens)} total tokens...")

        # Access the singleton bridge directly or via prep
        if prep.nuve:
            prep.nuve.pre_analyze(all_tokens)

    # 1. Hybrid (Nuve + Zemberek)
    # This will use the new 'hybrid' engine mode which populates both feature sets
    res = run_experiment(
        train_config={"include_gold_train": True, "external_sources": []},
        feature_config={"use_gazetteers": True, "use_morphology": True},
        engine="hybrid", # Trigger hybrid mode
        cv=True,
        k=5
    )

    print(f"\nHybrid Experiment F1: {res['metrics']['f1_score']:.4f}")
    print(f"CV Average F1: {res['metrics']['cross_validation']['average_f1']:.4f}")

    # Also save as a special named file for easy identification on dashboard
    base_path = "results/experiments"
    orig_file = f"{base_path}/train_Gold__hybrid_feat_use_gazetteers_use_morphology.json" # Default name likely
    new_file = f"{base_path}/Hybrid_Nuve_Zemberek.json"

    # Experiments runner generates filename based on config.
    # It constructs exp_id based on config keys.
    # exp_id = f"train_{gold_str}_{ext_str}_feat_{'_'.join([k for k,v in feature_config.items() if v])}"
    # But engine isn't in exp_id by default in run_experiment (it creates cache key with it, but not experiment_id).
    # Wait, experiments_runner.py line 79:
    # exp_id = f"train_{gold_str}_{ext_str}_feat_{'_'.join([k for k,v in feature_config.items() if v])}"
    # It DOES NOT include engine in the filename! This is a potential collision if we run zemberek/nuve/hybrid setups with same config.

    # We should probably rename the output file manually to avoid overwriting or confusion.
    # The run_experiment returns the result. experiment_id is inside it.

    exp_id = res['experiment_id']
    # The runner saves to results/experiments/{exp_id}.json

    # Since experiments_runner key generation ignores engine, let's manually rename or copy it
    # to ensure it's distinct for the dashboard.

    src_path = f"results/experiments/{exp_id}.json"
    if os.path.exists(src_path):
        import shutil
        shutil.copy(src_path, new_file)
        logging.info(f"Saved copy as {new_file}")

if __name__ == "__main__":
    main()
