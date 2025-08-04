import streamlit as st
import pandas as pd
import io

def parse_karate_clubs(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    clubs = []
    club = {}

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.isupper() and not line.startswith(("ADRESSE", "EMAIL", "TELEPHONE")):
            if club:
                clubs.append(club)
                club = {}
            club["Nom"] = line
            club["Adresse"] = ""
            club["Téléphone"] = ""
            club["Email"] = ""
            i += 1
            continue
        
        if line.upper() == "ADRESSE":
            i += 1
            adresse_lines = []
            while i < len(lines) and lines[i].upper() not in ["EMAIL", "TELEPHONE"] and not (lines[i].isupper() and lines[i] not in ["ADRESSE", "EMAIL", "TELEPHONE"]):
                adresse_lines.append(lines[i])
                i += 1
            club["Adresse"] = ", ".join(adresse_lines).strip()
            continue
        
        if line.upper() == "TELEPHONE" or (line.replace(" ", "").replace(".", "").isdigit() and len(line.replace(" ", "").replace(".", "")) >= 8):
            phones = []
            while i < len(lines) and (lines[i].replace(" ", "").replace(".", "").isdigit() or lines[i].startswith("0") or "/" in lines[i] or any(c.isdigit() for c in lines[i])):
                phones.append(lines[i])
                i += 1
            club["Téléphone"] = " / ".join(phones)
            continue
        
        if line.upper() == "EMAIL" or "@" in line:
            emails = []
            while i < len(lines) and ("@" in lines[i] or lines[i].upper() == "EMAIL"):
                if lines[i].upper() != "EMAIL":
                    emails.append(lines[i])
                i += 1
            club["Email"] = " / ".join(emails)
            continue
        
        i += 1

    if club:
        clubs.append(club)

    return pd.DataFrame(clubs)


st.title("Parser clubs de karaté Savoie vers XLSX")

input_text = st.text_area("Colle ici la liste brute des clubs de karaté (comme dans ton exemple)", height=400)

if st.button("Parser et générer XLSX"):
    if not input_text.strip():
        st.warning("Merci de coller le texte avant de lancer le parsing.")
    else:
        try:
            df = parse_karate_clubs(input_text)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ClubsKarate')
            output.seek(0)
            st.success("Fichier XLSX généré avec succès !")
            st.download_button(
                label="Télécharger le fichier Excel",
                data=output,
                file_name="clubs_karate_savoie.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erreur lors du parsing : {e}")
