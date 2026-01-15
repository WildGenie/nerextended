import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px

st.set_page_config(page_title="Morfoloji Analizi", layout="wide")

def load_all_results(directory):
    files = glob.glob(os.path.join(directory, "*.json"))
    data = []
    for f in files:
        try:
            with open(f, 'r') as file:
                d = json.load(file)
                config = d.get("config", {})
                f_config = config.get("feature_config", {})
                t_config = config.get("train_config", {})
                cv = d.get("metrics", {}).get("cross_validation", {})
                entry = {
                    "File": os.path.basename(f),
                    "Experiment ID": d.get("experiment_id", ""),
                    "F1 Score": d.get("metrics", {}).get("f1_score", 0),
                    "CV Avg": cv.get("average_f1", 0),
                    "Morphology": f_config.get("use_morphology", False),
                    "Embeddings": f_config.get("use_embeddings", False),
                    "Engine": f_config.get("embedding_model", "Baseline"),
                    "Dataset": t_config.get("dataset_name", "Unknown")
                }
                data.append(entry)
        except:
            pass
    return pd.DataFrame(data)

st.title("Morfoloji Analizi")
st.header("Karşılaştırmalı Analiz: Morfoloji Motorları & Gömülüler")

df_all = load_all_results("results/experiments")
if not df_all.empty:
    # Filter for the main morphology configurations
    df_morph = df_all[df_all["Dataset"].astype(str).str.contains("Gold", case=False, na=False)]

    # Sort by F1 to show progression
    df_morph = df_morph.sort_values("F1 Score")

    fig = px.bar(df_morph, x="Experiment ID", y="F1 Score", color="Engine",
                 hover_data=["Morphology", "Embeddings", "CV Avg"],
                 title="F1 Performans İlerlemesi",
                 text_auto='.4f')

    # Adjust Y axis
    min_f1 = df_morph["F1 Score"].min()
    max_f1 = df_morph["F1 Score"].max()
    if pd.notna(min_f1) and pd.notna(max_f1):
        fig.update_layout(yaxis_range=[max(0.7, min_f1 - 0.05), min(1.0, max_f1 + 0.05)])

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Deney Kurulum Detayları")
    st.dataframe(df_morph[["Experiment ID", "Engine", "Morphology", "Embeddings", "F1 Score", "CV Avg"]])
else:
    st.info("Deney sonucu bulunamadı. Lütfen karşılaştırma scriptlerini çalıştırın.")

st.info("Nuve (Derin Morfoloji), basit Zemberek lemmatizasyonuna kıyasla daha ayrıntılı morfolojik özellikler sağlar.")
