import streamlit as st
import pandas as pd
import io
import os
from PIL import Image, ImageOps

# ==========================================
# CONFIG STRONY
# ==========================================
st.set_page_config(page_title="Poznań Travel - Wyprawy z Krzysztofem", page_icon="🚌", layout="wide")

FOLDER_ZDJEC = "zdjecia"

# TESTOWY BANER ZMIANY WERSI
st.error("🚨 TEST WERSI 2.0 – JEŚLI TO WIDZISZ, CHMURA POBRAŁA NOWY KOD!")

def daj_sciezke(nazwa_pliku):
    if not nazwa_pliku:
        return None
    mozliwe = [
        nazwa_pliku,
        os.path.join(FOLDER_ZDJEC, nazwa_pliku),
        os.path.basename(nazwa_pliku),
        os.path.join(FOLDER_ZDJEC, os.path.basename(nazwa_pliku))
    ]
    for s in mozliwe:
        if os.path.exists(s) and os.path.isfile(s):
            return s
    return None

@st.cache_resource
def zaladuj_i_zmniejsz_zdjecie(nazwa_pliku, max_dim=800):
    sciezka = daj_sciezke(nazwa_pliku)
    if sciezka and os.path.exists(sciezka):
        try:
            img = Image.open(sciezka)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
            return img
        except Exception:
            return None
    return None

def pokaz_zdjecie_szybko(zrodlo):
    if not zrodlo:
        st.image("https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=700", use_container_width=True)
        return
        
    if isinstance(zrodlo, str) and zrodlo.startswith("http"):
        st.image(zrodlo, use_container_width=True)
    else:
        img_pil = zaladuj_i_zmniejsz_zdjecie(zrodlo)
        if img_pil is not None:
            st.image(img_pil, use_container_width=True)
        else:
            st.image("https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=700", use_container_width=True)

# STYLIZACJA CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .top-contact-bar {
        background-color: #0f172a; color: #f8fafc; padding: 10px 20px;
        border-radius: 10px; display: flex; justify-content: space-between;
        align-items: center; font-size: 0.95rem; margin-bottom: 25px;
    }
    .poz_header { text-align: center; margin-bottom: 15px; }
    .poz_title { color: #1e3a8a; font-size: 3rem; font-weight: 800; margin: 0; }
    .poz_subtitle { color: #475569; font-size: 1.15rem; margin-top: 5px; }
    .wycieczka-card {
        background: #ffffff; border-radius: 16px; padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05); margin-bottom: 30px; border: 1px solid #cbd5e1;
    }
    .wycieczka-title { color: #0f172a; font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; }
    .bio-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); color: white;
        border-radius: 16px; padding: 30px; margin-bottom: 30px;
    }
    .stack-card { background: #ffffff; border-radius: 16px; padding: 18px; border: 1px solid #cbd5e1; }
    .stack-title { font-weight: 800; font-size: 1.2rem; color: #0f172a; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-contact-bar">
    <div>📍 Zbiórki z Poznania (Dworzec Letni / MTP)</div>
    <div>💬 Napisz bezpośrednio do Krzyśka: <b>kontakt@poznantravel.pl</b> | 📞 <b>+48 600 100 200</b></div>
</div>
""", unsafe_allow_html=True)

if "krok" not in st.session_state: st.session_state.krok = 1
if "wybrana_wycieczka" not in st.session_state: st.session_state.wybrana_wycieczka = None
if "wybrane_miejsca" not in st.session_state: st.session_state.wybrane_miejsca = []
if "zajete_miejsca" not in st.session_state: st.session_state.zajete_miejsca = [2, 5, 6, 12]

if "i_city" not in st.session_state: st.session_state.i_city = 0
if "i_egzotyka" not in st.session_state: st.session_state.i_egzotyka = 0
if "i_natura" not in st.session_state: st.session_state.i_natura = 0

dane_raw = """Id,Nazwa,Kategoria,Dni,CenaOsoba,Termin,Zbiorka,LimitOsob,Zdjecie,Opis,Program
1,Jarmark Bożonarodzeniowy w Dreznie,Jednodniowe,1,260,Grudzień 2026,Poznań Dworzec Letni (05:30),20,https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=700,Najstarsi producenci piernika i słynny Striezelmarkt! Klimatyczny wyjazd małym komfortowym busem.,📌 05:30 – Zbiórka Poznań Dworzec Letni|📌 10:30 – Zwiedzanie Drezna z przewodnikiem|📍 Pałac Zwinger Frauenkirche Opera Sempera|📌 13:30 – Czas wolny na Striezelmarkt|📌 18:30 – Wyjazd w drogę powrotną|📌 23:00 – Powrót do Poznania
2,Weekend w Berlinie i Poczdamie,Weekendowe,2,690,Maj 2026,Poznań MTP (06:30),20,https://images.unsplash.com/photo-1560969184-10fe8719e047?w=700,Odkryj pałace Sanssouci oraz tętniący życiem Berlin. Nocleg ze śniadaniem w hotelu 3★.,📌 DZIEŃ 1: Wyjazd z Poznania 06:30 ➔ Poczdam Ogrody Sanssouci ➔ Nocleg w Berlinie|📌 DZIEŃ 2: Śniadanie ➔ Brama Brandenburska Reichstag ➔ Rejs statkiem po Szprewie ➔ Powrót 21:00
3,Górski Reset: Karpacz i Karkonosze,Wyprawy Górskie,4,1150,Czerwiec 2026,Poznań Dworzec Letni (07:00),18,https://images.unsplash.com/photo-1519681393784-d120267933ba?w=700,Kameralny wyjazd w Góry. Zdobywamy Śnieżkę wchodzimy do Świątyni Wang i odpoczywamy.,📌 DZIEŃ 1: Wyjazd 07:00 ➔ Karpacz ➔ Świątynia Wang|📌 DZIEŃ 2: Śnieżka przez Samotnię|📌 DZIEŃ 3: Szklarska Poręba i Wodospad|📌 DZIEŃ 4: Termy Cieplickie i powrót
4,Magiczny Jarmark we Wrocławiu,Jednodniowe,1,180,Grudzień 2026,Poznań Dworzec Letni (07:30),20,https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=700,Najpiękniejszy jarmark w Polsce! Bajkowy klimat Wrocławskiego Rynku bez martwienia się o auto.,📌 07:30 – Wyjazd z Poznania|📌 10:00 – Spacer z przewodnikiem po Ostrowie Tumskim|📌 13:00 – Czas wolny na jarmarku|📌 19:00 – Wyjazd z Wrocławia | 21:30 Powrót
5,Urokliwy Szprewald – Niemiecka Wenecja,Jednodniowe,1,290,Lipiec 2026,Poznań Dworzec Letni (06:30),20,https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=700,Tradycyjny rejs łodziami pychówkami po malowniczych kanałach wodnych z degustacją ogórków.,📌 06:30 – Wyjazd z Poznania|📌 10:00 – 3-godzinny rejs płaskodennymi łodziami|📍 Czas wolny w wiosce Lübbenau|📌 17:30 – Wyjazd do Polski | 21:00 Powrót
6,Wiedeń i Budapeszt – Perły Dunaju,Egzotyka i Objazdówki,4,1490,Majówka 2026,Poznań MTP (05:00),18,https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=700,Intensywna objazdówka małą grupą! Pałac Schönbrunn w Wiedniu i nocny rejs w Budapeszcie.,📌 DZIEŃ 1: Przejazd do Wiednia|📌 DZIEŃ 2: Zwiedzanie Wiednia i przejazd do Budapesztu|📌 DZIEŃ 3: Budapeszt i wieczorny rejs statkiem|📌 DZIEŃ 4: Powrót do Poznania
"""

@st.cache_data
def laduj_dane():
    return pd.read_csv(io.StringIO(dane_raw))

df_wycieczki = laduj_dane()

st.markdown("<div class='poz_header'><div class='poz_title'>🚌 Poznań Travel</div><div class='poz_subtitle'>Autorskie Mikrowyprawy z Poznania | Twój Organizator: Krzysiek</div></div>", unsafe_allow_html=True)
st.write("---")

st.sidebar.title("🔍 Nawigacja")
tryb_aplikacji = st.sidebar.radio("Wybierz sekcję:", ["Katalog Wycieczek", "🙋‍♂️ O Krzyśku & Galeria Podróży", "📊 Panel Finansowy"])

if tryb_aplikacji == "Katalog Wycieczek":
    st.sidebar.header("🎯 Filtruj Wyjazdy")
    kat_filter = st.sidebar.selectbox("Kategoria:", ["Wszystkie", "Jednodniowe", "Weekendowe", "Wyprawy Górskie", "Egzotyka i Objazdówki"])
    max_cena = st.sidebar.slider("Maksymalna cena (PLN):", 150, 1600, 1600, step=50)

    dane_f = df_wycieczki[df_wycieczki["CenaOsoba"] <= max_cena]
    if kat_filter != "Wszystkie":
        dane_f = dane_f[dane_f["Kategoria"] == kat_filter]

    st.subheader(f"Dostępne Mikrowyprawy ({len(dane_f)}):")
    for idx, row in dane_f.iterrows():
        st.markdown(f"<div class='wycieczka-card'>", unsafe_allow_html=True)
        c_img, c_info, c_action = st.columns([2.5, 3.5, 2])
        with c_img:
            pokaz_zdjecie_szybko(row["Zdjecie"])
        with c_info:
            st.markdown(f"<div class='wycieczka-title'>{row['Nazwa']}</div>", unsafe_allow_html=True)
            st.caption(f"📅 **Termin:** {row['Termin']} | ⏱️ **Czas:** {row['Dni']} dni")
            st.write(row['Opis'])
            st.write(f"📍 **Zbiórka:** {row['Zbiorka']}")
        with c_action:
            st.metric(label="Cena / osobę", value=f"{row['CenaOsoba']} PLN")
        st.markdown("</div>", unsafe_allow_html=True)

elif tryb_aplikacji == "🙋‍♂️ O Krzyśku & Galeria Podróży":
    st.markdown("<div class='bio-card'><h2>Siema, tu Krzysiek! 🌍</h2></div>", unsafe_allow_html=True)
    pokaz_zdjecie_szybko("krzysiek_profil.jpg")

else:
    st.title("📊 Panel Finansowy Organizatora")