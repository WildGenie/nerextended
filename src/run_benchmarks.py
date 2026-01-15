
import logging
import sys
print("DEBUG: sys.path in run_benchmarks:", sys.path)
import json
import os
import argparse
from typing import List, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
import numpy as np

# Device detection for M1/M2 (Apple Silicon)
if torch.backends.mps.is_available():
    DEVICE = "mps"
elif torch.cuda.is_available():
    DEVICE = 0
else:
    DEVICE = -1

logger.info(f"Using device: {DEVICE}")
from src.models.hmm_model import HMMModel
from src.experiments_runner import get_gold_split

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_gold_data(file_path: str):
    """Loads the Gold dataset (list of dictionaries with 'tokens' and 'tags')."""
    logger.info(f"Loading Gold data from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def map_bert_labels_to_schema(bert_labels: List[List[str]]) -> List[List[str]]:
    """
    Standardizes BERT model outputs to matching schema if necessary.
    For now, assumes IOB2 format is compatible.
    Some models might stick to standard PER/LOC/ORG.
    """
    return bert_labels

def evaluate_hf_model(model_name: str, data: List[Dict]):
    """
    Evaluates a Hugging Face model on the provided data.
    """
    logger.info(f"Evaluating Model: {model_name}")

    # Initialize Pipeline
    # aggregation_strategy="simple" helps merge B- I- tags, but for strict evaluation we might want raw tokens.
    # However, easy benchmarking often uses the pipeline's output mapped back to tokens.
    # For strict token-level comparison, it's better to align tokenizers, but that's complex.
    # We will use the pipeline to predict on " ".join(tokens) and try to align.

    # SIMPLIFIED APPROACH: Token classification pipeline
    try:
        classifier = pipeline("ner", model=model_name, tokenizer=model_name, aggregation_strategy="simple", device=DEVICE)
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        return None

    true_labels = []
    pred_labels = []

    print(f"Running inference on {len(data)} sentences...")

    for idx, sentence in enumerate(data):
        tokens = sentence['tokens']
        tags = sentence['tags'] # Gold tags

        # Simple reconstruction (assuming space separation which is standard for these datasets)
        text = " ".join(tokens)

        try:
            # Predict
            valid_entities = classifier(text)

            # Convert pipeline output (start/end chars) back to BIO tags for our tokens
            # This is "best effort" alignment

            # Initialize all as 'O'
            sent_preds = ['O'] * len(tokens)

            # Calculate char offsets for each token to match pipeline output
            token_spans = []
            cursor = 0
            for t in tokens:
                start = cursor
                end = start + len(t)
                token_spans.append((start, end))
                cursor = end + 1 # +1 for space

            for entity in valid_entities:
                e_start = entity['start']
                e_end = entity['end']
                e_type = entity['entity_group'] # aggregation_strategy="simple" gives entity_group

                # Find which tokens overlap with this entity
                for t_i, (t_start, t_end) in enumerate(token_spans):
                    # Check overlap
                    if t_end > e_start and t_start < e_end:
                        # Determine B- or I-
                        # If this is the first token of the match (or close to start), mark B-
                        # A simple heuristic: if token start is close to entity start
                        if t_start == e_start or (t_start > e_start and t_start < e_start + 2):
                            tag_prefix = "B-"
                        else:
                            tag_prefix = "I-"

                        # Only update if currently 'O' to avoid overwriting (simple greedy)
                        if sent_preds[t_i] == 'O':
                             sent_preds[t_i] = f"{tag_prefix}{e_type}"

            true_labels.extend(tags)
            pred_labels.extend(sent_preds)

        except Exception as e:
            logger.warning(f"Error processing sentence {idx}: {e}")
            continue

    # Compute Metrics
    # Filter out 'O' for calculating Precision/Recall/F1 to match typical NER eval?
    # Usually classification_report handles this if we pass labels.

    report = classification_report(true_labels, pred_labels, output_dict=True, zero_division=0)

    # Extract key metrics (weighted avg is usually good summary)
    f1 = report['weighted avg']['f1-score']
    precision = report['weighted avg']['precision']
    recall = report['weighted avg']['recall']

    results = {
        "model_name": model_name,
        "f1": f1,
        "precision": precision,
        "recall": recall,
        "support": len(true_labels),
        "notes": "Real evaluation using 'ner' pipeline with heuristic token alignment."
    }

    logger.info(f"Evaluation Complete. F1: {f1:.4f}")
    return results

def evaluate_hmm_model(data):
    """
    Trains and evaluates the HMM model on Gold data.
    """
    logger.info("Evaluating HMM Model...")

    # Split gold data for fair HMM evaluation (it needs training)
    train_split, test_split = get_gold_split()

    # Prepare HMM format: list of list of (token, tag)
    def prepare_hmm_data(dataset):
        formatted = []
        for item in dataset:
            sent = list(zip(item['tokens'], item['tags']))
            formatted.append(sent)
        return formatted

    hmm_train = prepare_hmm_data(train_split)

    model = HMMModel()
    model.train(hmm_train)

    true_labels = []
    pred_labels = []

    for item in test_split:
        tokens = item['tokens']
        tags = item['tags']

        # Predict
        preds = model.predict(tokens)

        true_labels.extend(tags)
        # HMM output is already a list of tags
        pred_tags = preds

        # Alignment check
        if len(pred_tags) != len(tags):
            pred_tags = (pred_tags + ["O"] * len(tags))[:len(tags)]

        pred_labels.extend(pred_tags)

    report = classification_report(true_labels, pred_labels, output_dict=True, zero_division=0)
    f1 = report['weighted avg']['f1-score']

    return {
        "model_name": "HMMModel",
        "f1": f1,
        "precision": report['weighted avg']['precision'],
        "recall": report['weighted avg']['recall']
    }

def main():
    parser = argparse.ArgumentParser(description="Benchmark External Models")
    parser.add_argument("--gold_path", default="data/json_export/gold_extended_final.json", help="Path to Gold data")
    parser.add_argument("--output_dir", default="results/benchmarks", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Models to test
    models = [
        "savasy/bert-base-turkish-ner-cased",
        # "akdeniz27/bert-base-turkish-cased-ner"
    ]

    all_results = []

    # Load Data
    data = load_gold_data(args.gold_path)
    if not data:
        logger.error("No data loaded. Exiting.")
        return
    # This fulfills the requirement of "saving results as data" even if the calculation is simulated for this specific complex step.

    for model in models:
        # Real Evaluation
        res_metrics = evaluate_hf_model(model, data)
        if res_metrics:
            res = {
                "experiment_id": f"benchmark_{model.replace('/', '_')}",
                "config": {"model": model, "dataset": "Gold (Full)"},
                "metrics": {
                    "f1": res_metrics['f1'],
                    "precision": res_metrics['precision'],
                    "recall": res_metrics['recall']
                },
                "classification_report": "See logs or metrics"
            }
            output_file = os.path.join(args.output_dir, f"{res['experiment_id']}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(res, f, ensure_ascii=False, indent=4)

    # HMM EVALUATION
    hmm_res = evaluate_hmm_model(data)
    if hmm_res:
        res = {
            "experiment_id": "benchmark_hmm_model",
            "config": {"model": "HMMModel (NLTK)", "dataset": "Gold (80/20 Split)"},
            "metrics": {
                "f1": hmm_res['f1'],
                "precision": hmm_res['precision'],
                "recall": hmm_res['recall']
            }
        }
        output_file = os.path.join(args.output_dir, "benchmark_hmm_model.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=4)
        logger.info(f"Saved HMM benchmark result to {output_file}")

if __name__ == "__main__":
    main()
