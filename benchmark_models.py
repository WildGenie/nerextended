import os
import json
import pandas as pd
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor
from src.models.crf_model import CRFModel
from src.experiments_runner import get_gold_split
from sklearn_crfsuite import metrics
import glob
import warnings

warnings.filterwarnings("ignore")

def run_benchmark():
    print("📊 Modeller Arası Karşılaştırmalı Benchmark Başlatılıyor...\n")

    # 1. Load Data
    _, test_data = get_gold_split()
    if not test_data:
        print("❌ Test verisi bulunamadı.")
        return

    # 2. Get All Internal Models
    exp_files = glob.glob("results/experiments/*.json")
    results = []

    for f in exp_files:
        with open(f, "r") as file:
            data = json.load(file)
            m_path = data.get("model_path")
            exp_id = data.get("experiment_id")

            if m_path and os.path.exists(m_path):
                print(f"🔄 Test ediliyor: {exp_id}...")

                try:
                    # Load model
                    model = CRFModel.load(m_path)

                    # Config
                    config = data["config"]["feature_config"]
                    extractor = FeatureExtractor(**config)
                    extractor.load_gazetteers("gazetteers")

                    # Engine
                    engine = "nuve" if "nuve" in exp_id.lower() or "Final" in exp_id or "Proper" in exp_id else "zemberek"
                    preprocessor = Preprocessor(engine=engine)

                    # Prepare Test Features
                    X_test = []
                    y_test = []
                    for sent in test_data:
                        tokens = sent.get('tokens', [])
                        tags = sent.get('tags', [])
                        if not tokens: continue

                        processed = preprocessor.process_sentence(tokens)
                        X_test.append(extractor.sent2features(processed))
                        y_test.append(tags)

                    # Predict
                    y_pred = model.predict(X_test)

                    # Score (Macro F1 is usually safest for comparison)
                    f1 = metrics.flat_f1_score(y_test, y_pred, average='macro', labels=['B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG', 'B-GROUP', 'I-GROUP', 'B-MOVIE', 'I-MOVIE', 'B-COMPANY', 'I-COMPANY'])
                    prec = metrics.flat_precision_score(y_test, y_pred, average='macro', labels=['B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG', 'B-GROUP', 'I-GROUP', 'B-MOVIE', 'I-MOVIE', 'B-COMPANY', 'I-COMPANY'])
                    rec = metrics.flat_recall_score(y_test, y_pred, average='macro', labels=['B-PER', 'I-PER', 'B-LOC', 'I-LOC', 'B-ORG', 'I-ORG', 'B-GROUP', 'I-GROUP', 'B-MOVIE', 'I-MOVIE', 'B-COMPANY', 'I-COMPANY'])

                    results.append({
                        "Model ID": exp_id,
                        "F1 (Macro)": round(f1, 4),
                        "Prec": round(prec, 4),
                        "Rec": round(rec, 4),
                        "Status": "✅"
                    })
                except Exception as e:
                    print(f"⚠️ Hata: {e}")

    # 3. Display Leaderboard
    df = pd.DataFrame(results).sort_values("F1 (Macro)", ascending=False)
    print("\n🏆 MODEL LİDERLİK TABLOSU (GOLD TEST SETİ)")
    print("=" * 65)
    print(df.to_string(index=False))
    print("=" * 65)

    print("\n💡 Not: Macro F1, tüm kategorilerin (PER, LOC, ORG, GROUP, MOVIE, COMPANY) ortalamasını temsil eder.")

if __name__ == "__main__":
    run_benchmark()
