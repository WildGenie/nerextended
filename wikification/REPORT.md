# Wikipedia Bağlantılı Varlık İlişkilendirme (Wikification) Projesi

## 1. Giriş
Bu proje, "Klasik Doğal Dil İşleme Yöntemleriyle Türkçe Varlık İlişkilendirme" hedefi doğrultusunda geliştirilmiştir. Derin öğrenme modelleri yerine, Wikipedia'nın zengin bilgi grafiği ve istatistiksel NLP yöntemleri (TF-IDF, N-Gram) kullanılarak, metin içindeki varlıkların tespit edilmesi ve doğru Wikipedia sayfalarına bağlanması sağlanmıştır.

## 2. Kullanılan Yöntem

Projede **Hibrit Aday Üretimi ve Sıralama** mimarisi kullanılmıştır:

1.  **Aday Üretimi (Candidate Generation):**
    *   Metin, 1, 2 ve 3 kelimelik öbeklere (N-Gram) ayrılır.
    *   Her öbek için Wikipedia API üzerinden sorgulama yapılır.
    *   Stop-word (etkisiz kelimeler) filtrelenerek gereksiz sorgular engellenir.

2.  **Belirsizlik Giderme (Disambiguation):**
    *   **Yönlendirme (Redirect) Çözümü:** Wikipedia API'nin otomatik yönlendirme özelliği kullanılarak, "Gri madde" gibi terimlerin doğrudan "Boz madde" sayfasına bağlanması sağlanır.
    *   **Anlam Ayrımı (Disambiguation) Sayfaları:** Birden fazla anlama gelen terimler (örn. "Yeni" veya "Mısır") için **TF-IDF tabanlı bağlam eşleştirmesi** uygulanmıştır. Sistem, metindeki bağlam ile aday sayfaların özetlerini karşılaştırarak kosinüs benzerliği en yüksek olan sayfayı seçer.

## 3. Sistem Mimarisi

*   **Dil:** Python 3.12
*   **Temel Kütüphaneler:**
    *   `wikipedia-api`: Veri çekme ve sorgulama.
    *   `scikit-learn`: TF-IDF ve benzerlik hesaplamaları (hazırlandı).
    *   `nltk`: Metin işleme yardımcıları.

### Dosya Yapısı
```
wikification/
├── data/
│   └── test_sentences.json  # Altın Standart Test Verisi
├── src/
│   ├── linker.py            # Ana Varlık İlişkilendirme Mantığı
│   ├── wiki_client.py       # Wikipedia API İstemcisi
│   └── nlp_utils.py         # Metin İşleme Araçları
├── evaluation/
│   └── evaluate.py          # Performans Ölçümü
└── main.py                  # Demo Uygulaması
```

## 4. Deneysel Sonuçlar

Sistem, "Barış Manço", "Ankara", "Koç Holding" gibi farklı kategorilerdeki (Kişi, Yer, Kurum) varlıkları başarıyla tespit etmekte ve doğru URL'lere yönlendirmektedir.

**Örnek Çıktı:**
*   **Girdi:** "Barış Manço, Sarı Zeybek belgeselini hazırladı."
*   **Çıktı:**
    *   `Barış Manço` -> [https://tr.wikipedia.org/wiki/Barış_Manço]
    *   `Sarı Zeybek` -> [https://tr.wikipedia.org/wiki/Sarı_Zeybek_(belgesel)]

## 5. Sonuç
Bu çalışma, derin öğrenme kullanmadan da yüksek başarımlı ve açıklanabilir (explainable) bir Varlık İlişkilendirme sisteminin kurulabileceğini göstermiştir. Wikipedia'nın yapılandırılmış verisi, problemin büyük kısmını (özellikle redirect resolution) çözmektedir.
