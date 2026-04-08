import streamlit as st
import requests
import io
import uuid
import random
from PIL import Image
from openai import OpenAI
from supabase import create_client, Client

# --- SUPABASE ADATOK ---
SUPABASE_URL = "https://jsxvvtvcitgtowpzjpyh.supabase.co"
SUPABASE_KEY = "sb_publishable_KC7QotIFwX4T8bWr4g-WWQ_mhiBxesb"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="AI Kep Mester Pro", layout="wide")

# --- ALLAPOT KEZELES ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_image' not in st.session_state:
    st.session_state['current_image'] = None

# --- LOGIN MODUL ---
def login_logic():
    if not st.session_state['user']:
        st.title("Belepes")
        tab1, tab2 = st.tabs(["Login", "Regisztracio"])
        
        with tab1:
            email = st.text_input("Email")
            pw = st.text_input("Jelszo", type="password")
            if st.button("Belepes"):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                    st.session_state['user'] = res.user
                    st.rerun()
                except:
                    st.error("Hiba a belepesnel")
            
            st.divider()
            if st.button("Google Login (Kulso)"):
                supabase.auth.sign_in_with_oauth({"provider": "google"})

        with tab2:
            reg_email = st.text_input("Uj Email")
            reg_pw = st.text_input("Uj Jelszo", type="password")
            if st.button("Regisztracio"):
                try:
                    supabase.auth.sign_up({"email": reg_email, "password": reg_pw})
                    st.success("Sikeres! Igazold vissza az emailedben.")
                except:
                    st.error("Hiba a regisztracional")
        return False
    return True

# --- FO PROGRAM ---
if login_logic():
    st.sidebar.write(f"Bejelentkezve: {st.session_state['user'].email}")
    if st.sidebar.button("Kijelentkezes"):
        supabase.auth.sign_out()
        st.session_state['user'] = None
        st.rerun()

    st.title("AI Kep Mester Pro")
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Kep feltoltes vagy letrehozas")
        
        # Kep feltoltes
        up_file = st.file_uploader("Kep feltoltese", type=["png", "jpg", "jpeg"])
        if up_file:
            st.session_state['current_image'] = up_file.read()
            st.image(st.session_state['current_image'], caption="Feltoltott kep")

        # API Kulcs bekero a munka elott
        api_k = st.text_input("OpenAI API Kulcsod", type="password")
        prompt = st.text_input("Mit csinaljon az AI?")

        if st.button("MEHET", type="primary"):
            if api_k and prompt:
                try:
                    client = OpenAI(api_key=api_k)
                    with st.spinner("AI dolgozik..."):
                        # Itt fut a DALL-E generalas
                        res = client.images.generate(
                            model="dall-e-3",
                            prompt=prompt,
                            n=1,
                            size="1024x1024"
                        )
                        img_url = res.data[0].url
                        st.session_state['current_image'] = requests.get(img_url).content
                        st.session_state['chat_history'].append({"role": "user", "content": prompt})
                except Exception as e:
                    st.error(f"Hiba: {e}")
            else:
                st.warning("Adj meg kulcsot es leirast")

        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], use_container_width=True)
            st.download_button("Kep Mentese", st.session_state['current_image'], "ai_kesz.png", "image/png")

    with col2:
        st.subheader("Chat Szerkeszto")
        for m in st.session_state['chat_history']:
            with st.chat_message(m["role"]):
                st.write(m["content"])
        
        chat_in = st.chat_input("Ird ide a modositast...")
        if chat_in and st.session_state['current_image']:
            # Chat alapu modositas logikaja ide jon (DALL-E edit)
            st.session_state['chat_history'].append({"role": "user", "content": chat_in})
            st.rerun()