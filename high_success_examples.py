import os
import joblib
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor
from src.models.crf_model import CRFModel
import warnings
warnings.filterwarnings("ignore")

def find_high_success_paragraphs():
    # Using the No-Emb model for speed and memory stability in this environment
    model_path = "models/crf_gold_no_emb.pkl"
    if not os.path.exists(model_path):
        model_path = "/Users/wildgenie/Projects/nerextended/results/models/train_Gold__feat_use_gazetteers_use_morphology.joblib"

    model = CRFModel.load(model_path)
    config = {"use_gazetteers": True, "use_morphology": True, "use_embeddings": False}
    preprocessor = Preprocessor(engine="nuve")
    extractor = FeatureExtractor(**config)
    extractor.load_gazetteers("gazetteers")

    test_paragraphs = [
        "Manga ve Duman grupları İstanbul'da verdikleri konserde binlerce hayranıyla buluştu.",
        "Hababam Sınıfı filmi Türk sinemasının en değerli eseridir. Rıfat Ilgaz bu başarının mimarıdır.",
        "OpenAI ve Google yapay zeka alanında rekabet ediyor.",
        "Fenerbahçe ve Beşiktaş maçı yarın oynanacak.",
        "Barış Manço'nun Gülpembe şarkısı hala çok popüler."
    ]

    print("🏆 Başarısı Yüksek Örnekler:\n")

    import nltk
    from nltk.tokenize import word_tokenize

    for text in test_paragraphs:
        tokens = word_tokenize(text)
        processed = preprocessor.process_sentence(tokens)
        feats = [extractor.sent2features(processed)]
        preds = model.predict(feats)[0]

        entities = [f"{t}({p})" for t, p in zip(tokens, preds) if p != "O"]
        print(f"📄 Metin: {text}")
        print(f"✨ Tespitler: {', '.join(entities) if entities else 'Varlık bulunamadı'}")
        print("-" * 40)

if __name__ == "__main__":
    find_high_success_paragraphs()
