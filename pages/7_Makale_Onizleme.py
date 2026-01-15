import streamlit as st
import os

st.set_page_config(page_title="Makale Önizleme", layout="wide")

st.title("Makale Önizleme")
st.header("Akademik Makale Taslağı")

# Try to load either .md or .tex
if os.path.exists("docs/Paper.md"):
    with open("docs/Paper.md", "r") as f:
        st.markdown(f.read())
else:
    st.info("Makale taslağı (Paper.md) henüz oluşturulmamış. Lütfen `generate_docs` scriptini çalıştırın.")
