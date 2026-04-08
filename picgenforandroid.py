import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import random

# Oldal konfiguráció (telefon barát megjelenés)
st.set_page_config(
    page_title="AI Kép Generátor Mobil",
    page_icon="🎨",
    layout="centered"
)

# Cím és leírás
st.title("🎨 AI Kép Generátor Mobil")
st.markdown("Írd le magyarul vagy angolul, mit szeretnél látni, és az AI megrajzolja!")

# Beviteli mező a promptnak (leírásnak)
prompt = st.text_area(
    "Mit rajzoljak?",
    placeholder="pl: Egy cyberpunk macska űrruhában, realisztikus, 8k",
    height=150
)

# Stílus választó (ez sokat segít telefonon)
style = st.selectbox(
    "Stílus kiválasztása:",
    ["Realisztikus", "Anime", "Digitális Művészet", "Manga", "Pixel Art", "3D Render", "Vízfesték"]
)

# Kép generálása gomb
if st.button("KÉP GENERÁLÁSA ✨", type="primary"):
    if prompt:
        # Animált várakozó ikon
        with st.spinner("Az AI éppen alkot... Kérlek várj egy pillanatot."):
            try:
                # Bővítjük a promptot a kiválasztott stílussal a jobb eredményért
                final_prompt = f"{prompt}, {style}, highly detailed, intricate, masterpiece"
                
                # Ingyenes, kulcs nélküli API (Pollinations.ai)
                # Használunk egy véletlen számot (seed), hogy minden generálás egyedi legyen
                seed = random.randint(0, 999999)
                # Kódoljuk a promptot az URL formátumhoz (szóközök kicserélése)
                encoded_prompt = final_prompt.replace(" ", "%20") 
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}"
                
                # Kép letöltése az API-tól
                response = requests.get(image_url)
                
                if response.status_code == 200:
                    image_bytes = BytesIO(response.content)
                    img = Image.open(image_bytes)
                    
                    # Kép megjelenítése a telefon képernyőjén
                    st.image(img, caption=f"Generált kép: {prompt}", use_container_width=True)
                    
                    # Letöltés gomb, hogy el tudja menteni a telefonjára
                    st.download_button(
                        label="📥 KÉP MENTÉSE",
                        data=image_bytes,
                        file_name=f"ai_image_{seed}.png",
                        mime="image/png"
                    )
                else:
                    st.error("❌ Hiba történt a kép generálása közben (Szerver hiba). Próbáld újra!")
            except Exception as e:
                st.error(f"❌ Váratlan hiba történt: {e}")
    else:
        st.warning("⚠️ Kérlek, először írd le, mit szeretnél látni!")

# Lábléc
st.markdown("---")
st.caption("Powered by Pollinations.ai (Ingyenes, kulcs nélküli képalkotó)")