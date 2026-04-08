import streamlit as st
import requests
import base64
import random
from PIL import Image
from io import BytesIO

# --- KONFIGURACIO ---
# A kulcsokat a Streamlit Cloud Settings -> Secrets menujeben add meg!
STABILITY_KEY = st.secrets["STABILITY_KEY"]
API_HOST = "https://api.stability.ai"

st.set_page_config(page_title="AI Studio", page_icon="*")

# --- LOGIN RENDSZER (Username + Password) ---
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True

    st.title("Login")
    
    # A Secrets-bol olvassuk ki a megadott nevet es jelszot
    user_input = st.text_input("User Name:")
    pass_input = st.text_input("Password:", type="password")
    
    if st.button("Login"):
        if user_input == st.secrets["MY_USER"] and pass_input == st.secrets["MY_PASS"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Hibas adatok!")
    return False

if not check_auth():
    st.stop()

# --- FO PROGRAM ---
st.title("AI Image Generator")

prompt_text = st.text_area("Mit rajzoljon az AI?", placeholder="pl: A butterfly on a flower...")
style_choice = st.selectbox("Stilus:", ["Cinematic", "Photorealistic", "Digital Art", "Fantasy Art"])

if st.button("GENERATE", type="primary"):
    if prompt_text:
        with st.spinner("Wait..."):
            try:
                full_prompt = f"{prompt_text}, {style_choice}, highly detailed, masterpiece"
                
                url = f"{API_HOST}/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
                header = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {STABILITY_KEY}"
                }
                body = {
                    "text_prompts": [{"text": full_prompt, "weight": 1}],
                    "cfg_scale": 7, "height": 1024, "width": 1024, "samples": 1, "steps": 30
                }

                response = requests.post(url, headers=header, json=body)

                if response.status_code == 200:
                    image_data = base64.b64decode(response.json()["artifacts"][0]["base64"])
                    st.image(Image.open(BytesIO(image_data)), use_container_width=True)
                    st.download_button("Save Image", data=image_data, file_name="ai_result.png")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"System error: {e}")
    else:
        st.warning("Type something first!")
