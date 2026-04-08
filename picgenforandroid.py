import streamlit as st
import requests
import io
from PIL import Image

# --- BIZTONSAGI BEALLITASOK ---
# A kulcsokat a Streamlit Secrets-bol olvassuk ki
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("HIBA: Hianyoznak az API kulcsok a Secrets-bol!")
    st.stop()

# Konfiguracio
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"}

# Oldal beallitasa (mobil-barat)
st.set_page_config(page_title="AI Kep Pro", layout="centered")

# --- 1. LOGIN RENDSZER ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Bejelentkezes")
    st.write("A baratod appja. Kerlek, add meg a jelszot!")
    pwd_input = st.text_input("Jelszo", type="password")
    
    if st.button("BELEPES"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- 2. FO TARTALOM (Csak Kepgenerator) ---
st.title("🤖 AI Kep Pro Kozpont")

# Kijelentkezes gomb az oldalsavban
if st.sidebar.button("Kijelentkezes"):
    st.session_state['logged_in'] = False
    st.rerun()

st.header("Flux Kepgenerator")
st.write("Ird le a kepet angolul a legjobb eredmenyert. Pelda: 'A photorealistic portrait of an old man, 8k'.")

# Szoveg bevitel a kep leirasahoz
draw_prompt = st.text_area("Mit rajzoljak?", placeholder="Pelda: Realistic photo of Viktor Orban with a hat...")

if st.button("RAJZOLJ"):
    if draw_prompt:
        with st.spinner("Alkotas folyamatban... Ez 10-20 masodpercig tarthat."):
            try:
                # Keres kuldese a Hugging Face API-nak
                response = requests.post(HF_API_URL, headers=hf_headers, json={"inputs": draw_prompt})
                
                if response.status_code == 200:
                    image_bytes = BytesIO(response.content)
                    generated_img = Image.open(image_bytes)
                    
                    # Kep megjelenitese
                    st.image(generated_img, caption=f"Generalt kep: {draw_prompt}", use_container_width=True)
                    
                    # Letoltes gomb
                    buf = io.BytesIO()
                    generated_img.save(buf, format="PNG")
                    st.download_button("📥 KEP MENTESE", buf.getvalue(), "ai_kep.png", "image/png")
                else:
                    st.error(f"Hiba a generalasnal (Kod: {response.status_code}). Probald ujra!")
                    
            except Exception as e:
                st.error(f"Váratlan hiba: {e}")
    else:
        st.warning("Kerlek, irjal be egy temat!")
