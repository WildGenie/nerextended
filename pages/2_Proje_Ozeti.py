import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px

st.set_page_config(page_title="Proje Özeti", layout="wide")

def load_all_results(directory):
    files = glob.glob(os.path.join(directory, "*.json"))
    data = []
    for f in files:
        try:
            with open(f, 'r') as file:
                d = json.load(file)
                cv = d.get("metrics", {}).get("cross_validation", {})
                entry = {
                    "File": os.path.basename(f),
                    "F1 Score": d.get("metrics", {}).get("f1_score", 0),
                    "CV Avg": cv.get("average_f1", 0)
                }
                data.append(entry)
        except:
            pass
    return pd.DataFrame(data)

st.title("Proje Özeti")

st.markdown("""
### Genişletilmiş Türkçe Varlık İsmi Tanıma (NER)

Bu proje, standart Türkçe NER yeteneklerini (Kişi, Yer, Organizasyon) **Şirket, Grup ve Film** varlıklarını da kapsayacak şekilde genişletmeyi amaçlamaktadır.

#### 🚀 Temel Teknolojiler
- **Öznitelikler**: Derin Morfoloji (Nuve), Anlamsal Gömülüler (BERT/VBART).
- **Model**: Dizi etiketleme için Linear-Chain CRF.
- **Optimizasyon**: Hiper-parametreler üzerinde Grid Search.
""")

col1, col2, col3 = st.columns(3)
results_dir = "results/experiments"
if os.path.exists(results_dir):
    df = load_all_results(results_dir)
    if not df.empty:
        best_f1 = df["F1 Score"].max()
        best_cv = df["CV Avg"].max()
        col1.metric("En İyi Test F1", f"{best_f1:.4f}")
        col2.metric("En İyi CV Ort.", f"{best_cv:.4f}")
        col3.metric("Deney Sayısı", len(df))
