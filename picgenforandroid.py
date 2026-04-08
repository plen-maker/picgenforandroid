import streamlit as st
import requests
import io
import random

st.set_page_config(page_title="AI Kep Chat Szerkeszto", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_image' not in st.session_state:
    st.session_state['current_image'] = None
if 'current_prompt' not in st.session_state:
    st.session_state['current_prompt'] = ""
if 'current_seed' not in st.session_state:
    st.session_state['current_seed'] = random.randint(0, 9999999)

def generate_image(full_prompt, seed):
    try:
        url = f"https://image.pollinations.ai/prompt/{full_prompt.replace(' ', '%20')}?seed={seed}&model=flux"
        response = requests.get(url, timeout=90)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception:
        return None

if not st.session_state['logged_in']:
    st.header("Bejelentkezes")
    user = st.text_input("Felhasznalonev")
    password = st.text_input("Jelszo", type="password")
    if st.button("Belepes"):
        if user == "Astrofinger" and password == "98976987596785y798jk":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas adatok")
else:
    st.title("AI Kep Chat Szerkeszto")
    st.write("Ird le az elso kepet, majd a chat ablakban kerj modositasokat")

    if st.sidebar.button("Kijelentkezes"):
        st.session_state['logged_in'] = False
        st.rerun()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Aktualis Kep")
        initial_prompt = st.text_input("Elso kep leirasa", placeholder="pl: A majestic lion on a rock")
        
        if st.button("ELSO KEP LETREHOZASA", type="primary"):
            if initial_prompt:
                with st.spinner("Az AI alkot..."):
                    st.session_state['current_seed'] = random.randint(0, 9999999)
                    st.session_state['current_prompt'] = initial_prompt
                    st.session_state['chat_history'] = [{"role": "user", "content": initial_prompt}]
                    
                    image_data = generate_image(initial_prompt, st.session_state['current_seed'])
                    
                    if image_data:
                        st.session_state['current_image'] = image_data
                    else:
                        st.error("Hiba a generalas soran")
            else:
                st.warning("Irj be egy leirast")

        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], use_container_width=True)
            st.download_button(
                label="KEP MENTESE (LETOLTES)",
                data=st.session_state['current_image'],
                file_name=f"ai_image_{st.session_state['current_seed']}.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

    with col2:
        st.subheader("Szerkesztes Chaten")
        chat_container = st.container(height=400)
        
        for message in st.session_state['chat_history']:
            with chat_container.chat_message(message["role"]):
                st.write(message["content"])

        if st.session_state['current_image']:
            if edit_input := st.chat_input("Hogyan modositsam a kepet?"):
                st.session_state['chat_history'].append({"role": "user", "content": edit_input})
                with chat_container.chat_message("user"):
                    st.write(edit_input)
                
                with st.spinner("AI modositas folyamatban..."):
                    new_full_prompt = f"{st.session_state['current_prompt']}, modification: {edit_input}"
                    image_data = generate_image(new_full_prompt, st.session_state['current_seed'])
                    
                    if image_data:
                        st.session_state['current_image'] = image_data
                        st.session_state['current_prompt'] = new_full_prompt
                        st.rerun()
                    else:
                        st.error("A modositas nem sikerult")
        else:
            st.info("Hozd letre az elso kepet a szerkeszteshez")

    if st.session_state['chat_history'] and st.button("CHAT TORLESE ES UJ KEP"):
        st.session_state['chat_history'] = []
        st.session_state['current_image'] = None
        st.session_state['current_prompt'] = ""
        st.rerun()