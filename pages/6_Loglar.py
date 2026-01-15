import streamlit as st
import pandas as pd
import json
import os
import glob

st.set_page_config(page_title="Loglar", layout="wide")

def load_all_results(directory):
    files = glob.glob(os.path.join(directory, "*.json"))
    data = []
    for f in files:
        try:
            with open(f, 'r') as file:
                d = json.load(file)
                entry = {
                    "File": os.path.basename(f),
                    "Experiment ID": d.get("experiment_id", ""),
                    "F1 Score": d.get("metrics", {}).get("f1_score", 0),
                    "Model Path": d.get("model_path", "N/A"),
                }
                data.append(entry)
        except:
            pass
    return pd.DataFrame(data)

st.title("Loglar")
st.header("Deneysel Günlükler")

df_all = load_all_results("results/experiments")
if not df_all.empty:
    st.dataframe(df_all)
else:
    st.info("Log bulunamadı.")
