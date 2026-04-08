import streamlit as st
import requests
import urllib.parse
import google.generativeai as genai

# Kulcsok betoltese (A Gemini-hez kell a GOOGLE_API_KEY a Secrets-be!)
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    # Gemini modell a fordításhoz
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception:
    st.error("Hiba: GOOGLE_API_KEY hianyzik a Secrets-bol!")
    st.stop()

# Alapbeallitasok
APP_PASSWORD = "admin"
st.set_page_config(page_title="Magyar AI Kepalkoto", page_icon="🎨")

# --- LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    pwd_input = st.text_input("Jelszo", type="password")
    if st.button("OK"):
        if pwd_input == APP_PASSWORD:
            st.session_state['logged_in'] = True
            st.rerun()
    st.stop()

st.title("🎨 Magyar AI Kepalkoto - 404 Nélkül")
st.write("Irj barmit magyarul, es az AI pontosan megrajzolja!")

# --- CHAT INPUT ---
# Ez a mezo mindig az oldal aljan marad
chat_input = st.chat_input("Pl.: 'Egy modern török rendőr kék uniformisban'...")

if chat_input:
    # Megjelenitjük a felhasznalo kereset
    with st.chat_message("user"):
        st.markdown(chat_input)

    # Generalas folyamata
    with st.chat_message("assistant"):
        with st.spinner("AI forditas es rajzolas folyamatban..."):
            try:
                # 1. FORDITAS: A Gemini leforditja a magyar kerest profi angol prompthoz
                # A Gemini nem csak simán fordít, hanem kiegészíti a szükséges kontextussal
                translation_prompt = f"Translate and enhance this image generation request for a realistic photo of a human: '{chat_input}'. Ensure details like clothing style, professional context, realistic lighting, and photorealistic style are included for Pollinations.ai. Only output the English translation, nothing else."
                translated_res = gemini_model.generate_content(translation_prompt)
                english_prompt = translated_res.text.strip()
                
                # Kiirjuk kicsiben, hogy mit forditott, hogy tudd, mi tortenik
                st.caption(f"🇬🇧 AI forditas: {english_prompt}")

                # 2. RAJZOLAS: Pollinations API (nem dob 404-et)
                encoded_prompt = urllib.parse.quote(english_prompt)
                final_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true"
                
                # Kep lekerese
                res = requests.get(final_url)
                
                if res.status_code == 200:
                    # Megjelenitjük a kepet a chaten belul
                    st.image(res.content, use_container_width=True)
                    
                    # Mentes gomb a kep alatt
                    st.download_button(
                        label="📥 Kep mentese",
                        data=res.content,
                        file_name="ai_kep.png",
                        mime="image/png"
                    )
                else:
                    st.error("Sajnos a kepalkoto szerver most nem valaszol.")
            
            except Exception as e:
                st.error(f"Hiba tortent: {e}")

st.divider()
st.caption("Tipp: Minel reszletesebben irod le (angolul), annal szebb lesz a kep! MIvel a Magyar egy szar nyelv! Ha valami nem mukodik rafogom a fideszre ! Created by ddnemet  For support conctact me on discord: ddnemet")
