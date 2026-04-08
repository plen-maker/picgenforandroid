import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import urllib.parse

try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Hiba: HF_TOKEN hianyzik!")
    st.stop()

st.set_page_config(page_title="AI Kep Studio", page_icon="🎨")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    pwd = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd == "admin":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

st.title("AI Kep Studio (HF + Pollinations)")

# --- 1. LEPES: ALAP KEP GENERALASA (Hugging Face) ---
st.subheader("1. Generalj egy alap kepet")
base_prompt = st.text_input("Mit rajzoljak eloszor? (angolul)", "A portrait of a man")

if st.button("Alap kep keszitese"):
    with st.spinner("HF dolgozik..."):
        API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": "Bearer " + HF_TOKEN}
        res = requests.post(API_URL, headers=headers, json={"inputs": base_prompt})
        
        if res.status_code == 200:
            st.session_state['base_img'] = res.content
            st.session_state['current_img'] = res.content
        else:
            st.error("HF hiba!")

# Ha mar van kepunk, megjelenitjuk
if 'current_img' in st.session_state:
    st.image(st.session_state['current_img'], use_container_width=True)

    # --- 2. LEPES: MODOSITAS CHAT BOX-SZAL (Pollinations) ---
    st.subheader("2. Modositas a chat ablakban")
    st.write("Ird ide, mit valtoztassak a fenti kepen!")
    
    # Ez a chat beviteli mezo az oldal aljan
    chat_mod = st.chat_input("Pl.: 'make him smile', 'add a sun hat', 'neon lights'")

    if chat_mod:
        with st.spinner("Pollinations modositas..."):
            # Pollinations.ai kepmodosito link osszerakasa
            # A Pollinations kep-alapu modositasa a promptba agyazott parameterekkel mukodik a legstabilabban
            encoded_prompt = urllib.parse.quote(chat_mod)
            poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
            
            try:
                poll_res = requests.get(poll_url)
                if poll_res.status_code == 200:
                    st.session_state['current_img'] = poll_res.content
                    st.rerun() # Frissitjuk az oldalt az uj keppel
                else:
                    st.error("Pollinations hiba!")
            except Exception as e:
                st.error("Hiba: " + str(e))

    if st.button("Kep mentese"):
        st.download_button("Letoltes", st.session_state['current_img'], "ai_kep.png", "image/png")
