import os
import joblib
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor
from src.models.crf_model import CRFModel
from nltk.tokenize import word_tokenize
import warnings
warnings.filterwarnings("ignore")

def score_specific_paragraphs():
    model_path = "models/final_model.pkl"
    if not os.path.exists(model_path):
        print("Model bulunamadı.")
        return

    model = CRFModel.load(model_path)
    # Most powerful config
    config = {"use_gazetteers": True, "use_morphology": True, "use_embeddings": True}
    preprocessor = Preprocessor(engine="nuve")
    extractor = FeatureExtractor(**config)
    extractor.load_gazetteers("gazetteers")

    # Paragraphs with their expected critical entities (to calculate a success rate)
    test_suite = [
        {
            "id": "🏆 Fenerbahçe",
            "text": "Fenerbahçe, bu sezon şampiyonluk yarışında iddialı.",
            "expected": ["Fenerbahçe"]
        },
        {
            "id": "🏆 Titanik & Matrix",
            "text": "Titanik ve Matrix filmleri çocukluğumun en unutulmaz yapımlarıydı. James Cameron ve Wachowski kardeşler harika iş çıkardı.",
            "expected": ["Titanik", "Matrix", "James", "Cameron"]
        },
        {
             "id": "❄️ John Snow",
             "text": "Kuzey'in kralı olmanın dışında, John Snow, İngiliz bir doktor ve anestezi uzmanıdır.",
             "expected": ["John", "Snow"]
        },
        {
            "id": "👤 Bill Gates",
            "text": "William Henry Gates III (28 Ekim 1955 doğumlu) Amerikalı bir iş insanı, yazılım geliştiricisi, yatırımcı ve hayırseverdir.",
            "expected": ["William", "Henry", "Gates"]
        },
        {
            "id": "🎨 Mona Lisa",
            "text": "Mona Lisa, Leonardo tarafından yaratılmış 16. yüzyıldan kalma bir yağlı boya tablodur. Louvre'da Paris'te sergilenmektedir.",
            "expected": ["Mona", "Lisa", "Leonardo", "Louvre", "Paris"]
        },
        {
            "id": "🏆 Duman & Manga",
            "text": "Duman ve Manga, Türkiye'nin en sevilen rock gruplarındandır. Özellikle Manga, Eurovision başarısıyla tanınır.",
            "expected": ["Duman", "Manga"]
        },
        {
            "id": "🏆 Barış Manço",
            "text": "Barış Manço'nun Gülpembe şarkısı çok güzel.",
            "expected": ["Barış", "Manço"]
        },
        {
            "id": "🏢 Facebook",
            "text": "Facebook, 4 Şubat 2004'te TheFacebook olarak başlatılan bir sosyal ağ hizmetidir. Mark Zuckerberg tarafından kurulmuştur.",
            "expected": ["Facebook", "TheFacebook", "Mark", "Zuckerberg"]
        }
    ]

    scored_results = []
    print(f"{'Örnek ID':<20} | {'Başarı Skoru':<15} | {'Bulunan Varlıklar'}")
    print("-" * 60)

    for item in test_suite:
        tokens = word_tokenize(item["text"])
        processed = preprocessor.process_sentence(tokens)
        feats = [extractor.sent2features(processed)]
        preds = model.predict(feats)[0]

        found = []
        for t, p in zip(tokens, preds):
            if p != "O":
                found.append(t)

        # Calculate score: found expected / total expected
        expected_found = [e for e in item["expected"] if any(e in f for f in found)]
        score = len(expected_found) / len(item["expected"]) if item["expected"] else 0

        scored_results.append({
            "id": item["id"],
            "score": score,
            "found": ", ".join(found) if found else "Varlık bulunamadı",
            "text": item["text"]
        })

        print(f"{item['id']:<20} | %{score*100:<13.1f} | {', '.join(found) if found else 'Yok'}")

    return scored_results

if __name__ == "__main__":
    results = score_specific_paragraphs()
    print("\n✅ Analiz tamamlandı. Skorları 0 olan paragraflar elenebilir.")
