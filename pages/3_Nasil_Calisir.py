import streamlit as st
import pandas as pd
from src.preprocessing import Preprocessor
from src.features import FeatureExtractor

st.set_page_config(page_title="Nasıl Çalışır?", layout="wide")

st.title("Nasıl Çalışır?")
st.header("Adım Adım NLP İş Akışı Simülasyonu")
st.markdown("Bu simülasyon, ham bir metnin NER etiketlerine dönüşürken geçtiği adımları gösterir.")

sim_text = st.text_input("Simülasyon için örnek cümle giriniz:", "Tarkan İstanbul'da harika bir konser verdi.")

# 1. Tokenization
st.subheader("Adım 1: Tokenizasyon (Parçalama)")
import nltk
from nltk.tokenize import word_tokenize
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except:
    nltk.download('punkt')
    nltk.download('punkt_tab')
tokens = word_tokenize(sim_text)
st.write("**Tokenler:**")
st.code(str(tokens))
st.info("Tokenizasyon, cümleyi anlamlı en küçük birimlerine ayırır. 'İstanbul'da' ifadesinin tek bir parça olarak kalmasına dikkat edin.")

# 2. Morphological Analysis
st.subheader("Adım 2: Morfolojik Analiz (Nuve/Zemberek)")
engine = st.radio("Morfoloji Motoru Seçiniz", ["nuve", "zemberek"], horizontal=True)
prep = Preprocessor(engine=engine)
processed = prep.process_sentence(tokens)

morph_data = []
for p in processed:
    suffixes = []
    # Morph can be a list or direct depending on engine, handle safely
    morph_info = p.get('morph', [])
    if isinstance(morph_info, list):
        suffixes = [m.get('Id', '') for m in morph_info if m.get('Type') != 'Root']

    morph_data.append({
        "Token": p.get('word', ''),
        "Kök (Lemma)": p.get('lemma', ''),
        "POS": p.get('pos', 'UNK'),
        "Ekler": ", ".join(suffixes) if suffixes else "-"
    })
st.table(pd.DataFrame(morph_data))
st.info("Morfoloji, kelimenin kökünü (lemma) ve kelime türünü (POS) belirler.")

# 3. Feature Extraction
st.subheader("Adım 3: Öznitelik Çıkarımı")
extractor = FeatureExtractor(use_morphology=True, use_gazetteers=True)
feats = extractor.sent2features(processed)

selected_token_idx = st.selectbox("Özniteliklerini İncelemek İstediğiniz Token'ı Seçin", range(len(tokens)), format_func=lambda i: tokens[i])
st.write(f"**'{tokens[selected_token_idx]}' için Öznitelikler:**")
st.json(feats[selected_token_idx])
st.info("Öznitelikler, CRF modelinin tahmin yaparken kullandığı ipuçlarıdır.")

# 4. CRF Scoring (Simplified)
st.subheader("Adım 4: CRF Dizi Etiketleme")
st.markdown("""
CRF, öznitelikler ve etiketler arasındaki 'uyumluluğu' iki tür ağırlıkla hesaplar:
1. **Durum Ağırlıkları**: Bir özelliğin (örn. `word.istitle()`) bir etiketi (örn. `B-PER`) ne kadar desteklediği.
2. **Geçiş Ağırlıkları**: Bir etiketin (örn. `I-PER`) başka bir etiket (örn. `B-PER`) ardından gelme olasılığı.
""")

st.graphviz_chart("""
digraph {
    rankdir=LR;
    T1 [label="Tarkan"]
    L1 [label="B-PER", shape=rectangle, style=filled, color=lightblue]
    L2 [label="I-PER", shape=rectangle, style=filled, color=lightblue]
    T2 [label="İstanbul'da"]
    L3 [label="B-LOC", shape=rectangle, style=filled, color=lightgreen]

    T1 -> L1 [label="Durum\nÖzellik:Başlık"]
    L1 -> L2 [label="Geçiş\nOlasılık:Yüksek"]
    T2 -> L3 [label="Durum\nÖzellik:Gazetteer"]
}
""")
st.success("Viterbi algoritması, olası tüm etiket dizileri arasından 'en yüksek puanlı' yolu bulur.")
