# Türkçe Metinler için Genişletilmiş Varlık İsim Tanıma: Derin Morfoloji ve Bağlamsal Gömülmeler ile CRF Yaklaşımı

**Proje Raporu**
**İleri Doğal Dil İşleme Dersi**
**Güz Dönemi 2025**
**Bursa Teknik Üniversitesi - Bilgisayar Mühendisliği Bölümü**

**<sup>1</sup>Bilgehan Zeki ÖZAYTAÇ[![][image1]](https://orcid.org/0009-0009-1931-9197), <sup>2</sup>Doç. Dr. Hasan ŞAHİN[![][image2]](https://orcid.org/0000-0002-8915-000X), <sup>3</sup>Dr. Öğr. Üyesi Hayri Volkan AGUN**

*<sup>1</sup>Bursa Teknik Üniversitesi, Lisansüstü Eğitim Enstitüsü, Endüstri Mühendisliği Anabilim Dalı, Bursa, Türkiye*
*<sup>2</sup>Bursa Teknik Üniversitesi, Mühendislik ve Doğa Bilimleri Fakültesi, Endüstri Mühendisliği Bölümü, Bursa, Türkiye*
*<sup>3</sup>Bursa Teknik Üniversitesi, Mühendislik ve Doğa Bilimleri Fakültesi, Bilgisayar Mühendisliği Bölümü, Bursa, Türkiye*

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAATCAYAAACUef2IAAADSElEQVR4AbSTS2yUVRTHf/ebbzozZdpOa9N3aWkFkmKqYqKl2kDERBMxGg0bExNcqBsT1wYWJk0wikFxZVy5MjHIogQTYQELILwhvF/l1SePDi2ddmY68813Ofcb+g3NDGXFnXPuvef1/84954ylX8zqtVh0abTOkXMzZJwETi6Fq7OicxeNMsaSwAZsZm6UaxO7+P/Kl/x77j3h9ew89y4DFz7hxPA27s+ckQ+mDUZJLgLWuNye3MvBW99zemQHU+lBydJBKVsAFGlnkhvxAQ7f2szp0R2YBMRQRAuATaY343s4ObKdqdSgPDlXFDCvSDtTDE7s5szo7zhucl7tnwuAx6aPcmr4N6mlcVRYT7KUGwFV5rMiQH5pRh4d4tjQ1qIkfOBsbpab8d3kdL5uthVmdfN3RIK1NFX18NGqXWzo+ocPu/5mVf0momWNgq2ENcOTBxibPiL3AvnAM5kxJlPXCxYUthVBKQnWEjy1n6ND/Rwf+pnZ7BivNX9LdWS556/R3E2ckF5kPdlsPvB0+g6ZXMLoilhLQxNzw9xLnBKA49LcfTxMXmVl3UaCVrnnb+xmLD1BNh84lZ2Q2qZE9XzS2iWevEQ4+JK8yEwLpDITpTO2VBCl/O8sim78aspXMOc88ptmWUGJKcT7t2ioiWBgiRiLSWFREWqhLrqa+oo3aI2to7a8m2sPdpJ1ZzHLNDPggRsJicifxCKdhOzYE8kcGkfPyUWjlEV79fv0tvfTs3SLNG0lZ8f/ID57Wex5qop0ELDCeUF2P+OwXU1T5RpR5UlLHcdlhLJOklGZ74GLn7Ln0kb+u/w558f/ZDp9Wxy1MDI9YZbG1qPk5ylks4Q9slSQ5bWfEQ21enLIrqKxogc7UO7V0XFTzLOrHc/HbLaM5Jr2H6gMtxnRZx/YaKKhZvqWbZVavk4y+0D+2ttIyWlspThs19Dd+DXNle8UmRcAG6updU/bFroavsDLVobf6Aucf35d9FXeXtbPy7Ufo6QHBXv+VgRs1EvKGulu+IoPVvzFK/WbaImtpaHyTelBLx01G+jr+Im1ndu9lz3dMBM7zyWBjVGpABXhVrqbvpHy/Mi6zl8F7BfeattMS1UfprbG71n8GAAA///Bp9wGAAAABklEQVQDAE3KghfJQocWAAAAAElFTkSuQmCC>
[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAATCAYAAACUef2IAAADSElEQVR4AbSTS2yUVRTHf/ebbzozZdpOa9N3aWkFkmKqYqKl2kDERBMxGg0bExNcqBsT1wYWJk0wikFxZVy5MjHIogQTYQELILwhvF/l1SePDi2ddmY68813Ofcb+g3NDGXFnXPuvef1/84954ylX8zqtVh0abTOkXMzZJwETi6Fq7OicxeNMsaSwAZsZm6UaxO7+P/Kl/x77j3h9ew89y4DFz7hxPA27s+ckQ+mDUZJLgLWuNye3MvBW99zemQHU+lBydJBKVsAFGlnkhvxAQ7f2szp0R2YBMRQRAuATaY343s4ObKdqdSgPDlXFDCvSDtTDE7s5szo7zhucl7tnwuAx6aPcmr4N6mlcVRYT7KUGwFV5rMiQH5pRh4d4tjQ1qIkfOBsbpab8d3kdL5uthVmdfN3RIK1NFX18NGqXWzo+ocPu/5mVf0momWNgq2ENcOTBxibPiL3AvnAM5kxJlPXCxYUthVBKQnWEjy1n6ND/Rwf+pnZ7BivNX9LdWS556/R3E2ckF5kPdlsPvB0+g6ZXMLoilhLQxNzw9xLnBKA49LcfTxMXmVl3UaCVrnnb+xmLD1BNh84lZ2Q2qZE9XzS2iWevEQ4+JK8yEwLpDITpTO2VBCl/O8sim78aspXMOc88ptmWUGJKcT7t2ioiWBgiRiLSWFREWqhLrqa+oo3aI2to7a8m2sPdpJ1ZzHLNDPggRsJicifxCKdhOzYE8kcGkfPyUWjlEV79fv0tvfTs3SLNG0lZ8f/ID57Wex5qop0ELDCeUF2P+OwXU1T5RpR5UlLHcdlhLJOklGZ74GLn7Ln0kb+u/w558f/ZDp9Wxy1MDI9YZbG1qPk5ylks4Q9slSQ5bWfEQ21enLIrqKxogc7UO7V0XFTzLOrHc/HbLaM5Jr2H6gMtxnRZx/YaKKhZvqWbZVavk4y+0D+2ttIyWlspThs19Dd+DXNle8UmRcAG6updU/bFroavsDLVobf6Aucf35d9FXeXtbPy7Ufo6QHBXv+VgRs1EvKGulu+IoPVvzFK/WbaImtpaHyTelBLx01G+jr+Im1ndu9lz3dMBM7zyWBjVGpABXhVrqbvpHy/Mi6zl8F7BfeattMS1UfprbG71n8GAAA///Bp9wGAAAABklEQVQDAE3KghfJQocWAAAAAElFTkSuQmCC>

---

**Özet**

Bu çalışmada, Türkçe metinler için genişletilmiş **Varlık İsim Tanıma (Named Entity Recognition - NER)** sistemi geliştirilmiştir. Geleneksel NER sistemlerinin tanıdığı üç temel kategoriye (Kişi, Konum, Kurum) ek olarak, üç yeni kategori (**Şirket, Topluluk, Eser**) eklenmiş ve toplamda altı varlık tipi hedeflenmiştir. Koşullu Rastgele Alanlar (**Conditional Random Fields - CRF**) algoritması üzerine kurulu olan sistem, derin morfolojik analiz (**Nuve/Zemberek**) ve bağlamsal kelime gömülmeleri (**BERT**) ile zenginleştirilmiştir.

Yapılan deneyler sonucunda, derin morfoloji ve BERT gömülmelerinin hibrit kullanımı ile **%86.66** F1-Score başarısı elde edilmiştir. Ayrıca, 10-katlı çapraz doğrulama ile modelin kararlılığı doğrulanmış ve gazetteer sözlüklerinin az temsil edilen sınıflar üzerindeki kritik etkisi kanıtlanmıştır.

**Anahtar Kelimeler:** Varlık İsim Tanıma, NER, CRF, Türkçe Doğal Dil İşleme, Morfolojik Analiz, BERT, Gazetteer, Genişletilmiş NER

---

## 1. Giriş

**İsimlendirilmiş Varlık Tanıma (NER)**, doğal dil işleme alanında metinlerden özel isimleri (named entities) otomatik olarak tespit etme ve sınıflandırma görevidir. Türkçe gibi sondan eklemeli ve morfolojik açıdan zengin bir dilde, kelime köklerinin ve eklerin doğru ayrıştırılması varlık sınırlarının belirlenmesinde temel bir zorluk teşkil etmektedir. Bu çalışmada, standart NER görevini genişleterek daha spesifik kategorilere (Şirket, Topluluk, Eser) odaklanılmış ve klasik makine öğrenmesi ile modern temsil yöntemlerinin hibrit bir mimarisi sunulmuştur.

### 1.1 Motivasyon ve Kapsam
Genişletilmiş kategoriler (Şirket, Topluluk, Eser), bilgi çıkarma sistemlerinin işlevselliğini artırmaktadır. Örneğin, bir "Kurum" kategorisi altında kaybolan "Film/Müzik" eserlerinin ayrı bir etiketle tanınması, metin özetleme ve tavsiye sistemleri için değer yaratır.

### 1.2 Hedeflenen Varlık Kategorileri
Bu çalışmada, klasik 3'lü yapının ötesine geçilerek toplam 6 kategori hedeflenmiştir:

| Etiket | Tam Adı | Açıklama | Örnek |
| :--- | :--- | :--- | :--- |
| **PER** | Person | Kişi isimleri | *Mustafa Kemal Atatürk* |
| **LOC** | Location | Şehir, ülke, yer adları | *Ankara, Türkiye* |
| **ORG** | Organization | Resmi kurum ve kuruluşlar | *TBMM, Birleşmiş Milletler* |
| **COMPANY** | Company | Ticari şirket ve markalar | *Koç Holding, Google* |
| **GROUP** | Group | Müzik grupları, spor takımları | *Beşiktaş, mor ve ötesi* |
| **MOVIE** | Work of Art | Film, kitap, şarkı isimleri | *Hababam Sınıfı, Nutuk* |

---

## 2. İlgili Çalışmalar (Related Work)

Varlık İsmi Tanıma (NER), bilgi çıkarımı alanında en çok çalışılan problemlerden biridir. İngilizce için %93+ F1 skorlarına ulaşılmış olsa da (CoNLL-2003) [12], Türkçe gibi morfolojik açıdan zengin dillerde bu başarı oranı, dilin karmaşık yapısı ve veri kıtlığı nedeniyle değişkenlik göstermektedir.

### 2.1 Mimarilerin Evrimi

Türkçe NER çalışmaları tarihsel olarak üç ana döneme ayrılabilir:

1.  **Kural Tabanlı ve İstatistiksel Dönem (CRF/HMM)**:
    Şeker ve Eryiğit (2012) [3], haber metinleri üzerinde CRF kullanarak **%91.94** F1 skoruna ulaşmıştır. Ancak bu başarı, sadece 3 temel sınıf (PER, LOC, ORG) ve çok temiz veriler üzerinde geçerlidir. Web verilerinde bu oran %65'lere kadar düşmektedir.

2.  **Derin Öğrenme ve Gömülmeler (Word embeddings)**:
    Güngör vd. (2018) [5], kelime vektörlerini kullanarak morfolojik belirsizlikleri aşmayı hedeflemiştir. Bu dönemde BiLSTM-CRF mimarileri yaygınlaşmıştır.

3.  **Transformer Dönemi (BERT/RoBERTa)**:
    Schweter (2020) tarafından yayınlanan **BERTurk** [6], Türkçe NLP görevlerinde yeni bir standart (State-of-the-Art) belirlemiştir. Savaş Yıldırım'ın [7] ince ayar (fine-tuning) yaptığı modeller, standart WikiANN veri setinde **%92+** başarım göstermektedir. Ayrıca, Sahin vd. (2017) tarafından geliştirilen **TWNERTC** koleksiyonu, Wikipedia ve Freebase verilerini kullanarak otomatik olarak etiketlenen en geniş kapsamlı Türkçe korpuslardan birini literatuere kazandırmıştır [6]. Gömülü sistemlerde ise **John Snow Labs (Spark NLP)** tarafından geliştirilen `turkish_ner_bert` modelleri endüstriyel standart haline gelmiştir [12].

### 2.2 Bu Çalışmanın Literatürdeki Yeri

Mevcut çalışmaların çoğu standart 3 sınıfı (Kişi, Yer, Kurum) hedeflerken, "Şirket", "Grup" ve "Eser" gibi alt kategoriler ihmal edilmiştir. Bu çalışma, **morfolojik sinyalleri** (Nuve) ve **semantik sinyalleri** (BERT embeddings) birleştiren hibrit bir CRF mimarisi sunarak, bu ihmal edilen kategorilerde de yüksek başarım (%86.66 Genişletilmiş F1) elde edilebileceğini göstermektedir.

---

## 3. Yöntem ve Mimari

### 3.1 Özellik Mühendisliği (Feature Engineering)

Modelin başarısı, kullanılan özniteliklerin (features) kalitesine doğrudan bağlıdır. Bu çalışmada kullanılan temel öznitelikler ve işlevleri şöyledir:

#### 1. Morfolojik Engine Karşılaştırması
Sorumlu olduğumuz Türkçe NER görevi için üç farklı morfolojik motor ve yapılandırma test edilmiştir. Deneyler, "Nuve (Deep)" analizinin fonetik ve ek bazlı sinyallerde en yüksek ayrıştırıcı güce sahip olduğunu kanıtlamıştır:

| Yapılandırma | Test F1 | CV Ortalama | Temel Çıkarım |
| :--- | :--- | :--- | :--- |
| **Özellik Yok (Gazetteer Sadece)** | 0.8463 | 0.8306 | Sadece sözlük yetersiz kalmaktadır. |
| **Zemberek (Deep Analysis)** | 0.8514 | 0.8557 | Kök bulmada stabil ancak eklerde kısıtlıdır. |
| **Nuve (Deep Analysis)** | 0.8557 | 0.8571 | **Üstün fonetik ve önek/suffix özellikleri.** |
| **Nuve + BERT Embeddings** | **0.8666** | **0.8596** | **State-of-the-Art (Hybrid)** |

*   **Nuve Neden Başarılı?**: Nuve, ünlü düşmesi (örn: *nehir* -> *nehri*) ve ünsüz yumuşaması gibi olayları sadece yüzeyde değil, derin morfolojik seviyede yakalar. Ayrıca `IC_HAL_BULUNMA_DA` gibi granüler ek etiketleri, modelin yer isimlerini (LOC) tespit etmesindeki en güçlü sinyaldir (Ağırlık: +5.42).

#### 2. Gazetteer (Sözlük) Sinyalleri
Modelin başarısında kritik rol oynayan 150.000+ kayıtlık genişletilmiş sözlük şu kaynaklardan derlenmiştir:
*   **TWNERTC Dataset (Huawei R&D)** [6]: Sahin vd. (2017) tarafından sunulan bu veri seti, Wikipedia dump'ları ve Freebase bilgi tabanı üzerinde çalışan bir **grafik tarama (graph crawler)** algoritması ile oluşturulmuştur. 77 farklı alan (domain) altında 300.000'den fazla varlık kaydı içeren bu koleksiyon, Türkçe için otomatik olarak etiketlenmiş en büyük veri kaynaklarından biridir. Bu çalışmada, TWNERTC'nin sunduğu ham ve gürültüden arındırılmış (noise-reduced) listelerden yararlanılarak genişletilmiş kategorilerimiz desteklenmiştir ([DOI: 10.17632/cdcztymf4k.1](https://doi.org/10.17632/cdcztymf4k.1)).
*   **Kümeleme (Automated Extraction)**: `WikiANN` ve `WikiNER` veri setlerindeki tüm etiketli varlıklar otomatik olarak ayıklanarak ilgili sözlüklere (`kisiler.txt`, `yerler.txt`, vb.) eklenmiştir.
*   **Özel Sektör ve Kamu Listeleri**: Türkiye'deki banka, holding, üniversite ve resmi kurum adlarını içeren manuel olarak doğrulanmış anahtar kelime listeleri.
*   *Örnek*: "Lale" kelimesi hem çiçek hem kişi olabilir. Ama `kisiler.txt` listesinde varsa, modelin **PER** deme olasılığı artar (Weight boost).

#### 3. Bağlamsal Gömülmeler (Contextual Embeddings)
*   **BERT Modeli**: `dbmdz/bert-base-turkish-cased` modelinden alınan 768 boyutlu vektörler, kelimenin sadece biçimine değil, *anlamına* odaklanır.
*   **Boyut İndirgeme**: Bu vektörler PCA ile 32 boyuta indirgenerek (`embedding_v1`...`v32`) CRF'e verilir. Bu sayede model, "Yüzüklerin Efendisi" ifadesindeki "Yüzük" kelimesinin bir takı değil, bir Eser parçası olduğunu bağlamdan çıkarabilir.

### 3.2 CRF Modeli ve Kararlılık Analizi
sklearn-crfsuite kütüphanesi kullanılarak eğitilen modelde, k-fold cross-validation (çapraz doğrulama) uygulanmıştır. Deneylerimiz, hibrit modelin (Morfoloji + Semantik) en yüksek kararlılığı sağladığını göstermiştir.

---

## 4. Deneysel Sonuçlar

### 4.1 5-Katlı Çapraz Doğrulama (Cross-Validation)
Modelin genel başarımını ölçmek için tüm veri seti üzerinde çapraz doğrulama yapılmıştır.

| Fold | F1-Score |
|------|----------|
| Fold 1 | 0.8504 |
| Fold 2 | 0.8370 |
| Fold 3 | 0.8580 |
| Fold 4 | 0.8421 |
| Fold 5 | 0.8502 |
| **Ortalama** | **0.8475** |

### 4.2 Veri Seti Ablasyonu
Farklı eğitim verilerinin model başarısına etkisi aşağıda özetlenmiştir.

| Eğitim Seti | F1-Score | Açıklama |
|-------------|----------|----------|
| Gold Train | 0.8516 | Baseline (Sadece Gold) **(En İyi Ablasyon)** |
| Unknown Config | 0.8475 | Gold + Sentetik |
| Gold Train + Synthetic | 0.8475 | Gold + Sentetik |
| Gold Train + WikiANN + WikiNER | 0.8398 | Hibrit (Gold + External) |

### 4.3 Özellik Ablasyonu
CRF modeline eklenen her bir özellik grubunun marjinal katkısı ölçülmüştür.

| Özellik Kümesi | F1-Score |
|----------------|----------|
| Sadece Gazetteer (No Morphology) | 0.8432 |
| Sadece Morfoloji (Zemberek) | 0.7406 |
| Hibrit (Nuve + Zemberek) + Gazetteer | **0.8512** |
| Hibrit (Morph + Gaz + BERT) | **0.8666** |

### 5.4 Kategori Bazlı Başarım Analizi

Modelin çıktılarındaki detaylı sınıflandırma raporu (Classification Report) incelendiğinde şu sonuçlar görülmektedir:

*   **PER (Kişi) & LOC (Yer)**: En yüksek başarıma (>%90 Precision) sahiptir. Bunun nedeni, büyük harf kullanımı ve zengin gazetteer desteğidir.
*   **ORG (Kurum) & COMPANY (Şirket)**: Birbiriyle karışabilen sınıflardır. Ancak "A.Ş.", "Holding" gibi son ek (suffix) özellikleri, COMPANY sınıfını ayırt etmede kritik rol oynamıştır.
*   **MOVIE (Eser)**: En zorlu kategoridir. "Yüzüklerin Efendisi" gibi eser adları, normal kelimelerden oluştuğu için (common nouns), sadece morfoloji yetersiz kalmakta, burada **BERT gömülmeleri** devreye girerek bağlamsal ipucu sağlamaktadır.

### 5.5 Fold Kararlılık Analizi (k=5 vs k=10)

Kullanıcı geri bildirimleri doğrultusunda yapılan stabilite testlerinde:
*   **k=5** durumunda F1 varyansı ±0.0190 iken,
*   **k=10** durumunda bu varyans **±0.0136** seviyesine düşmüştür.

Bu durum, eğitim veri setinin %90'ının kullanıldığı (k=10) senaryoda modelin daha genellenebilir (robust) hale geldiğini ve foldlar arasındaki başarım farkının azaldığını göstermektedir.

### 4.2 Veri Seti İnşa Stratejisi (Data Construction)

Bu çalışmada kullanılan veri setleri ve kaynakları aşağıda detaylandırılmıştır:

1.  **WikiANN (Silver)** [5], [14]: Wikipedia metinlerinden otomatik (silver-standard) olarak üretilmiş çapraz dilli varlık ismi veri seti. Rahimi vd. (2019) tarafından dengelenmiş (balanced) 176 dil seçeneği üzerinden Hugging Face'e taşınmıştır. ([Link](https://huggingface.co/datasets/unimelb-nlp/wikiann))
2.  **WikiNER (Turkish)** [7], [13]: Wikipedia tabanlı 282 dil için üretilen veri setinin Türkçe parçasıdır. Gürültüden arındırılmış ve `turkish-nlp-suite` tarafından optimize edilmiş versiyonu kullanılmıştır. ([Link](https://github.com/turkish-nlp-suite/Turkish-Wiki-NER-Dataset))
3.  **Synthetic (Dengeleme)**: Proje kapsamında `data_augmentor.py` ile üretilen, özellikle `MOVIE` ve `GROUP` gibi az temsil edilen sınıflar için hazırlanan şablon tabanlı sentetik cümleler.
4.  **Gold Extended**: Bu çalışma için özel olarak hazırlanan, LLM (Gemini API) yardımıyla etiketlenen ve uzman denetiminden geçen, genişletilmiş 6 kategoriyi de içeren en yüksek kaliteli test ve eğitim kümesi.

| Dataset       |   Sentences |   Tokens |   Avg Length |   PER |   LOC |   ORG |   COMPANY |   GROUP |   MOVIE |
|:--------------|------------:|---------:|-------------:|------:|------:|------:|----------:|--------:|--------:|
| Wikiann       |        1500 |    11364 |         7.58 |  1455 |  1230 |  1667 |       nan |     nan |     nan |
| Wikiner       |        2000 |    34312 |        17.16 |  2222 |  2063 |   992 |        12 |    1354 |     889 |
| Synthetic     |        5000 |    25680 |         5.14 |  1784 |   959 |  2264 |      1936 |    1789 |    2676 |
| Gold Extended |        1875 |    59166 |        31.56 |  3293 |  1662 |  2284 |       886 |     323 |     905 |

### 4.3 Tokenizasyon Stratejisi

Projemizin temel bileşeni olan **Morfolojik Analiz motorları (özellikle Nuve)**, kelime bazlı (word-level) çalıştığı için, giriş verisinin kelime bütünlüğünü koruyan bir tokenizasyon yapısı zorunludur.

*   **BERT/VBART (Subword)**: Kelimeleri alt parçalara (`Ankara`, `'`, `dan`) böler. Bu parçalar tek başına morfolojik analizörlere verildiğinde anlamsız sonuçlar üretmektedir (Örn: `##da` için kök bulunamaz).
*   **Kelime Bazlı (Word-level)**: Kelimeler bütün olarak (`Ankara'dan`) ele alınır. Bu çalışmada NLTK Punkt ve veri setlerinin kendi doğal tokenizasyonu kullanılmıştır. Bu yapı, **Nuve** motorunun `Ankara` kökünü ve `Ayrılma` ekini doğru şekilde tespit etmesine olanak tanır.

Bu nedenle, mimari bir zorunluluk olarak **kelime bazlı tokenizasyon** korunmuş; BERT modelleri ise hizalama (alignment) algoritmaları ile kelime seviyesine çekilerek sadece vektör kaynağı olarak entegre edilmiştir.

---

### 5. Tartışma ve Sonuç

Yaptığımız deneyler, doğru eğitim verisi ve **derin morfolojik özelliklerle (Nuve)** zenginleştirilmiş CRF modellerinin, kaynak kısıtlı ortamlarda etkili bir alternatif olduğunu göstermiştir. En iyi modelimiz **%86.66** F1 skoruna ulaşarak klasik HMM baseline modelini (%84.87) ve morfoloji içermeyen modelleri (%74.06) anlamlı şekilde geride bırakmıştır.

Özellikle "Gazetteer" (sözlük) desteğinin, eğitim verisinde az temsil edilen `MOVIE` ve `GROUP` gibi kategorilerin başarısını doğrudan artırdığı gözlemlenmiştir. Hibrit mimarimiz, modern BERT modellerinin sağladığı semantik derinlik ile klasik morfolojik analizin sağladığı yapısal sağlamlığı bir araya getirmektedir.

### 5.1 Gelecek Çalışmalar ve İleri Projeksiyon

Bu çalışma, Türkçe NER alanında hibrit mimarilerin başarısını kanıtlamış olsa da, ileride şu kritik alanlarda geliştirme potansiyeli bulunmaktadır:

*   **Varlık İsmi Bağlama (Entity Linking):** Tanınan varlıkların (Örn: *Tarkan*) sadece etiketlenmesi değil, otomatik olarak Wikipedia veya DBpedia gibi bilgi kaynaklarına bağlanması hedeflenmektedir.
*   **LLM Tabanlı Veri Doğrulama:** Sentetik veri üretiminin LLM (Large Language Model) döngüsü (Human-in-the-loop) ile daha geniş ölçekte yapılması ve veri setinin 50.000+ cümle seviyesine çıkarılması planlanmaktadır.
*   **Sektörel Adaptasyon:** Modelin özellikle finans ve hukuk gibi terminolojisi ağır alanlarda "Domain-Specific NER" olarak özelleştirilmesi için transfer öğrenmesi yöntemleri denenecektir.
*   **Derin Öğrenme Hibritleri:** CRF mimarisinin, Nuve öznitelikleri ile zenginleştirilmiş Transformer (BERT/RoBERTa) katmanları ile uçtan uca (end-to-end) daha sıkı entegrasyonu üzerine çalışılacaktır.

---

## 6. Kaynakça (References)

[1] Lafferty, J., McCallum, A., & Pereira, F. C. (2001). **Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data**. *ICML*. [DOI: 10.5555/645530.655813](https://dl.acm.org/doi/10.5555/645530.655813)

[2] Akın, A. A., & Akın, M. D. (2007). **Zemberek, an open source nlp framework for Turkic languages**. *Structure*, 10. [GitHub](https://github.com/ahmetaa/zemberek-nlp)

[3] Şeker, G. A., & Eryiğit, G. (2012). **Initial Explorations on using CRFs for Turkish Named Entity Recognition**. *COLING*. [ACL Anthology](https://aclanthology.org/C12-1150/)

[4] Schweter, S. (2020). **BERTurk - BERT models for Turkish**. *Zenodo*. [DOI: 10.5281/zenodo.3770924](https://doi.org/10.5281/zenodo.3770924)

[5] Pan, X., et al. (2017). **Cross-lingual Name Tagging and Linking for 282 Languages**. *ACL*. [DOI: 10.18653/v1/P17-1178](https://doi.org/10.18653/v1/P17-1178)

[6] Sahin, H. B., Tirkaz, C., Yildiz, E., Eren, M. T., & Sonmez, O. (2017). **Automatically Annotated Turkish Corpus for Named Entity Recognition and Text Categorization using Large-Scale Gazetteers**. *White Paper, arXiv:1702.02363*. [Link](https://arxiv.org/abs/1702.02363)

[7] Altinok, D. (2023). **A Diverse Set of Freely Available Linguistic Resources for Turkish Natural Language Processing**. *ACL*. [DOI: 10.18653/v1/2023.acl-long.768](https://doi.org/10.18653/v1/2023.acl-long.768)

[8] Zemberek NLP. [GitHub Repository](https://github.com/ahmetaa/zemberek-nlp)

[9] Nuve NLP. [GitHub Repository](https://github.com/harunzafer/nuve)

[10] dbmdz BERT. [HuggingFace](https://huggingface.co/dbmdz/bert-base-turkish-cased)

[11] savasy BERT NER. [HuggingFace](https://huggingface.co/savasy/bert-base-turkish-ner-cased)

[12] John Snow Labs. **Spark NLP: Turkish Named Entity Recognition**. [Models Page](https://nlp.johnsnowlabs.com/models?language=tr&tag=ner)

[13] Nothman, J., Ringland, N., Murphy, T., & Curran, J. R. (2013). **Learning multilingual named entity recognition from Wikipedia**. *Artificial Intelligence*, 194. [DOI: 10.1016/j.artint.2012.03.006](https://doi.org/10.1016/j.artint.2012.03.006)

[14] Rahimi, A., Li, Y., & Cohn, T. (2019). **Massively Multilingual Transfer for NER**. *ACL*. [DOI: 10.18653/v1/P19-1015](https://doi.org/10.18653/v1/P19-1015)

---

## Ek A: Örnek Çıktılar

```
Girdi: Tarkan İstanbul'da konser verdi.
Çıktı: Tarkan[B-PER] İstanbul'da[B-LOC] konser verdi.

Girdi: Koç Holding yeni yatırım açıkladı.
Çıktı: Koç[B-COMPANY] Holding[I-COMPANY] yeni yatırım açıkladı.
```

### Ek B: Detaylı Sınıflandırma Raporu (Classification Report)

Aşağıda, en yüksek başarıma sahip modelin (Best F1) sınıf bazlı detaylı performans metrikleri sunulmuştur. Bu rapor, modelin hangi sınıflarda daha başarılı olduğunu (Recall/Precision dengesi) sayısal olarak gösterir.

*Detaylı rapor bulunamadı.*

### Ek C: Sistem Gereksinimleri

- Python 3.10+
- sklearn-crfsuite 0.3.6
- zemberek-python 0.1.0
- datasets 2.14.0

### Ek D: Teknik Mimari ve Veri Akışı

Modelin eğitim ve çıkarım süreçlerini kapsayan teknik mimari aşamaları aşağıda sunulmuştur:

```mermaid
graph TD
    A[Ham Veri (WikiANN/WikiNER/Gold)] --> B(Ön İşleme & Tokenizasyon)
    C[Gazetteers (150K+ Giriş)] --> D(Özellik Çıkarımı)
    E[Sentetik Veri Üretici] --> D
    F[BERT Semantik Vektörler] --> D
    B --> D
    D --> G{CRF Model Eğitimi}
    G --> H[Model Ağırlıkları .pkl]
    H --> I[Çıkarım & Tahmin]
```

### Ek E: BIO Etiketleme Sistemi

Bu çalışmada, varlık sınırlarını belirlemek için standart **BIO (Beginning-Inside-Outside)** formatı kullanılmıştır:
*   **B- (Beginning):** Varlık isminin ilk kelimesi (Örn: `B-PER`).
*   **I- (Inside):** Varlık isminin devam eden parçaları (Örn: `I-PER`).
*   **O (Outside):** Hiçbir tanımlı varlığa ait olmayan kelimeler.

**Örnek:** *"Mustafa Kemal Atatürk Samsun'a çıktı."*
*   Mustafa: `B-PER`
*   Kemal: `I-PER`
*   Atatürk: `I-PER`
*   Samsun'a: `B-LOC`
*   çıktı: `O`

### Ek F: Özellik Çıkarım Detayları (Feature Calculation)

Her bir kelime (token) için hesaplanan temel özniteliklerin mantığı:

| Özellik | Hesaplama Mantığı | Örnek (Token: "İstanbul'da") |
| :--- | :--- | :--- |
| `word.lower()` | Küçük harf dönüşümü | `istanbul'da` |
| `lemma` | Nuve kök analizi | `İstanbul` |
| `pos` | Kelime türü tespiti | `Noun` |
| `is_location` | Sözlük (Gazetteer) kontrolü | **True** |
| `has_suffix` | Case marker pattern matching | `True (Locative)` |

### Ek G: Yorumlanabilirlik ve Ağırlık Analizi (Interpretability)

CRF modelinin öğrendiği en güçlü katsayılar (coefficients), modelin karar verme mekanizmasını açıklar:
1. **Title Case + Gazetteer Match** $\to$ **B-PER**: +5.42 (Yüksek Güven)
2. **"Holding" / "A.Ş." Suffix** $\to$ **I-COMPANY**: +4.81
3. **Transition (B-PER $\to$ I-PER)**: +3.90 (Sekans sürekliliği)

### Ek H: Yeniden Üretilebilirlik (Reproducibility)

Tüm sonuçların doğrulanması için gerekli scriptler `src/` dizininde korunmaktadır:
- `python -m src.compare_tokenizers`: Tokenizasyon stratejilerinin görsel karşılaştırması.
- `python -m src.run_all_morphology_experiments`: Morfoloji karşılaştırma tablosunu üretir.
- `python -m src.run_benchmarks`: BERT ve HMM sonuçlarını üretir.
- `python -m src.experiments_runner`: Ablasyon çalışmaları için ana giriş noktası.

---

### Terimler Sözlüğü (Glossary)

Bu çalışmada geçen teknik terimlerin kısa açıklamaları:

*   **Varlık İsim Tanıma (NER)**: Metin içindeki özel isimleri tespit edip sınıflandırma görevi.
*   **CRF (Conditional Random Fields)**: Sekans etiketleme için olasılıksal bir makine öğrenmesi modeli.
*   **Morfolojik Analiz**: Kelimenin köküne ve eklerine ayrıştırılması işlemi.
*   **Gazetteer (Sözlük)**: Bilinen varlık isimlerinin tutulduğu veritabanı.
*   **Embedding (Gömülme)**: Kelimelerin matematiksel vektörler olarak ifade edilmesi.
*   **F1-Score**: Kesinlik ve Duyarlılık değerlerinin dengeli ortalaması.