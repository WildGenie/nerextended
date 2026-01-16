import streamlit as st
import pandas as pd
import json
import os
import glob
import platform
from src.models.crf_model import CRFModel
from src.features import FeatureExtractor
from src.preprocessing import Preprocessor

st.set_page_config(page_title="Türkçe NER Demo", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark mode adaptive classes */
    :root {
        --token-bg: var(--secondary-background-color, #f0f2f6);
        --token-text: var(--text-color, #31333F);
    }

    .stApp {
        /* Remove hardcoded white background */
    }
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .result-token {
        display: inline-block;
        margin: 3px;
        padding: 6px 12px;
        border-radius: 8px;
        font-family: 'Source Code Pro', monospace;
        font-size: 1.05em;
        line-height: 1.6;
        color: var(--token-text);
        background-color: var(--token-bg);
        border: 1px solid rgba(128, 128, 128, 0.2);
        transition: all 0.2s ease;
    }
    .result-token:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .result-token.entity {
         color: #000; /* Entities keep high contrast black text for visibility on colors */
         font-weight: 600;
         border: none;
    }
    .entity-label {
        font-size: 0.7em;
        font-weight: 800;
        text-transform: uppercase;
        margin-left: 8px;
        padding: 2px 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)

# --- HARDWARE & ENV DETECTION ---
IS_ARM64 = platform.machine() == "arm64"
IS_HF = "SPACE_ID" in os.environ

if IS_HF:
    st.info("🚀 Hugging Face Spaces üzerinde çalışıyor. Modeller ilk seferde indirilebilir.")

# --- SPARK NLP SETUP (Optional) ---
HAS_SPARK = False
try:
    import sparknlp
    from sparknlp.base import DocumentAssembler, Pipeline, LightPipeline
    from sparknlp.annotator import Tokenizer, SentenceDetector, BertEmbeddings, WordEmbeddingsModel, NerDLModel, NerConverter
    HAS_SPARK = True
except ImportError:
    pass

# --- PYSPARK COMPAT PATCH ---
try:
    from pyspark.sql.utils import get_column_class
except ImportError:
    pass

@st.cache_resource
def get_spark_session():
    if not HAS_SPARK: return None
    try:
        return sparknlp.start(apple_silicon=IS_ARM64)
    except Exception as e:
        st.error(f"Spark başlatılamadı: {e}")
        return None

# --- UI HEADER ---
st.markdown('<div class="main-header"><h1>🇹🇷 Genişletilmiş Türkçe NER Demo</h1><p>Geliştirmiş olduğumuz hibrit CRF modeli ile Türkçe metinlerdeki biyografik ve kurumsal verileri analiz edin.</p></div>', unsafe_allow_html=True)

# --- MODEL DEFINITIONS ---
internal_pkl_models = {
    "🚀 Bizim En İyi Model (Full + BERT)": {
        "path": "models/crf_gold_best.pkl",
        "config": {"use_gazetteers": True, "use_morphology": True, "use_embeddings": True}
    },
    "⚖️ Standart Model (Gaz + Morf)": {
        "path": "models/crf_gold_no_emb.pkl",
        "config": {"use_gazetteers": True, "use_morphology": True, "use_embeddings": False}
    },
    "📉 Temel Model (Sadece Sözlük)": {
        "path": "models/crf_gold_gaz_only.pkl",
        "config": {"use_gazetteers": True, "use_morphology": False, "use_embeddings": False}
    }
}

external_models = ["External: savasy/bert-base-turkish-ner-cased"]
if HAS_SPARK:
    # Adding Spark NLP models as external options
    external_models = ["External: Spark NLP (BERT)", "External: Spark NLP (GloVe)"] + external_models

all_model_names = list(internal_pkl_models.keys()) + external_models

col_sel, col_compare = st.columns([2, 1])
with col_sel:
    model_id = st.selectbox("Kullanılacak Model:", all_model_names, index=0)
with col_compare:
    st.write("") # Padding for alignment
    st.write("")
    compare_mode = st.toggle("⚔️ Benchmark Modu", help="Diğer modellerle yan yana kıyasla")

# --- SIDEBAR INFO ---
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/database.png", width=80)
    st.header("📊 Veri Seti Detayları")
    st.markdown("""
    Modelimiz hibrit bir veri seti havuzu ile eğitilmiştir:

    *   **WikiANN & WikiNER:** Wikipedia kaynaklı cümleler. ([HF Link](https://huggingface.co/datasets/unimelb-nlp/wikiann))
    *   **TWNERTC (Huawei R&D):** 300.000+ Varlık içeren grafik tarama tabanlı sözlük. ([arXiv](https://arxiv.org/abs/1702.02363))
    *   **Sentetik Veri:** Şablon tabanlı üretilen 5,000 cümle.
    *   **Gold Standard:** LLM tarafından etiketlenen yüksek kaliteli 1,875 cümle.

    | Kaynak | Cümle |
    | :--- | :--- |
    | WikiANN | 1,500 |
    | WikiNER | 2,000 |
    | Synthetic | 5,000 |
    | Gold | 1,875 |
    | **Toplam** | **10,375** |

    **Sözlük Boyutu:**
    27,500+ Varlık (Gazetteer)
    """)
    st.markdown("---")
    st.info("💡 **İpucu:** Sol taraftan farklı modelleri seçerek performans farklarını gözlemleyebilirsiniz.")

examples = {
    "👤 Bill Gates (Biyografi)": "William Henry Gates III (28 Ekim 1955 doğumlu) Amerikalı bir iş insanı, yazılım geliştiricisi, yatırımcı ve hayırseverdir. En çok Microsoft Corporation'ın kurucu ortağı olarak tanınır.",
    "🏛️ Cumhuriyet Tarihi": "Mustafa Kemal Atatürk, 1923 yılında Türkiye Cumhuriyeti'ni kurdu. Ankara yeni devletin başkenti olarak belirlendi.",
    "🏢 Facebook (Şirket Tarihçesi)": "Facebook, 4 Şubat 2004'te TheFacebook olarak başlatılan bir sosyal ağ hizmetidir. Mark Zuckerberg tarafından kurulmuştur.",
    "🧠 Alan Turing (Bilim Tarihi)": "1950'de, Alan Turing 'Computing Machinery and Intelligence' başlıklı bir makale yayımlamış ve günümüzde Turing testi olarak bilinen zekâ kriterini önermiştir.",
    "🏆 Titanik & Matrix (Film)": "Titanik ve Matrix filmleri çocukluğumun en unutulmaz yapımlarıydı. James Cameron ve Wachowski kardeşler harika iş çıkardı.",
    "✈️ Türk Hava Yolları": "Türk Hava Yolları, Avrupa'nın en iyi havayolu şirketlerinden biri seçildi. İstanbul Havalimanı bu başarının merkezinde yer alıyor.",
    "🏆 Fenerbahçe (Spor Kulübü)": "Fenerbahçe, bu sezon şampiyonluk yarışında iddialı.",
    "✍️ Kendi Metnim": ""
}

selected_example_key = st.selectbox("Örnek Metin Seçiniz:", list(examples.keys()), index=0)
default_text = examples[selected_example_key] if selected_example_key != "✍️ Kendi Metnim" else "Mustafa Kemal Atatürk 1881 yılında Selanik'te doğdu."
user_text = st.text_area("Analiz Edilecek Türkçe Metni Giriniz:", value=default_text, height=150)

# --- PIPELINE LOADING ---
@st.cache_resource
def get_spark_pipeline(model_name):
    spark = get_spark_session()
    if not spark: return None

    documentAssembler = DocumentAssembler().setInputCol("text").setOutputCol("document")
    sentenceDetector = SentenceDetector().setInputCols(["document"]).setOutputCol("sentence")
    tokenizer = Tokenizer().setInputCols(["sentence"]).setOutputCol("token")

    if model_name == 'turkish_ner_840B_300':
        embeddings = WordEmbeddingsModel.pretrained('glove_840B_300', "xx").setInputCols(["sentence", 'token']).setOutputCol("embeddings").setCaseSensitive(True)
    else:
        embeddings = BertEmbeddings.pretrained('bert_multi_cased', 'xx').setInputCols(["sentence", "token"]).setOutputCol("embeddings")

    public_ner = NerDLModel.pretrained(model_name, 'tr').setInputCols(["sentence", "token", "embeddings"]).setOutputCol("ner")
    ner_converter = NerConverter().setInputCols(["sentence", "token", "ner"]).setOutputCol("ner_chunk")

    nlp_pipeline = Pipeline(stages=[documentAssembler, sentenceDetector, tokenizer, embeddings, public_ner, ner_converter])

    empty_df = spark.createDataFrame([['']]).toDF('text')
    pipeline_model = nlp_pipeline.fit(empty_df)
    return LightPipeline(pipeline_model)

@st.cache_resource
def load_internal_model(m_id):
    if m_id not in internal_pkl_models: return None, "Model tanımsız."
    m_info = internal_pkl_models[m_id]
    if not os.path.exists(m_info["path"]):
        return None, f"Hata: {m_info['path']} bulunamadı."

    config = m_info["config"]
    extractor = FeatureExtractor(
        use_gazetteers=True,
        use_morphology=config.get("use_morphology", True),
        use_embeddings=config.get("use_embeddings", False),
        embedding_model="dbmdz/bert-base-turkish-cased"
    )
    # Use Nuve as requested (requires .NET SDK in Docker)
    preprocessor = Preprocessor(engine="nuve")
    model = CRFModel.load(m_info["path"])
    return (extractor, preprocessor, model), None

# --- VISUALIZATION ---
def visualize_result(tokens, tags):
    colors = {
        "PER": "#a4c2f4", "LOC": "#ffb6b6", "ORG": "#b6d7a8", "ORGANIZATION": "#b6d7a8",
        "COMPANY": "#ffe599", "GROUP": "#d5a6bd", "MOVIE": "#d9d2e9",
        "DATE": "#e0e0e0", "MISC": "#eeeeee", "MONEY": "#cfe2f3"
    }

    html = '<div style="line-height: 2.5;">'
    i = 0
    while i < len(tokens):
        token = tokens[i]
        tag = tags[i]
        if tag.startswith("B-"):
            etype = tag[2:]
            bg = colors.get(etype, "#e0e0e0")

            chunk = [token]
            j = i + 1
            while j < len(tokens) and tags[j] == f"I-{etype}":
                chunk.append(tokens[j])
                j += 1

            text_chunk = " ".join(chunk)
            html += f'<span class="result-token entity" style="background-color: {bg};">{text_chunk}<span class="entity-label">{etype}</span></span>'
            i = j
        else:
            html += f'<span class="result-token">{token}</span>'
            i += 1
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- RUN LOGIC ---
if st.button("Analiz Et 🚀", type="primary"):
    import nltk
    try: nltk.data.find('tokenizers/punkt')
    except: nltk.download('punkt')
    from nltk.tokenize import word_tokenize

    tokens = word_tokenize(user_text)

    with st.spinner("Analiz ediliyor..."):
        try:
            # 1. MAIN RESULT
            st.subheader(f"✅ Sonuç ({model_id})")

            # --- PREDICT ---
            final_tags = ["O"] * len(tokens)

            if model_id in internal_pkl_models:
                pipe_data, err = load_internal_model(model_id)
                if err: st.error(err)
                else:
                    ext, prep, model = pipe_data
                    processed = prep.process_sentence(tokens)
                    X = [ext.sent2features(processed)]
                    final_tags = model.predict(X)[0]

            elif "Spark NLP" in model_id:
                m_key = 'turkish_ner_840B_300' if "GloVe" in model_id else 'turkish_ner_bert'
                pipe = get_spark_pipeline(m_key)
                if pipe:
                    res = pipe.fullAnnotate(user_text)[0]
                    chunks = res['ner_chunk']
                    curr = 0
                    for i, t in enumerate(tokens):
                        s = user_text.find(t, curr)
                        if s == -1: continue
                        e = s + len(t)
                        curr = e
                        for ch in chunks:
                            if not (e <= ch.begin or s > ch.end):
                                l = ch.metadata['entity']
                                final_tags[i] = f"B-{l}" if s >= ch.begin and s < ch.begin+2 else f"I-{l}"
                                break

            elif model_id.startswith("External: "):
                from transformers import pipeline
                m_name = model_id.replace("External: ", "")
                hf_pipe = pipeline("ner", model=m_name, tokenizer=m_name, aggregation_strategy="simple")
                res = hf_pipe(user_text)
                curr = 0
                for i, t in enumerate(tokens):
                    s = user_text.find(t, curr)
                    if s == -1: continue
                    e = s + len(t)
                    curr = e
                    for r in res:
                        if not (e <= r['start'] or s >= r['end']):
                            final_tags[i] = f"B-{r['entity_group']}" if s >= r['start'] and s < r['start']+2 else f"I-{r['entity_group']}"
                            break

            visualize_result(tokens, final_tags)

            # 2. COMPARISON MODE
            if compare_mode:
                st.markdown("---")
                st.markdown("### ⚔️ Rakip Modeller")

                rival_list = []
                if "En İyi Model" not in model_id: rival_list.append(("Bizim En İyi Model", "🚀 Bizim En İyi Model (Full + BERT)"))
                rival_list.append(("HF (savasy/bert)", "External: savasy/bert-base-turkish-ner-cased"))
                if HAS_SPARK: rival_list.append(("Spark NLP (BERT)", "External: Spark NLP (BERT)"))

                cols = st.columns(len(rival_list))
                for idx, (r_name, r_id) in enumerate(rival_list):
                    with cols[idx]:
                        st.write(f"**{r_name}**")
                        r_tags = ["O"] * len(tokens)

                        try:
                            if r_id in internal_pkl_models:
                                p_d, _ = load_internal_model(r_id)
                                if p_d:
                                    ext_r, prep_r, model_r = p_d
                                    X_r = [ext_r.sent2features(prep_r.process_sentence(tokens))]
                                    r_tags = model_r.predict(X_r)[0]

                            elif "Spark NLP" in r_id:
                                m_k = 'turkish_ner_840B_300' if "GloVe" in r_id else 'turkish_ner_bert'
                                p = get_spark_pipeline(m_k)
                                if p:
                                    res_s = p.fullAnnotate(user_text)[0]
                                    curr_s = 0
                                    for i, t in enumerate(tokens):
                                        st_ind = user_text.find(t, curr_s)
                                        if st_ind == -1: continue
                                        en_ind = st_ind + len(t)
                                        curr_s = en_ind
                                        for ch in res_s['ner_chunk']:
                                            if not (en_ind <= ch.begin or st_ind > ch.end):
                                                l_r = ch.metadata['entity']
                                                r_tags[i] = f"B-{l_r}" if st_ind >= ch.begin and st_ind < ch.begin+2 else f"I-{l_r}"
                                                break

                            elif r_id.startswith("External: "):
                                from transformers import pipeline
                                m_n = r_id.replace("External: ", "")
                                h_p = pipeline("ner", model=m_n, tokenizer=m_n, aggregation_strategy="simple")
                                res_h = h_p(user_text)
                                curr_h = 0
                                for i, t in enumerate(tokens):
                                    st_h = user_text.find(t, curr_h)
                                    if st_h == -1: continue
                                    en_h = st_h + len(t)
                                    curr_h = en_h
                                    for rh in res_h:
                                        if not (en_h <= rh['start'] or st_h >= rh['end']):
                                            r_tags[i] = f"B-{rh['entity_group']}" if st_h >= rh['start'] and st_h < rh['start']+2 else f"I-{rh['entity_group']}"
                                            break

                            visualize_result(tokens, r_tags)
                        except Exception as ex:
                            st.warning(f"Bağlantı Hatası ({r_name})")

        except Exception as general_ex:
            st.error(f"Sistem Hatası: {str(general_ex)}")
