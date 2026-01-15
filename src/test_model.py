import pickle
from src.preprocessing import Preprocessor
from src.features import FeatureExtractor

def test_sentences():
    prep = Preprocessor()
    feat = FeatureExtractor("gazetteers")

    with open("models/ner_crf_model.pkl", "rb") as f:
        model = pickle.load(f)

    test_cases = [
        "Barış Manço Sarı Zeybek’i Ankara’da söyledi.",
        "Arçelik TOGG ile iş birliği yaptı.",
        "Hayvanseverler Derneği İstanbul’da etkinlik düzenledi.",
        "Tarkan İstanbul'da konser verdi.",
        "Sezen Aksu yeni albümünü çıkardı.",
        "Fenerbahçe Galatasaray'ı 3-0 yendi.",
        "Koç Holding yeni yatırım açıkladı.",
        "Türk Hava Yolları seferleri iptal etti.",
        "Ahmet Kaya'nın Yorgun Demokrat şarkısı çok sevildi.",
        "MFÖ grubu Ankara'da sahne aldı.",
        "Kızılay Derneği depremzedelere yardım ulaştırdı.",
        "Yapı Kredi Bankası kredi faizlerini düşürdü.",
        "Cem Yılmaz yeni filmi için İzmir'e gitti.",
        "Netflix Türkiye'de yeni dizi yayınladı.",
        "Eskişehir Anadolu Üniversitesi öğrenci kabul ediyor.",
        "Hababam Sınıfı filmi yeniden vizyona girdi.",
        "Müslüm Gürses İstanbul'da anıldı.",
        "Beşiktaş JK şampiyonluğu kutladı."
    ]

    print("\n=== NER Model Test Results ===\n")
    for sent in test_cases:
        tokens = sent.split()
        proc = prep.process_sentence(tokens)
        features = feat.sent2features(proc)
        pred = model.predict([features])[0]

        print(f"Cümle: {sent}")
        output = []
        for w, t in zip(tokens, pred):
            if t != 'O':
                output.append(f"{w}[{t}]")
            else:
                output.append(w)
        print(f"Sonuç: {' '.join(output)}")
        print("-" * 50)

if __name__ == "__main__":
    test_sentences()
