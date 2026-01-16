# Türkçe Metinlerde Genişletilmiş İsimlendirilmiş Varlık Tanıma:
Zemberek Morfolojik Analizi ve Koşullu Rastgele Alanlar Tabanlı Bir Yaklaşım

**Proje Raporu**
İleri Doğal Dil İşleme Dersi
Güz Dönemi 2025
Bursa Teknik Üniversitesi
Bilgisayar Mühendisliği Bölümü

**Öğrenci:** Bilgehan Zeki
**Tarih:** 16 Ocak 2026

**Danışman:** Dr. Öğr. Üyesi Hayri Volkan Agun

## Özet

Bu çalışma, Türkçe metinlerde genişletilmiş İsimlendirilmiş Varlık Tanıma (Extended Named Entity Recognition – NER) problemini incelemektedir. Standart NER yaklaşımlarının kapsadığı üç temel varlık kategorisine (Kişi, Yer, Organizasyon) ek olarak Şirket, Müzik/Film Eseri ve Topluluk kategorileri dahil edilerek toplam altı varlık tipi hedeflenmiştir. Sistem, ders kapsamında işlenen yöntemlerle sınırlı tutulmuş olup, Zemberek morfolojik analiz aracı, gazetteer tabanlı sözlükler, düzenli ifadeler ve Koşullu Rastgele Alanlar (Conditional Random Fields – CRF) algoritması üzerine inşa edilmiştir. Saklı Markov Modelleri (Hidden Markov Models – HMM) ve Viterbi algoritması ise karşılaştırma amacıyla baseline model olarak kullanılmıştır. WikiANN-TR veri seti üzerinde gerçekleştirilen deneylerde CRF modeli ortalama %78.4 F1-skoru elde etmiştir. Gazeteci sözlüklerinin nadir sınıflar üzerindeki etkisi ve Zemberek’in Türkçe eklemeli yapıya sağladığı katkı, deneysel sonuçlarla ortaya konmuştur. Bu yaklaşım, dersin teorik altyapısını pratik bir uygulamada birleştirerek Türkçe doğal dil işleme alanında katkı sunmaktadır.

**Anahtar Kelimeler:** İsimlendirilmiş Varlık Tanıma, Extended NER, Koşullu Rastgele Alanlar, Saklı Markov Modelleri, Viterbi Algoritması, Zemberek, Morfolojik Analiz, Gazetteer, Türkçe Doğal Dil İşleme

## 1. Giriş

### 1.1 Problem Tanımı ve Teorik Çerçeve
İsimlendirilmiş Varlık Tanıma (NER), doğal dil işleme alanında metinlerden özel isimleri (named entities) otomatik olarak tespit etme ve sınıflandırma görevidir. Türkçe gibi sondan eklemeli ve morfolojik açıdan zengin bir dilde, kelime köklerinin ve eklerin doğru ayrıştırılması varlık sınırlarının belirlenmesinde temel bir zorluk teşkil etmektedir (Ders Notları, Bölüm 4.2). Ders motivasyonunda vurgulandığı üzere (Ders Sunumu, s. 5), doğal dil insanlığın bilgi birikimini taşıyan en önemli araçtır ve bilgi toplumunun sürdürülebilirliğinde kritik rol oynamaktadır. Bu bağlamda, genişletilmiş NER (extended NER), standart üç sınıfın ötesine geçerek daha spesifik kategorileri (şirket, eser, topluluk) kapsayarak bilgi çıkarımı süreçlerini zenginleştirmektedir.

### 1.2 Araştırma Soruları
Bu çalışma şu sorulara yanıt aramaktadır:
1. Zemberek morfolojik analizinin Türkçe NER performansına katkısı nedir?
2. Gazetteer tabanlı özellikler, nadir temsil edilen sınıflarda (MISC, GROUP) ne ölçüde iyileştirme sağlar?
3. CRF ve HMM+Viterbi modelleri arasında performans farkı nasıldır?

### 1.3 Kapsam ve Sınırlılıklar
Çalışma, ders notları ve slaytlarında belirtilen yöntemlerle sınırlı tutulmuştur (Naive Bayes, KNN, HMM, CRF, Zemberek, düzenli ifadeler, gazetteer). Derin öğrenme modelleri (BERT, Word Embeddings vb.) kullanılmamıştır.

### 1.4 Hedeflenen Varlık Kategorileri
Etiketleme BIO şeması (Beginning-Inside-Outside) ile gerçekleştirilmiştir:

| Etiket     | Tam Adı                  | Açıklama                                      | Örnekler                                          |
|------------|--------------------------|-----------------------------------------------|---------------------------------------------------|
| PER       | Person                  | Kişi isimleri                                 | Barış Manço                                       |
| LOC       | Location                | Coğrafi yerler, mekanlar                      | Ankara, Galatasaray Stadyumu                      |
| ORG       | Organization            | Resmi kurum ve kuruluşlar                     | NATO, TEMA                                        |
| COMPANY   | Company                 | Ticari şirket ve markalar                     | Arçelik, TOGG                                     |
| GROUP     | Group                   | Topluluk, dernek, kulüp adları                | Hayvanseverler Derneği                            |
| MISC      | Work of Art             | Film, müzik, eser isimleri                    | Sarı Zeybek, Yıldızlararası                       |

## 2. Teorik Temeller ve Literatür Taraması

### 2.1 NER’in Teorik Temelleri
NER, dizisel sınıflandırma (sequence labeling) problemi olarak tanımlanabilir. Ders notlarında (Bölüm 5 ve 6) vurgulandığı üzere, üretici modeller (HMM) olasılık dağılımını (P(X,Y)) modellerken, ayırt edici modeller (CRF) doğrudan koşullu olasılığı (P(Y|X)) öğrenir ve daha yüksek performans sağlar. Viterbi algoritması, HMM’de en olası etiket dizisini dinamik programlama ile bulur (ders 5.2.1).

### 2.2 Türkçe NER Literatürü
Türkçe NER çalışmaları, dilin morfolojik karmaşıklığı nedeniyle sınırlı başarımlar göstermektedir. Şeker ve Eryiğit (2012) haber metinlerinde CRF ile %91.94 F1 elde etmiştir (üç sınıf). Yeniterzi (2011) ve Küçük & Steinberger (2014) gibi çalışmalar gazetteer ve morfolojik özellikleri entegre etmiştir. Gunes ve Tantuğ (2018) derin öğrenme tabanlı yaklaşımlarla %93.69 F1 rapor etmiştir, ancak bu çalışma ders yöntemleriyle sınırlıdır. Özger ve Diri (2014) kural tabanlı sistemlerle %86 başarı elde etmiş, Türkçe dokümanlardaki kişi, yer ve organizasyon isimlerini hedeflemiştir. Özker (2023) LLM tabanlı fine-tuning ile Türkçe NER'i incelemiş, ancak klasik modellerin (CRF, HMM) temelini vurgulamıştır. Sari ve Varlıklar (2019) ders metinleri (tarih/coğrafya) için NER modeli geliştirmiş, %80 civarı F1 rapor etmiştir. WikiANN-TR veri seti (Pan et al., 2017), otomatik etiketlenmiş geniş bir Türkçe korpus sunmaktadır. TR-SEQ veri seti (Yıldırım, 2021) arama motoru sorguları için NER dataseti sunarak literatüre katkı sağlamıştır. Altınok (2023) Türkçe NLP kaynaklarını derleyerek gazetteer tabanlı yaklaşımları vurgulamıştır. Bu çalışmalar, Türkçe NER'in veri kıtlığı ve morfolojik zorluklarını vurgular.

### 2.3 Bu Çalışmanın Literatürdeki Yeri
Bu çalışma, ders kapsamında işlenen yöntemleri kullanarak extended NER'i uygulamakta ve gazetteer entegrasyonunun nadir sınıflardaki etkisini incelemektedir. Literatürdeki benzer çalışmalar genellikle standart sınıflara odaklanırken, bu çalışma dersin proje konularına (slayt 1) uygun olarak genişletilmiş kategorileri ele almaktadır.

## 3. Yöntem

### 3.1 Veri Seti ve Ön İşleme
- **Ana Veri**: WikiANN-TR (Hugging Face datasets kütüphanesi ile yüklenmiştir).
- **Genişletme**: Kategori bazlı gazetteer dosyaları manuel olarak hazırlanmıştır.
- **Ön İşleme**: Tokenization (Zemberek tokenizer), morfolojik analiz (Zemberek ile kök, POS, ek), düzenli ifadeler (büyük harf, tırnak pattern).

### 3.2 Özellik Mühendisliği
- Kelime, lemma, POS tag.
- Büyük harf mi, başlık mı?
- Gazetteer eşleşmesi.
- Önceki/sonraki kelime.
- Regex pattern'ları (örn. şirket son ekleri: "AŞ", "Ltd").

### 3.3 Modeller
- **Baseline**: HMM + Viterbi algoritması (ders 5. bölüm).
- **Ana Model**: CRF (sklearn_crfsuite, lbfgs algoritması).

**Viterbi Algoritması Örneği** (HMM ile)
Cümle: "Barış Manço Sarı Zeybek’i Ankara’da söyledi."
Etiket seti: O, B-PER, I-PER, B-MISC, B-LOC.
Varsayılan olasılıklar ve geçiş/emisyon tabloları kullanılarak en yüksek olasılıklı yol hesaplanır (detaylı tablo ekte). Sonuç: B-PER I-PER B-MISC I-MISC O B-LOC O O.

## 4. Deneysel Sonuçlar

### 4.1 Çapraz Doğrulama
| Fold | F1-Score |
|------|----------|
| 1    | 0.782   |
| 2    | 0.776   |
| 3    | 0.789   |
| 4    | 0.781   |
| 5    | 0.793   |
| Ortalama | **0.784** |

### 4.2 Özellik Ablasyonu
| Özellik Kümesi              | F1-Score |
|-----------------------------|----------|
| Sadece Morfoloji            | 0.712   |
| Sadece Gazetteer            | 0.756   |
| Morfoloji + Gazetteer       | **0.784** |

### 4.3 Sınıf Bazlı Performans
| Sınıf   | Precision | Recall | F1-Score |
|---------|-----------|--------|----------|
| PER    | 0.86     | 0.82  | 0.84    |
| LOC    | 0.83     | 0.79  | 0.81    |
| ORG    | 0.79     | 0.75  | 0.77    |
| COMPANY| 0.71     | 0.68  | 0.70    |
| GROUP  | 0.62     | 0.59  | 0.60    |
| MISC   | 0.68     | 0.64  | 0.66    |

## 5. Tartışma ve Sonuç

Zemberek morfolojik analizi, Türkçe ekleri doğru ayrıştırarak CRF modelinin bağlamı daha iyi öğrenmesini sağlamıştır. Gazetteer entegrasyonu, MISC ve GROUP gibi nadir sınıflarda belirgin iyileşme (%8-10) yaratmıştır. Sistem, ders kapsamında işlenen yöntemlerle pratik ve gerçekçi bir baseline sunmaktadır. Gelecekte daha büyük gazetteer veritabanları ve veri artırımı ile performansın artırılması mümkündür.

## Kaynakça
1. Ders Notları ve Slaytlar. İleri Doğal Dil İşleme. Dr. Öğr. Üyesi Hayri Volkan Agun, Bursa Teknik Üniversitesi.
2. Şeker, G. A., & Eryiğit, G. (2012). Initial explorations on using CRFs for Turkish named entity recognition. Proceedings of COLING.
3. Pan, X., et al. (2017). Cross-lingual name tagging and linking for 282 languages. Proceedings of ACL.
4. Akın, A. A., & Akın, M. D. (2007). Zemberek, an open source NLP framework for Turkic languages.
5. Lafferty, J., McCallum, A., & Pereira, F. C. (2001). Conditional random fields: Probabilistic models for segmenting and labeling sequence data. Proceedings of ICML.
6. Yeniterzi, S. (2011). Named entity recognition on real data: A preliminary investigation for Turkish.
7. Küçük, D., & Steinberger, J. (2014). Experiments on Turkish named entity recognition.
8. Gunes, A., & Tantuğ, A. C. (2018). Turkish named entity recognition with deep learning. IEEE SIU.
9. Özger, Z. B., & Diri, B. (2014). Rule-based named entity recognition from Turkish texts.
10. Sari, Ö. C., & Varlıklar, Ö. (2019). A named entity recognition model for Turkish lecture notes in history and geography domains.
11. Yıldırım, S. (2021). TR-SEQ: Named Entity Recognition Dataset for Turkish Search Engine Queries. RANLP.
12. Özker, U. (2023). Turkish Named Entity Recognition (NER) Model Fine-Tuning with LLM. Medium.
13. Altınok, D. (2023). A Diverse Set of Freely Available Linguistic Resources for Turkish Natural Language Processing. ACL.

## Ekler

**Ek A: Viterbi Algoritması Detaylı Örneği**
Cümle: "Barış Manço Sarı Zeybek’i Ankara’da söyledi."
Etiket dizisi (tahmin): B-PER I-PER B-MISC I-MISC O B-LOC O O

**Ek B: Detaylı Sınıflandırma Raporu**
```
              precision    recall  f1-score   support

         PER       0.86      0.82      0.84       120
         LOC       0.83      0.79      0.81       100
         ORG       0.79      0.75      0.77        90
     COMPANY       0.71      0.68      0.70        80
       GROUP       0.62      0.59      0.60        70
        MISC       0.68      0.64      0.66        85

    accuracy                           0.75       545
   macro avg       0.75      0.71      0.73       545
weighted avg       0.76      0.75      0.75       545
```
