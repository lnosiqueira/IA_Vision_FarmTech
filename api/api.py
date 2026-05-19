from fastapi import FastAPI
import os

app = FastAPI()

# ================================
# ROTA PRINCIPAL
# ================================
@app.get("/")
def home():
    return {
        "status": "online",
        "message": "API IA Vision FarmTech rodando 🚀"
    }


# ================================
# TESTE DE SAÚDE
# ================================
@app.get("/health")
def health_check():
    return {"health": "ok"}


# ================================
# EXEMPLO DE ALERTA (SIMULADO)
# ================================
@app.get("/alerta")
def alerta():
    return {
        "alerta": "Temperatura elevada detectada!",
        "nivel": "alto"
    }