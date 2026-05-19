import streamlit as st
import requests

st.title("🌱 IA Vision FarmTech")

temp = st.slider("Temperatura", 0, 50, 25)
umidade = st.slider("Umidade", 0, 100, 50)

if st.button("Analisar"):
    url = f"https://farmtech-vision-ia.onrender.com/analise?temp={temp}&umidade={umidade}"
    
    response = requests.get(url)
    data = response.json()

    st.subheader("Resultado:")
    st.write(data)