import streamlit as st
import datetime
import pytz

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
    cislo_pilota = st.text_input("Číslo dálkově řídícího pilota:", placeholder="CZE-RP-...")
    misto_letu = st.text_input("Lokalita letu (město / ulice):")

with col2:
    model_dronu = st.text_input("Model dronu:", placeholder="např. DJI Mini 4 Pro")
    registrace_dronu = st.text_input("Registrační číslo provozovatele:", placeholder="CZE-...")
    kategorie_open = st.selectbox(
        "Podkategorie OPEN:",
        ["A1 (drony do 900g, např. DJI Mini)", 
         "A2 (drony do 4kg, zkouška A2)", 
         "A3 (těžší drony do 25kg, dál od lidí)"]
    )

st.markdown("---")

# --- 2. LETECKÝ ČAS (UTC) VS MÍSTNÍ ČAS ---
st.header("2. Kontrola leteckého času")
st.write("Systém DroneMap používá světový čas (UTC). Zde je váš automatický přepočet:")

cz_tz = pytz.timezone('Europe/Prague')
aktualni_local_cas = datetime.datetime.now(cz_tz)
aktualni_utc_cas = aktualni_local_cas.astimezone(pytz.utc)

time_col1, time_col2 = st.columns(2)
with time_col1:
    st.metric(label="Aktuální čas v ČR", value=aktualni_local_cas.strftime("%H:%M"))
with time_col2:
    st.metric(label="Čas pro DroneMap (UTC)", value=aktualni_utc_cas.strftime("%H:%M"))

st.markdown("---")

# --- 3. GEOGRAFICKÉ OVĚŘENÍ (DRONEMAP) ---
st.header("3. Vzdušný prostor (DroneMap)")

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
ch_map1 = st.checkbox("Potvrzuji, že jsem zkontroloval DroneMap a prostor je pro můj let VOLNÝ (případně splňuji výškové a časové limity).")

st.markdown("---")

# --- 4. TECHNICKÝ A BEZPEČNOSTNÍ CHECKLIST ---
st.header("4. Fyzická a bezpečnostní kontrola")

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

# --- 5. VYHODNOCENÍ A LETOVÝ DENÍK ---
st.header("5. Status a Letový deník")

# Kontrola, zda je vše vyplněno a zaškrtnuto
vsechny_checkboxy = [ch_map1, ch_tech1, ch_tech2, ch_tech3, ch_kat, ch_tech4]
vsechna_textova_pole = [jmeno, cislo_pilota, misto_letu, model_dronu, registrace_dronu]

if all(vsechny_checkboxy) and all(pole.strip() != "" for pole in vsechna_textova_pole) and screenshot is not None:
    st.success("🎉 Všechny body splněny! Jste připraveni k legálnímu a bezpečnému vzletu.")
    
    # Textový obsah letového deníku
    log_obsah = f"""--- PŘEDLETOVÝ PROTOKOL A LETOVÝ DENÍK ---
Datum a čas (Místní): {aktualni_local_cas.strftime('%d.%m.%Y %H:%M:%S')}
Datum a čas (UTC): {aktualni_utc_cas.strftime('%d.%m.%Y %H:%M:%S')}

ÚDAJE O PILOTOVI A DRONU:
Pilot: {jmeno}
Číslo pilota: {cislo_pilota}
Model dronu: {model_dronu}
Registrační číslo provozovatele: {registrace_dronu}
Podkategorie OPEN: {kategorie_open}
Lokalita letu: {misto_letu}

PROHLÁŠENÍ O KONTROLE:
[ANO] Vzdušný prostor ověřen v systému DroneMap a vyhodnocen jako bezpečný k letu.
[ANO] Screenshot mapy byl pilotem pořízen a nahrán během přípravy.
[ANO] Vizuální kontrola stroje a baterií proběhla bez závad.
[ANO] Pravidla bezpečné vzdálenosti od osob a budov pro danou kategorii ověřena.
[ANO] GPS lock a Return-To-Home (RTH) výška nastaveny.

STAV: SCHVÁLENO K LETU
--------------------------------------------
"""
    
    # Tlačítko pro stažení
    st.download_button(
        label="📄 Stáhnout letový deník (.txt)",
        data=log_obsah,
        file_name=f"Letovy_denik_{aktualni_local_cas.strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain"
    )
    st.info("💡 Nezapomeňte si stažený textový soubor uložit do stejné složky společně s nahraným screenshotem mapy pro kompletní archivaci.")

else:
    st.warning("❌ K dokončení přípravy a vygenerování protokolu musíte vyplnit všechna textová pole, nahrát screenshot z DroneMap a odškrtnout všechny body checklistu.")
