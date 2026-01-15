import os
import joblib
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor
from src.models.crf_model import CRFModel
import warnings
warnings.filterwarnings("ignore")

def run_console_test():
    print("🚀 Konsol Testi Başlatılıyor...\n")

    # 1. Model & Pipeline Loading
    model_path = "models/final_model.pkl"
    if not os.path.exists(model_path):
        print(f"❌ Model dosyası bulunamadı: {model_path}")
        return

    print(f"📦 Model yükleniyor: {model_path}")
    model = CRFModel.load(model_path)

    # Config matching the model (Gold standard one)
    config = {
        "use_gazetteers": True,
        "use_morphology": True,
        "use_embeddings": True, # The final model I copied had embeddings enabled
        "embedding_model": "dbmdz/bert-base-turkish-cased"
    }

    preprocessor = Preprocessor(engine="nuve") # Defaulting to Nuve
    extractor = FeatureExtractor(**config)
    extractor.load_gazetteers("gazetteers")

    # 2. Examples
    examples = {
        "🏆 Duman & Manga (Müzik Grubu)": "Duman ve Manga, Türkiye'nin en sevilen rock gruplarındandır. Özellikle Manga, Eurovision başarısıyla tanınır.",
        "🏆 Titanik & Matrix (Film)": "Titanik ve Matrix filmleri çocukluğumun en unutulmaz yapımlarıydı. James Cameron ve Wachowski kardeşler harika iş çıkardı.",
        "🏆 Fenerbahçe (Spor Kulübü)": "Fenerbahçe, bu sezon şampiyonluk yarışında iddialı.",
        "🏆 Barış Manço (Kişi/Sanatçı)": "Barış Manço'nun Gülpembe şarkısı çok güzel.",
        "👤 Bill Gates (Biyografi)": "William Henry Gates III (28 Ekim 1955 doğumlu) Amerikalı bir iş insanı, yazılım geliştiricisi, yatırımcı ve hayırseverdir. En çok Microsoft Corporation'ın kurucu ortağı olarak tanınır.",
        "🎨 Mona Lisa (Sanat Eseri)": "Mona Lisa, Leonardo tarafından yaratılmış 16. yüzyıldan kalma bir yağlı boya tablodur. Louvre'da Paris'te sergilenmektedir.",
        "🏢 Facebook (Şirket Tarihçesi)": "Facebook, 4 Şubat 2004'te TheFacebook olarak başlatılan bir sosyal ağ hizmetidir. Mark Zuckerberg tarafından kurulmuştur.",
        "🎬 Titanik (Film Detay)": "Titanic, James Cameron tarafından yönetilmiş, 1997 Amerikan epik romantik ve felaket filmidir.",
        "❄️ John Snow (Tarih/Tıp)": "Kuzey'in kralı olmanın dışında, John Snow, İngiliz bir doktor ve anestezi uzmanıdır.",
        "🚗 Sebastian Thrun (Teknoloji)": "Sebastian Thrun, 2007 yılında Google'da kendi kendine giden arabalar üzerinde çalışmaya başladığında, şirket dışındaki pek çok insan onu ciddiye almadı.",
        "🧠 Alan Turing (Bilim Tarihi)": "1950'de, Alan Turing 'Computing Machinery and Intelligence' başlıklı bir makale yayımlamış ve günümüzde Turing testi olarak bilinen zekâ kriterini önermiştir.",
        "👨‍🔬 Geoffrey Hinton (Yapay Zeka)": "Geoffrey Everest Hinton, yapay sinir ağları üzerindeki çalışmaları ile en çok tanınan İngiliz Kanadalı bilişsel psikolog ve bilgisayar bilimcisidir.",
        "☕ Starbucks (Günlük Konuşma)": "John'a Alaska'ya taşınmak istediğimi söylediğimde, orada bir Starbucks bulmanın zor olacağını bana söyledi.",
        "🍏 Steve Jobs (Biyografi)": "Steven Paul Jobs, Amerikalı bir iş insanı, endüstriyel tasarımcı, yatırımcı ve medya sahibi olarak bilinir. Apple Inc.'in başkanı ve CEO'su idi."
    }

    import nltk
    try: nltk.data.find('tokenizers/punkt')
    except: nltk.download('punkt')
    from nltk.tokenize import word_tokenize

    # 3. Inference Loop
    for title, text in examples.items():
        print(f"\n🔹 {title}")
        print(f"📄 Metin: {text[:100]}..." if len(text)> 100 else f"📄 Metin: {text}")

        try:
            tokens = word_tokenize(text)
            processed = preprocessor.process_sentence(tokens)
            features = [extractor.sent2features(processed)]
            predictions = model.predict(features)[0]

            # Format Output
            output = []
            for t, p in zip(tokens, predictions):
                if p != "O":
                    output.append(f"[{t}]({p})")
                else:
                    output.append(t)

            print(f"👉 Sonuç: {' '.join(output)}")
        except Exception as e:
            print(f"⚠️ Hata: {e}")

        print("-" * 60)

if __name__ == "__main__":
    run_console_test()
