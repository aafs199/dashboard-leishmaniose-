import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import folium
from streamlit_folium import folium_static
from branca.colormap import LinearColormap
import json

# ============================================
# CONFIGURAÇÃO DA PÁGINA COM DESENHO UNIVERSAL
# ============================================

st.set_page_config(
    page_title="VigiLeish - Painel de Vigilância da Leishmaniose",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PERSONALIZADO COM PRINCÍPIOS DE DESENHO UNIVERSAL
# ============================================

st.markdown("""
<style>
    /* PRINCÍPIO 1: IGUALITÁRIO - Acessível para todos */
    :root {
        --primary: #2c3e50;
        --secondary: #3498db;
        --accent: #e74c3c;
        --success: #27ae60;
        --warning: #f39c12;
        --light: #ecf0f1;
        --dark: #2c3e50;
        --text-primary: #2c3e50;
        --text-secondary: #7f8c8d;
        --contrast-ratio: 4.5; /* WCAG AA */
    }
    
    /* Contraste adequado para daltonismo */
    .colorblind-friendly {
        color: var(--text-primary);
        background-color: var(--light);
    }
    
    /* PRINCÍPIO 2: ADAPTÁVEL - Responsivo e flexível */
    @media (max-width: 768px) {
        .metric-card {
            padding: 1rem !important;
        }
        .metric-value {
            font-size: 2rem !important;
        }
    }
    
    /* Tamanhos de fonte relativos para zoom do navegador */
    html {
        font-size: 16px;
    }
    
    /* PRINCÍPIO 3: INTUITIVO - Navegação clara */
    .stApp {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
    }
    
    /* Indicadores visuais claros */
    .active-tab {
        border-bottom: 3px solid var(--secondary) !important;
        font-weight: bold !important;
    }
    
    /* PRINCÍPIO 4: INFORMAÇÃO DE FÁCIL PERCEPÇÃO */
    /* Alto contraste para texto */
    .high-contrast {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    
    /* Tamanho de fonte mínimo WCAG */
    * {
        font-size: min(1rem, 16px);
    }
    
    /* Espaçamento adequado para leitura */
    p, li, .metric-title {
        line-height: 1.8;
        letter-spacing: 0.3px;
    }
    
    /* Labels descritivos */
    [aria-label]:hover::after {
        content: attr(aria-label);
        position: absolute;
        background: var(--dark);
        color: white;
        padding: 0.5rem;
        border-radius: 4px;
        z-index: 1000;
    }
    
    /* PRINCÍPIO 5: TOLERÂNCIA AO ERRO */
    /* Confirmação para ações críticas */
    .danger-action {
        background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
        color: white !important;
        border: 2px solid #c0392b !important;
    }
    
    .danger-action:hover {
        background: linear-gradient(135deg, #c0392b, #a93226) !important;
        transform: scale(1.02);
    }
    
    /* Feedback visual para ações */
    .success-feedback {
        animation: pulse-green 2s ease-in-out;
    }
    
    @keyframes pulse-green {
        0%, 100% { background-color: white; }
        50% { background-color: rgba(39, 174, 96, 0.1); }
    }
    
    /* PRINCÍPIO 6: BAIXO ESFORÇO FÍSICO */
    /* Áreas clicáveis grandes */
    button, .clickable {
        min-height: 44px !important; /* Tamanho mínimo WCAG */
        min-width: 44px !important;
        padding: 12px 24px !important;
    }
    
    /* Espaçamento entre elementos interativos */
    .stButton > button {
        margin: 8px 0;
    }
    
    /* PRINCÍPIO 7: TAMANHO E ESPAÇO PARA USO */
    /* Espaço adequado para toque */
    .touch-friendly {
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Texto não justificado para dislexia */
    p, div, span {
        text-align: left !important;
    }
    
    /* Fonte sans-serif para melhor legibilidade */
    * {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
    }
    
    /* ESTILOS DO VIGILEISH */
    .main-header {
        background: linear-gradient(135deg, var(--primary), #34495e);
        color: white;
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }
    
    .accessibility-bar {
        background: var(--light);
        padding: 0.5rem 2rem;
        display: flex;
        gap: 1rem;
        align-items: center;
        border-bottom: 1px solid #ddd;
    }
    
    .accessibility-button {
        background: none;
        border: 1px solid var(--secondary);
        color: var(--secondary);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        cursor: pointer;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 5px solid var(--secondary);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .section-divider {
        height: 4px;
        background: linear-gradient(90deg, var(--secondary), var(--accent));
        margin: 2rem 0;
        border-radius: 2px;
    }
    
    /* WCAG - Foco visível para navegação por teclado */
    :focus {
        outline: 3px solid var(--secondary) !important;
        outline-offset: 2px !important;
    }
    
    /* Modo alto contraste */
    .high-contrast-mode {
        filter: invert(1) hue-rotate(180deg);
    }
    
    /* Suporte a leitores de tela */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# BARRA DE ACESSIBILIDADE
# ============================================

st.markdown("""
<div class="accessibility-bar" role="toolbar" aria-label="Ferramentas de acessibilidade">
    <span class="sr-only">Ferramentas de acessibilidade:</span>
    <button class="accessibility-button" onclick="toggleHighContrast()" aria-label="Ativar modo alto contraste">
        🌗 Alto Contraste
    </button>
    <button class="accessibility-button" onclick="increaseFontSize()" aria-label="Aumentar tamanho da fonte">
        🔍 A+ 
    </button>
    <button class="accessibility-button" onclick="decreaseFontSize()" aria-label="Diminuir tamanho da fonte">
        🔍 A-
    </button>
    <button class="accessibility-button" onclick="activateScreenReader()" aria-label="Ativar leitor de tela">
        🔊 Ler Conteúdo
    </button>
</div>

<script>
function toggleHighContrast() {
    document.body.classList.toggle('high-contrast-mode');
    alert('Modo alto contraste ' + (document.body.classList.contains('high-contrast-mode') ? 'ativado' : 'desativado'));
}

function increaseFontSize() {
    var currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    document.documentElement.style.fontSize = (currentSize + 2) + 'px';
}

function decreaseFontSize() {
    var currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    if (currentSize > 12) {
        document.documentElement.style.fontSize = (currentSize - 2) + 'px';
    }
}

function activateScreenReader() {
    // Em produção, integrar com API de leitura
    alert('Funcionalidade de leitor de tela ativada. Use Tab para navegar.');
}
</script>
""", unsafe_allow_html=True)

# ============================================
# CABEÇALHO COM TODAS AS INFORMAÇÕES DO PROJETO
# ============================================

st.markdown(f"""
<div class="main-header" role="banner">
    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2.2rem;">🏥 VigiLeish</h1>
        <span style="background: rgba(255,255,255,0.2); padding: 0.25rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            Painel de Vigilância Epidemiológica
        </span>
    </div>
    
    <p style="margin: 0 0 1rem 0; opacity: 0.95; max-width: 800px;">
        <strong>Sistema interativo para monitoramento e prevenção da Leishmaniose Visceral em Belo Horizonte - MG</strong>
    </p>
    
    <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem;">
        <span style="background: rgba(52, 152, 219, 0.2); color: #3498db; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(52, 152, 219, 0.3);">
            📊 ODS 3: Saúde e Bem-Estar
        </span>
        <span style="background: rgba(46, 204, 113, 0.2); color: #27ae60; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(46, 204, 113, 0.3);">
            🎯 ODS 10: Redução de Desigualdades
        </span>
        <span style="background: rgba(155, 89, 182, 0.2); color: #8e44ad; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(155, 89, 182, 0.3);">
            🏙️ ODS 11: Cidades Sustentáveis
        </span>
        <span style="background: rgba(241, 196, 15, 0.2); color: #f39c12; padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.85rem; border: 1px solid rgba(241, 196, 15, 0.3);">
            🤝 ODS 17: Parcerias
        </span>
    </div>
    
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.9;">
        <strong>Atividade Extensionista II - UNINTER | CST Ciência de Dados</strong><br>
        Aline Alice Ferreira da Silva (RU: 5277514) | Naiara Chaves Figueiredo (RU: 5281798)
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# FUNÇÕES PARA CARREGAR DADOS REAIS
# ============================================

@st.cache_data
def carregar_dados_completos():
    """Carrega todos os dados necessários para o painel"""
    # Dados humanos anuais
    dados_humanos = pd.DataFrame({
        'Ano': list(range(1994, 2026)),
        'Casos': [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 110, 
                 160, 145, 131, 93, 54, 40, 39, 48, 51, 64, 39, 41, 30, 30, 24, 30, 29, 11],
        'Óbitos': [6, 4, 4, 3, 4, 3, 9, 10, 8, 9, 25, 9, 12, 6, 18, 31, 23, 
                   14, 12, 5, 3, 7, 7, 12, 5, 7, 1, 3, 5, 6, 8, 0],
        'População': [2084100, 2106819, 2091371, 2109223, 2124176, 2139125, 2238332, 
                      2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 
                      2238332, 2238332, 2375151, 2375151, 2375151, 2375151, 2375151, 
                      2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 
                      2315560, 2315560, 2315560, 2315560]
    })
    
    dados_humanos['Incidência_100k'] = (dados_humanos['Casos'] / dados_humanos['População'] * 100000).round(2)
    dados_humanos['Letalidade_%'] = (dados_humanos['Óbitos'] / dados_humanos['Casos'].replace(0, 1) * 100).round(2)
    
    # Dados regionais
    dados_regionais = pd.DataFrame({
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                    'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
        '2024': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        '2023': [2, 1, 0, 6, 5, 0, 4, 0, 4, 1],
        '2022': [0, 0, 3, 3, 6, 4, 1, 0, 2, 3],
        '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
        '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0],
        '2019': [4, 0, 3, 6, 8, 3, 5, 2, 8, 3],
        '2018': [1, 3, 7, 7, 5, 8, 3, 1, 2, 3]
    })
    
    # Dados caninos
    dados_caninos = pd.DataFrame({
        'Ano': list(range(2014, 2025)),
        'Sorologias_Realizadas': [44536, 20659, 22965, 33029, 31330, 27983, 
                                 28954, 17044, 23490, 43571, 49927],
        'Cães_Soropositivos': [6198, 3807, 5529, 6539, 6591, 6165, 
                               5624, 3539, 4077, 5440, 4459],
        'Imóveis_Borrifados': [54436, 56475, 5617, 19538, 26388, 14855, 
                               73593, 78279, 64967, 51591, 30953]
    })
    
    dados_caninos['Positividade_%'] = (dados_caninos['Cães_Soropositivos'] / 
                                      dados_caninos['Sorologias_Realizadas'].replace(0, 1) * 100).round(2)
    
    return dados_humanos, dados_regionais, dados_caninos

# ============================================
# DADOS GEOESPACIAIS PARA MAPA DE BH
# ============================================

@st.cache_data
def carregar_coordenadas_regionais():
    """Coordenadas aproximadas dos centros das regionais de BH"""
    return {
        'Barreiro': [-19.9667, -44.0333],
        'Centro Sul': [-19.9333, -43.9333],
        'Leste': [-19.8833, -43.8833],
        'Nordeste': [-19.8500, -43.9167],
        'Noroeste': [-19.9000, -43.9667],
        'Norte': [-19.8500, -43.9667],
        'Oeste': [-19.9167, -43.9500],
        'Pampulha': [-19.8500, -43.9833],
        'Venda Nova': [-19.8167, -43.9500],
        'Ignorado': [-19.9167, -43.9333]  # Centro da cidade
    }

# ============================================
# MODO DE VISUALIZAÇÃO (Profissional x Comunidade)
# ============================================

modo = st.radio(
    "**Selecione o modo de visualização:**",
    ["👨‍⚕️ Modo Profissional (Gestores)", "👥 Modo Comunitário (Público Geral)"],
    horizontal=True,
    key="modo_visualizacao"
)

# ============================================
# CARREGAR DADOS
# ============================================

with st.spinner('🔄 Carregando dados de vigilância epidemiológica...'):
    dados_humanos, dados_regionais, dados_caninos = carregar_dados_completos()
    coordenadas = carregar_coordenadas_regionais()

# ============================================
# SEÇÃO DE FILTROS DINÂMICOS
# ============================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h2 style="margin-bottom: 1rem;">🔍 FILTROS E PARÂMETROS DE ANÁLISE</h2>', unsafe_allow_html=True)

# Container para filtros
with st.container():
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    
    with col_f1:
        ano_min = int(dados_humanos['Ano'].min())
        ano_max = int(dados_humanos['Ano'].max())
        anos_selecionados = st.slider(
            "Período de Análise",
            min_value=ano_min,
            max_value=ano_max,
            value=(2015, 2024),
            help="Selecione o intervalo de anos para análise"
        )
    
    with col_f2:
        regionais = list(dados_regionais['Regional'])
        regionais_selecionadas = st.multiselect(
            "Regionais",
            options=regionais,
            default=regionais[:5],
            help="Selecione as regionais para análise"
        )
    
    with col_f3:
        tipo_analise = st.selectbox(
            "Tipo de Análise",
            ["Casos Totais", "Incidência (por 100k hab.)", "Letalidade", "Casos vs Controle Vetorial"],
            help="Escolha o tipo de análise a ser realizada"
        )
    
    with col_f4:
        agregacao_temporal = st.selectbox(
            "Agregação Temporal",
            ["Anual", "Quinquenal (5 anos)", "Por Década"],
            help="Nível de agregação dos dados temporais"
        )
    
    # Botão para limpar filtros
    col_reset1, col_reset2, col_reset3 = st.columns([1, 2, 1])
    with col_reset2:
        if st.button("🔄 Limpar Todos os Filtros", use_container_width=True):
            st.rerun()

# ============================================
# CALCULAR MÉTRICAS COM FILTROS
# ============================================

# Aplicar filtro de anos
dados_filtrados = dados_humanos[
    (dados_humanos['Ano'] >= anos_selecionados[0]) & 
    (dados_humanos['Ano'] <= anos_selecionados[1])
]

# Métricas principais
total_casos_periodo = int(dados_filtrados['Casos'].sum())
media_letalidade = dados_filtrados['Letalidade_%'].mean().round(1)
incidencia_media = dados_filtrados['Incidência_100k'].mean().round(2)

# Cálculo de variação
if len(dados_filtrados) > 1:
    casos_primeiro_ano = dados_filtrados.iloc[0]['Casos']
    casos_ultimo_ano = dados_filtrados.iloc[-1]['Casos']
    if casos_primeiro_ano > 0:
        variacao = ((casos_ultimo_ano - casos_primeiro_ano) / casos_primeiro_ano * 100).round(1)
    else:
        variacao = 0
else:
    variacao = 0

# ============================================
# SEÇÃO 1: INDICADORES-CHAVE
# ============================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h2>📊 INDICADORES PRINCIPAIS</h2>', unsafe_allow_html=True)

# Cards de métricas
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card" role="region" aria-label="Casos no período">
        <div class="metric-title" aria-hidden="true">📅 CASOS NO PERÍODO</div>
        <div class="metric-value" aria-label="{total_casos_periodo} casos no período selecionado">
            {total_casos_periodo:,}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            {anos_selecionados[0]}-{anos_selecionados[1]}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    variacao_classe = "negative" if variacao > 0 else "positive"
    variacao_text = f"{'+' if variacao > 0 else ''}{variacao}%"
    
    st.markdown(f"""
    <div class="metric-card" role="region" aria-label="Variação de casos">
        <div class="metric-title" aria-hidden="true">📈 VARIAÇÃO</div>
        <div class="metric-value" aria-label="Variação de {variacao} por cento">
            {variacao_text}
        </div>
        <div class="metric-change {variacao_classe}" aria-hidden="true">
            {"🔼 Aumento" if variacao > 0 else "🔽 Redução"}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card" role="region" aria-label="Letalidade média">
        <div class="metric-title" aria-hidden="true">⚡ LETALIDADE MÉDIA</div>
        <div class="metric-value" aria-label="Letalidade média de {media_letalidade} por cento">
            {media_letalidade}%
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            Taxa de óbitos
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card" role="region" aria-label="Incidência média">
        <div class="metric-title" aria-hidden="true">📊 INCIDÊNCIA MÉDIA</div>
        <div class="metric-value" aria-label="Incidência média de {incidencia_media} por 100 mil habitantes">
            {incidencia_media}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            por 100 mil hab.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    # Regional com mais casos no último ano
    if '2023' in dados_regionais.columns:
        idx_max = dados_regionais['2023'].idxmax()
        reg_prioritaria = dados_regionais.loc[idx_max, 'Regional']
        casos_reg = dados_regionais.loc[idx_max, '2023']
    else:
        reg_prioritaria = "Nordeste"
        casos_reg = 8
    
    st.markdown(f"""
    <div class="metric-card" role="region" aria-label="Regional prioritária">
        <div class="metric-title" aria-hidden="true">🎯 PRIORIDADE ATUAL</div>
        <div class="metric-value" aria-label="Regional prioritária: {reg_prioritaria}">
            {reg_prioritaria[:10]}
        </div>
        <div style="font-size: 0.9rem; color: var(--text-secondary);">
            {casos_reg} casos (2023)
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# SEÇÃO 2: MAPA INTERATIVO DE BH
# ============================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h2>🗺️ MAPA DE DISTRIBUIÇÃO ESPACIAL</h2>', unsafe_allow_html=True)

# Container para o mapa
map_container = st.container()

with map_container:
    # Criar mapa centrado em BH
    m = folium.Map(location=[-19.9167, -43.9333], zoom_start=11, control_scale=True)
    
    # Adicionar pontos para cada regional
    for regional in dados_regionais['Regional']:
        if regional in coordenadas and regional != 'Ignorado':
            lat, lon = coordenadas[regional]
            
            # Número de casos em 2023 (ou último ano disponível)
            casos = dados_regionais[dados_regionais['Regional'] == regional]['2023'].values[0]
            
            # Definir cor baseada no número de casos
            if casos == 0:
                color = 'green'
            elif casos <= 3:
                color = 'orange'
            else:
                color = 'red'
            
            # Criar popup informativo
            popup_html = f"""
            <div style="min-width: 200px;">
                <h4 style="margin: 0; color: #2c3e50;">{regional}</h4>
                <hr style="margin: 5px 0;">
                <p style="margin: 5px 0;"><strong>Casos (2023):</strong> {casos}</p>
                <p style="margin: 5px 0;"><strong>Status:</strong> {"🟢 Baixo risco" if casos == 0 else "🟡 Médio risco" if casos <= 3 else "🔴 Alto risco"}</p>
                <p style="margin: 5px 0; font-size: 0.9em; color: #7f8c8d;">
                    Clique para mais informações
                </p>
            </div>
            """
            
            # Adicionar marcador
            folium.CircleMarker(
                location=[lat, lon],
                radius=15 + (casos * 2),  # Tamanho proporcional aos casos
                popup=folium.Popup(popup_html, max_width=300),
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"{regional}: {casos} casos"
            ).add_to(m)
    
    # Adicionar legenda
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 180px; height: 120px; 
                background-color: white; border: 2px solid grey; z-index: 9999;
                font-size: 12px; padding: 10px; border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <h4 style="margin-top: 0; margin-bottom: 10px;">Legenda</h4>
        <p style="margin: 5px 0;">
            <span style="color: green;">●</span> Baixo risco (0 casos)
        </p>
        <p style="margin: 5px 0;">
            <span style="color: orange;">●</span> Médio risco (1-3 casos)
        </p>
        <p style="margin: 5px 0;">
            <span style="color: red;">●</span> Alto risco (>3 casos)
        </p>
        <p style="margin: 5px 0; font-size: 10px; color: grey;">
            Tamanho = Nº de casos
        </p>
    </div>
    '''
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Exibir mapa
    folium_static(m, width=1200, height=500)

# ============================================
# SEÇÃO 3: ANÁLISE TEMPORAL AVANÇADA
# ============================================

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h2>📈 ANÁLISE TEMPORAL AVANÇADA</h2>', unsafe_allow_html=True)

# Gráficos temporais
col_temp1, col_temp2 = st.columns(2)

with col_temp1:
    # Gráfico de série temporal com área
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Casos'],
        mode='lines+markers',
        name='Casos',
        line=dict(color='#3498db', width=3),
        fill='tozeroy',
        fillcolor='rgba(52, 152, 219, 0.2)',
        hovertemplate='<b>Ano %{x}</b><br>Casos: %{y}<extra></extra>'
    ))
    
    fig1.update_layout(
        title='Evolução dos Casos de LV (1994-2025)',
        xaxis_title='Ano',
        yaxis_title='Número de Casos',
        height=400,
        template='plotly_white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig1, use_container_width=True)

with col_temp2:
    # Gráfico de barras comparativo
    anos_comparar = [2020, 2021, 2022, 2023]
    
    # Preparar dados para comparação
    comparacao_data = []
    for ano in anos_comparar:
        if str(ano) in dados_regionais.columns:
            total_ano = dados_regionais[str(ano)].sum()
            comparacao_data.append({
                'Ano': ano,
                'Casos': total_ano,
                'Incidência': (total_ano / 2315560 * 100000).round(2)  # População aproximada
            })
    
    if comparacao_data:
        df_comparacao = pd.DataFrame(comparacao_data)
        
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig2.add_trace(go.Bar(
            x=df_comparacao['Ano'],
            y=df_comparacao['Casos'],
            name='Casos',
            marker_color='#2ecc71',
            opacity=0.7,
            hovertemplate='<b>Ano %{x}</b><br>Casos: %{y}<extra></extra>'
        ), secondary_y=False)
        
        fig2.add_trace(go.Scatter(
            x=df_comparacao['Ano'],
            y=df_comparacao['Incidência'],
            name='Incidência',
            line=dict(color='#e74c3c', width=3),
            mode='lines+markers',
            hovertemplate='<b>Ano %{x}</b><br>Incidência: %{y:.2f}/100k<extra></extra>'
        ), secondary_y=True)
        
        fig2.update_layout(
            title='Comparativo de Casos e Incidência (2020-2023)',
            xaxis_title='Ano',
            height=400,
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig2.update_yaxes(title_text="
