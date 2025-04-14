import streamlit as st
import pandas as pd
import datetime
import os

# Pad naar suggesties
suggesties_path = "suggesties.csv"

# Functie om suggesties te laden
def laad_suggesties():
    if os.path.exists(suggesties_path):
        return pd.read_csv(suggesties_path, sep=";", names=["timestamp", "Class-codenotatie", "suggestie"])
    else:
        return pd.DataFrame(columns=["timestamp", "Class-codenotatie", "suggestie"])

# Laad de Excel-data
df = pd.read_json("nlsfb-ifcapps-extract.json")

suggesties_df = laad_suggesties()

# Titel
st.title("Zoek op NL/SfB of IFC Entities")

col1, col2 = st.columns(2)

with col1:
    user_input = st.text_input("Zoek op NL/SfB code of deel ervan (bijv. '3-', '2.1', 'grond'): ")

with col2:
    entity_input = st.text_input("Zoek op IFC entiteit (bijv. 'IfcWall', 'IfcDoor'): ")

# Combineer beide zoekmogelijkheden
if user_input or entity_input:
    matches = df.copy()

    if user_input:
        matches = matches[matches['Class-codenotatie'].astype(str).str.contains(user_input, case=False, na=False) |
                          matches['tekst_NL-SfB'].astype(str).str.contains(user_input, case=False, na=False)]

    if entity_input:
        matches = matches[matches['IfcEntities'].astype(str).str.contains(entity_input, case=False, na=False)]

    if not matches.empty:
        st.write(f"**{len(matches)} resultaat(en) gevonden:**")
        for idx, row in matches.iterrows():
            st.subheader(f"Code: {row['Class-codenotatie']}")
            st.write(f"**Omschrijving**: {row['tekst_NL-SfB']}")

            # Toon IFC Entities als aparte code-elementen
            if pd.notna(row['IfcEntities']):
                entiteiten = [e.strip() for e in row['IfcEntities'].split(",") if e.strip()]
                if entiteiten:
                    cols = st.columns(len(entiteiten))
                    for i, entiteit in enumerate(entiteiten):
                        with cols[i]:
                            st.code(entiteit, language="")
            else:
                st.write("**IFC Entities**: Geen gegevens beschikbaar")

            # Suggestieformulier
            with st.expander("💡 Geef een suggestie voor betere IFC Entities"):
                suggestion = st.text_area(f"Jouw suggestie voor {row['Class-codenotatie']}", key=f"suggestion_{idx}")
                if st.button("Verzend suggestie", key=f"submit_{idx}"):
                    timestamp = datetime.datetime.now().isoformat()
                    with open(suggesties_path, "a", encoding="utf-8") as f:
                        f.write(f"{timestamp};{row['Class-codenotatie']};{suggestion}\n")
                    st.success("Suggestie verzonden! Bedankt voor je input.")
                    suggesties_df = laad_suggesties()

            # Toon suggesties van andere gebruikers
            relevante_suggesties = suggesties_df[suggesties_df['Class-codenotatie'] == row['Class-codenotatie']]
            if not relevante_suggesties.empty:
                st.markdown("**Suggesties van andere gebruikers:**")
                for _, s_row in relevante_suggesties.iterrows():
                    st.info(f"\u2022 {s_row['suggestie']}")

            st.markdown("---")
    else:
        st.warning("Geen resultaten gevonden voor deze zoekactie.")

# Footer
st.markdown("---")
st.caption("Gegevens uit: nlsfb-ifcapps-extract.xlsx")

