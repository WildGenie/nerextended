import json
import os
from src.preprocessing import Preprocessor

def main():
    # Initialize both engines
    print("Initialising Engines...")
    z_prep = Preprocessor(engine="zemberek")
    n_prep = Preprocessor(engine="nuve")

    # Load Gold dataset
    gold_data_path = "data/json_export/gold_extended_final.json"
    with open(gold_data_path, "r", encoding="utf-8") as f:
        gold_data = json.load(f)

    # Sample tokens
    sample_limit = 2000
    all_tokens = []
    for item in gold_data:
        all_tokens.extend(item['tokens'])
        if len(all_tokens) > sample_limit:
            break

    tokens = all_tokens[:sample_limit]
    print(f"Analyzing agreement on {len(tokens)} tokens...")

    # Analyzing with Nuve (Bridge uses batching internally)
    nuve_all = n_prep.nuve.analyze_batch(tokens)

    agreement_count = 0
    diffs = []

    for token in tokens:
        z_lemma, _, _ = z_prep.analyze_word(token)
        n_res = nuve_all.get(token, {'lemma': token})
        n_lemma = n_res['lemma']

        if z_lemma.lower() == n_lemma.lower():
            agreement_count += 1
        else:
            diffs.append((token, z_lemma, n_lemma))

    agreement_rate = (agreement_count / sample_limit) * 100
    print(f"\nLemma Agreement Rate: {agreement_rate:.2f}%")

    print("\nSample Disagreements (Token | Zemberek | Nuve):")
    for t, z, n in diffs[:15]:
        print(f"{t} | {z} | {n}")

if __name__ == "__main__":
    main()
