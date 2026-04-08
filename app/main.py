import streamlit as st
from pathlib import Path

st.title("Müll-Sortierer")
st.write("Lade ein Bild hoch und die KI erkennt automatisch, in welche Tonne der Müll gehört.")

st.divider()

col_upload, _ = st.columns(2)

with col_upload:
    st.subheader("Bild hochladen")
    uploaded = st.file_uploader(
        "Bild auswählen (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded:
        from PIL import Image
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption=uploaded.name, use_container_width=True)

        if st.button("Klassifizieren"):
            st.write("läuft")
