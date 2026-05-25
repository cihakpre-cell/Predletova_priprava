import streamlit as st
import datetime
import pytz
from fpdf import FPDF
import io
import unicodedata
from PIL import Image
import google.generativeai as genai

# Pomocná funkce pro bezpečné odstranění diakritiky před tiskem do PDF
def odstran_diakritiku(text):
    return "".join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')

# --- ZÁKLADNÍ NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="Předletová příprava dronaře", page_icon="🛸", layout="centered")

st.title("🛸 Předletová příprava pilota dronu + Multi-AI")
st.write("Oficiální asistent pro létání v kategorii OPEN. Podpora více screenshotů a hromadné AI analýzy.")
st.markdown("---")

# --- BOČNÍ PANEL (SIDEBAR) PRO GEMINI API KLÍČ ---
st.sidebar.header("⚙️ Nastavení AI (ZDARMA)")
gemini_api_key = st.sidebar.text_input("Vložte Google Gemini API klíč:", type="password")
st.sidebar.markdown("""
[Získat klíč zdarma v Google AI Studio](https://aistudio.google.com/)
*(Přihlaste se Google účtem a klikněte na 'Get API key')*
""")

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

cz_tz = pytz.timezone('Europe/Prague')
local_time = datetime.datetime.now(cz_tz)
utc_time = local_time.astimezone(pytz.utc)

time_col1, time_col2 = st.columns(2)
with time_col1:
    st.metric(label="Aktuální čas v ČR", value=local_time.strftime("%H:%M:%S"))
with time_col2:
    st.metric(label="Čas pro DroneMap (UTC)", value=utc_time.strftime("%H:%M:%S"))

st.link_button("🌐 Otevřít oficiální mapu DroneMap.gov.cz", "https://dronemap.gov.cz/")

with st.expander("💡 Nápověda: Jak číst modré řádky v DroneMap?"):
    st.write("""
    Pokud se po kliknutí do mapy objeví v pravém panelu modré řádky, rozbalte je:
    * **AD LKPR / CTR / MCTR:** Jste v řízeném okrsku letiště. Pozor na přísné výškové limity.
    * **Grid CTR:** Čtvercová síť. Ukazuje maximální povolenou výšku letu bez koordinace s věží.
    * **Maloplošná chráněná území / Národní park:** Létání je zde bez povolení ochrany přírody zakázáno.
    * **TSA / TRA (Dočasně vyhrazený prostor):** Sledujte čas (UTC) a *Vertikální hranice*.
    """)

screenshots = st.file_uploader("Nahrajte screenshoty z DroneMap (můžete i více najednou):", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# --- OPRAVENO: AI ANALÝZA S PAMĚTÍ (SESSION STATE) PROTI OPAKOVANÉMU SPOUŠTĚNÍ ---
if 'ai_final_text' not in st.session_state:
    st.session_state['ai_final_text'] = "AI analýza nebyla spuštěna (vyberte soubory a klikněte na tlačítko níže)."
if 'last_uploaded_files' not in st.session_state:
    st.session_state['last_uploaded_files'] = []

# Detekce, zda uživatel změnil nahrané soubory (pokud ano, resetujeme starou analýzu)
current_files_ids = [f.name + str(f.size) for f in screenshots] if screenshots else []
if current_files_ids != st.session_state['last_uploaded_files']:
    st.session_state['ai_final_text'] = "AI analýza nebyla spuštěna (klikněte na tlačítko níže)."
    st.session_state['last_uploaded_files'] = current_files_ids

if screenshots and gemini_api_key:
    # Tlačítko se zobrazí pouze pokud jsou nahrány soubory a zadán klíč
    if st.button("🤖 Spustit hromadnou AI analýzu mapy", type="primary"):
        combined_results = []
        progress_bar = st.progress(0)
        
        for idx, shot in enumerate(screenshots):
            with st.spinner(f"🤖 AI analyzuje screenshot č. {idx+1}..."):
                try:
                    genai.configure(api_key=gemini_api_key)
                    img = Image.open(shot)
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    
                    prompt = """
                    Jsi expert na českou leteckou legislativu dronů. Analyzuj tento screenshot z DroneMap. 
                    Podívej se na aktivní zóny v pravém panelu. Napiš stručné zhodnocení (max 2 věty). 
                    Varuj před limity výšky (GRID CTR) nebo aktivními zónami.
                    Odpovídej česky.
                    """
                    
                    response = model.generate_content([prompt, img])
                    combined_results.append(f"Obrázek {idx+1}: {response.text}")
                except Exception as e:
                    combined_results.append(f"Obrázek {idx+1}: Chyba analýzy ({e})")
            
            progress_bar.progress((idx + 1) / len(screenshots))
        
        # Uložení výsledku do session_state paměti
        st.session_state['ai_final_text'] = "\n".join(combined_results)

# Zobrazení výsledku z paměti na obrazovce
if "nebyla spuštěna" not in st.session_state['ai_final_text']:
    st.success("### 🤖 Výsledek hromadné AI analýzy:")
    st.write(st.session_state['ai_final_text'])
else:
    st.info(st.session_state['ai_final_text'])

ch_map1 = st.checkbox("Potvrzuji, že jsem zkontroloval DroneMap a prostor je pro můj let VOLNÝ (případně splňuji výškové a časové limity).")

st.markdown("---")

# --- 3. TECHNICKÝ A BEZPEČNOSTNÍ CHECKLIST ---
st.header("3. Fyzická a bezpečnostní kontrola")

ch_tech1 = st.checkbox("Vrtule jsou bez prasklin, ramena pevně drží, baterie není nafouklá.")
ch_tech2 = st.checkbox("Baterie dronu i ovladače jsou dostatečně nabité.")
ch_tech3 = st.checkbox("Kamera je čistá, kryt gimbalu sundán.")

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

def vytvor_pdf(ai_text_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(pdf.epw, 10, text="--- PREDLETOVY PROTOKOL A LETOVY DENIK ---", align='C')
    pdf.ln(12)
    
    pdf.set_font("Arial", size=10)

    log_obsah = f"""Datum a cas (Mistni): {local_time.strftime('%d.%m.%Y %H:%M:%S')}
Datum a cas (UTC): {utc_time.strftime('%d.%m.%Y %H:%M:%S')}

UDAJE O PILOTOVI A DRONU:
Pilot: {jmeno}
Cislo pilota: {cislo_pilota}
Model dronu: {model_dronu}
Seriove manualni cislo dronu: {seriove_cislo_dronu}
Registracni cislo provozovatele: {registrace_dronu}
Podkategorie OPEN: {kategorie_open}
Lokalita letu: {misto_letu}

PROHLASENI O KONTROLE:
[ANO] Vzduchy prostor overen v systemu DroneMap a vyhodnocen jako bezpecny k letu.
[ANO] {len(screenshots)} screenshotu mapy bylo pilotem porizen a nahrano.
[ANO] Vizualni kontrola stroje a baterii probehla bez zavad.
[ANO] Pravidla bezpecne vzdalenosti od osob a budov pro danou kategorii overena.
[ANO] GPS lock a Return-To-Home (RTH) vyska nastaveny.

STAV: SCHVALENO K LETU.

AI VYHODNOCENI PROSTORU:
{ai_text_list}"""

    cisty_text = odstran_diakritiku(log_obsah)
    pdf.multi_cell(w=pdf.epw, h=6, text=cisty_text)

    # Vložení všech obrázků do PDF
    if screenshots:
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(pdf.epw, 10, text=f"Priloha: {len(screenshots)}x Screenshot mapy")
        pdf.ln(10)
        
        for i, shot in enumerate(screenshots):
            temp_name = f"temp_mapa_{i}.png"
            with open(temp_name, "wb") as f:
                f.write(shot.getbuffer())
            
            pdf.image(temp_name, x=10, y=None, w=180)
            pdf.ln(5)
            
    return bytes(pdf.output())

vsechny_checkboxy = [ch_map1, ch_tech1, ch_tech2, ch_tech3, ch_kat, ch_tech4]
vsechna_textova_pole = [jmeno, cislo_pilota, misto_letu, model_dronu, seriove_cislo_dronu, registrace_dronu]

if all(vsechny_checkboxy) and all(pole.strip() != "" for pole in vsechna_textova_pole) and screenshots:
    st.success(f"🎉 Všechny body splněny! Máte nahraných {len(screenshots)} screenshotů.")
    
    # OPRAVENO: PDF generujeme z uloženého textu v session_state
    pdf_bytes = vytvor_pdf(st.session_state['ai_final_text'])
    
    st.download_button(
        label="📄 Stáhnout kompletní PDF protokol",
        data=pdf_bytes,
        file_name=f"Protokol_letu_{local_time.strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )
else:
    st.warning("❌ Vyplňte všechna pole, nahrajte alespoň jeden screenshot, spusťte analýzu a zaškrtněte checklist.")
