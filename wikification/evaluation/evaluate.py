import json
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.linker import EntityLinker

def evaluate():
    linker = EntityLinker()

    data_path = "data/test_sentences.json"
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    true_positives = 0
    false_positives = 0
    false_negatives = 0

    print("\n--- Running Evaluation ---\n")

    for item in data:
        text = item["text"]
        expected = set(item["expected_entities"])

        results = linker.link_entities(text)
        predicted = set([res['text'] for res in results])

        # We need to map predicted text back to expected (fuzzy match or exact?)
        # For this simple eval, we assume exact string match on the entity name found in text
        # But wait, linker returns original text segment.

        tp = len(expected.intersection(predicted))
        fp = len(predicted - expected)
        fn = len(expected - predicted)

        true_positives += tp
        false_positives += fp
        false_negatives += fn

        print(f"Text: {text}")
        print(f"  Expected: {expected}")
        print(f"  Predicted: {predicted}")
        print(f"  TP: {tp}, FP: {fp}, FN: {fn}")
        print("-" * 30)

    # Metrics
    if true_positives == 0:
        precision = 0
        recall = 0
        f1 = 0
    else:
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1 = 2 * (precision * recall) / (precision + recall)

    print("\n--- Final Metrics ---")
    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")
    print(f"F1 Score:  {f1:.2f}")

if __name__ == "__main__":
    evaluate()
