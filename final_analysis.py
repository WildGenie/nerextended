import os
import joblib
import pandas as pd
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor
from src.models.crf_model import CRFModel
import warnings
warnings.filterwarnings("ignore")

def final_comparison_analysis():
    print("🔬 Örnek Metinler Üzerinden Model Analizi Başlatılıyor...\n")

    # 1. Models to Test
    models_to_test = [
        {"name": "Bizim En İyi Model (Best)", "path": "models/crf_gold_best.pkl", "config": {"use_gazetteers": True, "use_morphology": True, "use_embeddings": True}},
        {"name": "Orta Seviye (No Emb)", "path": "models/crf_gold_no_emb.pkl", "config": {"use_gazetteers": True, "use_morphology": True, "use_embeddings": False}},
        {"name": "Temel Seviye (Gaz Only)", "path": "models/crf_gold_gaz_only.pkl", "config": {"use_gazetteers": True, "use_morphology": False, "use_embeddings": False}},
    ]

    # 2. Example Texts
    examples = {
        "Duman & Manga": "Duman ve Manga, Türkiye'nin en sevilen rock gruplarındandır. Özellikle Manga, Eurovision başarısıyla tanınır.",
        "Titanik & Matrix": "Titanik ve Matrix filmleri çocukluğumun en unutulmaz yapımlarıydı. James Cameron ve Wachowski kardeşler harika iş çıkardı.",
        "Fenerbahçe": "Fenerbahçe, bu sezon şampiyonluk yarışında iddialı.",
        "OpenAI & Google": "OpenAI yapay zeka alanında devrim yarattı. Google ise kendi dil modelleriyle rekabete dahil oldu.",
        "Bill Gates": "William Henry Gates III (28 Ekim 1955 doğumlu) Amerikalı bir iş insanı, yazılım geliştiricisi, yatırımcı ve hayırseverdir.",
        "Mona Lisa": "Mona Lisa, Leonardo tarafından yaratılmış 16. yüzyıldan kalma bir yağlı boya tablodur. Louvre'da Paris'te sergilenmektedir.",
        "John Snow": "Kuzey'in kralı olmanın dışında, John Snow, İngiliz bir doktor ve anestezi uzmanıdır.",
        "Barış Manço": "Barış Manço'nun Gülpembe şarkısı çok güzel."
    }

    import nltk
    try: nltk.data.find('tokenizers/punkt')
    except: nltk.download('punkt')
    from nltk.tokenize import word_tokenize

    preprocessor = Preprocessor(engine="nuve")

    # 3. Execution
    for title, text in examples.items():
        print(f"\n📌 Örnek: {title}")
        print(f"📄 Metin: {text}")
        print("-" * 30)

        comparison_data = []
        tokens = word_tokenize(text)
        processed = preprocessor.process_sentence(tokens)

        for m_info in models_to_test:
            if not os.path.exists(m_info["path"]):
                continue

            try:
                model = CRFModel.load(m_info["path"])
                extractor = FeatureExtractor(**m_info["config"])
                extractor.load_gazetteers("gazetteers")

                feats = [extractor.sent2features(processed)]
                preds = model.predict(feats)[0]

                # Extract entities only for cleaner look
                entities = []
                for t, p in zip(tokens, preds):
                    if p != "O":
                        entities.append(f"{t}({p})")

                comparison_data.append({
                    "Model": m_info["name"],
                    "Tespit Edilen Varlıklar": ", ".join(entities) if entities else "Varlık bulunamadı"
                })
            except Exception as e:
                comparison_data.append({"Model": m_info["name"], "Tespit Edilen Varlıklar": f"Hata: {e}"})

        df = pd.DataFrame(comparison_data)
        print(df.to_string(index=False))
        print("=" * 80)

if __name__ == "__main__":
    final_comparison_analysis()
