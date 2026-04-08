import streamlit as st
import requests
import urllib.parse

# Alapbeallitasok
APP_PASSWORD = "admin"
st.set_page_config(page_title="AI Kep Chat", page_icon="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRntRZVOrqGu_lXojFBN--lmsNttJ2TuxQ4Xg&s")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title(" Belepes")
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- APP FELULET ---
st.title(" AI Kepalkoto Chat")
st.write("Ird le angolul a chatbe, mit rajzoljak neked!")

# --- CHAT INPUT ---
# Ez a mezo mindig az oldal aljan marad
chat_input = st.chat_input("Pl.: 'A cyberpunk city', 'A cute cat with glasses'...")

if chat_input:
    # Megjelenitjük a felhasznalo kereset
    with st.chat_message("user"):
        st.markdown(chat_input)

    # Generalas folyamata
    with st.chat_message("assistant"):
        with st.spinner("Rajzolas folyamatban..."):
            try:
                # Szoveg kodolasa az URL-hez
                encoded_prompt = urllib.parse.quote(chat_input)
                
                # Pollinations API link (gyors es ingyenes)
                final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
                
                # Kep lekerese
                res = requests.get(final_url)
                
                if res.status_code == 200:
                    # Megjelenitjuk a kepet a chaten belul
                    st.image(res.content, use_container_width=True)
                    
                    # Mentes gomb a kep alatt
                    st.download_button(
                        label=" Kep mentese",
                        data=res.content,
                        file_name="ai_generalt_kep.png",
                        mime="image/png"
                    )
                else:
                    st.error("Sajnos a kepalkoto szerver most nem valaszol.")
            
            except Exception as e:
                st.error(f"Hiba tortent: {e}")

st.divider()
st.caption("Tipp: Minel reszletesebben irod le (angolul), annal szebb lesz a kep! MIvel a Magyar egy szar nyelv! Ha valami nem mukodik rafogom a fideszre ! Created by ddnemet  For support conctact me on discord: ddnemet")
