import json
import os
from collections import defaultdict

def load_json_data(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_entities_from_data(data):
    entities = defaultdict(set)

    for item in data:
        tokens = item['tokens']
        tags = item['tags']

        current_entity = []
        current_type = None

        for token, tag in zip(tokens, tags):
            if tag == 'O':
                if current_entity:
                    entities[current_type].add(" ".join(current_entity))
                    current_entity = []
                    current_type = None
            elif tag.startswith('B-'):
                if current_entity:
                    entities[current_type].add(" ".join(current_entity))
                current_entity = [token]
                current_type = tag[2:]
            elif tag.startswith('I-'):
                if current_entity and current_type == tag[2:]:
                    current_entity.append(token)
                else:
                    # Invalid I- without B- or type mismatch, start fresh (loose handling)
                    if current_entity:
                         entities[current_type].add(" ".join(current_entity))
                    current_entity = [token]
                    current_type = tag[2:]

        # End of sentence flush
        if current_entity:
            entities[current_type].add(" ".join(current_entity))

    return entities

def main():
    datasets = [
        "data/json_export/wikiann_final.json",
        "data/json_export/wikiner_final.json",
        "data/json_export/gold_extended_final.json",
        # Synthetic might be too noisy or redundant, but let's include it for coverage if desired
        # "data/json_export/synthetic_final.json"
    ]

    mapping = {
        "PER": "gazetteers/kisiler.txt",
        "LOC": "gazetteers/yerler.txt",
        "ORG": "gazetteers/kurumlar.txt",
        "COMPANY": "gazetteers/sirketler.txt",
        "GROUP": "gazetteers/topluluklar.txt",
        "MOVIE": "gazetteers/film_muzik.txt"
    }

    print("Extracting entities from datasets...")
    all_new_entities = defaultdict(set)

    for ds in datasets:
        print(f"Processing {ds}...")
        data = load_json_data(ds)
        extracted = extract_entities_from_data(data)
        for etype, names in extracted.items():
            all_new_entities[etype].update(names)

    print("\nUpdating gazetteers...")
    for etype, filename in mapping.items():
        if etype not in all_new_entities:
            continue

        new_names = all_new_entities[etype]

        # Read existing
        existing_names = set()
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    existing_names.add(line.strip())

        # Merge
        combined = existing_names.union(new_names)
        added_count = len(combined) - len(existing_names)

        if added_count > 0:
            # Sort and write back
            sorted_names = sorted(list(combined))
            with open(filename, "w", encoding="utf-8") as f:
                for name in sorted_names:
                    f.write(name + "\n")
            print(f"Updated {filename}: Added {added_count} new entries. Total: {len(combined)}")
        else:
            print(f"No new entries for {filename}. Total: {len(existing_names)}")

    print("\nGazetteer enrichment complete.")

if __name__ == "__main__":
    main()
