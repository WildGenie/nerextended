import streamlit as st
import os

st.set_page_config(page_title="Makale Önizleme", layout="wide")

st.title("Makale Önizleme")
st.header("Akademik Makale Taslağı")

# Try to load the generated academic article
if os.path.exists("docs/Akademik_Makale.md"):
    with open("docs/Akademik_Makale.md", "r") as f:
        st.markdown(f.read())
else:
    st.info("Makale taslağı (Akademik_Makale.md) henüz oluşturulmamış. Lütfen `generate_docs` scriptini çalıştırın.")
