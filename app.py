import streamlit as st
import datetime
import pytz
from fpdf import FPDF
import io

# Nastavení stránky
st.set_page_config(page_title="Předletová příprava", page_icon="🛸")
st.title("🛸 Předletová příprava pilota dronu")

# --- VSTUPNÍ DATA ---
jmeno = st.text_input("Jméno a příjmení pilota:")
cislo_pilota = st.text_input("Číslo dálkově řídícího pilota:", value="CZE-RP-fj1kki0j9ajl")
misto_letu = st.text_input("Lokalita letu:")
model_dronu = st.text_input("Model dronu:")
screenshot = st.file_uploader("Nahrajte screenshot z DroneMap:", type=['png', 'jpg', 'jpeg'])

# --- FUNKCE PRO PDF ---
def vytvor_pdf(jmeno, cislo, model, misto, img_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Protokol o predletove priprave", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Pilot: {jmeno}", ln=True)
    pdf.cell(200, 10, txt=f"Cislo pilota: {cislo}", ln=True)
    pdf.cell(200, 10, txt=f"Dron: {model}", ln=True)
    pdf.cell(200, 10, txt=f"Lokalita: {misto}", ln=True)
    pdf.cell(200, 10, txt=f"Datum: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    
    if img_file is not None:
        pdf.ln(10)
        pdf.cell(200, 10, txt="Priloha: Screenshot mapy", ln=True)
        # Uložení screenshotu do paměti a vložení do PDF
        image_bytes = img_file.getvalue()
        pdf.image(io.BytesIO(image_bytes), x=10, y=None, w=180)
        
    return pdf.output(dest='S').encode('latin-1')

# --- GENEROVÁNÍ ---
if st.button("Vygenerovat PDF protokol"):
    if screenshot and jmeno:
        pdf_bytes = vytvor_pdf(jmeno, cislo_pilota, model_dronu, misto_letu, screenshot)
        st.download_button(
            label="📄 Stáhnout PDF protokol",
            data=pdf_bytes,
            file_name="Protokol_letu.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Vyplňte jméno a nahrajte screenshot mapy!")
