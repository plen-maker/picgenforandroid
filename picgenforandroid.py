import streamlit as st
import requests
import io
import random
from PIL import Image
from openai import OpenAI

st.set_page_config(page_title="AI Kep Mester Pro", layout="wide")

# --- LOGIN RENDSZER ALLAPOT ---
if 'auth_step' not in st.session_state:
    st.session_state['auth_step'] = "email_input"
if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
if 'sent_code' not in st.session_state:
    st.session_state['sent_code'] = None
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_image' not in st.session_state:
    st.session_state['current_image'] = None

# --- BEJELENTKEZES LOGIKA ---
def login_screen():
    st.title("Belepes")
    
    if st.session_state['auth_step'] == "email_input":
        email = st.text_input("Add meg az e-mail cimed")
        if st.button("Kod kuldese"):
            if "@" in email:
                # Itt generalunk egy 6 jegyu kodot
                code = str(random.randint(100000, 999999))
                st.session_state['sent_code'] = code
                st.session_state['auth_step'] = "code_verify"
                
                # Mivel nincs kulso email szerverunk, most kiirjuk a kepernyore 
                # (Elesben itt menne ki az email API-n keresztul)
                st.info(f"Kuldott kod (teszt uzemmod): {code}")
                st.rerun()
            else:
                st.error("Ervenytelen e-mail cim")

    elif st.session_state['auth_step'] == "code_verify":
        user_code = st.text_input("Ird be az e-mailben kapott kodot", type="password")
        if st.button("Ellenorzes"):
            if user_code == st.session_state['sent_code']:
                st.session_state['user_logged_in'] = True
                st.success("Sikeres belepes!")
                st.rerun()
            else:
                st.error("Hibas kod!")
        
        if st.button("Vissza"):
            st.session_state['auth_step'] = "email_input"
            st.rerun()

# --- FO PROGRAM ---
if not st.session_state['user_logged_in']:
    login_screen()
else:
    st.sidebar.button("Kijelentkezes", on_click=lambda: st.session_state.update({"user_logged_in": False, "auth_step": "email_input"}))
    st.title("AI Kep Mester Pro")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Kep letrehozasa")
        
        up_file = st.file_uploader("Kep feltoltese", type=["png", "jpg", "jpeg"])
        if up_file:
            st.session_state['current_image'] = up_file.read()

        st.divider()
        
        api_k = st.text_input("OpenAI API Kulcs (sk-...)", type="password")
        prompt = st.text_area("Leiras az AI-nak")

        if st.button("GENERALAS", type="primary"):
            if api_k and prompt:
                try:
                    client = OpenAI(api_key=api_k)
                    with st.spinner("Alkotas folyamatban..."):
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
                st.warning("Hianyzik a kulcs vagy a leiras")

        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], use_container_width=True)
            st.download_button("LETOLTES", st.session_state['current_image'], "kep.png", "image/png")

    with col2:
        st.subheader("Chat")
        for m in st.session_state['chat_history']:
            with st.chat_message(m["role"]):
                st.write(m["content"])
        
        chat_in = st.chat_input("Modositas...")
        if chat_in and st.session_state['current_image'] and api_k:
            st.session_state['chat_history'].append({"role": "user", "content": chat_in})
            with st.spinner("Modositas..."):
                try:
                    client = OpenAI(api_key=api_k)
                    res = client.images.generate(
                        model="dall-e-3",
                        prompt=f"Modify this: {chat_in}",
                        n=1,
                        size="1024x1024"
                    )
                    st.session_state['current_image'] = requests.get(res.data[0].url).content
                    st.rerun()
                except Exception as e:
                    st.error(f"Hiba: {e}")
