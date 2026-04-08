import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import urllib.parse
import os

# Jelszó a barátodnak
APP_PASSWORD = "admin"

# Oldal konfiguráció (telefon-barát)
st.set_page_config(page_title="AI Kepmodosito Studio", page_icon="🎨")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Belepes")
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("BELEPES 🚀"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- APP ---
st.title("🎨 AI Kepmodosito Kozpont")

st.divider()

# 1. LEPES: KEP FELTOLTESE (ez az alap)
st.header("1. Tolts fel egy kepet alapnak")
uploaded_file = st.file_uploader("Valassz egy kepet...", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Megjelenitjuk az eredeti kepet
    st.image(uploaded_file, caption="Eredeti kep", use_container_width=True)
    st.divider()

    # 2. LEPES: CHAT ABLAK A MODOSITASHOZ (Pollinations)
    st.header("2. Mi legyen a modositas?")
    # Az st.chat_input az oldal aljára kerül
    chat_mod = st.chat_input("Pl.: 'make him smile', 'add a sun hat', 'neon lights'")

    if chat_mod:
        with st.spinner("AI modositas folyamatban..."):
            try:
                # Trükk: A feltöltött képet feltöltjük egy ideiglenes tárhelyre (temp.sh), 
                # hogy a Pollinations.ai el tudja érni URL-ként.
                files = {'file': uploaded_file.getvalue()}
                upload_res = requests.post('https://temp.sh/upload', files=files)
                
                if upload_res.status_code == 200:
                    temp_image_url = upload_res.text.strip()
                    
                    # Pollinations.ai image-to-image kérés összeállítása
                    encoded_prompt = urllib.parse.quote(chat_mod)
                    encoded_url = urllib.parse.quote(temp_image_url)
                    poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed=42&width=1024&height=1024&nologo=true&image-url={encoded_url}"
                    
                    poll_res = requests.get(poll_url)
                    
                    if poll_res.status_code == 200:
                        # Megjelenitjük a módosított képet
                        st.image(poll_res.content, caption="Modositott kep", use_container_width=True)
                        
                        # Letöltés gomb
                        st.download_button("📥 Kép mentése", poll_res.content, "ai_modositott_kep.png", "image/png")
                    else:
                        st.error("Nem sikerult a modositas a Pollinations.ai-val.")
                else:
                    st.error("Hiba tortent az ideiglenes kepfeltoltesnel.")

            except Exception as e:
                st.error("Hiba tortent a modositasnal: " + str(e))
else:
    st.info("Tölts fel egy képet az induláshoz!")
