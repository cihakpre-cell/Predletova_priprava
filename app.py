import streamlit as st
import datetime
import pytz
from fpdf import FPDF
import io

# --- NASTAVENÍ ---
st.set_page_config(page_title="Předletová příprava", page_icon="🛸", layout="centered")
st.title("🛸 Předletová příprava pilota dronu")

# --- 1. PROFIL ---
col1, col2 = st.columns(2)
with col1:
    jmeno = st.text_input("Jméno a příjmení:")
    cislo_pilota = st.text_input("Číslo dálkově řídícího pilota:", value="CZE-RP-fj1kki0j9ajl")
    misto_letu = st.text_input("Lokalita letu:")
with col2:
    model_dronu = st.text_input("Model dronu:")
    registrace_dronu = st.text_input("Registrační číslo:", value="CZE-RP-fj1kki0j9ajl")
    kategorie = st.selectbox("Kategorie OPEN:", ["A1", "A2", "A3"])

# --- 2. ČAS A MAPA ---
cz_tz = pytz.timezone('Europe/Prague')
local_time = datetime.datetime.now(cz_tz)
utc_time = local_time.astimezone(pytz.utc)

st.write(f"**Čas (místní):** {local_time.strftime('%d.%m.%Y %H:%M:%S')}")
st.write(f"**Čas (UTC):** {utc_time.strftime('%d.%m.%Y %H:%M:%S')}")
st.link_button("🌐 Otevřít DroneMap", "https://dronemap.gov.cz/")

with st.expander("💡 Nápověda: Jak číst modré řádky?"):
    st.write("Sledujte vertikální hranice a aktivitu TSA/TRA prostorů v UTC čase.")

screenshot = st.file_uploader("Nahrajte screenshot mapy:", type=['png', 'jpg', 'jpeg'])

# --- 3. CHECKLIST ---
st.header("3. Bezpečnostní checklist")
ch1 = st.checkbox("Prostor ověřen v DroneMap.")
ch2 = st.checkbox("Vizuální kontrola stroje a baterií.")
ch3 = st.checkbox("Pravidla bezpečné vzdálenosti ověřena.")
ch4 = st.checkbox("GPS lock a RTH nastaveny.")

# --- 4. PDF GENERÁTOR ---
def vytvor_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="PREDLETOVY PROTOKOL A LETOVY DENIK", ln=True, align='C')
    pdf.set_font("Arial", size=11)
    pdf.ln(5)
    
    text = f"""Datum a cas (Mistni): {local_time.strftime('%d.%m.%Y %H:%M:%S')}
Datum a cas (UTC): {utc_time.strftime('%d.%m.%Y %H:%M:%S')}

UDAJE O PILOTOVI A DRONU:
Pilot: {jmeno}
Cislo pilota: {cislo_pilota}
Model dronu: {model_dronu}
Registracni cislo provozovatele: {registrace_dronu}
Podkategorie OPEN: {kategorie}
Lokalita letu: {misto_letu}

PROHLASENI O KONTROLE:
[ANO] Vzdusny prostor overen v systemu DroneMap.
[ANO] Screenshot mapy byl porizen.
[ANO] Vizualni kontrola stroje a baterii probehla.
[ANO] Pravidla bezpecne vzdalenosti overena.
[ANO] GPS lock a RTH vyska nastaveny.

STAV: SCHVALENO K LETU"""
    
    for line in text.split('\n'):
        pdf.cell(200, 7, txt=line, ln=True)
        
    if screenshot:
        pdf.ln(5)
        pdf.cell(200, 10, txt="Priloha: Screenshot mapy", ln=True)
        with open("temp_mapa.png", "wb") as f:
            f.write(screenshot.getbuffer())
        pdf.image("temp_mapa.png", x=10, y=None, w=180)
        
    return pdf.output(dest='S').encode('latin-1')

if all([jmeno, screenshot, ch1, ch2, ch3, ch4]):
    if st.button("Vygenerovat a stáhnout PDF protokol"):
        pdf_bytes = vytvor_pdf()
        st.download_button("📄 Stáhnout PDF", pdf_bytes, "Protokol_letu.pdf", "application/pdf")
else:
    st.warning("Vyplňte údaje, nahrajte screenshot a zaškrtněte checklist.")
