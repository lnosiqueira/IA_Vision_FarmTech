import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time
from datetime import datetime

# =========================
# CONFIG
# =========================
API_URL         = "https://farmtech-vision-ia.onrender.com"
OPENMETEO_URL   = "https://api.open-meteo.com/v1/forecast"
SP_LAT, SP_LON  = -23.5505, -46.6333

st.set_page_config(
    page_title="FarmTech Vision IA",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; }
[data-testid="stHeader"]  { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu { display: none !important; }
footer    { display: none !important; }
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0b0f1a !important;
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}
[data-testid="stMainBlockContainer"] { padding-top: 1.5rem !important; }
[data-testid="stSidebar"] {
    background-color: #080d14 !important;
    border-right: 1px solid #0f2240;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #22c55e !important; }
[data-testid="stSidebar"] hr { border-color: #0f2240 !important; margin: 12px 0 !important; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f1e2e 0%, #0d1829 100%);
    border: 1px solid #1a3a5c;
    border-radius: 14px;
    padding: 20px !important;
    transition: border-color 0.3s ease, transform 0.2s ease;
    animation: fadeSlideUp 0.5s ease both;
}
[data-testid="metric-container"]:hover { border-color: #22c55e66; transform: translateY(-2px); }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 12px !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 28px !important; font-weight: 600 !important; }
h1 { color: #22c55e !important; font-weight: 600 !important; letter-spacing: -0.5px; }
h2, h3 { color: #4ade80 !important; font-weight: 500 !important; }
.stButton > button {
    background: linear-gradient(135deg, #14532d, #166534) !important;
    color: #4ade80 !important;
    border: 1px solid #22c55e44 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #166534, #15803d) !important;
    border-color: #22c55e !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(34,197,94,0.2) !important;
}
.stSuccess { background: linear-gradient(135deg, #052e1688, #14532d88) !important; border: 1px solid #22c55e44 !important; border-radius: 10px !important; animation: fadeIn 0.4s ease; }
.stWarning { background: linear-gradient(135deg, #1c100088, #78350f88) !important; border: 1px solid #f59e0b44 !important; border-radius: 10px !important; animation: fadeIn 0.4s ease; }
.stError   { background: linear-gradient(135deg, #1c000088, #7f1d1d88) !important; border: 1px solid #ef444444 !important; border-radius: 10px !important; animation: fadeIn 0.4s ease; }
.stInfo    { background: linear-gradient(135deg, #0c1a2e88, #1e3a5f88) !important; border: 1px solid #3b82f644 !important; border-radius: 10px !important; animation: fadeIn 0.4s ease; }
[data-testid="stTabs"] button { color: #64748b !important; border-radius: 8px 8px 0 0 !important; font-weight: 500 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color: #22c55e !important; border-bottom: 2px solid #22c55e !important; background: transparent !important; }
[data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid #1a3a5c !important; overflow: hidden; }
hr { border-color: #1a2744 !important; }
.stDownloadButton > button { background: #0d1829 !important; color: #60a5fa !important; border: 1px solid #1e3a5f !important; border-radius: 8px !important; }
.badge-online  { display:inline-flex;align-items:center;gap:6px;background:#052e16;color:#4ade80;border:1px solid #22c55e44;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:500; }
.badge-offline { display:inline-flex;align-items:center;gap:6px;background:#1c0000;color:#f87171;border:1px solid #ef444444;border-radius:20px;padding:4px 12px;font-size:12px;font-weight:500; }
.dot-pulse { width:7px;height:7px;border-radius:50%;background:currentColor;animation:pulse 1.5s infinite;display:inline-block; }
.section-header { display:flex;align-items:center;gap:10px;margin-bottom:4px; }
.section-icon   { width:32px;height:32px;border-radius:8px;background:#052e16;display:flex;align-items:center;justify-content:center;font-size:16px; }
@keyframes fadeSlideUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn      { from{opacity:0} to{opacity:1} }
@keyframes pulse       { 0%,100%{opacity:1} 50%{opacity:.4} }
</style>
""", unsafe_allow_html=True)

# =========================
# BUSCAR CLIMA REAL SP (Open-Meteo, gratuito sem API key)
# =========================
@st.cache_data(ttl=600)
def buscar_clima_sp():
    try:
        r = requests.get(OPENMETEO_URL, params={
            "latitude":           SP_LAT,
            "longitude":          SP_LON,
            "current":            "temperature_2m,relative_humidity_2m,weathercode",
            "hourly":             "temperature_2m,relative_humidity_2m",
            "forecast_days":      1,
            "timezone":           "America/Sao_Paulo"
        }, timeout=10)
        d = r.json()
        cur = d.get("current", {})
        return {
            "temp":    round(cur.get("temperature_2m", 0), 1),
            "umidade": cur.get("relative_humidity_2m", 0),
            "hora":    cur.get("time", "")[-5:],
        }
    except:
        return None

# =========================
# BUSCAR DADOS DA API
# =========================
@st.cache_data(ttl=30)
def buscar_leitura():
    try:
        r = requests.get(f"{API_URL}/analisar", timeout=40)
        return r.json()
    except:
        return None

@st.cache_data(ttl=30)
def buscar_historico(lim):
    try:
        r = requests.get(f"{API_URL}/historico", params={"limite": lim}, timeout=40)
        return r.json()
    except:
        return []

@st.cache_data(ttl=30)
def buscar_stats():
    try:
        r = requests.get(f"{API_URL}/stats", timeout=40)
        return r.json()
    except:
        return {}

# =========================
# PLOTLY — tema dark padrão
# =========================
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0b1120",
    font=dict(color="#94a3b8", family="Inter"),
    xaxis=dict(gridcolor="#1a2744", zerolinecolor="#1a2744"),
    yaxis=dict(gridcolor="#1a2744", zerolinecolor="#1a2744"),
    margin=dict(l=10, r=10, t=30, b=10),
)

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
    intervalo    = st.slider("Intervalo (seg)", 10, 120, 30, step=5)

    st.divider()
    st.markdown("### 🌡️ Simular Sensor")
    temp_manual = st.slider("Temperatura (°C)", 0, 50, 25)
    umid_manual = st.slider("Umidade (%)", 0, 100, 60)

    if st.button("🚀 Enviar Leitura", use_container_width=True):
        try:
            r = requests.get(f"{API_URL}/analisar",
                params={"temp": temp_manual, "umidade": umid_manual}, timeout=40)
            res   = r.json()
            risco = res.get("risco", "?")
            if risco == "ALTO":   st.error(f"🚨 Risco: {risco}")
            elif risco == "MÉDIO": st.warning(f"⚠️ Risco: {risco}")
            else:                  st.success(f"✅ Risco: {risco}")
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Erro: {e}")

    st.divider()
    limite = st.selectbox("Registros no histórico", [20, 50, 100, 200], index=1)
    st.caption(f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# =========================
# HEADER
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
# CARREGAR DADOS
# =========================
clima    = buscar_clima_sp()
leitura  = buscar_leitura()
historico = buscar_historico(limite)
stats    = buscar_stats()

# =========================
# CLIMA REAL SÃO PAULO
# =========================
st.markdown("""
<div class="section-header">
  <div class="section-icon">🌤️</div>
  <h2 style="margin:0">Clima Real — São Paulo</h2>
</div>
""", unsafe_allow_html=True)

if clima:
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        st.metric("🌡️ Temperatura SP agora", f"{clima['temp']} °C")
    with cc2:
        st.metric("💧 Umidade relativa SP", f"{clima['umidade']} %")
    with cc3:
        st.metric("🕐 Última atualização", clima['hora'])
else:
    st.warning("Não foi possível obter clima de São Paulo.")

st.divider()

# =========================
# LEITURA ATUAL SENSOR
# =========================
st.markdown("""
<div class="section-header">
  <div class="section-icon">📊</div>
  <h2 style="margin:0">Leitura Atual do Sensor</h2>
</div>
""", unsafe_allow_html=True)

if leitura and "erro" not in leitura:
    temp    = leitura.get("temperatura", "--")
    umidade = leitura.get("umidade", "--")
    risco   = leitura.get("risco", "--")
    acao    = leitura.get("acao", "--")
    data_l  = leitura.get("data", "--")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🌡️ Temperatura", f"{temp} °C",
        delta=f"{round(temp - clima['temp'], 1)}°C vs SP" if clima and isinstance(temp, (int,float)) else None)
    with c2: st.metric("💧 Umidade", f"{umidade} %",
        delta=f"{round(umidade - clima['umidade'], 1)}% vs SP" if clima and isinstance(umidade, (int,float)) else None)
    with c3:
        icone = {"ALTO":"🔴","MÉDIO":"🟡","BAIXO":"🟢"}.get(risco,"⚪")
        st.metric("⚠️ Nível de Risco", f"{icone} {risco}")
    with c4:
        hora = str(data_l)[-8:] if len(str(data_l)) >= 8 else data_l
        st.metric("🕐 Última leitura", hora)

    st.write("")
    if risco == "ALTO":   st.error(f"🚨 **Ação recomendada:** {acao}")
    elif risco == "MÉDIO": st.warning(f"⚠️ **Ação recomendada:** {acao}")
    else:                  st.success(f"✅ **Ação recomendada:** {acao}")
else:
    st.error("Não foi possível obter leitura da API.")

st.divider()

# =========================
# ESTATÍSTICAS
# =========================
if stats and "erro" not in stats:
    st.markdown("""
    <div class="section-header">
      <div class="section-icon">📈</div>
      <h2 style="margin:0">Estatísticas Gerais</h2>
    </div>
    """, unsafe_allow_html=True)

    alertas = stats.get("alertas", {})
    s1,s2,s3,s4,s5 = st.columns(5)
    with s1: st.metric("📋 Total Registros",  stats.get("total_registros", 0))
    with s2: st.metric("🌡️ Temp. Média",      f"{stats.get('temperatura_media','--')} °C")
    with s3: st.metric("💧 Umidade Média",    f"{stats.get('umidade_media','--')} %")
    with s4: st.metric("🔴 Alertas Altos",    alertas.get("alto", 0))
    with s5: st.metric("🟡 Alertas Médios",   alertas.get("medio", 0))
    st.divider()

# =========================
# GRÁFICOS PLOTLY INTERATIVOS
# =========================
st.markdown("""
<div class="section-header">
  <div class="section-icon">📉</div>
  <h2 style="margin:0">Gráficos Interativos</h2>
</div>
""", unsafe_allow_html=True)

if historico and isinstance(historico, list) and len(historico) > 0:
    df = pd.DataFrame(historico)
    df["temperatura"]   = pd.to_numeric(df["temperatura"], errors="coerce")
    df["umidade"]       = pd.to_numeric(df["umidade"], errors="coerce")
    df["data_registro"] = pd.to_datetime(df["data_registro"], errors="coerce")
    df = df.sort_values("data_registro")
    mapa_risco = {"BAIXO":1,"MÉDIO":2,"ALTO":3}
    df["risco_num"] = df["risco"].map(mapa_risco)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️ Temperatura", "💧 Umidade", "⚠️ Risco", "📊 Comparativo", "📋 Tabela"
    ])

    with tab1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["data_registro"], y=df["temperatura"],
            mode="lines+markers",
            name="Temperatura",
            line=dict(color="#ef4444", width=2),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(239,68,68,0.08)",
            hovertemplate="<b>%{x}</b><br>Temperatura: %{y}°C<extra></extra>"
        ))
        if clima:
            fig.add_hline(y=clima["temp"], line_dash="dash",
                line_color="#f97316", annotation_text=f"SP agora: {clima['temp']}°C",
                annotation_font_color="#f97316")
        fig.update_layout(**PLOTLY_LAYOUT, title="Temperatura ao longo do tempo",
            yaxis_title="°C", height=340)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df["data_registro"], y=df["umidade"],
            mode="lines+markers",
            name="Umidade",
            line=dict(color="#22c55e", width=2),
            marker=dict(size=5),
            fill="tozeroy",
            fillcolor="rgba(34,197,94,0.08)",
            hovertemplate="<b>%{x}</b><br>Umidade: %{y}%<extra></extra>"
        ))
        if clima:
            fig2.add_hline(y=clima["umidade"], line_dash="dash",
                line_color="#60a5fa", annotation_text=f"SP agora: {clima['umidade']}%",
                annotation_font_color="#60a5fa")
        fig2.update_layout(**PLOTLY_LAYOUT, title="Umidade do solo ao longo do tempo",
            yaxis_title="%", height=340)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        cores_risco = df["risco"].map({"BAIXO":"#22c55e","MÉDIO":"#f59e0b","ALTO":"#ef4444"})
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=df["data_registro"], y=df["risco_num"],
            marker_color=cores_risco,
            name="Risco",
            hovertemplate="<b>%{x}</b><br>Risco: %{customdata}<extra></extra>",
            customdata=df["risco"]
        ))
        fig3.update_layout(**PLOTLY_LAYOUT, title="Nível de risco ao longo do tempo",
            yaxis=dict(tickvals=[1,2,3], ticktext=["Baixo","Médio","Alto"],
                       gridcolor="#1a2744"),
            height=340)
        st.plotly_chart(fig3, use_container_width=True)

    with tab4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            x=df["data_registro"], y=df["temperatura"],
            name="Temperatura (°C)", line=dict(color="#ef4444", width=2),
            hovertemplate="Temp: %{y}°C<extra></extra>"
        ))
        fig4.add_trace(go.Scatter(
            x=df["data_registro"], y=df["umidade"],
            name="Umidade (%)", line=dict(color="#22c55e", width=2),
            yaxis="y2",
            hovertemplate="Umidade: %{y}%<extra></extra>"
        ))
        fig4.update_layout(
            **PLOTLY_LAYOUT,
            title="Temperatura vs Umidade",
            height=340,
            yaxis=dict(title="Temperatura (°C)", gridcolor="#1a2744", color="#ef4444"),
            yaxis2=dict(title="Umidade (%)", overlaying="y", side="right",
                        gridcolor="#1a2744", color="#22c55e"),
            legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1a2744")
        )
        st.plotly_chart(fig4, use_container_width=True)

        # Pizza distribuição risco
        contagem = df["risco"].value_counts()
        fig5 = go.Figure(go.Pie(
            labels=contagem.index,
            values=contagem.values,
            hole=0.5,
            marker=dict(colors=["#22c55e","#f59e0b","#ef4444"]),
            hovertemplate="%{label}: %{value} leituras (%{percent})<extra></extra>"
        ))
        fig5.update_layout(**PLOTLY_LAYOUT, title="Distribuição de risco", height=300)
        st.plotly_chart(fig5, use_container_width=True)

    with tab5:
        st.dataframe(
            df[["data_registro","temperatura","umidade","risco","acao"]]
            .rename(columns={
                "data_registro":"Data/Hora","temperatura":"Temp (°C)",
                "umidade":"Umidade (%)","risco":"Risco","acao":"Ação"
            }),
            use_container_width=True, hide_index=True
        )
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", data=csv,
            file_name=f"farmtech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv")
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
