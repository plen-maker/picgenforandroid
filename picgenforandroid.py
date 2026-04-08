# -*- coding: utf-8 -*-
import streamlit as st
import requests
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# --- BIZTONSÁGI BEÁLLÍTÁSOK ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    st.error("Hiba: Hianyoznak a kulcsok a Streamlit Secrets-bol!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# Modell eleresi utak
MODEL_FLUX = "black-forest-labs/FLUX.1-schnell"
MODEL_SDXL = "stabilityai/stable-diffusion-xl-base-1.0"

st.set_page_config(page_title="AI Mobil Asszisztens", page_icon="🤖")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Bejelentkezes")
    pwd = st.text_input("Jelszo", type="password")
    if st.button("Belepes"):
        if pwd == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- APP TARTALOM ---
st.title("🤖 AI Pro Mobil")

# Csak ketto ful maradt
tab1, tab2 = st.tabs(["💬 Chat & Latas", "🎨 Kepgenerator"])

# --- TAB 1: GEMINI (Okos Chat és Képfelismerés) ---
with tab1:
    st.header("Gemini 1.5 Flash")
    st.write("Tolts fel kepet a konyvrol, vagy csak kerdezz!")
    
    vision_img = st.file_uploader("Kep feltoltese", type=['jpg', 'png', 'jpeg'])
    chat_prompt = st.text_area("Kerdesed:")
    
    if st.button("KULDÉS 🚀"):
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
                    st.error(f"Hiba: {e}")

# --- TAB 2: KEPGENERATOR (FLUX & SDXL) ---
with tab2:
    st.header("AI Kepalkoto")
    prompt = st.text_input("Mit rajzoljak? (Angolul)")
    
    if st.button("RAJZOLAS 🎨"):
        if prompt:
            with st.spinner("Alkotas folyamatban..."):
                def fetch_image(m_id):
                    url = f"https://api-inference.huggingface.co/models/{m_id}"
                    h = {"Authorization": f"Bearer {HF_TOKEN}"}
                    return requests.post(url, headers=h, json={"inputs": prompt}, timeout=30)

                # Elso proba: FLUX
                res = fetch_image(MODEL_FLUX)
                
                # Ha 410 vagy hiba, jöhet a tartalék SDXL
                if res.status_code in [410, 404, 500]:
                    st.info("Tartalek modellre valtas...")
                    res = fetch_image(MODEL_SDXL)

                if res.status_code == 200:
                    image = Image.open(BytesIO(res.content))
                    st.image(image, use_container_width=True)
                    
                    # Mentes gomb
                    buf = BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("Kep mentese", buf.getvalue(), "generalt_kep.png", "image/png")
                elif res.status_code == 503:
                    st.warning("A szerver melegszik, varj 15 masodpercet es nyomd meg ujra!")
                else:
                    st.error(f"Hiba kod: {res.status_code}. Probald mas szavakkal!")
