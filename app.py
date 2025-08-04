import streamlit as st
import pandas as pd
import io
import re

def parse_karate_clubs_v2(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clubs = []
    club = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Détecter nom du club : ligne en majuscules, pas mot clé
        if line.isupper() and line not in ["ADRESSE", "EMAIL", "TELEPHONE"]:
            if club:
                clubs.append(club)
                club = {}
            club["Nom"] = line
            club["Adresse"] = ""
            club["Code Postal"] = ""
            club["Téléphone"] = ""
            i += 1
            continue
        
        # Adresse : après "ADRESSE" prendre toutes les lignes jusqu'à EMAIL, TELEPHONE ou nouveau club
        if line.upper() == "ADRESSE":
            i += 1
            adresse_lines = []
            while i < len(lines):
                l = lines[i]
                if l.upper() in ["EMAIL", "TELEPHONE"]:
                    break
                # Si nouvelle ligne majuscule = nouveau club, stop adresse
                if l.isupper() and l not in ["ADRESSE", "EMAIL", "TELEPHONE"]:
                    break
                adresse_lines.append(l)
                i += 1
            adresse = ", ".join(adresse_lines).strip()
            club["Adresse"] = adresse
            
            # Extraire code postal (5 chiffres)
            cp_match = re.search(r"\b(\d{5})\b", adresse)
            club["Code Postal"] = cp_match.group(1) if cp_match else ""
            continue
        
        # Téléphone(s) : ligne(s) après "TELEPHONE" ou ligne(s) avec format n° classique
        if line.upper() == "TELEPHONE":
            i += 1
            phones = []
            while i < len(lines):
                l = lines[i]
                # Stop si on arrive à EMAIL, nouveau club, ou ADRESSE
                if l.upper() in ["EMAIL", "ADRESSE"]:
                    break
                if l.isupper() and l not in ["ADRESSE", "EMAIL", "TELEPHONE"]:
                    break
                # Garder les lignes contenant chiffres ou séparateurs habituels
                if re.search(r"[\d\s\./\-]+", l):
                    phones.append(l)
                else:
                    break
                i += 1
            club["Téléphone"] = " / ".join(phones).strip()
            continue
        
        # Ligne isolée avec numéro de téléphone (sans "TELEPHONE" label)
        if re.fullmatch(r"(\d[\d\s\./\-]{7,}\d)", line):
            # rajoute au téléphone existant
            if "Téléphone" in club and club["Téléphone"]:
                club["Téléphone"] += " / " + line
            else:
                club["Téléphone"] = line
            i += 1
            continue
        
        i += 1
    
    # Dernier club à ajouter
    if club:
        clubs.append(club)

    return pd.DataFrame(clubs)


st.title("Parser clubs de karaté Savoie vers XLSX - V2")

input_text = st.text_area("Colle ici la liste brute des clubs de karaté (comme dans ton exemple)", height=400)

if st.button("Parser et générer XLSX"):
    if not input_text.strip():
        st.warning("Merci de coller le texte avant de lancer le parsing.")
    else:
        try:
            df = parse_karate_clubs_v2(input_text)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ClubsKarate')
            output.seek(0)
            st.success("Fichier XLSX généré avec succès !")
            st.download_button(
                label="Télécharger le fichier Excel",
                data=output,
                file_name="clubs_karate_savoie_v2.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erreur lors du parsing : {e}")
