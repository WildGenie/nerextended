# Türkçe Wikification (Varlık İlişkilendirme)

Bu proje, Türkçe metinlerdeki varlıkları tespit edip ilgili Wikipedia sayfalarına bağlayan (Entity Linking) bir sistemdir. Derin öğrenme kullanılmamış, tamamen klasik NLP ve Wikipedia API üzerine kurulmuştur.

## Kurulum

1.  Python 3.9+ gereklidir.
2.  Bağımlılıkları yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

## Kullanım

### Demo Çalıştırma
Sistemi örnek cümlelerle test etmek için:
```bash
python main.py
```

### Değerlendirme (Evaluation)
Test veri seti (Gold Standard) üzerindeki performansı ölçmek için:
```bash
python evaluation/evaluate.py
```

## Özellikler
*   **N-Gram Analizi:** 3 kelimeye kadar olan varlıkları tanır.
*   **Otomatik Yönlendirme:** "Gri madde" -> "Boz madde" gibi eşleştirmeleri otomatik yapar.
*   **Genişletilebilir Yapı:** TF-IDF tabanlı bağlam analizi için altyapı hazırdır (`linker.py` içinde `disambiguate_tf_idf` metodu).
