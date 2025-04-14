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
st.title("NL/SfB naar IFC Entities lookup")

# Invoerveld voor Class-codenotatie
user_input = st.text_input("Zoek een NL/SfB code of deel ervan (bijv. '3-', '2.1', 'grond'): ")

if user_input:
    # Filter op deels overeenkomende invoer in Class-codenotatie of tekst
    matches = df[df['Class-codenotatie'].astype(str).str.contains(user_input, case=False, na=False) |
                 df['tekst_NL-SfB'].astype(str).str.contains(user_input, case=False, na=False)]

    if not matches.empty:
        st.write(f"**{len(matches)} resultaat(en) gevonden:**")
        for idx, row in matches.iterrows():
            st.subheader(f"{row['Class-codenotatie']}")
            st.write(f"{row['tekst_NL-SfB']}")
            st.write(f"**IFC Entities**: {row['IfcEntities'] if pd.notna(row['IfcEntities']) else 'Geen gegevens beschikbaar'}")

            # Suggestieformulier
            with st.expander("💡 Geef een suggestie voor betere IFC Entities"):
                suggestion = st.text_area(f"Jouw suggestie voor {row['Class-codenotatie']}", key=f"suggestion_{idx}")
                if st.button("Verzend suggestie", key=f"submit_{idx}"):
                    timestamp = datetime.datetime.now().isoformat()
                    with open(suggesties_path, "a", encoding="utf-8") as f:
                        f.write(f"{timestamp};{row['Class-codenotatie']};{suggestion}\n")
                    st.success("Suggestie verzonden! Bedankt voor je input.")
                    # Herlaad suggesties zodat ze meteen zichtbaar zijn
                    suggesties_df = laad_suggesties()

            # Toon suggesties van andere gebruikers
            relevante_suggesties = suggesties_df[suggesties_df['Class-codenotatie'] == row['Class-codenotatie']]
            if not relevante_suggesties.empty:
                st.markdown("**Suggesties van andere gebruikers:**")
                for _, s_row in relevante_suggesties.iterrows():
                    st.info(f"\u2022 {s_row['suggestie']}")

            st.markdown("---")
    else:
        st.warning("Geen resultaten gevonden voor deze zoekterm.")

# Footer
st.markdown("---")
st.caption("Gegevens uit: nlsfb-ifcapps-extract.xlsx")
