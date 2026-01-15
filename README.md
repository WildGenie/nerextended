# Türkçe Genişletilmiş Varlık İsim Tanıma (Extended NER)

Bu proje, Türkçe metinler için gelişmiş **Varlık İsim Tanıma (NER)** gerçekleştiren hibrit bir sistemdir. Geleneksel **CRF (Conditional Random Fields)** yöntemini, derin morfolojik analiz (**Nuve/Zemberek**) ve modern bağlamsal kelime gömülmeleri (**BERT**) ile birleştirerek yüksek başarım hedefler.

## 🌟 Öne Çıkan Özellikler

- **6 Genişletilmiş Kategori:** Standart 3 kategoriye (PER, LOC, ORG) ek olarak `COMPANY` (Şirket), `GROUP` (Topluluk) ve `MOVIE` (Eser) sınıflarını tanır.
- **Derin Morfoloji:** Nuve motoru ile Türkçe'ye özgü ünlü düşmesi, ünsüz yumuşaması ve granüler ek etiketlerini (pos, case markers) öznitelik olarak kullanır.
- **Hibrit Mimari:** BERT (BERTurk) vektörlerini klasik CRF öznitelikleriyle harmanlayarak hem yapısal hem semantik bilgi sağlar.
- **Geniş Sözlük Desteği:** 160.000+ kayıtlık kapsamlı gazetteer (sözlük) tabanlı öznitelik sinyalleri.

## � Performans Özet (SOTA)

Modelimiz, **Gold Test Seti** üzerinde aşağıdaki başarımı yakalamıştır:

| Metrik | Değer |
| :--- | :--- |
| **En İyi F1-Score** | **%86.66** |
| Precision | %87.42 |
| Recall | %85.91 |

*Detaylı analizler ve karşılaştırmalı tablolar için dökümantasyona bakınız.*

## 🚀 Başlangıç

### Gereksinimler
- **Python 3.11 veya 3.12** (Önerilen)
- 4GB+ RAM

### Kurulum ve Çalıştırma

```bash
# 1. Klonla ve dizine gir
git clone https://github.com/kullanici/nerextended.git
cd nerextended

# 2. Sanal ortamı kur
python3.12 -m venv venv
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Görsel Demoyu Başlat (Streamlit)
streamlit run Demo.py
```

## 📚 Dökümantasyon

Projenin teknik, akademik ve uygulama detayları tek bir ana dökümanda konsolide edilmiştir:

- **[Akademik ve Teknik Makale (Full Documentation)](docs/Akademik_Makale.md)**
    - Veri seti inşa stratejisi (WikiANN, WikiNER, Gold Extended).
    - Teknik mimari ve özellik mühendisliği (Feature Engineering).
    - Morfolojik motor karşılaştırmaları (Zemberek vs Nuve).
    - Detaylı ablasyon analizleri ve benchmark sonuçları.
    - BIO etiketleme standartları ve Terimler Sözlüğü.

## � Proje Yapısı

- `main.py`: Eğitim ve test süreçlerini yöneten ana terminal girişi.
- `Demo.py`: İnteraktif çıkarım ve dashboard arayüzü (Streamlit).
- `src/`: Morfolojik analiz, özellik çıkarımı ve model sarmalayıcıları.
- `gazetteers/`: 6 farklı kategorideki varlık isim listeleri (.txt).
- `docs/`: Akademik makale ve dökümantasyon şablonları.
- `results/`: Deney çıktıları ve sınıflandırma raporları.

## Lisans
MIT License - Akademik ve eğitim amaçlı geliştirilmiştir.✨
