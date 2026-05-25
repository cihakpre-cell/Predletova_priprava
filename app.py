import streamlit as st
import datetime
import pytz
from fpdf import FPDF
import io
import unicodedata

# Pomocná funkce pro bezpečné odstranění diakritiky před tiskem do PDF
def odstran_diakritiku(text):
    return "".join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

# --- ZÁKLADNÍ NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Předletová příprava dronaře", page_icon="🛸", layout="centered")

st.title("🛸 Předletová příprava pilota dronu")
st.write("Oficiální asistent pro létání v kategorii OPEN v České republice.")
st.markdown("---")

# --- 1. ÚDAJE O PILOTOVI A DRONU ---
st.header("1. Profil letu")

col1, col2 = st.columns(2)
with col1:
    jmeno = st.text_input("Jméno a příjmení pilota:")
    cislo_pilota = st.text_input("Číslo dálkově řídícího pilota:", value="CZE-RP-fj1kki0j9ajl")
    misto_letu = st.text_input("Lokalita letu (město / ulice):")

with col2:
    model_dronu = st.text_input("Model dronu:", placeholder="např. DJI Mini 4 Pro")
    seriove_cislo_dronu = st.text_input("Sériové číslo dronu (identifikace):", placeholder="např. 1581F...")
    registrace_dronu = st.text_input("Registrační číslo provozovatele:", value="CZE-RP-fj1kki0j9ajl")

kategorie_open = st.selectbox(
    "Podkategorie OPEN:",
    ["A1 (drony do 900g, např. DJI Mini)", 
     "A2 (drony do 4kg, zkouška A2)", 
     "A3 (těžší drony do 25kg, dál od lidí)"]
)

st.markdown("---")

# --- 2. LETECKÝ ČAS (UTC) VS MÍSTNÍ ČAS ---
st.header("2. Kontrola leteckého času a prostoru")
st.write("Systém DroneMap používá světový čas (UTC). Zde je váš automatický přepočet:")

cz_tz = pytz.timezone('Europe/Prague')
local_time = datetime.datetime.now(cz_tz)
utc_time = local_time.astimezone(pytz.utc)

time_col1, time_col2 = st.columns(2)
with time_col1:
    st.metric(label="Aktuální čas v ČR", value=local_time.strftime("%H:%M:%S"))
with time_col2:
    st.metric(label="Čas pro DroneMap (UTC)", value=utc_time.strftime("%H:%M:%S"))

st.info("Klikněte na tlačítko níže, vyhledejte na mapě místo vašeho vzletu a zkontrolujte, zda tam neleží aktivní omezení. Nezapomeňte si pořídit snímek obrazovky (screenshot)!")

# Tlačítko jako odkaz na DroneMap
st.link_button("🌐 Otevřít oficiální mapu DroneMap.gov.cz", "https://dronemap.gov.cz/")

with st.expander("💡 Nápověda: Jak číst modré řádky v DroneMap?"):
    st.write("""
    Pokud se po kliknutí do mapy objeví v pravém panelu modré řádky, rozbalte je:
    * **AD LKPR / CTR / MCTR:** Jste v řízeném okrsku letiště. Pozor na přísné výškové limity.
    * **Grid CTR:** Čtvercová síť. Ukazuje maximální povolenou výšku letu bez koordinace s věží (např. 100m, 60m, nebo 0m).
    * **Maloplošná chráněná území / Národní park:** Létání je zde bez povolení ochrany přírody zakázáno.
    * **Hustě osídlený prostor:** V kategorii A3 sem nesmíte vletět. V A1/A2 se vyhněte shromáždění osob.
    * **Železniční / Silniční zóna:** Nelétejte přímo nad pozemní komunikací.
    * **TSA / TRA (Dočasně vyhrazený prostor):** Sledujte čas (UTC) a *Vertikální hranice*. Pokud začíná např. v 91 m AGL, smíte létat bezpečně pod ním (do 90 m).
    """)

# Nahrání důkazu
screenshot = st.file_uploader("Nahrajte screenshot z DroneMap jako důkaz pro případ kontroly:", type=['png', 'jpg', 'jpeg'])

# Potvrzení legislativy
ch_map1 = st.checkbox("Potvrzuji, že jsem zkontroloval DroneMap and prostor je pro můj let VOLNÝ (případně splňuji výškové a časové limity).")

st.markdown("---")

# --- 3. TECHNICKÝ A BEZPEČNOSTNÍ CHECKLIST ---
st.header("3. Fyzická a bezpečnostní kontrola")

ch_tech1 = st.checkbox("Vrtule jsou bez prasklin, ramena pevně drží, baterie není nafouklá.")
ch_tech2 = st.checkbox("Baterie dronu i ovladače jsou dostatečně nabité.")
ch_tech3 = st.checkbox("Kamera je čistá, kryt gimbalu sundán.")

# Dynamický bod podle kategorie
if "A3" in kategorie_open:
    ch_kat = st.checkbox("Kategorie A3: Jsem v bezpečné vzdálenosti (min. 150 metrů) od obytných, obchodních nebo rekreačních zón.")
elif "A2" in kategorie_open:
    ch_kat = st.checkbox("Kategorie A2: Dodržuji odstup minimálně 30 metrů od nezúčastněných osob (5 metrů v pomalém režimu).")
else:
    ch_kat = st.checkbox("Kategorie A1: Nelétám nad shromážděním lidí. Pokud přelétnu jednotlivce, udělám to co nejrychleji.")

ch_tech4 = st.checkbox("Na startovní pozici: Aplikace hlásí dostatek satelitů (GPS) a správně nastavenou bezpečnou výšku návratu (RTH).")

st.markdown("---")

# --- 4. VYHODNOCENÍ A GENERÁTOR PDF ---
st.header("4. Status a Letový deník")

def vytvor_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="--- PREDLETOVY PROTOKOL A LETOVY DENIK ---", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(5)

    # Kompletní textový výstup obohacený o Sériové číslo dronu
    log_obsah = f"""Datum a cas (Mistni): {local_time.strftime('%d.%m.%Y %H:%M:%S')}
Datum a cas (UTC): {utc_time.strftime('%d.%m.%Y %H:%M:%S')}

UDAJE O PILOTOVI A DRONU:
Pilot: {jmeno}
Cislo pilota: {cislo_pilota}
Model dronu: {model_dronu}
Seriove manuální cislo dronu: {seriove_cislo_dronu}
Registracni cislo provozovatele: {registrace_dronu}
Podkategorie OPEN: {kategorie_open}
Lokalita letu: {misto_letu}

PROHLASENI O KONTROLE:
[ANO] Vzduchy prostor overen v systemu DroneMap a vyhodnocen jako bezpecny k letu.
[ANO] Screenshot mapy byl pilotem porizen a nahran behem pripravy.
[ANO] Vizualni kontrola stroje a baterii probehla bez zavad.
[ANO] Pravidla bezpecne vzdalenosti od osob a budov pro danou kategorii overena.
[ANO] GPS lock a Return-To-Home (RTH) vyska nastaveny.

STAV: SCHVALENO K LETU."""

    # Vyčištění od diakritiky pro PDF engine
    cisty_text = odstran_diakritiku(log_obsah)

    for radek in cisty_text.split('\n'):
        pdf.cell(200, 6, txt=radek, ln=True)

    if screenshot is not None:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(200, 10, txt="Priloha: Screenshot mapy", ln=True)
        with open("temp_mapa.png", "wb") as f:
            f.write(screenshot.getbuffer())
        pdf.image("temp_mapa.png", x=10, y=None, w=180)

    return bytes(pdf.output())

# Kontrola splnění všech podmínek pro odemčení stahování
vsechny_checkboxy = [ch_map1, ch_tech1, ch_tech2, ch_tech3, ch_kat, ch_tech4]
vsechna_textova_pole = [jmeno, cislo_pilota, misto_letu, model_dronu, seriove_cislo_dronu, registrace_dronu]

if all(vsechny_checkboxy) and all(pole.strip() != "" for pole in vsechna_textova_pole) and screenshot is not None:
    st.success("🎉 Všechny body splněny! Jste připraveni k legálnímu a bezpečnému vzletu.")
    
    pdf_bytes = vytvor_pdf()
    
    st.download_button(
        label="📄 Stáhnout kompletní PDF protokol",
        data=pdf_bytes,
        file_name=f"Protokol_letu_{local_time.strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
else:
    st.warning("❌ K dokončení přípravy a vygenerování PDF protokolu musíte vyplnit všechna pole, nahrát screenshot z DroneMap a zaškrtnout celý checklist.")
