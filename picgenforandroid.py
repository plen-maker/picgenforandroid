import streamlit as st
import requests
from io import BytesIO
from PIL import Image

# Secrets-bol vesszuk a tokent
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except Exception:
    st.error("Hiba: HF_TOKEN hianyzik a Secrets-bol!")
    st.stop()

# Alapbeallitasok
APP_PASSWORD = "admin"
st.set_page_config(page_title="Profi AI Kep Studio", page_icon="🎨")

# LOGIN
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

st.title("🎨 AI Kep-Mester")

# 1. KEP FELTOLTESE
uploaded_file = st.file_uploader("Tolts fel egy kepet alapnak:", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="Eredeti kep", use_container_width=True)

# 2. CHAT INPUT
chat_input = st.chat_input("Mit modositsak a kepen? (angolul)")

if chat_input:
    with st.spinner("AI dolgozik..."):
        try:
            # Ha van feltoltott kep, akkor "Image-to-Image" modellt hasznalunk
            if uploaded_file:
                # Ezt a modellt hasznaljuk kepmodositashoz
                API_URL = "https://router.huggingface.co/hf-inference/models/timbrooks/instruct-pix2pix"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                
                # Kep elokeszitese
                base_img = Image.open(uploaded_file).convert("RGB")
                buf = BytesIO()
                base_img.save(buf, format="JPEG")
                img_bytes = buf.getvalue()

                # Kuldes a Hugging Face-nek
                payload = {
                    "inputs": chat_input,
                    "image": uploaded_file.getvalue()
                }
                # Megjegyzes: a Pix2Pix modellnek maskepp kell kuldeni a kepet
                response = requests.post(API_URL, headers=headers, data=img_bytes, params={"prompt": chat_input})
            
            else:
                # Ha NINCS kep, akkor csak siman rajzolunk valami ujat (FLUX)
                API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                response = requests.post(API_URL, headers=headers, json={"inputs": chat_input})

            if response.status_code == 200:
                final_img = Image.open(BytesIO(response.content))
                st.image(final_img, caption="AI eredmeny", use_container_width=True)
                
                # Mentes gomb
                buf_save = BytesIO()
                final_img.save(buf_save, format="PNG")
                st.download_button("Mentes", buf_save.getvalue(), "ai_kep.png", "image/png")
            elif response.status_code == 503:
                st.warning("A modell eppen ebred, probald ujra 20 masodperc mulva!")
            else:
                st.error(f"Szerver hiba: {response.status_code}")
                
        except Exception as e:
            st.error(f"Hiba tortent: {e}")

st.divider()
st.caption("A 'Pix2Pix' technologia megprobalja megtartani az eredeti arcot.")
