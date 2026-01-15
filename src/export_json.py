import json
import os
import logging
from src.preprocessing import Preprocessor
from src.data_augmentor import DataAugmentor

# Strict project taxonomy
TARGET_TAGS = {'PER', 'LOC', 'ORG', 'COMPANY', 'MOVIE', 'GROUP'}

def scrub_tags(tags):
    clean = []
    for t in tags:
        if t == 'O':
            clean.append('O')
        elif t.startswith(('B-', 'I-')) and t[2:] in TARGET_TAGS:
            clean.append(t)
        else:
            clean.append('O')
    return clean

# Mapping for WikiNER (same as in main.py)
def map_wikiner_tags(tokens, tags):
    mapped = []
    comp_keywords = ["Holding", "A.Ş.", "Ltd", "Bankası", "Şirketi", "Holdingi"]
    for token, tag in zip(tokens, tags):
        if tag == 'O':
            mapped.append('O')
            continue
        prefix = tag[:2]
        base = tag[2:]
        new_base = 'O'
        if base == 'PERSON': new_base = 'PER'
        elif base == 'WORK_OF_ART': new_base = 'MOVIE'
        elif base in ['LOC', 'GPE', 'FAC']: new_base = 'LOC'
        elif base == 'ORG':
            if any(kw in token for kw in comp_keywords): new_base = 'COMPANY'
            else: new_base = 'ORG'
        elif base in ['NORP', 'EVENT']: new_base = 'GROUP'

        if new_base == 'O': mapped.append('O')
        else: mapped.append(f"{prefix}{new_base}")
    return scrub_tags(mapped)

def map_wikiann_tags(tags):
    label_map = {0: 'O', 1: 'B-PER', 2: 'I-PER', 3: 'B-ORG', 4: 'I-ORG', 5: 'B-LOC', 6: 'I-LOC'}
    return scrub_tags([label_map.get(t, 'O') for t in tags])

def export():
    output_dir = "data/json_export"
    os.makedirs(output_dir, exist_ok=True)
    prep = Preprocessor()

    # 1. WikiANN
    print("Exporting WikiANN...")
    ds_wikiann = prep.load_wikiann(split="train", limit=1500)
    if ds_wikiann:
        data = [{"tokens": item['tokens'], "tags": map_wikiann_tags(item['ner_tags'])} for item in ds_wikiann]
        with open(f"{output_dir}/wikiann_final.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 2. WikiNER
    print("Exporting WikiNER...")
    ds_wikiner = prep.load_wikiner(split="train", limit=2000)
    if ds_wikiner:
        data = [{"tokens": item['tokens'], "tags": map_wikiner_tags(item['tokens'], item['tags'])} for item in ds_wikiner]
        with open(f"{output_dir}/wikiner_final.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 3. Synthetic (High volume to recover accuracy)
    print("Exporting Synthetic...")
    aug = DataAugmentor("gazetteers")
    synth_data = aug.generate_dataset(n_samples=5000)
    data = [{"tokens": tokens, "tags": scrub_tags(tags)} for tokens, tags in synth_data]
    with open(f"{output_dir}/synthetic_final.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 4. Gold Extended (Gemini Labeled)
    print("Exporting Gold Extended...")
    gold_path = "data/gold_extended.txt"
    if os.path.exists(gold_path):
        data = []
        current_tokens = []
        current_tags = []
        with open(gold_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    if current_tokens:
                        data.append({"tokens": current_tokens, "tags": scrub_tags(current_tags)})
                        current_tokens = []
                        current_tags = []
                else:
                    parts = line.split()
                    current_tokens.append(parts[0])
                    current_tags.append(parts[-1])
        with open(f"{output_dir}/gold_extended_final.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Export completed. All datasets standardized and saved to {output_dir}/..._final.json")

if __name__ == "__main__":
    export()
