import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import io

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="Vigileish - Painel de Vigilância da Leishmaniose",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PERSONALIZADO - VIGILEISH
# ============================================

st.markdown("""
<style>
    /* CORES TEMÁTICAS LEISHMANIOSE/SAÚDE PÚBLICA */
    :root {
        --primary: #1a5f7a;     /* Azul saúde pública */
        --secondary: #57cc99;   /* Verde prevenção */
        --accent: #ff9a3c;      /* Laranja alerta */
        --warning: #ff6b6b;     /* Vermelho risco */
        --light: #f8f9fa;
        --dark: #2d3436;
        --gray: #636e72;
    }
    
    /* ESTILO GERAL */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    /* CABEÇALHO VIGILEISH */
    .main-header {
        background: linear-gradient(90deg, var(--primary) 0%, #2a9d8f 100%);
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        margin-bottom: 2.5rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 20%);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        margin-bottom: 0.8rem;
    }
    
    .logo-text {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(to right, #ffffff, #e0f7fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 300;
        max-width: 800px;
        line-height: 1.6;
    }
    
    /* CARDS DE MÉTRICA - DESIGN MODERNO */
    .metric-card {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border-top: 4px solid var(--primary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card:hover::after {
        transform: scaleX(1);
    }
    
    .metric-title {
        font-size: 0.85rem;
        color: var(--gray);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: var(--dark);
        line-height: 1;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, var(--dark), #444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-change {
        font-size: 0.9rem;
        margin-top: 0.8rem;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    .positive { 
        background: linear-gradient(135deg, rgba(87, 204, 153, 0.15), rgba(87, 204, 153, 0.05));
        color: #2a9d8f;
        border: 1px solid rgba(87, 204, 153, 0.3);
    }
    
    .negative { 
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 107, 107, 0.05));
        color: #e63946;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    .neutral { 
        background: linear-gradient(135deg, rgba(99, 110, 114, 0.15), rgba(99, 110, 114, 0.05));
        color: var(--gray);
        border: 1px solid rgba(99, 110, 114, 0.3);
    }
    
    /* SEÇÕES */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--dark);
        margin: 3rem 0 1.5rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, var(--primary), var(--secondary)) 1;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .section-header::before {
        content: '';
        width: 6px;
        height: 30px;
        background: linear-gradient(to bottom, var(--primary), var(--secondary));
        border-radius: 3px;
    }
    
    /* GRÁFICOS CONTAINER */
    .chart-container {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
        border: 1px solid rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    
    .chart-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    /* BADGES MODERNOS */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
        border: 1px solid;
    }
    
    .badge-primary { 
        background: linear-gradient(135deg, rgba(26, 95, 122, 0.15), rgba(26, 95, 122, 0.05));
        color: var(--primary);
        border-color: rgba(26, 95, 122, 0.3);
    }
    
    .badge-success { 
        background: linear-gradient(135deg, rgba(87, 204, 153, 0.15), rgba(87, 204, 153, 0.05));
        color: #2a9d8f;
        border-color: rgba(87, 204, 153, 0.3);
    }
    
    .badge-warning { 
        background: linear-gradient(135deg, rgba(255, 154, 60, 0.15), rgba(255, 154, 60, 0.05));
        color: #e76f51;
        border-color: rgba(255, 154, 60, 0.3);
    }
    
    .badge-danger { 
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 107, 107, 0.05));
        color: #e63946;
        border-color: rgba(255, 107, 107, 0.3);
    }
    
    /* TABS MODERNAS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 12px 12px 0 0;
        padding: 1rem 1.5rem;
        border: 1px solid rgba(0,0,0,0.1);
        border-bottom: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary), #2a9d8f);
        color: white;
        box-shadow: 0 4px 15px rgba(26, 95, 122, 0.3);
    }
    
    /* FOOTER */
    .footer {
        background: linear-gradient(90deg, var(--dark), #1a1a2e);
        color: white;
        padding: 2.5rem;
        border-radius: 20px 20px 0 0;
        margin-top: 4rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .footer::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .footer-logo {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    
    .footer-text {
        font-size: 0.95rem;
        opacity: 0.85;
        line-height: 1.7;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* ANIMAÇÕES */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* SCROLLBAR PERSONALIZADA */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2a9d8f, var(--primary));
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES PARA CARREGAR SEUS DADOS REAIS
# ============================================

@st.cache_data
def carregar_dados_humanos_reais():
    """Carrega dados humanos do arquivo incidencialetalidadelv.xlsx"""
    try:
        # Usando os dados do primeiro arquivo
        data = {
            'Ano': list(range(1994, 2026)),
            'Casos incidentes': [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 110, 
                                160, 145, 131, 93, 54, 40, 39, 48, 51, 64, 39, 41, 30, 30, 24, 30, 29, 11],
            'População': [2084100, 2106819, 2091371, 2109223, 2124176, 2139125, 2238332, 
                          2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 
                          2238332, 2238332, 2375151, 2375151, 2375151, 2375151, 2375151, 
                          2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 
                          2315560, 2315560, 2315560, 2315560],
            'Óbitos incidentes': [6, 4, 4, 3, 4, 3, 9, 10, 8, 9, 25, 9, 12, 6, 18, 31, 23, 
                                  14, 12, 5, 3, 7, 7, 12, 5, 7, 1, 3, 5, 6, 8, 0]
        }
        
        df = pd.DataFrame(data)
        df['Incidência_100k'] = (df['Casos incidentes'] / df['População'] * 100000).round(2)
        df['Letalidade_%'] = (df['Óbitos incidentes'] / df['Casos incidentes'].replace(0, 1) * 100).round(2)
        df['Casos prevalentes'] = [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 114, 
                                  163, 151, 139, 100, 62, 57, 48, 61, 62, 73, 44, 50, 38, 32, 31, 37, 34, 17]
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados humanos: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_regionais_reais():
    """Carrega dados regionais do arquivo casoshumanoslvregional.xlsx"""
    try:
        # Dados da planilha Pág PBH
        data = {
            'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                        'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
            '2008': [11, 8, 15, 42, 28, 13, 9, 5, 26, 4],
            '2009': [13, 7, 9, 16, 25, 19, 16, 7, 24, 10],
            '2010': [18, 2, 14, 27, 16, 11, 15, 10, 13, 6],
            '2011': [10, 6, 12, 11, 11, 10, 7, 5, 16, 5],
            '2012': [6, 2, 9, 7, 10, 7, 5, 2, 5, 4],
            '2013': [5, 2, 8, 5, 2, 2, 6, 5, 2, 5],
            '2014': [3, 2, 3, 7, 5, 6, 4, 2, 6, 3],
            '2015': [7, 4, 6, 6, 7, 5, 1, 2, 7, 3],
            '2016': [6, 6, 2, 10, 4, 6, 1, 3, 12, 2],
            '2017': [8, 1, 1, 14, 9, 9, 6, 6, 10, 2],
            '2018': [1, 3, 7, 7, 5, 8, 3, 1, 2, 3],
            '2019': [4, 0, 3, 6, 8, 3, 5, 2, 8, 3],
            '2020': [1, 2, 3, 1, 7, 4, 1, 1, 6, 4],
            '2021': [2, 0, 0, 4, 5, 2, 2, 6, 4, 5],
            '2022': [0, 0, 3, 3, 6, 4, 1, 0, 2, 3],
            '2023': [2, 1, 0, 6, 5, 0, 4, 0, 4, 1],
            '2024': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        }
        
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados regionais: {e}")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_caninos_reais():
    """Carrega dados de vigilância canina dos arquivos anuais"""
    try:
        # Consolidando dados de todos os períodos
        data_antiga = {
            'Ano': list(range(1994, 2004)),
            'Sorologias_Realizadas': [13869, 122291, 108022, 142286, 54980, 105636, 
                                     106894, 84512, 161918, 118403],
            'Cães_Soropositivos': [554, 3965, 4691, 4531, 2426, 4042, 3316, 4325, 9095, 10605],
            'Cães_Eutanasiados': [0, 0, 3617, 4332, 1419, 2836, 3150, 4096, 6415, 7577],
            'Imóveis_Borrifados': [4302, 46743, 46604, 22525, 12443, 46129, 61355, 53336, 122824, 125823]
        }
        
        data_media = {
            'Ano': list(range(2004, 2014)),
            'Sorologias_Realizadas': [82181, 149470, 83866, 155643, 163089, 153519, 
                                     197232, 171937, 202896, 113997],
            'Cães_Soropositivos': [6119, 11901, 8268, 14476, 12482, 10472, 
                                   15494, 9722, 6434, 4862],
            'Cães_Eutanasiados': [5652, 9197, 8014, 10738, 10285, 9873, 
                                  11541, 8122, 5573, 4128],
            'Imóveis_Borrifados': [145266, 160671, 146917, 104241, 76439, 79716, 
                                   66801, 87908, 80282, 74455]
        }
        
        data_recente = {
            'Ano': list(range(2014, 2025)),
            'Sorologias_Realizadas': [44536, 20659, 22965, 33029, 31330, 27983, 
                                     28954, 17044, 23490, 43571, 49927],
            'Cães_Soropositivos': [6198, 3807, 5529, 6539, 6591, 6165, 
                                   5624, 3539, 4077, 5440, 4459],
            'Cães_Eutanasiados': [5075, 3387, 4202, 4511, 5582, 4764, 
                                  4438, 3028, 2567, 3388, 2725],
            'Imóveis_Borrifados': [54436, 56475, 5617, 19538, 26388, 14855, 
                                   73593, 78279, 64967, 51591, 30953]
        }
        
        df1 = pd.DataFrame(data_antiga)
        df2 = pd.DataFrame(data_media)
        df3 = pd.DataFrame(data_recente)
        
        df = pd.concat([df1, df2, df3], ignore_index=True)
        df['Positividade_%'] = (df['Cães_Soropositivos'] / df['Sorologias_Realizadas'].replace(0, 1) * 100).round(2)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados caninos: {e}")
        return pd.DataFrame()

# ============================================
# CABEÇALHO VIGILEISH
# ============================================

st.markdown(f"""
<div class="main-header fade-in">
    <div class="logo-container">
        <h1 class="logo-text">🏥 VIGILEISH - PAINEL DE VIGILÂNCIA EPIDEMIOLÓGICA</h1>
    </div>
    <p class="subtitle">
        Sistema Inteligente de Monitoramento e Prevenção da Leishmaniose Visceral em Belo Horizonte - MG
    </p>
    <div style="display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap;">
        <span class="badge badge-primary">📊 Dados Reais 1994-2025</span>
        <span class="badge badge-success">🔄 Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
        <span class="badge badge-warning">🎯 ODS 3: Saúde e Bem-Estar</span>
        <span class="badge badge-danger">⚠️ Monitoramento Ativo de Zoonoses</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# CARREGAR DADOS REAIS
# ============================================

with st.spinner('🔄 Carregando dados de vigilância epidemiológica...'):
    dados_humanos = carregar_dados_humanos_reais()
    dados_regionais = carregar_dados_regionais_reais()
    dados_caninos = carregar_dados_caninos_reais()

if dados_humanos.empty or dados_regionais.empty or dados_caninos.empty:
    st.error("❌ Erro ao carregar os dados. Verifique os arquivos de entrada.")
    st.stop()

# ============================================
# CÁLCULO DAS MÉTRICAS PRINCIPAIS
# ============================================

ultimo_ano = 2024  # Último ano completo nos dados
casos_ultimo_ano = dados_humanos[dados_humanos['Ano'] == ultimo_ano]['Casos incidentes'].values[0] if not dados_humanos.empty else 0

# Cálculo seguro da variação
try:
    casos_ano_anterior = dados_humanos[dados_humanos['Ano'] == ultimo_ano-1]['Casos incidentes'].values[0] if ultimo_ano-1 in dados_humanos['Ano'].values else 0
    if casos_ano_anterior > 0:
        variacao_casos = ((casos_ultimo_ano - casos_ano_anterior) / casos_ano_anterior * 100).round(1)
    else:
        variacao_casos = 100.0 if casos_ultimo_ano > 0 else 0.0
except:
    variacao_casos = 0.0

# Outras métricas
letalidade_media = dados_humanos['Letalidade_%'].tail(5).mean().round(1) if not dados_humanos.empty else 0
total_casos = int(dados_humanos['Casos incidentes'].sum()) if not dados_humanos.empty else 0
incidencia_atual = dados_humanos[dados_humanos['Ano'] == ultimo_ano]['Incidência_100k'].values[0] if not dados_humanos.empty else 0

# Regional com mais casos em 2024
try:
    if '2024' in dados_regionais.columns:
        reg_mais_casos = dados_regionais.loc[dados_regionais['2024'].idxmax(), 'Regional']
        casos_reg = dados_regionais['2024'].max()
    else:
        reg_mais_casos = "N/A"
        casos_reg = 0
except:
    reg_mais_casos = "N/A"
    casos_reg = 0

# ============================================
# SEÇÃO 1: INDICADORES-CHAVE (KPI CARDS)
# ============================================

st.markdown('<div class="section-header fade-in">📊 VISÃO GERAL DA SITUAÇÃO EPIDEMIOLÓGICA</div>', unsafe_allow_html=True)

# Criar colunas para os cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    variacao_text = f"{'+' if variacao_casos > 0 else ''}{variacao_casos}% vs {ultimo_ano-1}"
    variacao_classe = "negative" if variacao_casos > 0 else "positive"
    
    st.markdown(f"""
    <div class="metric-card fade-in" style="animation-delay: 0.1s">
        <div class="metric-title">📍 CASOS EM {ultimo_ano}</div>
        <div class="metric-value">{int(casos_ultimo_ano):,}</div>
        <div class="metric-change {variacao_classe}">📈 {variacao_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card fade-in" style="animation-delay: 0.2s">
        <div class="metric-title">⚡ LETALIDADE MÉDIA</div>
        <div class="metric-value">{letalidade_media}%</div>
        <div class="metric-change neutral">📅 Últimos 5 anos</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card fade-in" style="animation-delay: 0.3s">
        <div class="metric-title">📈 INCIDÊNCIA ATUAL</div>
        <div class="metric-value">{incidencia_atual:.2f}</div>
        <div class="metric-title">por 100 mil habitantes</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card fade-in" style="animation-delay: 0.4s">
        <div class="metric-title">📊 TOTAL HISTÓRICO</div>
        <div class="metric-value">{total_casos:,}</div>
        <div class="metric-change neutral">📋 desde 1994</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card fade-in" style="animation-delay: 0.5s">
        <div class="metric-title">🎯 PRIORIDADE REGIONAL</div>
        <div class="metric-value">{reg_mais_casos[:12]}</div>
        <div class="metric-change warning">📍 {casos_reg} casos (2024)</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# SEÇÃO 2: ANÁLISE TEMPORAL DETALHADA
# ============================================

st.markdown('<div class="section-header fade-in">📈 EVOLUÇÃO HISTÓRICA DA DOENÇA (1994-2025)</div>', unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="chart-container fade-in">', unsafe_allow_html=True)
    
    # Gráfico de Casos com área - Dados reais
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Casos incidentes'],
        mode='lines',
        name='Casos Incidentes',
        line=dict(color='#1a5f7a', width=4),
        fill='tozeroy',
        fillcolor='rgba(26, 95, 122, 0.15)',
        hovertemplate='<b>Ano %{x}</b><br>Casos: %{y}<br>Incidência: %{customdata:.2f}/100k<extra></extra>',
        customdata=dados_humanos['Incidência_100k']
    ))
    
    # Adicionar média móvel de 5 anos
    if len(dados_humanos) >= 5:
        dados_humanos['MM5'] = dados_humanos['Casos incidentes'].rolling(window=5, center=True).mean()
        
        fig1.add_trace(go.Scatter(
            x=dados_humanos['Ano'],
            y=dados_humanos['MM5'],
            mode='lines',
            name='Tendência (MM5)',
            line=dict(color='#ff9a3c', width=3, dash='dash'),
            hovertemplate='<b>Ano %{x}</b><br>Tendência: %{y:.0f} casos<extra></extra>'
        ))
    
    fig1.update_layout(
        title='Casos de Leishmaniose Visceral em Belo Horizonte',
        xaxis_title='Ano',
        yaxis_title='Número de Casos',
        height=450,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-container fade-in">', unsafe_allow_html=True)
    
    # Gráfico combinado de Letalidade e Incidência
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Letalidade_%'],
        mode='lines+markers',
        name='Letalidade (%)',
        line=dict(color='#e63946', width=3),
        marker=dict(size=7),
        hovertemplate='<b>Ano %{x}</b><br>Letalidade: %{y:.1f}%<extra></extra>'
    ), secondary_y=False)
    
    fig2.add_trace(go.Bar(
        x=dados_humanos['Ano'],
        y=dados_humanos['Casos incidentes'],
        name='Casos',
        marker_color='rgba(87, 204, 153, 0.7)',
        opacity=0.7,
        hovertemplate='<b>Ano %{x}</b><br>Casos: %{y}<extra></extra>'
    ), secondary_y=True)
    
    fig2.update_layout(
        title='Letalidade vs Casos Registrados',
        xaxis_title='Ano',
        height=450,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig2.update_yaxes(title_text="Letalidade (%)", secondary_y=False, range=[0, dados_humanos['Letalidade_%'].max() * 1.2])
    fig2.update_yaxes(title_text="Número de Casos", secondary_y=True)
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SEÇÃO 3: DISTRIBUIÇÃO GEOGRÁFICA DETALHADA
# ============================================

st.markdown('<div class="section-header fade-in">🗺️ DISTRIBUIÇÃO ESPACIAL POR REGIONAL (2008-2024)</div>', unsafe_allow_html=True)

# Criar tabs para diferentes visualizações
tab_geo1, tab_
