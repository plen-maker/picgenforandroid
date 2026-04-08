import streamlit as st
import requests
import io
from PIL import Image
import time

# --- KONFIGURÁCIÓ ---
# IDE MÁSOLD A HUGGING FACE TOKENEDET!
HF_TOKEN = "IDE_A_TE_TOKENED"
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="HuggingFace Kép Mester", page_icon="🎨")

st.title("🎨 Profi Hugging Face Kép Generátor")
st.markdown("Ez az app a **FLUX.1** modellt használja a legszebb eredményekért.")

# --- EDITOR RÉSZ ---
prompt = st.text_area("Mit hozzak létre?", placeholder="pl: A majestic dragon sitting on a skyscraper, cinematic lighting, 8k, detailed", height=120)

col1, col2 = st.columns(2)
with col1:
    negative_prompt = st.text_input("Amit NE tartalmazzon (opcionális):", placeholder="blurry, distorted, low quality")
with col2:
    aspect_ratio = st.selectbox("Méret:", ["1024x1024", "800x600", "600x800"])

# --- GENERÁLÁS LOGIKA ---
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    elif response.status_code == 503: # Ha még töltődik a modell a szerveren
        st.info("Az AI szerver éppen ébredezik... Várj 10 másodpercet!")
        time.sleep(10)
        return query(payload)
    else:
        st.error(f"Hiba történt: {response.status_code}")
        return None

if st.button("KÉP LÉTREHOZÁSA ✨", type="primary"):
    if prompt:
        with st.spinner("Az AI éppen alkot (Hugging Face API)..."):
            # Összerakjuk a kérést
            image_bytes = query({
                "inputs": f"{prompt}. {negative_prompt}",
                "parameters": {"width": 1024, "height": 1024}
            })
            
            if image_bytes:
                img = Image.open(io.BytesIO(image_bytes))
                st.image(img, caption="Generált mű", use_container_width=True)
                
                # --- LETÖLTÉS GOMB ---
                st.download_button(
                    label="📥 KÉP LETÖLTÉSE",
                    data=image_bytes,
                    file_name="hf_generated_image.png",
                    mime="image/png",
                    use_container_width=True
                )
    else:
        st.warning("Írj be egy leírást!")

st.markdown("---")
st.caption("Modell: Black Forest Labs - FLUX.1 Schnell | Hosting: Hugging Face Inference API")