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
st.set_page_config(page_title="AI Kep Studio Pro", page_icon="🎨")

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

st.title("🎨 AI Kep-Mester (Stabil verzio)")

# 1. KEP FELTOLTESE (Csak a modositashoz kell)
st.markdown("### 1. Tolts fel egy kepet alapnak")
uploaded_file = st.file_uploader("Valassz egy kepet...", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption="Eredeti kep betoltve", use_container_width=True)

st.divider()

# 2. CHAT INPUT (Ez vezerli a modositast vagy a generast)
chat_input = st.chat_input("Mit modositsak vagy mit rajzoljak? (angolul)")

if chat_input:
    with st.spinner("AI dolgozik..."):
        try:
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            
            if uploaded_file:
                # --- MODOSITAS (Image-to-Image / ControlNet) ---
                # Ezt a modellt hasznaljuk, ami megtartja a kep szerkezetet
                API_URL = "https://router.huggingface.co/hf-inference/models/lllyasviel/ControlNet-v1-1-nightly"
                
                # Kep elokeszitese
                base_img = Image.open(uploaded_file).convert("RGB")
                buf = BytesIO()
                base_img.save(buf, format="JPEG")
                img_bytes = buf.getvalue()

                # ControlNet-nek mas a payloadja
                payload = {
                    "inputs": chat_input,
                    "image": uploaded_file.getvalue() # Ez a formatum is mukodik
                }
                
                # Probaljuk a multipart/form-data kuldest, ami a ControlNet-nel jobb
                response = requests.post(API_URL, headers=headers, data=img_bytes, params={"prompt": chat_input})
            
            else:
                # --- UJ KEP GENERALASA (FLUX) ---
                API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
                response = requests.post(API_URL, headers=headers, json={"inputs": chat_input})

            # Eredmeny ellenorzese
            if response.status_code == 200:
                final_img = Image.open(BytesIO(response.content))
                st.image(final_img, caption="AI eredmeny", use_container_width=True)
                
                # Mentes gomb
                buf_save = BytesIO()
                final_img.save(buf_save, format="PNG")
                st.download_button("📥 Kép mentése", buf_save.getvalue(), "ai_kep.png", "image/png")
            elif response.status_code == 503:
                st.warning("A modell toltodik, probald ujra 20 mp mulva!")
            elif response.status_code == 404:
                st.error("A kért modell már nem érhető el ezen az URL-en. ControlNet-re valtottunk, de ellenorizd az API_URL sorokat!")
            else:
                st.error(f"Szerver hiba: {response.status_code}")
                # Kiirjuk a valaszt, hogy lassuk, mi a baj
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Hiba tortent: {e}")

st.divider()
st.caption("A ControlNet technologia (ha van kep feltoltve) megtartja a kep szerkezetet.")
