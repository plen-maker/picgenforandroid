import streamlit as st
import requests
from io import BytesIO
from PIL import Image

try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    st.error("Hiba: Hianyoznak a kulcsok!")
    st.stop()

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="AI Kep", page_icon="*")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Belepes")
    pwd = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas!")
    st.stop()

st.title("AI Kepgenerator")

uploaded_file = st.file_uploader("Kep feltoltese", type=['png', 'jpg', 'jpeg'])
prompt = st.text_area("Leiras angolul:", "A photo of a man with a hat")

if st.button("Generalas"):
    if prompt:
        with st.spinner("Dolgozom..."):
            payload = {"inputs": prompt}
            res = requests.post(API_URL, headers=headers, json=payload)
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                st.image(img, use_container_width=True)
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.download_button("Mentes", buf.getvalue(), "kep.png", "image/png")
            elif res.status_code == 503:
                st.warning("Varj 20 masodpercet, a szerver ebred!")
            else:
                st.error("Hiba tortent!")
