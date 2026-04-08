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
        else:
            st.error("Hibas jelszo!")
    st.stop()

st.title("🎨 Univerzalis AI Kepstudio")

# --- 1. OPCIONALIS KEP FELTOLTES ---
st.markdown("### 1. Kep feltoltese (Opcionalis)")
uploaded_file = st.file_uploader("Ha modositani akarsz egy kepet, toltsd fel ide:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="Alap kep betoltve", use_container_width=True)
    st.info("Most ird meg a chatbe lent, mit valtoztassak a kepen!")
else:
    st.info("Nincs kep feltoltve. Ird meg a chatbe, mit rajzoljak a semmibol!")

st.divider()

# --- 2. CHAT ABLAK (Ez vezerli a generast vagy a modositast) ---
chat_input = st.chat_input("Ird ide a parancsot angolul...")

if chat_input:
    with st.spinner("AI munka folyamatban..."):
        try:
            encoded_prompt = urllib.parse.quote(chat_input)
            
            if uploaded_file:
                # MODOSITAS (Image-to-Image)
                # Feltoltjuk a kepet egy ideiglenes tarhelyre URL-ert
                files = {'file': uploaded_file.getvalue()}
                upload_res = requests.post('https://temp.sh/upload', files=files)
                
                if upload_res.status_code == 200:
                    temp_url = upload_res.text.strip()
                    encoded_url = urllib.parse.quote(temp_url)
                    # Pollinations URL kep-alapu modositassal
                    final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true&image-url={encoded_url}"
                else:
                    st.error("Kepfeltoltesi hiba a szerveren.")
                    st.stop()
            else:
                # UJ KEP (Text-to-Image)
                # Sima Pollinations URL
                final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"

            # Kep lekerese
            res = requests.get(final_url)
            if res.status_code == 200:
                st.image(res.content, caption="Az AI eredmenye", use_container_width=True)
                st.download_button("📥 Mentes", res.content, "ai_vegeredmeny.png", "image/png")
            else:
                st.error("AI hiba történt a generáláskor.")
                
        except Exception as e:
            st.error(f"Hiba: {e}")

st.divider()
st.caption("Tipp: Hasznalj angol leirast a jobb eredmenyert!")
