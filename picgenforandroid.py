# -*- coding: utf-8 -*-
import streamlit as st
import replicate
from PIL import Image
import requests
from io import BytesIO
import time

# --- BIZTONSÁGI BEÁLLÍTÁSOK (Secrets-ből) ---
try:
    # Kell egy Replicate API token (Settings -> API Tokens)
    REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
    # A te Hugging Face kulcsod (hátha kell tartaléknak)
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except KeyError:
    st.error("HIBA: Hianyoznak az API kulcsok a Streamlit Secrets-bol! (REPLICATE_API_TOKEN, HF_TOKEN, APP_PASSWORD)")
    st.stop()

# Replicate token konfigurálása
import os
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# Oldal konfiguráció (telefon-barát)
st.set_page_config(page_title="Profi Képalkotó", page_icon="🎨", layout="centered")

# --- 1. LOGIN RENDSZER ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Bejelentkezés")
    st.write("A barátod appja. Kérlek, add meg a jelszót!")
    pwd_input = st.text_input("Jelszó", type="password")
    
    if st.button("BELÉPÉS 🚀", type="primary"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibás jelszó! Próbáld újra.")
    st.stop()

# --- 2. AZ APP FŐ TARTALMA (Ha be van jelentkezve) ---
st.title("🎨 Profi Képalkotó Központ")

# Kijelentkezés gomb az oldalsávban
st.sidebar.title("Menü")
if st.sidebar.button("Kijelentkezés 🚪"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- FÜLEK (Tabs) a telefon-barát navigációhoz ---
tab1, tab2 = st.tabs(["🆕 Új Kép Létrehozása", "✏️ Kép Módosítása (Inpainting)"])

# --- TAB 1: ÚJ KÉP LÉTREHOZÁSA (PROFI MODELLEKKEL) ---
with tab1:
    st.header("Új Kép Generálása")
    st.write("Írd le angolul, mit szeretnél látni!")

    draw_prompt = st.text_area("Mit rajzoljak?", placeholder="pl. A realistic portrait of Viktor Orban wearing a traditional Hungarian fedora, 8k, cinematic lighting")
    
    # Modell választó
    model_choice = st.selectbox("Válassz modellt:", ["Stable Diffusion XL (Gyors, stabil)", "FLUX.1-schnell (Élethűbb arcok, de lassabb)"])
    
    if st.button("GENERÁLÁS ✨", type="primary", key="tab1_btn"):
        if draw_prompt:
            with st.spinner("AI alkotás... Ez 10-30 másodpercig tarthat."):
                try:
                    # Kérés küldése a Replicate API-nak
                    if "Stable Diffusion XL" in model_choice:
                        model_version = "stabilityai/sdxl:39ed46968c93390291244e497fd33360b0e5ee2460673369f0672b2dd2718121"
                    else:
                        model_version = "black-forest-labs/flux-schnell"

                    output = replicate.run(model_version, input={"prompt": draw_prompt})
                    
                    # Megjelenítés
                    st.image(output[0], caption=f"Generált kép: {draw_prompt}", use_container_width=True)
                    
                    # Letöltés gomb
                    res = requests.get(output[0])
                    st.download_button("📥 KÉP MENTÉSE", res.content, f"ai_kep_{int(time.time())}.png", "image/png")
                
                except Exception as e:
                    st.error(f"Váratlan hiba: {e}")
        else:
            st.warning("Kérlek, írj le egy témát!")

# --- TAB 2: KÉP MÓDOSÍTÁSA (INPAINTING / EDITING) ---
with tab2:
    st.header("Kép Módosítása")
    st.write("Tölts fel egy képet, és az AI megváltoztatja!")

    # Kép feltöltő
    edit_img = st.file_uploader("Kép feltöltése", type=['jpg', 'jpeg', 'png'])
    
    if edit_img:
        st.image(edit_img, caption="Eredeti kép", use_container_width=True)
        
        # Módosító szöveg
        edit_prompt = st.text_area("Mit változtassak?", placeholder="pl. Add a stylish fedora hat to his head, keep the face the same")
        
        if st.button("MÓDOSÍTÁS 🔧", type="primary", key="tab2_btn"):
            if edit_prompt:
                with st.spinner("AI átalakítás... Ez lassabb lehet."):
                    try:
                        # SDXL Inpainting modell használata
                        output = replicate.run(
                            "stabilityai/sdxl:39ed46968c93390291244e497fd33360b0e5ee2460673369f0672b2dd2718121",
                            input={
                                "image": edit_img,
                                "prompt": edit_prompt,
                                "mask_image": None, # Automatikus maszkolás
                                "num_outputs": 1
                            }
                        )
                        
                        # Megjelenítés
                        st.image(output[0], caption="Módosított kép", use_container_width=True)
                        
                        # Letöltés gomb
                        res = requests.get(output[0])
                        st.download_button("📥 KÉP MENTÉSE", res.content, f"ai_edit_{int(time.time())}.png", "image/png")
                    
                    except Exception as e:
                        st.error(f"Váratlan hiba: {e}")
            else:
                st.warning("Kérlek, írd le a módosítást!")
    else:
        st.info("Tölts fel egy képet a módosításhoz!")
