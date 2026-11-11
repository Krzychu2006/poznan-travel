import streamlit as st
import pandas as pd
import io
import os
import glob
from PIL import Image, ImageOps

# ==========================================
# CONFIG STRONY
# ==========================================
st.set_page_config(page_title="Poznań Travel - Wyprawy z Krzysztofem", page_icon="🚌", layout="wide")

FOLDER_ZDJEC = "zdjecia"

def daj_sciezke(nazwa_pliku):
    """Szuka pliku w root, subfolderze zdjecia/ oraz w dopasowaniach bez względu na wielkość liter."""
    if not nazwa_pliku:
        return None
    
    # 1. Sprawdź dokładną ścieżkę
    mozliwe_sciezki = [
        nazwa_pliku,
        os.path.join(FOLDER_ZDJEC, nazwa_pliku),
        os.path.basename(nazwa_pliku),
        os.path.join(FOLDER_ZDJEC, os.path.basename(nazwa_pliku))
    ]
    
    for s in mozliwe_sciezki:
        if os.path.exists(s) and os.path.isfile(s):
            return s
            
    # 2. Szukanie odporne na wielkość liter / rozszerzenia (.JPG vs .jpeg)
    czysta_nazwa = os.path.basename(nazwa_pliku).lower()
    szukaj_w = [".", FOLDER_ZDJEC] if os.path.exists(FOLDER_ZDJEC) else ["."]
    
    for kat in szukaj_w:
        for root, _, files in os.walk(kat):
            for f in files:
                if f.lower() == czysta_nazwa:
                    return os.path.join(root, f)
                    
    return None

# ==========================================
# CACHE & ULTRASZYBKI DOWNSCALING
# ==========================================
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
            # Fallback bez MediaFileStorageError
            st.image("https://images.unsplash.com/photo-1543589077-47d81606c1bf?w=700", use_container_width=True)

# ==========================================
# STYLIZACJA CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .top-contact-bar {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 10px 20px;
        border-radius: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
    .poz_header {
        text-align: center;
        margin-bottom: 15px;
    }
    .poz_title {
        color: #1e3a8a;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
        margin: 0;
    }
    .poz_subtitle {
        color: #475569;
        font-size: 1.15rem;
        margin-top: 5px;
    }
    .wycieczka-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
        border: 1px solid #cbd5e1;
    }
    .wycieczka-title {
        color: #0f172a;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .bio-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.3);
    }
    .bus-container {
        background-color: #ffffff;
        border: 2px solid #2563eb;
        border-radius: 16px;
        padding: 18px;
        max-width: 360px;
        margin: 0 auto 20px auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .bus-driver {
        text-align: right;
        font-weight: 700;
        color: #64748b;
        border-bottom: 2px dashed #e2e8f0;
        padding-bottom: 8px;
        margin-bottom: 15px;
    }
    .stack-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 18px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }
    .stack-title {
        font-weight: 800;
        font-size: 1.2rem;
        color: #0f172a;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# BELKA KONTAKTOWA
st.markdown("""
<div class="top-contact-bar">
    <div>📍 Zbiórki z Poznania (Dworzec Letni / MTP)</div>
    <div>💬 Napisz bezpośrednio do Krzyśka: <b>kontakt@poznantravel.pl</b> | 📞 <b>+48 600 100 200</b></div>
</div>
""", unsafe_allow_html=True)

# SESSION STATE
if "krok" not in st.session_state: st.session_state.krok = 1
if "wybrana_wycieczka" not in st.session_state: st.session_state.wybrana_wycieczka = None
if "wybrane_miejsca" not in st.session_state: st.session_state.wybrane_miejsca = []
if "zajete_miejsca" not in st.session_state: st.session_state.zajete_miejsca = [2, 5, 6, 12]

if "i_city" not in st.session_state: st.session_state.i_city = 0
if "i_egzotyka" not in st.session_state: st.session_state.i_egzotyka = 0
if "i_natura" not in st.session_state: st.session_state.i_natura = 0

# BAZA TRAS Z LINKAMI WEB DLA JEDNOLITOŚCI KATALOGU
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

# HEADER
st.markdown("<div class='poz_header'><div class='poz_title'>🚌 Poznań Travel</div><div class='poz_subtitle'>Autorskie Mikrowyprawy z Poznania | Twój Organizator: Krzysiek</div></div>", unsafe_allow_html=True)
st.write("---")

# NAWIGACJA
st.sidebar.title("🔍 Nawigacja")
tryb_aplikacji = st.sidebar.radio("Wybierz sekcję:", ["Katalog Wycieczek", "🙋‍♂️ O Krzyśku & Galeria Podróży", "📊 Panel Finansowy"])

if tryb_aplikacji == "Katalog Wycieczek":
    if st.session_state.krok == 2:
        w = st.session_state.wybrana_wycieczka
        st.button("⬅️ Wróć do pełnej listy wycieczek", key="back_top", use_container_width=True, on_click=lambda: st.session_state.update({"krok": 1, "wybrane_miejsca": []}))
        st.write("---")
        
        col_info, col_booking = st.columns([1.1, 1])
        with col_info:
            pokaz_zdjecie_szybko(w["Zdjecie"])
            st.title(w["Nazwa"])
            st.write(f"📅 **Termin:** {w['Termin']} | ⏱️ **Czas:** {w['Dni']} dni")
            st.write(f"📍 **Zbiórka:** {w['Zbiorka']}")
            st.markdown(f"**Opis trasy:** {w['Opis']}")
            
            st.markdown("### 🗺️ Ramowy Plan Wyjazdu")
            program_punkty = w["Program"].split("|")
            for p in program_punkty:
                st.markdown(f"* {p.strip()}")

        with col_booking:
            st.subheader("💺 Wybierz Miejsca w Busie")
            st.caption("Zaznacz wolne fotele na schemacie:")
            st.markdown("<div class='bus-container'><div class='bus-driver'>🚘 Kierowca / Pilot Krzysztof</div></div>", unsafe_allow_html=True)
            
            miejsca_cols = st.columns(4)
            wybrane = st.session_state.wybrane_miejsca

            for seat_num in range(1, 21):
                col_idx = (seat_num - 1) % 4
                with miejsca_cols[col_idx]:
                    if seat_num in st.session_state.zajete_miejsca:
                        st.button(f"❌ {seat_num}", key=f"seat_{seat_num}", disabled=True)
                    elif seat_num in wybrane:
                        if st.button(f"✅ {seat_num}", key=f"seat_{seat_num}", type="primary"):
                            st.session_state.wybrane_miejsca.remove(seat_num)
                            st.rerun()
                    else:
                        if st.button(f"💺 {seat_num}", key=f"seat_{seat_num}"):
                            st.session_state.wybrane_miejsca.append(seat_num)
                            st.rerun()

            st.write("---")
            if not st.session_state.wybrane_miejsca:
                st.warning("⚠️ Wybierz co najmniej jedno miejsce na schemacie powyżej.")
            else:
                ilosc = len(st.session_state.wybrane_miejsca)
                miejsca_str = ", ".join([f"nr {m}" for m in sorted(st.session_state.wybrane_miejsca)])
                cena_laczna = w['CenaOsoba'] * ilosc
                zaliczka = int(cena_laczna * 0.3)
                
                st.success(f"Rezerwujesz **{ilosc} os.** (Fotele: **{miejsca_str}**)")
                st.subheader("📋 Dane Rezerwującego")
                imie = st.text_input("Imię i Nazwisko:", value="Jan Kowalski")
                telefon = st.text_input("Numer telefonu:", value="+48 600 100 200")
                email = st.text_input("Adres e-mail:", value="jan.kowalski@gmail.com")
                
                c_a, c_b = st.columns(2)
                c_a.metric("Suma całkowita:", f"{cena_laczna} PLN")
                c_b.metric("Zaliczka (30%):", f"{zaliczka} PLN")
                
                metoda = st.radio("Metoda płatności zaliczki:", ["⚡ BLIK", "💳 Karta Płatnicza", "🅿️ PayPal / Google Pay", "🏦 Szybki Przelew"])
                
                if st.button("🔴 OPŁAĆ ZALICZKĘ I REZERWUJ", type="primary", use_container_width=True):
                    st.session_state.zajete_miejsca.extend(st.session_state.wybrane_miejsca)
                    st.session_state.dane_rezerwacji = {"imie": imie, "miejsca": sorted(st.session_state.wybrane_miejsca), "ilosc": ilosc, "suma": cena_laczna, "zaliczka": zaliczka, "metoda": metoda}
                    st.session_state.krok = 3
                    st.rerun()

    elif st.session_state.krok == 3:
        w = st.session_state.wybrana_wycieczka
        r = st.session_state.dane_rezerwacji
        miejsca_txt = ", ".join([f"nr {m}" for m in r['miejsca']])
        
        st.balloons()
        st.title("🎉 Miejsca Zostały Zarezerwowane!")
        st.success(f"Dziękujemy **{r['imie']}**! Fotele **{miejsca_txt}** na wyjazd **{w['Nazwa']}** zostały zablokowane.")
        st.divider()
        if st.button("🔄 Wróć do oferty wycieczek", use_container_width=True):
            st.session_state.wybrane_miejsca = []
            st.session_state.krok = 1
            st.rerun()

    else:
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
                with st.expander("🔍 Zobacz szczegółowy program wycieczki"):
                    for p in row["Program"].split("|"):
                        st.write(f"• {p.strip()}")
            with c_action:
                st.metric(label="Cena / osobę", value=f"{row['CenaOsoba']} PLN")
                if st.button("Wybierz Miejsca w Busie ➔", key=f"btn_{row['Id']}", type="primary", use_container_width=True):
                    st.session_state.wybrana_wycieczka = row.to_dict()
                    st.session_state.wybrane_miejsca = []
                    st.session_state.krok = 2
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# WIDOK: O KRZYSZTOFIE & OSOBISTE KADRY
# ==========================================
elif tryb_aplikacji == "🙋‍♂️ O Krzyśku & Galeria Podróży":
    st.markdown("""
    <div class='bio-card'>
        <h2>Siema, tu Krzysiek! 🌍</h2>
        <p>Mam 20 lat, mieszkam w Poznaniu i podróżuję nieprzerwanie od 16. roku życia. Przejechałem i przetestowałem na własnej skórze ponad 20 państw — od zamku w Trakach na Litwie, przez Pizę, mecz na Camp Nou w Barcelonie, Paryż, Londyn, Toskanię, Gibraltar, aż po egzotykę w Tunezji czy Fuerteventurę.</p>
        <p><b>Nie jestem bezdusznym biurem podróży.</b> Tworzę wyjazdy w relacji czystej i przyjacielskiej. Masz ekipę, chcesz gdzieś wyskoczyć albo masz własny pomysł na trasę z Poznania? Pisz śmiało!</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2])
    with c1:
        pokaz_zdjecie_szybko("krzysiek_profil.jpg")
            
    with c2:
        st.subheader("💡 Masz własny pomysł na wycieczkę z Poznania?")
        st.write("Chcesz skompletować własną paczkę 15-20 osób i pojechać w konkretne miejsce? Napisz do mnie!")
        with st.form("kontakt_krzysiek"):
            twoje_imie = st.text_input("Twoje Imię / Nick:")
            twoj_kontakt = st.text_input("Numer telefonu lub Instagram / e-mail:")
            pomysl = st.text_area("Gdzie chcesz pojechać?:", placeholder="Ej Krzysiek, ogarniamy wyjazd na mecz / w góry / na weekend do Czech?")
            if st.form_submit_button("📩 Wyślij wiadomość bezpośrednio do Krzyśka", type="primary"):
                st.success("Dzięki za wiadomość! Odezwę się do Ciebie najszybciej jak to możliwe 🚀")

    st.write("---")
    st.subheader("📸 Osobiste Kadry Krzysztofa z Podróży")

    z_city = [
        {"plik": "IMG_3676.jpeg", "nazwa": "Big Ben, Londyn", "opis": "Klimat brytyjskiej stolicy i deszczowy spacer nad Tamizą."},
        {"plik": "IMG_7032.jpeg", "nazwa": "Wieża Eiffla, Paryż", "opis": "Klasyczny punkt każdej wyprawy po Francji."},
        {"plik": "IMG_4050.jpeg", "nazwa": "Brama Brandenburska", "opis": "Weekendowy wypad do Berlina z ekipą."},
        {"plik": "IMG_3775.jpeg", "nazwa": "Zamek w Trakach", "opis": "Malowniczy zamek na wyspie na Litwie."},
        {"plik": "IMG_2590.jpeg", "nazwa": "Uliczki Europy", "opis": "Odkrywanie mniej znanych zakątków miast."}
    ]
    
    z_egzotyka = [
        {"plik": "IMG-5557.jpeg", "nazwa": "Wyspy Kanaryjskie", "opis": "Ocean i wulkaniczne krajobrazy Fuerteventury."},
        {"plik": "IMG_7044.jpeg", "nazwa": "Pustynia & Wielbłądy", "opis": "Egzotyczny wyjazd na Południe i tunezyjski piasek."},
        {"plik": "IMG_5712.JPG", "nazwa": "Spotkanie z Lemurem", "opis": "Bliski kontakt z naturą podczas podróży."},
        {"plik": "IMG_2042.jpeg", "nazwa": "Skała Gibraltaru", "opis": "Słynne małpki w miejscu spotkania Europy i Afryki."}
    ]
    
    z_natura = [
        {"plik": "IMG_4698.JPG", "nazwa": "Polskie Góry", "opis": "Górski reset z dziewczyną na szlaku."},
        {"plik": "IMG_1070.jpeg", "nazwa": "Klify i Ocean", "opis": "Szum fal i potęga natury na wybrzeżu."},
        {"plik": "IMG_4105.jpeg", "nazwa": "Górskie Jeziora", "opis": "Przejrzysta woda i spokój z dala od cywilizacji."},
        {"plik": "IMG_6395.jpeg", "nazwa": "Kanały i Zieleń", "opis": "Klimat rejsu łodziami po Szprewaldzie."}
    ]

    def pokaz_kategorie_z_opisem(tytul, lista_obiektow, state_key):
        st.markdown(f"<div class='stack-card'><div class='stack-title'>{tytul}</div>", unsafe_allow_html=True)
        if not lista_obiektow:
            st.info("Brak zdjęć w kategorii.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        col_main, col_thumbs = st.columns([1.6, 1])
        curr_i = st.session_state[state_key] % len(lista_obiektow)
        wybrany_kadr = lista_obiektow[curr_i]
            
        with col_main:
            pokaz_zdjecie_szybko(wybrany_kadr["plik"])
            st.caption(f"📍 **{wybrany_kadr['nazwa']}** — {wybrany_kadr['opis']}")
            
        with col_thumbs:
            st.caption("Kliknij miejsce:")
            for i, item in enumerate(lista_obiektow):
                if st.button(f"📌 {item['nazwa']}", key=f"btn_{state_key}_{i}", use_container_width=True):
                    st.session_state[state_key] = i
                    st.rerun()
                    
        st.markdown("</div>", unsafe_allow_html=True)

    col_k1, col_k2, col_k3 = st.columns(3)
    
    with col_k1:
        pokaz_kategorie_z_opisem("🏙️ City Break", z_city, "i_city")
    with col_k2:
        pokaz_kategorie_z_opisem("🌴 Egzotyka", z_egzotyka, "i_egzotyka")
    with col_k3:
        pokaz_kategorie_z_opisem("⛰️ Natura", z_natura, "i_natura")

# ==========================================
# PANEL FINANSOWY ORGANIZATORA
# ==========================================
else:
    st.title("📊 Panel Finansowy Organizatora")
    st.write("Narzędzie kalkulacji dochodu z wyjazdów.")