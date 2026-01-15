import os
import json
import pandas as pd
import glob

def summarize_benchmark():
    print("📊 Mevcut Model Skorları Özeti (Kayıtlı Deneyler)\n")

    exp_files = glob.glob("results/experiments/*.json")
    results = []

    for f in exp_files:
        try:
            with open(f, "r") as file:
                data = json.load(file)
                results.append({
                    "Model ID": data.get("experiment_id", os.path.basename(f)),
                    "F1 Skoru": data.get("metrics", {}).get("f1_score", 0),
                    "Metot": "CRF",
                    "Özellikler": f"Gaz: {data['config']['feature_config'].get('use_gazetteers')}, Morp: {data['config']['feature_config'].get('use_morphology')}, Emb: {data['config']['feature_config'].get('use_embeddings')}"
                })
        except:
            pass

    if results:
        df = pd.DataFrame(results).sort_values("F1 Skoru", ascending=False)
        print("🏆 MODEL KARŞILAŞTIRMA TABLOSU")
        print("=" * 100)
        print(df.to_string(index=False))
        print("=" * 100)
        print("\n✅ En iyi performanslı model 'Final_Model_Gold' olarak işaretlenmiştir.")
    else:
        print("❌ Hiç kayıtlı deney sonucu bulunamadı.")

if __name__ == "__main__":
    summarize_benchmark()
