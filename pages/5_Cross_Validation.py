import streamlit as st
import pandas as pd
import json
import os
import glob
import plotly.express as px

st.set_page_config(page_title="Cross-Validation", layout="wide")

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
                    "Experiment ID": d.get("experiment_id", ""),
                    "F1 Score": d.get("metrics", {}).get("f1_score", 0),
                    "CV Avg": cv.get("average_f1", 0),
                    "CV Std": cv.get("std_f1", 0),
                    "Folds": cv.get("fold_scores", []),
                    "Fold Reports": cv.get("fold_reports", []),
                    "Fold Model Paths": cv.get("fold_model_paths", []),
                    "Fold Weight Paths": cv.get("fold_weight_paths", []),
                    "Model": d.get("experiment_id", "Baseline")
                }
                data.append(entry)
        except:
            pass
    return pd.DataFrame(data)

st.title("Cross-Validation (Çapraz Doğrulama)")
st.header("Modellerin Kararlılık Analizi: K-Fold Sonuçları")

df_cv = load_all_results("results/experiments")
if not df_cv.empty:
    df_cv = df_cv[df_cv["CV Avg"] > 0] # Only those with CV
else:
    df_cv = pd.DataFrame()

if not df_cv.empty:
    # Create a "Long" format for boxplot
    long_data = []
    for _, row in df_cv.iterrows():
        for i, fold_val in enumerate(row["Folds"]):
            long_data.append({
                "Model": row["Model"] if row["Model"] != "Baseline" else row["Experiment ID"],
                "F1 Score": fold_val,
                "Fold": f"Fold {i+1}"
            })
    df_long = pd.DataFrame(long_data)

    fig_box = px.box(df_long, x="Model", y="F1 Score", color="Model",
                    title="5-Fold Üzerinden F1 Skor Dağılımı",
                    points="all")
    st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Özet Tablo")
    st.dataframe(df_cv[["Model", "CV Avg", "CV Std", "F1 Score"]].sort_values("CV Avg", ascending=False))

    st.markdown("---")
    st.subheader("Fold Bazlı Sınıflandırma Raporları")
    selected_model_cv = st.selectbox("Fold Raporlarını İncelemek İçin Model Seçin", df_cv["Model"].unique())
    model_row = df_cv[df_cv["Model"] == selected_model_cv].iloc[0]

    if model_row["Fold Reports"]:
        selected_fold = st.radio("İncelenecek Fold'u Seçin", [f"Fold {i+1}" for i in range(len(model_row["Fold Reports"]))], horizontal=True)
        fold_idx = int(selected_fold.split(" ")[1]) - 1

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader(f"{selected_fold} Sınıflandırma Raporu")
            st.text(model_row["Fold Reports"][fold_idx])

        with col_b:
            st.subheader(f"{selected_fold} Önemli Ağırlıklar")
            f_w_path = model_row["Fold Weight Paths"][fold_idx] if "Fold Weight Paths" in model_row and model_row["Fold Weight Paths"] else None

            if f_w_path and os.path.exists(f_w_path):
                with open(f_w_path, "r") as fw:
                    w_data = json.load(fw)

                st.markdown("**En Güçlü Durum Özellikleri**")
                st.dataframe(pd.DataFrame(w_data["top_features"]).head(15))

                st.markdown("**En Güçlü Geçişler**")
                st.dataframe(pd.DataFrame(w_data["top_transitions"]).head(10))
            else:
                st.info("Bu fold için ağırlık dosyası bulunamadı.")
    else:
        st.info("Bu model için detaylı fold raporu bulunmuyor.")
else:
    st.warning("Sonuçlarda K-Fold verisi bulunamadı. Lütfen deneyleri `cv=True` ile çalıştırın.")
