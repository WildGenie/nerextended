
import os
import json
import logging
from datetime import datetime
from sklearn_crfsuite import metrics
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
    logging.warning(f"{path} not found.")
    return []

def train_specific_model(name, train_sources, feature_config, engine="nuve"):
    logging.info(f"--- Training Model: {name} ---")

    # 1. Load Data
    train_data = []
    for source in train_sources:
        train_data.extend(load_json_data(source))

    if not train_data:
        logging.error(f"No training data for {name}")
        return

    # 2. Extract Features
    prep = Preprocessor(engine=engine)
    extractor = FeatureExtractor(
        use_gazetteers=feature_config.get("use_gazetteers", True),
        use_morphology=feature_config.get("use_morphology", True),
        use_embeddings=feature_config.get("use_embeddings", False)
    )
    extractor.load_gazetteers("gazetteers")

    # OPTIMIZATION: Pre-analyze all tokens in one batch
    if engine == "nuve" and prep.nuve:
        all_tokens = []
        for item in train_data:
            all_tokens.extend(item['tokens'])
        logging.info(f"Pre-analyzing {len(all_tokens)} total tokens ({len(set(all_tokens))} unique)...")
        prep.nuve.pre_analyze(all_tokens)

    X_train, y_train = [], []
    logging.info(f"Extracting features for {len(train_data)} sentences...")
    for item in train_data:
        tokens = item['tokens']
        tags = item['tags']
        processed = prep.process_sentence(tokens)
        X_train.append(extractor.sent2features(processed))
        y_train.append(tags)

    # 3. Train
    logging.info(f"Fitting CRF model for {name}...")
    crf = CRFModel(c1=0.1, c2=0.1)
    crf.train(X_train, y_train)

    # 4. Save
    os.makedirs("models", exist_ok=True)
    save_path = f"models/{name}.pkl"
    crf.save(save_path)
    logging.info(f"Saved {name} to {save_path}")

def main():
    # Model 1: Best (All Data + Morphology)
    train_specific_model(
        "crf_gold_best",
        ["gold_extended_final.json", "wikiann_final.json", "wikiner_final.json", "synthetic_final.json"],
        {"use_gazetteers": True, "use_morphology": True}
    )

    # Model 2: Standard (WikiANN + Gold)
    train_specific_model(
        "crf_gold_no_emb",
        ["gold_extended_final.json", "wikiann_final.json"],
        {"use_gazetteers": True, "use_morphology": True}
    )

    # Model 3: Basic (No Morphology)
    train_specific_model(
        "crf_gold_gaz_only",
        ["gold_extended_final.json"],
        {"use_gazetteers": True, "use_morphology": False}
    )

if __name__ == "__main__":
    main()
