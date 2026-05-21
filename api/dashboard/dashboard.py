import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

# =========================
# CONFIG
# =========================
API_URL = "https://farmtech-vision-ia.onrender.com"

st.set_page_config(
    page_title="FarmTech Vision IA",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO COMPLETO — Dark fluido
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0f1a !important;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #0d1117 !important;
    border-right: 1px solid #1a2744;
}

[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #22c55e !important; }

/* Cards métrica */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1e2e 0%, #0d1829 100%);
    border: 1px solid #1a3a5c;
    border-radius: 14px;
    padding: 20px !important;
    transition: border-color 0.3s ease, transform 0.2s ease;
    animation: fadeSlideUp 0.5s ease both;
}
[data-testid="metric-container"]:hover {
    border-color: #22c55e66;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetricValue"] {
    color: #f1f5f9 !important;
    font-size: 28px !important;
    font-weight: 600 !important;
}

/* Títulos */
h1 { color: #22c55e !important; font-weight: 600 !important; letter-spacing: -0.5px; }
h2, h3 { color: #4ade80 !important; font-weight: 500 !important; }

/* Botões */
.stButton > button {
    background: linear-gradient(135deg, #14532d, #166534) !important;
    color: #4ade80 !important;
    border: 1px solid #22c55e44 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.3px;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #166534, #15803d) !important;
    border-color: #22c55e !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(34,197,94,0.2) !important;
}

/* Alertas */
.stSuccess {
    background: linear-gradient(135deg, #052e1688, #14532d88) !important;
    border: 1px solid #22c55e44 !important;
    border-radius: 10px !important;
    color: #4ade80 !important;
    animation: fadeIn 0.4s ease;
}
.stWarning {
    background: linear-gradient(135deg, #1c100088, #78350f88) !important;
    border: 1px solid #f59e0b44 !important;
    border-radius: 10px !important;
    animation: fadeIn 0.4s ease;
}
.stError {
    background: linear-gradient(135deg, #1c000088, #7f1d1d88) !important;
    border: 1px solid #ef444444 !important;
    border-radius: 10px !important;
    animation: fadeIn 0.4s ease;
}
.stInfo {
    background: linear-gradient(135deg, #0c1a2e88, #1e3a5f88) !important;
    border: 1px solid #3b82f644 !important;
    border-radius: 10px !important;
    animation: fadeIn 0.4s ease;
}

/* Tabs */
[data-testid="stTabs"] button {
    color: #64748b !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
    transition: color 0.2s ease !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #22c55e !important;
    border-bottom: 2px solid #22c55e !important;
    background: transparent !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid #1a3a5c !important;
    overflow: hidden;
}

/* Slider */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #22c55e !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div {
    background: #0d1829 !important;
    border-color: #1a3a5c !important;
    border-radius: 8px !important;
}

/* Divider */
hr { border-color: #1a2744 !important; }

/* Download button */
.stDownloadButton > button {
    background: #0d1829 !important;
    color: #60a5fa !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
}

/* Animações */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}

/* Badge de status */
.badge-online {
    display: inline-flex; align-items: center; gap: 6px;
    background: #052e16; color: #4ade80;
    border: 1px solid #22c55e44;
    border-radius: 20px; padding: 4px 12px;
    font-size: 12px; font-weight: 500;
}
.badge-offline {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1c0000; color: #f87171;
    border: 1px solid #ef444444;
    border-radius: 20px; padding: 4px 12px;
    font-size: 12px; font-weight: 500;
}
.dot-pulse {
    width: 7px; height: 7px; border-radius: 50%;
    background: currentColor;
    animation: pulse 1.5s infinite;
    display: inline-block;
}

/* Seção header */
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 4px;
}
.section-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: #052e16; display: flex;
    align-items: center; justify-content: center;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:8px 0 16px">
      <div style="width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#14532d,#15803d);
                  display:flex;align-items:center;justify-content:center;font-size:22px">🌱</div>
      <div>
        <div style="font-size:15px;font-weight:600;color:#f1f5f9">FarmTech Vision IA</div>
        <div style="font-size:11px;color:#4ade80">Monitoramento Agrícola</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### ⚙️ Controles")
    auto_refresh = st.toggle("Atualização automática", value=True)
    intervalo = st.slider("Intervalo (seg)", 10, 120, 30, step=5)

    st.divider()
    st.markdown("### 🌡️ Simular Sensor")
    temp_manual = st.slider("Temperatura (°C)", 0, 50, 25)
    umid_manual = st.slider("Umidade (%)", 0, 100, 60)

    if st.button("🚀 Enviar Leitura", use_container_width=True):
        try:
            r = requests.get(
                f"{API_URL}/analisar",
                params={"temp": temp_manual, "umidade": umid_manual},
                timeout=40
            )
            res = r.json()
            risco_s = res.get("risco", "?")
            if risco_s == "ALTO":
                st.error(f"🚨 Risco: {risco_s}")
            elif risco_s == "MÉDIO":
                st.warning(f"⚠️ Risco: {risco_s}")
            else:
                st.success(f"✅ Risco: {risco_s}")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()
    limite = st.selectbox("Registros no histórico", [20, 50, 100, 200], index=1)
    st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# =========================
# HEADER PRINCIPAL
# =========================
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.title("🌱 FarmTech Vision IA")
    st.caption("Dashboard de monitoramento agrícola em tempo real")
with col_h2:
    st.write("")
    try:
        ping = requests.get(f"{API_URL}/", timeout=30)
        if ping.status_code == 200:
            st.markdown('<div class="badge-online"><span class="dot-pulse"></span>API Online</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-offline"><span class="dot-pulse"></span>Instável</div>', unsafe_allow_html=True)
    except:
        st.markdown('<div class="badge-offline"><span class="dot-pulse"></span>Offline</div>', unsafe_allow_html=True)

st.divider()

# =========================
# BUSCAR DADOS
# =========================
@st.cache_data(ttl=intervalo)
def buscar_leitura():
    try:
        r = requests.get(f"{API_URL}/analisar", timeout=40)
        return r.json()
    except:
        return None

@st.cache_data(ttl=intervalo)
def buscar_historico(lim):
    try:
        r = requests.get(f"{API_URL}/historico", params={"limite": lim}, timeout=40)
        return r.json()
    except:
        return []

@st.cache_data(ttl=intervalo)
def buscar_stats():
    try:
        r = requests.get(f"{API_URL}/stats", timeout=40)
        return r.json()
    except:
        return {}

st.toast("🌱 Conectando à API...", icon="⏳")
leitura  = buscar_leitura()
historico = buscar_historico(limite)
stats    = buscar_stats()

# =========================
# LEITURA ATUAL
# =========================
st.markdown("""
<div class="section-header">
  <div class="section-icon">📊</div>
  <h2 style="margin:0">Leitura Atual</h2>
</div>
""", unsafe_allow_html=True)

if leitura and "erro" not in leitura:
    temp    = leitura.get("temperatura", "--")
    umidade = leitura.get("umidade", "--")
    risco   = leitura.get("risco", "--")
    acao    = leitura.get("acao", "--")
    data_l  = leitura.get("data", "--")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🌡️ Temperatura", f"{temp} °C")
    with c2:
        st.metric("💧 Umidade", f"{umidade} %")
    with c3:
        icone = {"ALTO": "🔴", "MÉDIO": "🟡", "BAIXO": "🟢"}.get(risco, "⚪")
        st.metric("⚠️ Nível de Risco", f"{icone} {risco}")
    with c4:
        hora = str(data_l)[-8:] if len(str(data_l)) >= 8 else data_l
        st.metric("🕐 Última leitura", hora)

    st.write("")
    if risco == "ALTO":
        st.error(f"🚨 **Ação recomendada:** {acao}")
    elif risco == "MÉDIO":
        st.warning(f"⚠️ **Ação recomendada:** {acao}")
    else:
        st.success(f"✅ **Ação recomendada:** {acao}")
else:
    st.error("Não foi possível obter leitura da API. Verifique a conexão.")

st.divider()

# =========================
# ESTATÍSTICAS GERAIS
# =========================
if stats and "erro" not in stats:
    st.markdown("""
    <div class="section-header">
      <div class="section-icon">📈</div>
      <h2 style="margin:0">Estatísticas Gerais</h2>
    </div>
    """, unsafe_allow_html=True)

    alertas = stats.get("alertas", {})
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        st.metric("📋 Total Registros", stats.get("total_registros", 0))
    with s2:
        st.metric("🌡️ Temp. Média", f"{stats.get('temperatura_media', '--')} °C")
    with s3:
        st.metric("💧 Umidade Média", f"{stats.get('umidade_media', '--')} %")
    with s4:
        st.metric("🔴 Alertas Altos", alertas.get("alto", 0))
    with s5:
        st.metric("🟡 Alertas Médios", alertas.get("medio", 0))

    st.divider()

# =========================
# HISTÓRICO + GRÁFICOS
# =========================
st.markdown("""
<div class="section-header">
  <div class="section-icon">📋</div>
  <h2 style="margin:0">Histórico de Leituras</h2>
</div>
""", unsafe_allow_html=True)

if historico and isinstance(historico, list) and len(historico) > 0:
    df = pd.DataFrame(historico)
    df["temperatura"]   = pd.to_numeric(df["temperatura"], errors="coerce")
    df["umidade"]       = pd.to_numeric(df["umidade"], errors="coerce")
    df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
    df = df.sort_values("data_registro")

    mapa_risco = {"BAIXO": 1, "MÉDIO": 2, "ALTO": 3}
    df["risco_num"] = df["risco"].map(mapa_risco)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌡️ Temperatura", "💧 Umidade", "⚠️ Nível de Risco", "📋 Tabela"
    ])

    with tab1:
        st.line_chart(
            df.set_index("data_registro")["temperatura"],
            color="#ef4444",
            use_container_width=True,
            height=280
        )
    with tab2:
        st.line_chart(
            df.set_index("data_registro")["umidade"],
            color="#22c55e",
            use_container_width=True,
            height=280
        )
    with tab3:
        st.area_chart(
            df.set_index("data_registro")["risco_num"],
            color="#f59e0b",
            use_container_width=True,
            height=280
        )
        st.caption("1 = Baixo  |  2 = Médio  |  3 = Alto")

    with tab4:
        st.dataframe(
            df[["data_registro","temperatura","umidade","risco","acao"]]
            .rename(columns={
                "data_registro": "Data/Hora",
                "temperatura":   "Temp (°C)",
                "umidade":       "Umidade (%)",
                "risco":         "Risco",
                "acao":          "Ação"
            }),
            use_container_width=True,
            hide_index=True
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Baixar CSV",
            data=csv,
            file_name=f"farmtech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    st.divider()
    st.markdown("""
    <div class="section-header">
      <div class="section-icon">🔵</div>
      <h2 style="margin:0">Distribuição de Risco</h2>
    </div>
    """, unsafe_allow_html=True)

    contagem = df["risco"].value_counts().reset_index()
    contagem.columns = ["Risco", "Quantidade"]
    st.bar_chart(contagem.set_index("Risco"), use_container_width=True, height=220)

else:
    st.info("Nenhum dado histórico encontrado. Envie uma leitura pelo painel lateral!")

# =========================
# RODAPÉ
# =========================
st.divider()
st.markdown("""
<div style="text-align:center;color:#334155;font-size:12px;padding:8px 0">
  FarmTech Vision IA • Monitoramento Agrícola Inteligente • FIAP
</div>
""", unsafe_allow_html=True)

# =========================
# AUTO REFRESH
# =========================
if auto_refresh:
    time.sleep(intervalo)
    st.cache_data.clear()
    st.rerun()
