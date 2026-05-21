import time
import random
import requests
import os

API_URL = os.getenv("API_URL", "https://farmtech-vision-ia.onrender.com")
INTERVALO = int(os.getenv("INTERVALO", "30"))

print("🌱 FarmTech Sensor iniciado...")
print(f"📡 API: {API_URL}")
print(f"⏱ Intervalo: {INTERVALO}s")

while True:
    temperatura = round(random.uniform(20, 40), 1)
    umidade     = round(random.uniform(30, 90), 1)

    try:
        response = requests.get(
            f"{API_URL}/analisar",
            params={"temp": temperatura, "umidade": umidade},
            timeout=40
        )
        dados = response.json()
        risco = dados.get("risco", "?")
        print(f"[OK] Temp={temperatura}°C | Umidade={umidade}% | Risco={risco}")
    except requests.exceptions.Timeout:
        print("[ERRO] Timeout — API demorando para responder")
    except requests.exceptions.ConnectionError:
        print("[ERRO] Sem conexão com a API")
    except Exception as e:
        print(f"[ERRO] {e}")

    time.sleep(INTERVALO)