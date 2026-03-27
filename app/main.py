import streamlit as st
import sqlite3
from datetime import datetime
from pathlib import Path

# ── Seitenkonfiguration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Müll-KI | Sortierer",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hintergrund & Schrift */
    .stApp { background-color: #0f1a0f; color: #e8f5e9; }
    section[data-testid="stSidebar"] { background-color: #1a2e1a; }

    /* Metric-Karten */
    [data-testid="metric-container"] {
        background: #1e331e;
        border: 1px solid #2d5a2d;
        border-radius: 12px;
        padding: 16px;
    }

    /* Upload-Bereich */
    [data-testid="stFileUploader"] {
        border: 2px dashed #4caf50;
        border-radius: 12px;
        padding: 12px;
        background: #1a2e1a;
    }

    /* Buttons */
    .stButton > button {
        background: #4caf50;
        color: #0f1a0f;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        width: 100%;
    }
    .stButton > button:hover { background: #66bb6a; }

    /* Überschriften */
    h1, h2, h3 { color: #a5d6a7 !important; }

    /* Kategorie-Badge */
    .badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1.1rem;
        margin: 8px 0;
    }
    .badge-plastik  { background: #1565c0; color: #e3f2fd; }
    .badge-papier   { background: #4e342e; color: #fbe9e7; }
    .badge-glas     { background: #1b5e20; color: #e8f5e9; }
    .badge-metall   { background: #37474f; color: #eceff1; }
    .badge-restmuell{ background: #4a148c; color: #f3e5f5; }

    /* Trennlinie */
    hr { border-color: #2d5a2d; }
</style>
""", unsafe_allow_html=True)

# ── Datenbank-Hilfsfunktionen ────────────────────────────────────────────────
DB_PATH = "predictions.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            label     TEXT NOT NULL,
            confidence REAL NOT NULL,
            filename  TEXT
        )
    """)
    con.commit()
    con.close()

def save_prediction(label: str, confidence: float, filename: str = ""):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "INSERT INTO predictions (timestamp, label, confidence, filename) VALUES (?,?,?,?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), label, confidence, filename),
    )
    con.commit()
    con.close()

def get_stats():
    con = sqlite3.connect(DB_PATH)
    total  = con.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    counts = con.execute(
        "SELECT label, COUNT(*) FROM predictions GROUP BY label ORDER BY COUNT(*) DESC"
    ).fetchall()
    con.close()
    return total, counts

def get_recent(n: int = 5):
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT timestamp, label, confidence, filename FROM predictions ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    con.close()
    return rows

# ── Modell laden (Platzhalter) ───────────────────────────────────────────────
CLASSES = ["Plastik", "Papier", "Glas", "Metall", "Restmüll"]

BADGE_CLASSES = {
    "Plastik":  "badge-plastik",
    "Papier":   "badge-papier",
    "Glas":     "badge-glas",
    "Metall":   "badge-metall",
    "Restmüll": "badge-restmuell",
}

CATEGORY_EMOJI = {
    "Plastik":  "🔵",
    "Papier":   "🟤",
    "Glas":     "🟢",
    "Metall":   "⚫",
    "Restmüll": "🟣",
}

TONNE_FARBE = {
    "Plastik":  "Gelbe Tonne",
    "Papier":   "Blaue Tonne",
    "Glas":     "Glascontainer",
    "Metall":   "Gelbe Tonne",
    "Restmüll": "Graue Tonne",
}

@st.cache_resource
def load_model():
    """Modell laden – hier später echtes Keras-Modell einsetzen."""
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model("models/best_model.keras")
        return model
    except Exception:
        return None  # Demo-Modus wenn kein Modell vorhanden

def predict(image, model):
    """Vorhersage – gibt (label, confidence) zurück."""
    if model is None:
        # Demo-Modus: zufällige Vorhersage
        import random
        label = random.choice(CLASSES)
        conf  = round(random.uniform(0.70, 0.98), 2)
        return label, conf

    import numpy as np
    from PIL import Image as PILImage
    img = image.resize((224, 224))
    arr = np.array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    preds = model.predict(arr, verbose=0)[0]
    idx   = int(np.argmax(preds))
    return CLASSES[idx], float(preds[idx])

# ── App starten ──────────────────────────────────────────────────────────────
init_db()
model = load_model()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("♻️ Müll-KI")
    st.caption("Schulprojekt · Informatik · 2025")
    st.divider()

    st.subheader("📊 Statistiken")
    total, counts = get_stats()
    st.metric("Erkennungen gesamt", total)

    if counts:
        for label, cnt in counts:
            emoji = CATEGORY_EMOJI.get(label, "•")
            st.write(f"{emoji} **{label}** — {cnt}×")
    else:
        st.caption("Noch keine Daten vorhanden.")

    st.divider()
    model_status = "✅ Modell geladen" if model else "⚠️ Demo-Modus (kein Modell)"
    st.caption(model_status)

# ── Hauptbereich ─────────────────────────────────────────────────────────────
st.title("♻️ Müll-Sortierer")
st.write("Lade ein Bild hoch und die KI erkennt automatisch, in welche Tonne der Müll gehört.")

st.divider()

col_upload, col_result = st.columns([1, 1], gap="large")

# ── Linke Spalte: Upload ─────────────────────────────────────────────────────
with col_upload:
    st.subheader("📸 Bild hochladen")
    uploaded = st.file_uploader(
        "Bild auswählen (JPG, PNG)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded:
        from PIL import Image
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption=uploaded.name, use_container_width=True)

        if st.button("🔍 Klassifizieren"):
            with st.spinner("KI analysiert das Bild..."):
                label, conf = predict(img, model)
                save_prediction(label, conf, uploaded.name)
            st.session_state["result"] = (label, conf)
            st.rerun()

# ── Rechte Spalte: Ergebnis ──────────────────────────────────────────────────
with col_result:
    st.subheader("🎯 Ergebnis")

    if "result" in st.session_state:
        label, conf = st.session_state["result"]
        emoji  = CATEGORY_EMOJI.get(label, "")
        tonne  = TONNE_FARBE.get(label, "")
        badge_cls = BADGE_CLASSES.get(label, "")

        st.markdown(
            f'<div class="badge {badge_cls}">{emoji} {label}</div>',
            unsafe_allow_html=True,
        )

        st.metric("Sicherheit", f"{conf*100:.1f} %")
        st.info(f"🗑️ Gehört in die **{tonne}**")

        st.progress(conf, text=f"Konfidenz: {conf*100:.1f}%")

        st.divider()
        st.subheader("🕓 Letzte Erkennungen")
        recent = get_recent(5)
        if recent:
            for ts, lbl, c, fn in recent:
                em = CATEGORY_EMOJI.get(lbl, "•")
                st.write(f"{em} `{ts}` — **{lbl}** ({c*100:.0f}%) — _{fn}_")
        else:
            st.caption("Noch keine Erkennungen.")
    else:
        st.info("👈 Lade ein Bild hoch und klicke auf **Klassifizieren**.")
        st.divider()
        st.subheader("🕓 Letzte Erkennungen")
        recent = get_recent(5)
        if recent:
            for ts, lbl, c, fn in recent:
                em = CATEGORY_EMOJI.get(lbl, "•")
                st.write(f"{em} `{ts}` — **{lbl}** ({c*100:.0f}%) — _{fn}_")
        else:
            st.caption("Noch keine Erkennungen.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Müll-KI · Informatikunterricht · Mit ❤️ gebaut von eurem Team")
