
import os
import json
import logging
import argparse
import random
from datetime import datetime
from sklearn_crfsuite import metrics
from sklearn.model_selection import KFold
import numpy as np
from src.preprocessing import Preprocessor
from src.features import FeatureExtractor
from src.models.crf_model import CRFModel
import joblib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json_data(filename):
    path = f"data/json_export/{filename}"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    print(f"Warning: {path} not found.")
    return []

def get_gold_split(train_ratio=0.8, seed=42):
    """
    Loads Gold data and splits it into fixed Train/Test sets to ensure consistency across experiments.
    """
    data = load_json_data("gold_extended_final.json")
    if not data:
        return [], []

    random.seed(seed)
    random.shuffle(data)

    split_idx = int(len(data) * train_ratio)
    train_split = data[:split_idx]
    test_split = data[split_idx:]

    logging.info(f"Gold Split: {len(train_split)} Train / {len(test_split)} Test")
    return train_split, test_split

def get_external_data(source_names):
    """
    Combines external datasets (WikiANN, etc.).
    """
    data = []
    name_map = {
        "WikiANN": "wikiann_final.json",
        "WikiNER": "wikiner_final.json",
        "Synthetic": "synthetic_final.json"
    }

    for name in source_names:
        filename = name_map.get(name)
        if filename:
            items = load_json_data(filename)
            logging.info(f"Loaded {len(items)} sentences from {name}")
            data.extend(items)

    return data

    return data

def run_experiment(train_config, feature_config, output_dir="results/experiments", engine="zemberek", cv=False, k=5):
    """
    Runs experiment with flexible training configuration.
    train_config: {
        "include_gold_train": bool,
        "external_sources": list of strings
    }
    engine: "zemberek" or "nuve"
    """
    ext_str = "_".join(train_config.get("external_sources", []))
    gold_str = "Gold" if train_config.get("include_gold_train") else "NoGold"

    exp_id = f"train_{gold_str}_{ext_str}_feat_{'_'.join([k for k,v in feature_config.items() if v])}"
    logging.info(f"Starting Experiment: {exp_id}")

    # 1. Prepare Data
    # Static Split to ensure fairness
    gold_train, gold_test = get_gold_split()

    train_data = []
    if train_config.get("include_gold_train"):
        train_data.extend(gold_train)

    external_data = get_external_data(train_config.get("external_sources", []))
    train_data.extend(external_data)

    # Test ONLY on Gold Test Split
    test_data = gold_test

    def get_dataset_stats(dataset):
        from collections import Counter
        stats = {
            "total_sentences": len(dataset),
            "total_tokens": sum(len(item['tokens']) for item in dataset),
            "tag_counts": dict(Counter([tag for item in dataset for tag in item['tags']]))
        }
        return stats

    logging.info("Calculating dataset statistics...")
    train_stats = get_dataset_stats(train_data)
    test_stats = get_dataset_stats(test_data)

    # 2. Initialize Feature Extractor
    extractor = FeatureExtractor(
        use_gazetteers=feature_config.get("use_gazetteers", True),
        use_morphology=feature_config.get("use_morphology", True),
        use_embeddings=feature_config.get("use_embeddings", False),
        embedding_model=feature_config.get("embedding_model", "dbmdz/bert-base-turkish-cased")
    )

    prep = Preprocessor(engine=engine)

    def prepare_features(dataset, cache_key=None):
        if cache_key:
            cache_dir = "results/cache"
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, f"{cache_key}.joblib")
            if os.path.exists(cache_path):
                logging.info(f"Loading cached features: {cache_path}")
                return joblib.load(cache_path)

        X, y = [], []
        for item in dataset:
            tokens = item['tokens']
            tags = item['tags']
            processed_tokens = prep.process_sentence(tokens)
            feats = extractor.sent2features(processed_tokens)
            X.append(feats)
            y.append(tags)

        if cache_key:
            logging.info(f"Caching features to: {cache_path}")
            joblib.dump((X, y), cache_path)

        return X, y

    logging.info("Extracting features...")
    # Unique cache key based on configuration and engine
    train_cache_key = f"train_{gold_str}_{ext_str}_{engine}_feat_{'_'.join([k for k,v in feature_config.items() if v])}"
    test_cache_key = f"test_gold_{engine}_feat_{'_'.join([k for k,v in feature_config.items() if v])}"

    X_train, y_train = prepare_features(train_data, cache_key=train_cache_key)

    cv_results = {}
    if cv:
        logging.info(f"Running {k}-fold Cross-Validation...")
        kf = KFold(n_splits=k, shuffle=True, random_state=42)
        fold_scores = []
        fold_reports = []
        fold_model_paths = []
        fold_weight_paths = []

        fold_dir = os.path.join(output_dir.replace("experiments", "models"), "folds")
        os.makedirs(fold_dir, exist_ok=True)

        for i, (train_idx, val_idx) in enumerate(kf.split(X_train), 1):
            X_f_train = [X_train[j] for j in train_idx]
            y_f_train = [y_train[j] for j in train_idx]
            X_f_val = [X_train[j] for j in val_idx]
            y_f_val = [y_train[j] for j in val_idx]

            crf_f = CRFModel(c1=0.1, c2=0.1)
            crf_f.train(X_f_train, y_f_train)
            f1_f, report_f = crf_f.evaluate(X_f_val, y_f_val)
            fold_scores.append(f1_f)
            fold_reports.append(report_f)

            # Save fold model
            f_model_path = os.path.join(fold_dir, f"{exp_id}_fold_{i}.joblib")
            f_weight_path = os.path.join(fold_dir, f"{exp_id}_fold_{i}_weights.json")
            crf_f.save(f_model_path)
            crf_f.save_weights(f_weight_path)

            fold_model_paths.append(f_model_path)
            fold_weight_paths.append(f_weight_path)

            logging.info(f"Fold {i}: F1 = {f1_f:.4f}")

        cv_results = {
            "fold_scores": fold_scores,
            "fold_reports": fold_reports,
            "fold_model_paths": fold_model_paths,
            "fold_weight_paths": fold_weight_paths,
            "average_f1": np.mean(fold_scores),
            "std_f1": np.std(fold_scores)
        }
        logging.info(f"CV Average F1: {cv_results['average_f1']:.4f}")

    X_test, y_test = prepare_features(test_data, cache_key=test_cache_key)

    # 3. Train (Full)
    logging.info(f"Training final CRF model on {len(X_train)} samples...")
    crf = CRFModel(c1=0.1, c2=0.1)
    crf.train(X_train, y_train)

    # 4. Evaluate
    logging.info("Evaluating on Test set...")
    f1_score, report = crf.evaluate(X_test, y_test)

    # 5. Save Final Model and Weights
    model_dir = "results/models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"{exp_id}.joblib")
    weight_path = os.path.join(model_dir, f"{exp_id}_weights.json")

    crf.save(model_path)
    crf.save_weights(weight_path)

    # 6. Save Results
    result = {
        "experiment_id": exp_id,
        "timestamp": datetime.now().isoformat(),
        "model_path": os.path.abspath(model_path),
        "weight_path": os.path.abspath(weight_path),
        "config": {
            "train_config": train_config,
            "feature_config": feature_config,
            "cv": cv,
            "k": k,
            "engine": engine
        },
        "stats": {
            "train": train_stats,
            "test": test_stats
        },
        "metrics": {
            "f1_score": f1_score,
            "report": report,
            "cross_validation": cv_results
        }
    }

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                 return obj.tolist()
            if isinstance(obj, (np.float32, np.float64)):
                 return float(obj)
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            return super(NumpyEncoder, self).default(obj)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{exp_id}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False, cls=NumpyEncoder)

    logging.info(f"Result saved to {out_path}")
    print(f"Experiment {exp_id} F1: {f1_score:.4f}")
    if cv:
        print(f"CV Average F1: {cv_results['average_f1']:.4f}")
    return result

def main():
    # Define Experiments

    base_feature_config = {"use_gazetteers": True, "use_morphology": True}

    # 1. Gold Baseline (This should restore ~0.8)
    run_experiment(
        {"include_gold_train": True, "external_sources": []},
        base_feature_config
    )

    # 2. Gold + External (Does more data help?)
    run_experiment(
        {"include_gold_train": True, "external_sources": ["WikiANN", "WikiNER"]},
        base_feature_config
    )

    # 3. Gold + Synthetic (Does synthetic data help?)
    run_experiment(
        {"include_gold_train": True, "external_sources": ["Synthetic"]},
        base_feature_config
    )

    # 4. [ABLATION] Gold without Gazetteers (Does gazetteer help?)
    run_experiment(
        {"include_gold_train": True, "external_sources": []},
        {"use_gazetteers": False, "use_morphology": True}
    )

if __name__ == "__main__":
    main()
