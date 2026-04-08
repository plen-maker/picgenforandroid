import streamlit as st
import requests
import io
from PIL import Image

# --- KONFIGURACIO ---
# Regisztralj ingyen: https://huggingface.co/join
# Generalj egy API tokent itt: https://huggingface.co/settings/tokens
HF_TOKEN = st.secrets["HF_TOKEN"]

# Ez egy nagyon eros, modern modell (Flux.1 Schnell)
API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

st.set_page_config(page_title="Pro AI Studio", layout="wide")

# --- LOGIN RENDSZER ---
def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if st.session_state["authenticated"]:
        return True

    st.title("Login")
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
st.title("Next-Gen Free AI Studio")

if "full_prompt" not in st.session_state:
    st.session_state["full_prompt"] = ""

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Chat / Prompt Window")
    user_msg = st.text_area("Mit adjak hozza a kephez?", placeholder="pl: A majestic butterfly on a crystal flower...")
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("GENERATE", type="primary"):
            if user_msg:
                if st.session_state["full_prompt"] == "":
                    st.session_state["full_prompt"] = user_msg
                else:
                    st.session_state["full_prompt"] += f", {user_msg}"
    
    with col_btn2:
        if st.button("RESET"):
            st.session_state["full_prompt"] = ""
            st.rerun()

    if st.session_state["full_prompt"]:
        st.info(f"Aktualis leiras: {st.session_state['full_prompt']}")

with col2:
    st.header("Result")
    if st.session_state["full_prompt"]:
        with st.spinner("AI is thinking (High Quality)..."):
            try:
                # Hugging Face API hivas
                response = requests.post(API_URL, headers=headers, json={"inputs": st.session_state["full_prompt"]})
                
                if response.status_code == 200:
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, use_container_width=True)
                    st.download_button("Save High-Res Image", data=image_bytes, file_name="ai_pro_result.png")
                elif response.status_code == 503:
                    st.warning("A modell eppen toltodik, varj 10 masodpercet es probald ujra!")
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"System error: {e}")
    else:
        st.write("Start chatting to see results!")
