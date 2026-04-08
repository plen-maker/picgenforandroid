import streamlit as st
import requests
from io import BytesIO
from PIL import Image

# A kulcsot a Streamlit feluleten az Advanced Settings -> Secrets resznel add meg!
# Formatum: HF_TOKEN = "hf_...a_te_kulcsod..."

try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Hiba: A HF_TOKEN hianyzik a Secrets-bol!")
    st.stop()

st.set_page_config(page_title="AI Kep", page_icon="*")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Belepes")
    pwd = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd == "admin":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas!")
    st.stop()

st.title("AI Kepgenerator")

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
headers = {"Authorization": "Bearer " + HF_TOKEN}

uploaded_file = st.file_uploader("Kep alapnak", type=['png', 'jpg', 'jpeg'])
prompt = st.text_area("Mit rajzoljak? (angolul)", "A realistic photo of a cat with a hat")

if st.button("Generalas"):
    if prompt:
        with st.spinner("Varj..."):
            try:
                res = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=60)
                
                if res.status_code == 200:
                    img = Image.open(BytesIO(res.content))
                    st.image(img, use_container_width=True)
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    st.download_button("Mentes", buf.getvalue(), "kep.png", "image/png")
                elif res.status_code == 503:
                    st.warning("A szerver ebred, probald ujra 30 mp mulva!")
                elif res.status_code == 401:
                    st.error("Hiba: Rossz a token a Secrets-ben!")
                else:
                    st.error("Hiba kod: " + str(res.status_code))
                    st.write(res.text)
            except Exception as e:
                st.error("Varatlan hiba: " + str(e))
