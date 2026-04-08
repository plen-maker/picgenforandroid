import streamlit as st
import requests
import io
from PIL import Image

# --- BIZTONSAGI BEALLITASOK ---
try:
    # A kulcsokat a Streamlit Secrets-bol olvassuk ki
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_USER = st.secrets["APP_USER"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("HIBA: Hianyoznak az adatok a Secrets-bol! Ellenorizd a HF_TOKEN, APP_USER es APP_PASSWORD mezoket.")
    st.stop()

# Konfiguracio
HF_API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
hf_headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="AI Kep Pro", layout="centered")

# --- LOGIN RENDSZER ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Bejelentkezes")
    user_input = st.text_input("Felhasznalonev")
    pwd_input = st.text_input("Jelszo", type="password")
    
    if st.button("BELEPES"):
        if user_input == APP_USER and pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas adatok!")
    st.stop()

# --- FO TARTALOM ---
st.title("AI Kep Kozpont")

if st.sidebar.button("Kijelentkezes"):
    st.session_state['logged_in'] = False
    st.rerun()

st.header("Flux Kepgenerator")
draw_prompt = st.text_area("Mit rajzoljak? (Angolul)", placeholder="Pelda: Portrait of Viktor Orban with a hat...")

if st.button("RAJZOLJ"):
    if draw_prompt:
        with st.spinner("Alkotas..."):
            try:
                response = requests.post(HF_API_URL, headers=hf_headers, json={"inputs": draw_prompt})
                if response.status_code == 200:
                    image_bytes = io.BytesIO(response.content)
                    generated_img = Image.open(image_bytes)
                    st.image(generated_img, use_container_width=True)
                    
                    buf = io.BytesIO()
                    generated_img.save(buf, format="PNG")
                    st.download_button("Kep mentese", buf.getvalue(), "ai_kep.png", "image/png")
                else:
                    st.error(f"API Hiba: {response.status_code}. Ellenorizd a HF tokent!")
            except Exception as e:
                st.error(f"Hiba: {e}")
    else:
        st.warning("Irjal be egy leirast!")
