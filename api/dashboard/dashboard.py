import streamlit as st
import requests

st.set_page_config(page_title="IA Vision FarmTech", layout="centered")

st.title("🌱 IA Vision FarmTech")

temp = st.slider("Temperatura", 0, 50, 25)
umidade = st.slider("Umidade", 0, 100, 50)

if st.button("Analisar"):

    url = f"https://farmtech-vision-ia.onrender.com/analise?temp={temp}&umidade={umidade}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        st.subheader("Resultado:")

        risco = data["risco"]

        # 🎨 LÓGICA VISUAL
        if "CRÍTICO" in risco:
            st.error(f"🚨 {risco}")
        elif "ALTO" in risco:
            st.error(f"🔥 {risco}")
        elif "MÉDIO" in risco:
            st.warning(f"⚠️ {risco}")
        else:
            st.success(f"✅ {risco}")

        st.write(f"🌡️ Temperatura: {data['temperatura']}°C")
        st.write(f"💧 Umidade: {data['umidade']}%")

        st.info(f"📌 Ação recomendada: {data['acao']}")

    else:
        st.error("Erro ao conectar com a API 🚨")