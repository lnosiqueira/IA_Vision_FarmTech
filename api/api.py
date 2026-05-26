from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import oracledb
import random
from datetime import datetime
from twilio.rest import Client
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

# ORACLE THICK MODE (exigido pelo Oracle FIAP)
try:
    oracledb.init_oracle_client()
except Exception:
    pass  # fallback thin mode

app = FastAPI(title="FarmTech Vision IA", version="2.0.0")

from fastapi import Response

@app.head("/")
def health_check():
    return Response(status_code=200)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# 🔐 ORACLE (via .env)
# ================================
def get_connection():
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )

# ================================
# ☁️ AWS SNS (via .env)
# ================================
sns = boto3.client(
    "sns",
    region_name=os.getenv("AWS_REGION", "sa-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

def enviar_email_sns(mensagem: str, assunto: str):
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=mensagem,
            Subject=assunto
        )
        print("[SNS] Email enviado com sucesso")
    except Exception as e:
        print(f"[SNS] Erro ao enviar email: {e}")

# ================================
# 📲 TWILIO WHATSAPP (via .env)
# ================================
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def enviar_whatsapp(mensagem: str):
    try:
        msg = twilio_client.messages.create(
            from_=os.getenv("TWILIO_FROM", "whatsapp:+14155238886"),
            body=mensagem,
            to=os.getenv("TWILIO_TO")
        )
        print(f"[Twilio] WhatsApp enviado: {msg.sid}")
    except Exception as e:
        print(f"[Twilio] Erro: {e}")

# ================================
# 📢 CENTRAL DE ALERTAS
# Dispara SNS + WhatsApp juntos
# ================================
def disparar_alertas(temp: float, umidade: float, risco: str, acao: str):
    mensagem = (
        f"🚨 ALERTA CRÍTICO - FarmTech Vision IA\n\n"
        f"🌡 Temperatura: {temp}°C\n"
        f"💧 Umidade: {umidade}%\n"
        f"⚠️ Risco: {risco}\n"
        f"Ação recomendada: {acao}\n\n"
        f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    # Email via AWS SNS
    enviar_email_sns(
        mensagem=mensagem,
        assunto="🚨 ALERTA CRÍTICO - FarmTech Vision IA"
    )

    # WhatsApp via Twilio
    enviar_whatsapp(mensagem)

    # Salvar em IA_ALERTAS
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO IA_ALERTAS (MENSAGEM, NIVEL, DATA_REGISTRO)
            VALUES (:1, :2, :3)
        """, (mensagem, risco, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Oracle/IA_ALERTAS] Erro: {e}")

# ================================
# 🧠 LÓGICA DE RISCO
# ================================
def calcular_risco(temp: float, umidade: float) -> str:
    if temp > 30 and umidade > 80:
        return "ALTO"
    elif temp > 25 or umidade < 40:
        return "MÉDIO"
    else:
        return "BAIXO"

# ================================
# 🚀 STATUS
# ================================
@app.get("/")
def status():
    return {"status": "API ONLINE 🚀", "versao": "2.0.0"}

# ================================
# 🔥 ANALISAR SENSOR
# ================================
@app.get("/analisar")
def analisar(
    temp: float = Query(default=None),
    umidade: float = Query(default=None)
):
    if temp is None:
        temp = round(random.uniform(20, 40), 1)
    if umidade is None:
        umidade = round(random.uniform(40, 90), 1)

    risco = calcular_risco(temp, umidade)
    acoes = {
        "ALTO":  "🚨 Intervenção imediata!",
        "MÉDIO": "⚠️ Monitorar de perto",
        "BAIXO": "✅ Condições ideais",
    }
    acao = acoes[risco]
    agora = datetime.now()

    # 💾 Salvar em IA_ANALISES
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO IA_ANALISES (TEMPERATURA, UMIDADE, RISCO, ACAO, DATA_REGISTRO)
            VALUES (:1, :2, :3, :4, :5)
        """, (temp, umidade, risco, acao, agora))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Oracle/IA_ANALISES] Erro: {e}")

    # 🚨 Risco ALTO → SNS + WhatsApp + IA_ALERTAS
    if risco == "ALTO":
        disparar_alertas(temp, umidade, risco, acao)

    return {
        "temperatura": temp,
        "umidade":     umidade,
        "risco":       risco,
        "acao":        acao,
        "data":        agora.strftime("%Y-%m-%d %H:%M:%S")
    }

# ================================
# 📊 HISTÓRICO
# ================================
@app.get("/historico")
def historico(limite: int = Query(default=50)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT TEMPERATURA, UMIDADE, RISCO, ACAO, DATA_REGISTRO
            FROM IA_ANALISES
            ORDER BY DATA_REGISTRO DESC
            FETCH FIRST :1 ROWS ONLY
        """, (limite,))
        dados = [
            {
                "temperatura":   r[0],
                "umidade":       r[1],
                "risco":         r[2],
                "acao":          r[3],
                "data_registro": r[4].strftime("%Y-%m-%d %H:%M:%S")
            }
            for r in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return dados
    except Exception as e:
        return {"erro": str(e)}

# ================================
# 📈 ESTATÍSTICAS
# ================================
@app.get("/stats")
def stats():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*)                                           AS total,
                ROUND(AVG(TEMPERATURA), 1)                        AS temp_media,
                ROUND(AVG(UMIDADE), 1)                            AS umid_media,
                SUM(CASE WHEN RISCO = 'ALTO'  THEN 1 ELSE 0 END) AS altos,
                SUM(CASE WHEN RISCO = 'MEDIO' THEN 1 ELSE 0 END) AS medios,
                SUM(CASE WHEN RISCO = 'BAIXO' THEN 1 ELSE 0 END) AS baixos
            FROM IA_ANALISES
        """)
        r = cursor.fetchone()
        cursor.close()
        conn.close()
        return {
            "total_registros":   r[0],
            "temperatura_media": r[1],
            "umidade_media":     r[2],
            "alertas": {
                "alto":  r[3],
                "medio": r[4],
                "baixo": r[5],
            }
        }
    except Exception as e:
        return {"erro": str(e)}

# ================================
# 🔔 ALERTAS RECENTES
# ================================
@app.get("/alertas")
def alertas(limite: int = Query(default=10)):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT MENSAGEM, NIVEL, DATA_REGISTRO
            FROM IA_ALERTAS
            ORDER BY DATA_REGISTRO DESC
            FETCH FIRST :1 ROWS ONLY
        """, (limite,))
        dados = [
            {
                "mensagem":      r[0],
                "nivel":         r[1],
                "data_registro": r[2].strftime("%Y-%m-%d %H:%M:%S")
            }
            for r in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return dados
    except Exception as e:
        return {"erro": str(e)}