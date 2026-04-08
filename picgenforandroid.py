import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import google.generativeai as genai

# KULCSOK BETÖLTÉSE
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    st.error("Hiba: Hianyoznak a kulcsok a Secrets-bol!")
    st.stop()

# Gemini konfigurálása (INGYENES VERZIÓ)
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="AI Multi App", page_icon="🤖")

# LOGIN
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if not st.session_state['logged_in']:
    st.title("Belepes")
    pwd = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd == "admin":
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

# MENÜ
tab1, tab2 = st.tabs(["💬 Beszelgetes", "🎨 Kepkeszites"])

# --- CHAT ABLAK ---
with tab1:
    st.header("AI Chatbot")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Korábbi üzenetek megjelenítése
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Irj valamit..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("Hiba a chatekben. Ellenorizd az ingyenes API kulcsot!")

# --- KÉPGENERÁTOR ---
with tab2:
    st.header("Kepalkoto")
    st.write("Tipp: Ha nem ismer fel egy nevet, ird le az illetot (pl. haj, szemüveg, ruha).")
    img_prompt = st.text_area("Mit rajzoljak? (Angolul)", placeholder="A futuristic city with flying cars")
    
    if st.button("RAJZOLAS"):
        if img_prompt:
            with st.spinner("Alkotas..."):
                # UJ ROUTER URL
                API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
                headers = {"Authorization": "Bearer " + HF_TOKEN}
                
                res = requests.post(API_URL, headers=headers, json={"inputs": img_prompt})
                
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    st.image(img, use_container_width=True)
                else:
                    st.error("Hiba: " + str(res.status_code))
                    st.write("Lehet, hogy a Fine-grained tokenen nincs bepipalva az Inference Provider?")
