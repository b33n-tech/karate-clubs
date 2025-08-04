import streamlit as st
import pandas as pd
import io
import re

def parse_karate_clubs_simple(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clubs = []
    i = 0
    n = len(lines)
    
    while i < n:
        # Ligne 1 : nom du club
        nom = lines[i]
        i += 1
        if i >= n or lines[i].lower() != "adresse":
            # Format inattendu, on skip ce bloc
            # ou on peut lever une erreur selon besoin
            break
        i += 1
        # Ligne 3 + 4 : adresse
        if i + 1 >= n:
            break
        adresse = lines[i] + ", " + lines[i+1]
        i += 2
        # Ligne 5 : peut être téléphone ou non
        tel = ""
        if i < n:
            # Détecter si ligne téléphone : contient chiffres et espaces, pas trop longue
            if re.match(r"^[\d\s\./\-]+$", lines[i]) and len(lines[i]) < 20:
                tel = lines[i]
                i += 1
        
        clubs.append({"Nom": nom, "Adresse": adresse, "Téléphone": tel})
    
    return pd.DataFrame(clubs)

st.title("Parser clubs de karaté Savoie vers XLSX - Template strict")

input_text = st.text_area("Colle ici la liste brute des clubs de karaté (template strict)", height=400)

if st.button("Parser et générer XLSX"):
    if not input_text.strip():
        st.warning("Merci de coller le texte avant de lancer le parsing.")
    else:
        try:
            df = parse_karate_clubs_simple(input_text)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ClubsKarate')
            output.seek(0)
            st.success("Fichier XLSX généré avec succès !")
            st.download_button(
                label="Télécharger le fichier Excel",
                data=output,
                file_name="clubs_karate_savoie_template_strict.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erreur lors du parsing : {e}")
