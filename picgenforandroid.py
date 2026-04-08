## -*- coding: utf-8 -*-
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import time

# --- BIZTONSÁGI BEÁLLÍTÁSOK ---
try
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    st.error("Hiba: Hianyoznak a kulcsok a Secrets-bol!")
    st.stop()

# STABIL MODELL (Ez ritkábban dob 410-et)
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="Ingyenes AI Kep", page_icon="🎨")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Belepes")
    pwd = st.text_input("Jelszo", type="password")
    if st.button("Belepes"):
        if pwd == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- APP ---
st.title("🎨 Ingyenes AI Kepgenerator")

# Funkció a generáláshoz
def generate_image(prompt_text):
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt_text})
    return response

prompt = st.text_area("Mit rajzoljak? (Angolul)", "A realistic portrait of Viktor Orban with a hat")

if st.button("RAJZOLAS ✨"):
    if prompt:
        with st.spinner("AI alkotas... (Ez 30-60 mp is lehet ingyenesen)"):
            res = generate_image(prompt)
            
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                st.image(img, use_container_width=True)
            elif res.status_code == 503:
                st.warning("A modell eppen toltodik a Hugging Face-en. Varj 30 masodpercet es probald ujra!")
            elif res.status_code == 410:
                st.error("A modell ideiglenesen nem elerheto (410). Probald meg 5 perc mulva.")
            else:
                st.error(f"Hiba tortent: {res.status_code}")
                st.write(res.text)

st.info("TIPP: Ha 503-as hibat kapsz, az csak azt jelenti, hogy a szerver ebred. Ne add fel, nyomj ra megegyszer fel perc mulva!")
