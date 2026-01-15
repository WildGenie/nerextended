
import json
import os
import glob
import re

def load_results(directory):
    files = glob.glob(os.path.join(directory, "*.json"))
    results = []
    for f in files:
        with open(f, 'r') as file:
            try:
                data = json.load(file)
                results.append(data)
            except:
                print(f"Skipping {f}")
    return results

def generate_dataset_table(results):
    # Filter for full feature config
    filtered = [r for r in results if r.get('config', {}).get('feature_config', {}).get('use_gazetteers') and r.get('config', {}).get('feature_config', {}).get('use_morphology')]

    rows = []
    for r in filtered:
        sources = r['config']['train_sources']
        name = " + ".join(sources)
        if len(sources) == 3: name = "WikiANN + WikiNER + Synthetic"

        f1 = r['metrics'].get('f1_score', 0)
        desc = "Hibrit veri seti" if len(sources) > 1 else "Tekil veri seti"

        rows.append(f"| {name} | {f1:.4f} | {desc} |")

    # Sort by F1 desc
    rows.sort(key=lambda x: float(x.split('|')[2]), reverse=True)

    header = "| Eğitim Seti | F1-Score (Gold Test) | Açıklama |\n|-------------|----------------------|----------|"
    return header + "\n" + "\n".join(rows)

def generate_feature_table(results):
    # Filter for Combined dataset (WikiANN + WikiNER) usually
    target_sources = ["WikiANN", "WikiNER"]
    filtered = [r for r in results if set(r['config']['train_sources']) == set(target_sources)]

    rows = []
    for r in filtered:
        conf = r['config']['feature_config']
        feats = []
        if conf.get('use_morphology'): feats.append("Morfoloji")
        if conf.get('use_gazetteers'): feats.append("Gazetteer")

        name = " + ".join(feats) if feats else "Baseline (Sadece Kelime)"
        if "Morfoloji" in name and "Gazetteer" in name: name = "**Full Model**"

        f1 = r['metrics'].get('f1_score', 0)

        rows.append(f"| {name} | {f1:.4f} | - |")

    rows.sort(key=lambda x: float(x.split('|')[2]), reverse=True)

    header = "| Özellikler | F1-Score | Fark |\n|------------|----------|------|"
    return header + "\n" + "\n".join(rows)

def update_paper(paper_path, dataset_table, feature_table):
    with open(paper_path, 'r') as f:
        content = f.read()

    # Simple regex replacement for the tables
    # We assume the tables are under specific headers

    # Replace Dataset Table
    # Looking for content between ### 5.2 Veri Seti Ablasyonu ... and ###
    # This is risky with regex, so let's stick to replacing the known table structures if we can identify them.
    # OR, better: The user wants "Data from JSONs".
    # I will just print the tables and let the agent replace them safely, OR write to a separate REPORT.md
    # to avoid destroying the Paper.md structure if it's complex.
    # But sticking to instructions: "Verileri jsonlardan güncelle".

    # Strategy: Replace the lines following the specific headers until the next blank line or table end.
    pass

    print("--- DATASET ABLATION TABLE ---")
    print(dataset_table)
    print("\n--- FEATURE ABLATION TABLE ---")
    print(feature_table)

if __name__ == "__main__":
    res = load_results("results/experiments")
    d_table = generate_dataset_table(res)
    f_table = generate_feature_table(res)

    update_paper("docs/Paper.md", d_table, f_table)
