# -*- coding: utf-8 -*-
import streamlit as st
import requests
import google.generativeai as genai
from io import BytesIO
from PIL import Image
import time

# --- BIZTONSÁGI BEÁLLÍTÁSOK ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    st.error("Hiba: Hianyoznak a kulcsok a Secrets-bol!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Modell eleresi utak
MODEL_FLUX = "black-forest-labs/FLUX.1-schnell"
MODEL_SDXL = "stabilityai/stable-diffusion-xl-base-1.0"

st.set_page_config(page_title="AI Pro Mobil", page_icon="🤖")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Bejelentkezés")
    pwd = st.text_input("Jelszó", type="password")
    if st.button("Belépés"):
        if pwd == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibás jelszó!")
    st.stop()

# --- APP TARTALOM ---
st.title("🤖 AI Pro Mobil")

tab1, tab2 = st.tabs(["💬 Chat és Látás", "🎨 Képgenerátor"])

# --- TAB 1: GEMINI ---
with tab1:
    st.header("Gemini 1.5 Flash")
    vision_img = st.file_uploader("Kép feltöltése elemzéshez", type=['jpg', 'png', 'jpeg'])
    chat_prompt = st.text_area("Kérdésed az AI-hoz:")
    
    if st.button("KÜLDÉS 🚀"):
        if chat_prompt:
            with st.spinner("Gondolkodom..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    if vision_img:
                        img = Image.open(vision_img)
                        res = model.generate_content([chat_prompt, img])
                    else:
                        res = model.generate_content(chat_prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Hiba történt: {e}")

# --- TAB 2: KÉPGENERÁTOR ---
with tab2:
    st.header("AI Képalkotó")
    prompt = st.text_input("Mit rajzoljak? (Angolul írd!)")
    
    if st.button("RAJZOLÁS 🎨"):
        if prompt:
            with st.spinner("Kép készítése folyamatban..."):
                def fetch_image(m_id):
                    url = f"https://api-inference.huggingface.co/models/{m_id}"
                    h = {"Authorization": f"Bearer {HF_TOKEN}"}
                    return requests.post(url, headers=h, json={"inputs": prompt}, timeout=30)

                # Próba a FLUX-al
                res = fetch_image(MODEL_FLUX)
                
                # Ha nem elérhető, próbáljuk az SDXL-t
                if res.status_code in [410, 404, 500]:
                    st.info("Modell váltás (tartalék rendszer)...")
                    res = fetch_image(MODEL_SDXL)

                if res.status_code == 200:
                    image = Image.open(BytesIO(res.content))
                    st.image(image, use_container_width=True)
                    
                    # Mentés
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("Kép mentése", buf.getvalue(), "ai_kep.png", "image/png")
                elif res.status_code == 503:
                    st.warning("A szerver ébredezik, várj 15 másodpercet!")
                else:
                    st.error(f"Hiba kód: {res.status_code}")
                    st.write("Próbáld meg egyszerűbb kulcsszavakkal!")
