from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "message": "API IA Vision FarmTech rodando 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/alerta")
def alerta():
    return {
        "alerta": "Temperatura elevada detectada!",
        "nivel": "alto"
    }

@app.get("/analise")
def analise(temp: float, umidade: float):

    if temp > 40:
    risco = "CRÍTICO 🚨"
    
    if temp > 35 and umidade < 30:
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