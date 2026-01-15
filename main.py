import logging
import argparse
import os
from collections import Counter
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import make_scorer
from sklearn_crfsuite import metrics
from src.preprocessing import Preprocessor
from src.features import FeatureExtractor
from src.models.hmm_model import HMMModel
from src.models.crf_model import CRFModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def map_labels(tag_list):
    # Mapping raw WikiANN tags (0-6) to BIO strings if needed.
    # WikiANN 'tr' usually comes with 'ner_tags' as integers:
    # 0:O, 1:B-PER, 2:I-PER, 3:B-ORG, 4:I-ORG, 5:B-LOC, 6:I-LOC
    label_map = {0: 'O', 1: 'B-PER', 2: 'I-PER', 3: 'B-ORG', 4: 'I-ORG', 5: 'B-LOC', 6: 'I-LOC'}
    return [label_map.get(t, 'O') for t in tag_list]

def main():
    parser = argparse.ArgumentParser(description="Extended NER")
    parser.add_argument("--train_size", type=int, default=1000, help="Number of training sentences")
    args = parser.parse_args()

    # Dictionary to collect all results
    evaluation_results = {
        "cross_validation": {},
        "crf_model": {},
        "extended_model": {},
        "hmm_model": {},
        "demo_prediction": {}
    }

    # 1. Load & Preprocess
    prep = Preprocessor()
    ds_train = prep.load_wikiann("train", limit=args.train_size)
    ds_test = prep.load_wikiann("validation", limit=100) # Small text set

    if not ds_train:
        logging.error("Failed to load data.")
        return

    # Prepare Data for Models
    logging.info("Preparing data...")
    feature_extractor = FeatureExtractor("gazetteers")

    # helper for CRF
    def prepare_crf_data(dataset):
        X = []
        y = []
        for item in dataset:
            tokens = item['tokens']
            tags = map_labels(item['ner_tags'])

            # Analyze features
            processed_tokens = prep.process_sentence(tokens)
            features = feature_extractor.sent2features(processed_tokens)

            X.append(features)
            y.append(tags)
        return X, y

    # helper for HMM ((token, label) tuples)
    def prepare_hmm_data(dataset):
        data = []
        for item in dataset:
            tokens = item['tokens']
            tags = map_labels(item['ner_tags'])
            data.append(list(zip(tokens, tags)))
        return data

    X_train_crf, y_train_crf = prepare_crf_data(ds_train)
    X_test_crf, y_test_crf = prepare_crf_data(ds_test)

    # --- Load Data from Sanitized JSON Exports ---
    import json
    def load_json_data(filename):
        path = f"data/json_export/{filename}"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    logging.info("Loading sanitized datasets from JSON exports...")
    # Using the '_final.json' files which have been scrubbed of noise
    data_sources = {
        "WikiANN": load_json_data("wikiann_final.json"),
        "WikiNER": load_json_data("wikiner_final.json"),
        "Synthetic": load_json_data("synthetic_final.json"),
        "Gold": load_json_data("gold_extended_final.json")
    }

    X_train_final = []
    y_train_final = []
    train_hmm = []

    for name, sentences in data_sources.items():
        if not sentences: continue
        logging.info(f"Processing {name} ({len(sentences)} sentences)...")
        for item in sentences:
            tokens = item['tokens']
            tags = item['tags']

            # Feature extraction
            proc_toks = prep.process_sentence(tokens)
            feats = feature_extractor.sent2features(proc_toks)

            X_train_final.append(feats)
            y_train_final.append(tags)
            train_hmm.append(list(zip(tokens, tags)))

    if not X_train_final:
        logging.error("No training data found in JSON exports. Run export or scrub scripts first.")
        return

    # --- Dataset Statistics ---
    logging.info("Calculating Dataset Statistics...")
    all_tags = [tag for sent_tags in y_train_final for tag in sent_tags]
    from collections import Counter
    tag_counts = Counter(all_tags)
    print("\n--- Dataset Distribution ---")
    print(f"Total Sentences: {len(y_train_final)}")
    print(f"Total Tokens: {len(all_tags)}")
    for tag, count in tag_counts.items():
        print(f"{tag}: {count}")

    # --- Export Dataset (Requirement) ---
    export_path = "data/final_training_data.txt"
    logging.info(f"Exporting combined dataset to {export_path}...")
    os.makedirs("data", exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        # Reconstruct zip for export
        # Note: We need original tokens for X_train_crf (which are features now).
        # We process ds_train tokens again or store them.
        # For simplicity, we'll export what we have in HMM format since it keeps tokens.
        # But HMM data doesn't include synthetic features.
        # Let's use the 'train_hmm' + zipping synthetic tokens

        # Synthetic part is already in data_sources['Synthetic']
        # Re-gathering tokens for export
        all_sentences = []
        for name, sentences in data_sources.items():
            for item in sentences:
                all_sentences.append((item['tokens'], item['tags']))

        for tokens, tags in all_sentences:
            for w, t in zip(tokens, tags):
                f.write(f"{w} {t}\n")
            f.write("\n")

    # --- Cross Validation (Requirement) ---
    logging.info("Running 5-Fold Cross-Validation...")

    # We need a custom scorer since CRF predicts sequences
    # standard cross_val_score expects array-like, but sklearn-crfsuite works a bit differently with 'fit'
    # Actually sklearn-crfsuite mimics sklearn estimator.
    # But X and y are lists of lists. KFold works on indices.

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    fold = 1
    f1_scores = []

    for train_index, test_index in kf.split(X_train_final):
        logging.info(f"Fold {fold}/5")

        # Split data
        X_tr = [X_train_final[i] for i in train_index]
        y_tr = [y_train_final[i] for i in train_index]
        X_te = [X_train_final[i] for i in test_index]
        y_te = [y_train_final[i] for i in test_index]

        # Train
        crf_cv = CRFModel()
        crf_cv.train(X_tr, y_tr)

        # Evaluate
        labels = list(crf_cv.model.classes_)
        if 'O' in labels: labels.remove('O') # Focus on entities

        y_pred = crf_cv.model.predict(X_te)
        score = metrics.flat_f1_score(y_te, y_pred, average='weighted', labels=labels)
        f1_scores.append(score)
        print(f"Fold {fold} F1-Score: {score:.4f}")
        fold += 1

    print(f"\nAverage 5-Fold F1-Score: {sum(f1_scores)/len(f1_scores):.4f}")

    evaluation_results["cross_validation"] = {
        "fold_scores": f1_scores,
        "average_f1": sum(f1_scores)/len(f1_scores)
    }

    # Retrain on full data for final saving
    import pickle
    logging.info("Retraining on full dataset for final model...")
    crf = CRFModel()
    crf.train(X_train_final, y_train_final)

    # Save Model
    logging.info("Saving CRF model to models/ner_crf_model.pkl...")
    os.makedirs("models", exist_ok=True)
    with open("models/ner_crf_model.pkl", "wb") as f:
        pickle.dump(crf, f)

    # Eval on Test Set (Separate from CV)
    f1_crf, report_crf = crf.evaluate(X_test_crf, y_test_crf)
    print("\n--- Final Test Set (WikiANN - Classic Categories) Evaluation ---")
    print(report_crf)

    evaluation_results["crf_model"] = {
        "test_f1_score": f1_crf,
        "classification_report": report_crf
    }

    # --- NEW: Evaluate on Extended Test Set (MOVIE, GROUP, COMPANY) ---
    test_ext_path = "data/test_extended.txt"
    if os.path.exists(test_ext_path):
        X_test_ext = []
        y_test_ext = []
        current_tokens = []
        current_tags = []
        with open(test_ext_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    if current_tokens:
                        proc_toks = prep.process_sentence(current_tokens)
                        X_test_ext.append(feature_extractor.sent2features(proc_toks))
                        y_test_ext.append(current_tags)
                        current_tokens = []
                        current_tags = []
                else:
                    parts = line.split()
                    if len(parts) >= 2:
                        current_tokens.append(parts[0])
                        current_tags.append(parts[-1])

        if X_test_ext:
            f1_ext, report_ext = crf.evaluate(X_test_ext, y_test_ext)
            print("\n--- Extended Test Set (MOVIE, GROUP, COMPANY) Evaluation ---")
            print(report_ext)

            evaluation_results["extended_model"] = {
                "test_f1_score": f1_ext,
                "classification_report": report_ext
            }

    # 3. Train HMM (Baseline)
    hmm = HMMModel()
    hmm.train(train_hmm)
    # Basic eval for HMM
    logging.info("Evaluating HMM on Test Set...")
    y_pred_hmm = []
    # Re-extract tokens from ds_test for HMM prediction
    # Note: ds_test is not available here if we only imported json data?
    # Wait, ds_test was loaded at the beginning.

    # We need tokens for HMM. X_test_crf has features.
    # ds_test is available.
    if ds_test:
        hmm_test_tokens = [item['tokens'] for item in ds_test]
        # Only process if lengths match y_test_crf
        if len(hmm_test_tokens) == len(y_test_crf):
             for tokens in hmm_test_tokens:
                 y_pred_hmm.append(hmm.predict(tokens))

             print("\n--- HMM Model Evaluation (Baseline) ---")
             # Labels from CRF model (excluding 'O' usually)
             labels = list(crf.model.classes_)
             if 'O' in labels: labels.remove('O')

             print(metrics.flat_classification_report(y_test_crf, y_pred_hmm, labels=labels, digits=3))

             # Comparison Summary
             f1_hmm = metrics.flat_f1_score(y_test_crf, y_pred_hmm, average='weighted', labels=labels)
             print(f"HMM Weighted F1-Score: {f1_hmm:.4f}")
             print(f"CRF Weighted F1-Score: {f1_crf:.4f}")

             evaluation_results["hmm_model"] = {
                 "weighted_f1_score": f1_hmm,
                 "crf_comparison_f1": f1_crf,
                 "note": "HMM baseline compared on same test set as CRF"
             }
        else:
            logging.warning("Test dataset token/label mismatch, skipping HMM eval.")

    # 4. Demo: "Barış Manço Sarı Zeybek’i Ankara’da söyledi."
    print("\n--- Project Demo ---")
    demo_sent = "Barış Manço Sarı Zeybek’i Ankara’da söyledi.".split() # Simple split

    # Process
    processed_demo = prep.process_sentence(demo_sent)
    features_demo = [feature_extractor.sent2features(processed_demo)]

    # Predict CRF (Better Model)
    pred_crf = crf.predict(features_demo)[0]

    # Predict HMM
    pred_hmm = hmm.predict(demo_sent)

    print(f"Sentence: {' '.join(demo_sent)}")
    print(f"CRF Pred: {pred_crf}")
    print(f"HMM Pred: {pred_hmm}")

    # Formatted Output
    print("\nFormatted Output (CRF):")
    output = []
    for w, t in zip(demo_sent, pred_crf):
        output.append(f"{w} [{t}]")
    print(" ".join(output))

    evaluation_results["demo_prediction"] = {
        "sentence": " ".join(demo_sent),
        "crf_tags": pred_crf,
        "hmm_tags": pred_hmm,
        "formatted_output": " ".join(output)
    }

    # Save results to JSON
    # Convert potential numpy types to native types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if hasattr(obj, 'tolist'):
                return obj.tolist()
            return super(NumpyEncoder, self).default(obj)

    # Save results to JSON with timestamp
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs("results/runs", exist_ok=True)
    results_path = f"results/runs/results_{timestamp}.json"

    # Also save a 'latest' copy for easy access
    latest_path = "results/results_latest.json"

    logging.info(f"Saving evaluation results to {results_path}...")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_results, f, indent=4, ensure_ascii=False, cls=NumpyEncoder)

    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_results, f, indent=4, ensure_ascii=False, cls=NumpyEncoder)

if __name__ == "__main__":
    main()
