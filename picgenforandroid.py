import streamlit as st
import requests
import base64
import random
from PIL import Image
from io import BytesIO

# --- BIZTONSAGOS KONFIGURACIO ---
# A kulcsokat a Streamlit Cloud Settings -> Secrets menujeben add meg!
STABILITY_KEY = st.secrets["STABILITY_KEY"]
API_HOST = "https://api.stability.ai"

st.set_page_config(page_title="AI Studio", page_icon="*")

# --- LOGIN RENDSZER ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True

    st.title("Login")
    # A jelszo is a Secrets-bol jon: APP_PASSWORD
    password_input = st.text_input("Jelszo:", type="password")
    if st.button("Belepes"):
        if password_input == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    return False

if not check_password():
    st.stop()

# --- FO PROGRAM ---
st.title("SDXL Generator")

kep_leiras = st.text_area("Mit rajzoljon az AI?", placeholder="pl: A butterfly on a flower...")
stilus = st.selectbox("Stilus:", ["Cinematic", "Photorealistic", "Digital Art", "Fantasy Art"])

if st.button("GENERALAS", type="primary"):
    if kep_leiras:
        with st.spinner("Alkotas folyamatban..."):
            try:
                vegleges_prompt = f"{kep_leiras}, {stilus}, highly detailed, masterpiece"
                
                url = f"{API_HOST}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
                header = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {STABILITY_KEY}"
                }
                body = {
                    "text_prompts": [{"text": vegleges_prompt, "weight": 1}],
                    "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 30
                }

                response = requests.post(url, headers=header, json=body)

                if response.status_code == 200:
                    image_data = base64.b64decode(response.json()["artifacts"][0]["base64"])
                    st.image(Image.open(BytesIO(image_data)), use_container_width=True)
                    st.download_button("Mentes", data=image_data, file_name="ai_kep.png")
                else:
                    st.error(f"Hiba: {response.status_code}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Hiba tortent: {e}")
    else:
        st.warning("Irj be egy leirast!")
