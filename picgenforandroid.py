import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import urllib.parse

# Alapbeallitasok
APP_PASSWORD = "admin"
st.set_page_config(page_title="AI Kep Studio", page_icon="🎨")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Belepes")
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

st.title("🎨 AI Kep Studio (Stabil)")

# 1. OPCIONALIS KEP FELTOLTES
st.markdown("### 1. Tolts fel egy kepet alapnak")
uploaded_file = st.file_uploader("Valassz egy kepet a modositashoz:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="Eredeti kep betoltve", use_container_width=True)

st.divider()

# 2. CHAT INPUT
chat_input = st.chat_input("Ird ide a parancsot angolul...")

if chat_input:
    with st.spinner("AI dolgozik..."):
        try:
            encoded_prompt = urllib.parse.quote(chat_input)
            
            if uploaded_file:
                # --- MODOSITAS (Image-to-Image) ---
                # A kepet Base64 helyett feltoltjuk egy ideiglenes tarhelyre
                files = {'file': uploaded_file.getvalue()}
                upload_res = requests.post('https://temp.sh/upload', files=files)
                
                if upload_res.status_code == 200:
                    temp_url = upload_res.text.strip()
                    encoded_url = urllib.parse.quote(temp_url)
                    # Pollinations stabil Image-to-Image URL
                    final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&image-url={encoded_url}"
                else:
                    st.error("Kepfeltoltesi hiba.")
                    st.stop()
            else:
                # --- UJ KEP (Text-to-Image) ---
                final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"

            # Kep lekerese a Pollinations-tol (nem dob 404-et)
            res = requests.get(final_url)
            
            if res.status_code == 200:
                st.image(res.content, caption="AI eredmeny", use_container_width=True)
                st.download_button("📥 Mentes", res.content, "ai_kep.png", "image/png")
            else:
                st.error(f"AI hiba: {res.status_code}")
                
        except Exception as e:
            st.error(f"Hiba tortent: {e}")

st.divider()
st.caption("Ez a verzio a Pollinations API-t hasznalja, ami ingyenes es stabil.")
