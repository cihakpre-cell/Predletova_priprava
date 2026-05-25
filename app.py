import streamlit as st
import datetime
import pytz
from fpdf import FPDF
import io

# --- ZÁKLADNÍ NASTAVENÍ ---
st.set_page_config(page_title="Předletová příprava dronaře", page_icon="🛸", layout="centered")

st.title("🛸 Předletová příprava pilota dronu")
st.write("Oficiální asistent pro létání v kategorii OPEN v České republice.")
st.markdown("---")

# --- 1. ÚDAJE O PILOTOVI ---
st.header("1. Profil letu")
col1, col2 = st.columns(2)
with col1:
    jmeno = st.text_input("Jméno a příjmení pilota:")
    cislo_pilota = st.text_input("Číslo dálkově řídícího pilota:", value="CZE-RP-fj1kki0j9ajl")
    misto_letu = st.text_input("Lokalita letu:")
with col2:
    model_dronu = st.text_input("Model dronu:")
    registrace_dronu = st.text_input("Registrační číslo provozovatele:")
    kategorie_open = st.selectbox("Podkategorie OPEN:", ["A1", "A2", "A3"])

# --- 2. ČAS A MAPA ---
st.header("2. Kontrola času a prostoru")
cz_tz = pytz.timezone('Europe/Prague')
aktualni_local_cas = datetime.datetime.now(cz_tz)
aktualni_utc_cas = aktualni_local_cas.astimezone(pytz.utc)

st.info(f"Aktuální čas pro DroneMap (UTC): **{aktualni_utc_cas.strftime('%H:%M')}**")
st.link_button("🌐 Otevřít oficiální mapu DroneMap.gov.cz", "https://dronemap.gov.cz/")

with st.expander("💡 Nápověda: Jak číst modré řádky v DroneMap?"):
    st.write("""
    Rozbalte každý modrý řádek:
    * **CTR / Grid CTR:** Pozor na výškové limity.
    * **Chráněná území:** Létání bez povolení zakázáno.
    * **TSA / TRA:** Pokud jsou aktivní, sledujte *Vertikální hranice* (např. 91 m AGL znamená, že pod 90m je prostor volný).
    * **Hustě osídlený prostor:** V kategorii A3 sem nesmíte vletět.
    """)

screenshot = st.file_uploader("Nahrajte screenshot z DroneMap:", type=['png', 'jpg', 'jpeg'])

# --- 3. CHECKLIST ---
st.header("3. Bezpečnostní checklist")
ch1 = st.checkbox("Vrtule jsou bez prasklin, baterie nejsou nafouklé.")
ch2 = st.checkbox("Baterie dronu i ovladače jsou dostatečně nabité.")
ch3 = st.checkbox("Ověřil jsem, že nejsem v zakázané zóně (např. CHKO/NP).")
ch4 = st.checkbox("GPS lock a Return-To-Home výška nastaveny.")

# --- 4. PDF GENERÁTOR ---
st.header("4. Vygenerovat protokol")

def vytvor_pdf(jmeno, cislo, model, reg, kat, misto, img_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Protokol o predletove priprave", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Pilot: {jmeno} ({cislo})", ln=True)
    pdf.cell(200, 10, txt=f"Dron: {model} (Reg: {reg})", ln=True)
    pdf.cell(200, 10, txt=f"Lokalita: {misto} | Kategorie: {kat}", ln=True)
    pdf.cell(200, 10, txt=f"Datum: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}", ln=True)
    
    if img_file is not None:
        pdf.ln(10)
        pdf.cell(200, 10, txt="Priloha: Screenshot mapy", ln=True)
        image_bytes = img_file.getvalue()
        pdf.image(io.BytesIO(image_bytes), x=10, y=None, w=180)
    return pdf.output(dest='S').encode('latin-1')

if all([jmeno, screenshot, ch1, ch2, ch3, ch4]):
    pdf_data = vytvor_pdf(jmeno, cislo_pilota, model_dronu, registrace_dronu, kategorie_open, misto_letu, screenshot)
    st.download_button("📄 Stáhnout PDF protokol", pdf_data, "protokol_letu.pdf", "application/pdf")
else:
    st.warning("Pro vygenerování protokolu vyplňte všechny údaje, nahrajte screenshot a zaškrtněte checklist.")
