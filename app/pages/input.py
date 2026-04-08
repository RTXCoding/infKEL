import streamlit as st
from pathlib import Path

st.title("Klassenraumsauberkeit eintragen")

st.divider()

option = st.selectbox(
    "Wählen Sie einen Klassenraum zum Bewerten aus:",
    ("G5a", "G5b", "Mobile phone"),
    index=None,
    placeholder="Raum auswählen",
)

st.write("Aktuelle Auswahl:", option)

if option:
    sweep = st.select_slider(
        "Wie gut wurde gefegt?",
        options=[
            "gar nicht",
            "etwas",
            "mittelmäßig",
            "gut",
            "sehr gut",
        ],
    )

    rubbish = st.multiselect(
        "Welcher Müll wurde rausgebracht?",
        ["Restmüll", "Papierkorb", "Gelber Sack", "Kein Müll rausgebracht"],
    )