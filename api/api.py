from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "message": "API IA Vision FarmTech"}

@app.get("/analise")
def analise(temp: float, umidade: float):

    if temp > 40:
        risco = "CRÍTICO 🚨"
        recomendacao = "Ação urgente na plantação"

    elif temp > 35 and umidade < 30:
        risco = "ALTO 🔥"
        recomendacao = "Irrigar imediatamente"

    elif temp > 30:
        risco = "MÉDIO ⚠️"
        recomendacao = "Monitorar irrigação"

    else:
        risco = "BAIXO ✅"
        recomendacao = "Condições ideais"

    return {
        "temperatura": temp,
        "umidade": umidade,
        "risco": risco,
        "acao": recomendacao
    }