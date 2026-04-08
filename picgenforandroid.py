import streamlit as st
import requests
import urllib.parse
import google.generativeai as genai

# --- KULCSOK ES KONFIGURACIO ---
# Gyozodj meg rola, hogy a GOOGLE_API_KEY benne van a Streamlit Secrets-ben!
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    # A legstabilabb modellnev hasznalata a 404 elkerulesere
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Hiba a kulcsok betoltesenel: {e}")
    st.stop()

# Alapbeallitasok
APP_PASSWORD = "admin" # Ezt a jelszot kell beirnod
st.set_page_config(page_title="Magyar AI Kep Studio", page_icon="🎨")

# --- LOGIN RENDSZER ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("🔐 Belepes")
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Hibas jelszo!")
    st.stop()

# --- APP FELULET ---
st.title("🎨 Magyar AI Kepalkoto - Profi")
st.write("Irj le valamit magyarul, es az AI megrajzolja neked!")

# --- CHAT ABLAK ---
# Ez a mezo az oldal aljan jelenik meg
chat_input = st.chat_input("Pl.: 'Egy modern rendőr kék egyenruhában, Isztambul utcáin'...")

if chat_input:
    # 1. Megjelenitjuk amit a felhasznalo irt
    with st.chat_message("user"):
        st.markdown(chat_input)

    # 2. AI feldolgozas
    with st.chat_message("assistant"):
        with st.spinner("AI gondolkodik es rajzol..."):
            try:
                # FORDITAS ES FELJAVITAS GEMINI-VEL
                # Megkerjuk a Geminit, hogy csinaljon profi angol promptot
                instruction = (
                    "You are an expert AI image prompt engineer. Translate the following Hungarian request to a "
                    "highly detailed, photorealistic English prompt. Focus on human features, modern clothing, "
                    "and realistic lighting. Only output the English prompt text: "
                )
                
                response = gemini_model.generate_content(instruction + chat_input)
                english_prompt = response.text.strip()
                
                # Kicsiben megmutatjuk a forditas eredmenyet
                st.caption(f"🇬🇧 Forditott parancs: {english_prompt}")

                # KEPGENERALAS POLLINATIONS-SZAL
                encoded_prompt = urllib.parse.quote(english_prompt)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
                
                img_res = requests.get(image_url)
                
                if img_res.status_code == 200:
                    # Megjelenitjuk a kesz kepet
                    st.image(img_res.content, use_container_width=True)
                    
                    # Mentes gomb
                    st.download_button(
                        label="📥 Kep mentese",
                        data=img_res.content,
                        file_name="ai_generalt_kep.png",
                        mime="image/png"
                    )
                else:
                    st.error(f"Sajnos a kepalkoto szerver hibaat jelzett: {img_res.status_code}")
            
            except Exception as e:
                st.error(f"Hiba tortent a folyamat soran: {e}")
st.divider()
st.caption("Tipp: Minel reszletesebben irod le (angolul), annal szebb lesz a kep! MIvel a Magyar egy szar nyelv! Ha valami nem mukodik rafogom a fideszre ! Created by ddnemet  For support conctact me on discord: ddnemet")
