import streamlit as st
import requests
import io
import random
import time

st.set_page_config(page_title="AI Kep Chat", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
if 'current_image' not in st.session_state:
    st.session_state['current_image'] = None
if 'current_prompt' not in st.session_state:
    st.session_state['current_prompt'] = ""
if 'current_seed' not in st.session_state:
    st.session_state['current_seed'] = random.randint(0, 999999)

def get_image_with_retry(url, retries=3):
    for i in range(retries):
        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                return res.content
        except Exception:
            if i < retries - 1:
                time.sleep(2)
                continue
    return None

if not st.session_state['logged_in']:
    st.header("Login")
    u = st.text_input("User")
    p = st.text_input("Pass", type="password")
    if st.button("OK"):
        if u == "admin" and p == "1234":
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Rossz adatok")
else:
    st.title("AI Kep Chat")

    if st.sidebar.button("Exit"):
        st.session_state['logged_in'] = False
        st.rerun()

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("Kep")
        p_in = st.text_input("Leiras", placeholder="pl: space cat")
        
        if st.button("Generalas", type="primary"):
            if p_in:
                with st.spinner("Dolgozom..."):
                    st.session_state['current_seed'] = random.randint(0, 999999)
                    st.session_state['current_prompt'] = p_in
                    st.session_state['chat_history'] = [{"role": "user", "content": p_in}]
                    
                    link = f"https://image.pollinations.ai/prompt/{p_in.replace(' ', '%20')}?seed={st.session_state['current_seed']}&model=flux"
                    data = get_image_with_retry(link)
                    
                    if data:
                        st.session_state['current_image'] = data
                        st.rerun()
                    else:
                        st.error("A szerver tulterhelt, probald meg ujra 5 masodperc mulva")
            else:
                st.warning("Irj be valamit")

        if st.session_state['current_image']:
            st.image(st.session_state['current_image'], use_container_width=True)
            st.download_button("Mentes", st.session_state['current_image'], "kep.jpg", "image/jpeg")

    with c2:
        st.subheader("Chat")
        cont = st.container(height=400)
        for m in st.session_state['chat_history']:
            with cont.chat_message(m["role"]):
                st.write(m["content"])

        if st.session_state['current_image']:
            if edt := st.chat_input("Modositas"):
                st.session_state['chat_history'].append({"role": "user", "content": edt})
                with st.spinner("Modositas..."):
                    new_p = f"{st.session_state['current_prompt']}, {edt}"
                    link = f"https://image.pollinations.ai/prompt/{new_p.replace(' ', '%20')}?seed={st.session_state['current_seed']}&model=flux"
                    data = get_image_with_retry(link)
                    if data:
                        st.session_state['current_image'] = data
                        st.session_state['current_prompt'] = new_p
                        st.rerun()
        else:
            st.info("Hozd letre az elso kepet")

    if st.button("Torles"):
        st.session_state['chat_history'] = []
        st.session_state['current_image'] = None
        st.rerun()