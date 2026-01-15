
import logging
import json
import os
import itertools
from src.experiments_runner import get_gold_split, get_external_data, FeatureExtractor, Preprocessor
from src.models.crf_model import CRFModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_grid_search(output_dir="results/optimization"):
    logging.info("Starting Grid Search...")

    # 1. Prepare Data (Use Best Combination: Gold + WikiANN + WikiNER)
    # Based on assumption that more data is better, or we default to Gold Only if that was best.
    # Let's start with Gold Split Only to be safe and fast.

    gold_train, gold_test = get_gold_split(train_ratio=0.8, seed=42)
    # Optionally append external data here if previous experiments show it helps.
    # For now, let's optimize on Gold Train to get the solid 0.8+ baseline optimized.
    train_data = gold_train
    test_data = gold_test

    # 2. Extract Features
    extractor = FeatureExtractor(use_gazetteers=True, use_morphology=True)
    prep = Preprocessor()

    def prepare_features(dataset):
        X, y = [], []
        for item in dataset:
            tokens = item['tokens']
            tags = item['tags']
            processed_tokens = prep.process_sentence(tokens)
            feats = extractor.sent2features(processed_tokens)
            X.append(feats)
            y.append(tags)
        return X, y

    logging.info("Extracting features...")
    X_train, y_train = prepare_features(train_data)
    X_test, y_test = prepare_features(test_data)

    # 3. Grid Search Space
    params_space = {
        'c1': [0.05, 0.1, 0.2, 0.5],
        'c2': [0.001, 0.01, 0.05, 0.1]
    }

    keys = params_space.keys()
    combinations = [dict(zip(keys, v)) for v in itertools.product(*params_space.values())]

    results = []

    print(f"Running {len(combinations)} combinations...")

    for params in combinations:
        crf = CRFModel(c1=params['c1'], c2=params['c2'])
        try:
            crf.train(X_train, y_train)
            f1, report = crf.evaluate(X_test, y_test)

            res_entry = {
                "params": params,
                "f1_score": f1
            }
            results.append(res_entry)
            print(f"Params: {params} -> F1: {f1:.4f}")
            logging.info(f"Params: {params} -> F1: {f1:.4f}")

        except Exception as e:
            logging.error(f"Failed for {params}: {e}")

    # 4. Save and Report Best
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "grid_search_results.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    best_run = max(results, key=lambda x: x['f1_score'])
    print(f"\nBEST Params: {best_run['params']} with F1: {best_run['f1_score']:.4f}")
    return best_run

if __name__ == "__main__":
    run_grid_search()
