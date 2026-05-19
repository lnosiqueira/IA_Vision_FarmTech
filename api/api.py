@app.get("/analise")
def analise(temp: float, umidade: float):
    
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