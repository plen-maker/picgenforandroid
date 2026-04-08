import streamlit as st
import requests
import urllib.parse

# --- KONFIGURACIO ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]n
except Exception:
    st.error("Hiba: GOOGLE_API_KEY hianyzik a Secrets-bol!")
    st.stop()

APP_PASSWORD = "titkosjelszo123" # A kepeden lathato jelszo

st.set_page_config(page_title="AI Kep Studio", page_icon="https://i.redd.it/rigby-the-cat-v0-xrtpidpxlfif1.jpg?width=1179&format=pjpg&auto=webp&s=a76975fdc042035e8f0be2343a898902f2ce00ca")

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

# --- FORDITO FUNKCIO 
def translate_with_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Translate this to a detailed English image prompt (photorealistic, modern, cinematic): {text}. Only return the English text."
            }]
        }]
    }
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()['candidates'][0]['content']['parts'][0]['text'].strip()
    else:
        return text # Ha hiba van, az eredetit kuldi tovább

# --- APP FELULET ---
st.title("Bena kep generator 😼")
st.write("Irj magyarul, az AI automatikusan fordit es rajzol!")

chat_input = st.chat_input("Ha magyarul irsz bele akkor legyenek ekezetek vagy maskep nem mukodik")

if chat_input:
    with st.chat_message("user"):
        st.markdown(chat_input)

    with st.chat_message("assistant"):
        with st.spinner("AI dolgozik..."):
            try:
                # 1. Fordítás (Saját HTTP hívással, biztosan működik)
                english_prompt = translate_with_gemini(chat_input)
                st.caption(f"🇬🇧 AI Forditas: {english_prompt}")

                # 2. Rajzolás Pollinations-szal
                encoded_prompt = urllib.parse.quote(english_prompt)
                img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&enhance=true&seed=42"
                
                img_res = requests.get(img_url)
                
                if img_res.status_code == 200:
                    st.image(img_res.content, use_container_width=True)
                    st.download_button("📥 Kep mentese", img_res.content, "ai_kep.png", "image/png")
                else:
                    st.error("Kepgeneralasi hiba.")
            except Exception as e:
                st.error(f"Hiba: {e}")

st.divider()
st.caption("Created by ddnemet | Support: ddnemet (Discord)")
