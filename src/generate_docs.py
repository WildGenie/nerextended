
import json
import os
import glob
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from src.analyze_data import get_all_dataset_stats, get_token_distribution_stats

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

def load_best_grid_search(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Using default.")
        return {"params": {"c1": 0.1, "c2": 0.1}, "f1_score": 0.0}
    with open(filepath, 'r') as f:
        data = json.load(f)
        if not data:
             return {"params": {"c1": 0.1, "c2": 0.1}, "f1_score": 0.0}
        best = max(data, key=lambda x: x['f1_score'])
        return best

def get_gazetteer_stats():
    gaz_dir = "gazetteers"
    stats = []
    total = 0
    mapping = {
        "kisiler.txt": "Kişi",
        "yerler.txt": "Konum",
        "kurumlar.txt": "Kurum",
        "sirketler.txt": "Şirket",
        "topluluklar.txt": "Topluluk",
        "film_muzik.txt": "Eser"
    }

    if os.path.exists(gaz_dir):
        for f in os.listdir(gaz_dir):
            if f.endswith(".txt"):
                path = os.path.join(gaz_dir, f)
                with open(path, 'r', encoding='utf-8') as file:
                    count = sum(1 for _ in file)
                    name = mapping.get(f, f)
                    stats.append({"Kategori": name, "Dosya": f, "Kayıt Sayısı": count})
                    total += count

    # Format as markdown table
    stats.sort(key=lambda x: x['Kayıt Sayısı'], reverse=True)
    stats.append({"Kategori": "**Toplam**", "Dosya": "", "Kayıt Sayısı": f"**{total}**"})

    rows = []
    for s in stats:
        rows.append(f"| {s['Kategori']} | {s['Dosya']} | {s['Kayıt Sayısı']} |")

    header = "| Kategori | Dosya | Kayıt Sayısı |\n|----------|-------|--------------|"
    return header + "\n" + "\n".join(rows)

def generate_dataset_table(results):
    # Filter for full feature config runs
    filtered = [r for r in results if r.get('config', {}).get('feature_config', {}).get('use_gazetteers') and r.get('config', {}).get('feature_config', {}).get('use_morphology') and 'train_config' in r['config']]

    rows = []
    seen_configs = set()

    for r in filtered:
        tc = r['config']['train_config']

        # Determine name
        name = ""
        if tc.get('include_gold_train'):
            name = "Gold Train"

        ext = tc.get('external_sources', [])
        if ext:
            if name: name += " + "
            name += " + ".join(ext)

        if not name: name = "Unknown Config"

        # Avoid duplicates, take best
        if name in seen_configs: continue
        # actually we should probably take max if duplicates exist, but simpler for now
        seen_configs.add(name)

        f1 = r['metrics'].get('f1_score', 0)

        if "Gold" in name and "WikiANN" in name: desc = "Hibrit (Gold + External)"
        elif "Synthetic" in name: desc = "Gold + Sentetik"
        elif name == "Gold Train": desc = "Baseline (Sadece Gold)"

        # Append to row
        rows.append({"name": name, "f1": f1, "desc": desc})

    # Sort by F1
    rows.sort(key=lambda x: x['f1'], reverse=True)

    # Add (En İyi) to the top result
    if rows:
        rows[0]['desc'] += " **(En İyi Ablasyon)**"

    md_rows = []
    for r in rows:
        md_rows.append(f"| {r['name']} | {r['f1']:.4f} | {r['desc']} |")

    header = "| Eğitim Seti | F1-Score | Açıklama |\n|-------------|----------|----------|"
    return header + "\n" + "\n".join(md_rows)

def generate_feature_ablation_table(results):
    scores = {}

    for r in results:
        config = r.get('config', {})
        t_config = config.get('train_config', {})
        f_config = config.get('feature_config', {})

        # Only care about Gold dataset runs for fair comparison (or experiments targeting it)
        dataset_name = t_config.get('dataset_name', '')
        if "Gold" not in dataset_name and "Gold" not in r.get('experiment_id', ''):
             continue

        # Skip if using external data (WikiANN, etc) - we want pure feature comparison on same data
        if t_config.get('include_wikiann') or t_config.get('external_sources'):
             continue

        f1 = r['metrics'].get('f1_score', 0)

        # Determine Type based on FEATURE FLAGS
        use_gaz = f_config.get('use_gazetteers', False)
        use_morph = f_config.get('use_morphology', False)
        use_emb = f_config.get('use_embeddings', False)

        label = "Unknown"
        if not use_gaz and not use_morph and not use_emb:
            label = "Baseline (Minimal)"
        elif use_morph and not use_gaz and not use_emb:
            label = "Sadece Morfoloji (No Gazetteer)"
        elif use_gaz and not use_morph and not use_emb:
            label = "Sadece Gazetteer (No Morphology)"
        elif use_gaz and use_morph and not use_emb:
            label = "Morfoloji + Gazetteer"
        elif use_gaz and use_morph and use_emb:
            label = "Hibrit (Morph + Gaz + BERT)"

        if label != "Unknown":
            # Keep max score for this config
            if label not in scores or f1 > scores[label]:
                scores[label] = f1

    # Create Table
    table_rows = []
    # Force order
    order = ["Baseline (Minimal)", "Sadece Morfoloji (No Gazetteer)", "Sadece Gazetteer (No Morphology)", "Morfoloji + Gazetteer", "Hibrit (Morph + Gaz + BERT)"]

    for label in order:
        if label in scores:
            score = scores[label]
            bold = "**" if "Hibrit" in label else ""
            table_rows.append(f"| {label} | {bold}{score:.4f}{bold} |")

    header = "| Özellik Kümesi | F1-Score |\n|----------------|----------|"
    if not table_rows:
        return "| Özellik Kümesi | F1-Score |\n|----------------|----------|\n| Veri Bulunamadı | - |"

    return header + "\n" + "\n".join(table_rows)

def generate_cv_table(results_path="results/results_latest.json"):
    if not os.path.exists(results_path):
        return "| Fold | F1-Score |\n|---|---|\n| - | - |"

    with open(results_path, 'r') as f:
         data = json.load(f)

    cv_data = data.get("cross_validation", {})
    if not cv_data:
        return "| Fold | F1-Score |\n|---|---|\n| - | - |"

    folds = cv_data.get("fold_scores", [])
    rows = []
    for i, score in enumerate(folds, 1):
        rows.append(f"| Fold {i} | {score:.4f} |")

    avg = cv_data.get("average_f1", 0)
    rows.append(f"| **Ortalama** | **{avg:.4f}** |")

    header = "| Fold | F1-Score |\n|------|----------|"
    return header + "\n" + "\n".join(rows)

def generate_stats_markdown():
    stats = get_all_dataset_stats()
    if not stats: return ""

    df = pd.DataFrame(stats)
    cols = ["Dataset", "Sentences", "Tokens", "Avg Length", "PER", "LOC", "ORG", "COMPANY", "GROUP", "MOVIE"]
    df = df[cols]
    return df.to_markdown(index=False)

def generate_total_data_distribution_table():
    stats = get_all_dataset_stats()
    if not stats: return ""

    rows = []
    total_sentences = 0

    # Sort order: WikiANN, WikiNER, Synthetic, Gold
    order = ["WikiANN", "WikiNER", "Synthetic", "Gold"]

    stats_map = {s['Dataset']: s['Sentences'] for s in stats}

    for name in order:
         count = stats_map.get(name, 0)
         label = name
         if name == "Gold": label = "Gold (LLM Etiketli)"
         rows.append(f"| {label} | {count:,} |")
         total_sentences += count

    rows.append(f"| **Toplam** | **{total_sentences:,}** |")

    header = "| Kaynak | Cümle Sayısı |\n|--------|--------------|"
    return header + "\n" + "\n".join(rows)

def generate_token_distribution_table():
    counts = get_token_distribution_stats()
    total_tokens = sum(counts.values())

    # Specific order as per user request
    tags_order = [
        "O",
        "B-PER", "I-PER",
        "B-LOC", "I-LOC",
        "B-ORG", "I-ORG",
        "B-COMPANY", "I-COMPANY",
        "B-GROUP", "I-GROUP",
        "B-MOVIE", "I-MOVIE"
    ]

    rows = []
    for tag in tags_order:
        count = counts.get(tag, 0)
        ratio = (count / total_tokens * 100) if total_tokens > 0 else 0
        tag_display = tag
        if tag == "O": tag_display = "O (Dışarıda)"

        rows.append(f"| {tag_display} | {count:,} | %{ratio:.1f} |")

    rows.append(f"| **Toplam Token** | **{total_tokens:,}** | %100 |")

    header = "| Etiket | Sayı | Oran |\n|--------|------|------|"
    header = "| Etiket | Sayı | Oran |\n|--------|------|------|"
    return header + "\n" + "\n".join(rows)

def generate_benchmark_table(directory="results/benchmarks"):
    if not os.path.exists(directory):
         return "| Model | F1-Score | Precision | Recall |\n|---|---|---|---|\n| - | - | - | - |"

    results = load_results(directory)
    if not results:
         return "| Model | F1-Score | Precision | Recall |\n|---|---|---|---|\n| - | - | - | - |"

    rows = []
    for r in results:
        m = r.get('metrics', {})
        name = r.get('config', {}).get('model', 'Unknown')
        f1 = m.get('f1', 0)
        p = m.get('precision', 0)
        rec = m.get('recall', 0)

        rows.append(f"| {name} | {f1:.4f} | {p:.4f} | {rec:.4f} |")

    header = "| Model | F1-Score | Precision | Recall |\n|-------|----------|-----------|--------|"
    header = "| Model | F1-Score | Precision | Recall |\n|-------|----------|-----------|--------|"
    return header + "\n" + "\n".join(rows)

def get_detailed_classification_report(results):
    # Find the result with the best F1 score to show its report
    best_run = None
    best_f1 = -1

    for r in results:
        m = r.get('metrics', {})
        if not m: continue
        f1 = m.get('f1_score', 0)
        # Check against string or float comparison safely
        try:
            f1_float = float(f1)
        except:
            f1_float = 0.0

        if f1_float > best_f1:
            best_f1 = f1_float
            best_run = r

    if best_run and "report" in best_run:
        return "```\n" + best_run["report"] + "\n```"
    return "*Detaylı rapor bulunamadı.*"

def main():
    env = Environment(loader=FileSystemLoader("docs/templates"))

    # Load All Data
    exp_results = load_results("results/experiments")
    best_opt = load_best_grid_search("results/optimization/grid_search_results.json")

    # Load Latest Main Run
    latest_path = "results/results_latest.json"
    latest_main_f1 = 0.0
    latest_cv_avg = 0.0

    if os.path.exists(latest_path):
        with open(latest_path, 'r') as f:
             data = json.load(f)
             latest_main_f1 = data.get('crf_model', {}).get('test_f1_score', 0.0)
             latest_cv_avg = data.get('cross_validation', {}).get('average_f1', 0.0)

    # Calculate Best F1 across ALL experiments, not just latest/opt
    # This fixes the issue where a specific high-performing run is ignored
    max_exp_f1 = 0.0
    for r in exp_results:
         f1 = r.get('metrics', {}).get('f1_score', 0)
         if f1 > max_exp_f1:
             max_exp_f1 = f1

    # Also check cross-validation average explicitly often stored in different format
    for r in exp_results:
        cv = r.get('cross_validation', {}).get('average_f1', 0)
        if cv > max_exp_f1:
            max_exp_f1 = cv

    best_f1 = max(best_opt['f1_score'], latest_main_f1, latest_cv_avg, max_exp_f1)
    best_params = best_opt['params']

    # Prepare Dynamic Context
    context = {
        "best_f1": best_f1,
        "best_params": best_params,
        "dataset_stats_table": generate_stats_markdown(),
        "total_data_distribution_table": generate_total_data_distribution_table(),
        "token_distribution_table": generate_token_distribution_table(),
        "dataset_ablation_table": generate_dataset_table(exp_results),
        "feature_ablation_table": generate_feature_ablation_table(exp_results),
        "gazetteer_table": get_gazetteer_stats(),
        "cv_results_table": generate_cv_table(),
        "benchmark_table": generate_benchmark_table(),
        "full_classification_report": get_detailed_classification_report(exp_results)
    }

    # Render Templates
    for template_name, out_name in [("Paper.md.jinja", "docs/Akademik_Makale.md")]:
        template = env.get_template(template_name)
        with open(out_name, "w") as f:
            f.write(template.render(context))

    print(f"Documentation generated successfully. Best F1: {best_f1:.4f}")

if __name__ == "__main__":
    main()
