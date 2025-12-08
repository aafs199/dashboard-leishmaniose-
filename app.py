import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="VigiLeish - Painel de Vigilância",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONALIZADO (MANTIDO)
# ============================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a5f7a, #2a9d8f);
        color: white;
        padding: 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 5px solid #2a9d8f;
        margin-bottom: 1rem;
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1a5f7a;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2a9d8f;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a5f7a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DADOS DE REFERÊNCIA (HARDCODED PARA PROTÓTIPO)
# ============================================

# Dicionário de cores para a graduação AMARELO -> VERMELHO (Risco)
COLOR_MAP_RISK = {
    'Baixo': '#ffe066',  # Amarelo claro/Seguro
    'Médio': '#ff9900',  # Laranja
    'Alto': '#e74c3c'    # Vermelho
}

# Coordenadas aproximadas das regionais de BH
coordenadas_regionais = {
    'Barreiro': {'lat': -19.9667, 'lon': -44.0333},
    'Centro Sul': {'lat': -19.9333, 'lon': -43.9333},
    'Leste': {'lat': -19.8833, 'lon': -43.8833},
    'Nordeste': {'lat': -19.8500, 'lon': -43.9167},
    'Noroeste': {'lat': -19.9000, 'lon': -43.9667},
    'Norte': {'lat': -19.8500, 'lon': -43.9667},
    'Oeste': {'lat': -19.9167, 'lon': -43.9500},
    'Pampulha': {'lat': -19.8500, 'lon': -43.9833},
    'Venda Nova': {'lat': -19.8167, 'lon': -43.9500},
    'Ignorado': {'lat': -19.9167, 'lon': -43.9333}
}

# Dados regionais (adaptados do seu código)
dados_regionais = pd.DataFrame({
    'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                 'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
    '2024': [1, 0, 1, 0, 0, 0, 0, 0, 0, 0], # Dados ajustados para ter algum caso em 2024
    '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
    '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
    '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
    '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
})

# ... Outros DataFrames (dados_humanos, dados_caninos) omitidos para brevidade ...

# ============================================
# FUNÇÃO PARA CRIAR MAPA INTERATIVO (OTIMIZADA)
# ============================================

def criar_mapa_interativo(ano_selecionado, mostrar_nomes, filtro_risco):
    """Cria um mapa de pontos de dispersão (Scatter Map) com graduação de risco."""
    
    map_data = []
    for idx, row in dados_regionais.iterrows():
        regional = row['Regional']
        
        if regional == 'Ignorado':
            continue
        
        coords = coordenadas_regionais.get(regional)
        lat, lon = coords['lat'], coords['lon']
        casos = row[ano_selecionado]
        
        # Determinar cor e risco (Baixo: 0-1, Médio: 2-4, Alto: 5+)
        if casos <= 1:
            cor = COLOR_MAP_RISK['Baixo']
            risco = "Baixo (0-1 casos)"
        elif casos <= 4:
            cor = COLOR_MAP_RISK['Médio']
            risco = "Médio (2-4 casos)"
        else:
            cor = COLOR_MAP_RISK['Alto']
            risco = "Alto (5+ casos)"
        
        # Filtrar por risco
        if risco not in filtro_risco:
            continue
            
        # Determinar tamanho do marcador proporcional aos casos
        tamanho = 10 + (casos * 4) # Tamanho base 10
        
        map_data.append({
            'Regional': regional,
            'Latitude': lat,
            'Longitude': lon,
            'Casos': casos,
            'Cor_Hex': cor,
            'Risco': risco,
            'Tamanho': tamanho,
            'Texto_Hover': f"<b>{regional}</b><br>Casos em {ano_selecionado}: {casos}<br>Nível de Risco: {risco}"
        })
    
    df_map = pd.DataFrame(map_data)
    
    if df_map.empty:
        return None
    
    # Criar mapa scatter com Plotly
    fig = px.scatter_mapbox(
        df_map,
        lat='Latitude',
        lon='Longitude',
        size='Tamanho',
        color='Risco',
        color_discrete_map={k: v for k, v in zip(COLOR_MAP_RISK.keys(), COLOR_MAP_RISK.values())}, # Usa o mapa de cores definido
        hover_name='Regional',
        hover_data={'Casos': True, 'Risco': True, 'Latitude': False, 'Longitude': False, 'Tamanho': False},
        custom_data=['Texto_Hover'],
        title=f'Distribuição de Casos por Regional - {ano_selecionado}',
        zoom=10,
        height=600
    )
    
    # Atualizar layout do mapa para ser profissional
    fig.update_layout(
        mapbox_style="carto-positron", # Estilo de mapa claro e limpo
        mapbox_zoom=10,
        mapbox_center={"lat": -19.9167, "lon": -43.9333},
        margin={"r":0,"t":40,"l":0,"b":0},
        hovermode='closest',
        legend=dict(title='Nível de Risco')
    )
    
    # Atualizar hovertemplate
    fig.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    
    # Adicionar labels (nomes das regionais) se solicitado
    if mostrar_nomes:
        for idx, row in df_map.iterrows():
            fig.add_trace(
                go.Scattermapbox(
                    lat=[row['Latitude'] + 0.003], # Pequeno offset para o texto não sobrepor o ponto
                    lon=[row['Longitude']],
                    mode='text',
                    text=[row['Regional']],
                    textfont=dict(size=10, color='#1a5f7a'), # Cor do texto mais escura
                    showlegend=False,
                    hoverinfo='skip'
                )
            )
    
    return fig

# ============================================
# SIDEBAR (MANTIDO, mas com pequenas correções de filtro)
# ============================================

# ... Conteúdo da sidebar que você forneceu ...

with st.sidebar:
    st.markdown("### ⚙️ CONTROLES DO MAPA")
    
    # Seletor de ano para o mapa
    anos_disponiveis = [col for col in dados_regionais.columns if col.isdigit()]
    ano_selecionado = st.selectbox(
        "Selecione o ano para o mapa:",
        anos_disponiveis,
        index=anos_disponiveis.index('2023') if '2023' in anos_disponiveis else 0
    )
    
    st.markdown("---")
    st.markdown("### 🎨 OPÇÕES DE VISUALIZAÇÃO")
    
    # Tipo de visualização
    tipo_visualizacao = st.radio(
        "Visualizar por:",
        ["Número de Casos", "Tamanho Relativo", "Cores por Risco"] # Embora apenas o tamanho relativo e cores sejam usados
    )
    
    # Mostrar nomes
    mostrar_nomes = st.checkbox("Mostrar nomes das regionais", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 FILTROS")
    
    # Filtro por nível de risco
    filtro_risco = st.multiselect(
        "Nível de risco (Casos):",
        ["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"],
        default=["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"]
    )
    
    st.markdown("---")
    st.markdown("### 📈 LEGENDA")
    
    st.markdown(f"""
    **Graduação de Risco (Cor):**
    - <span style="color:{COLOR_MAP_RISK['Baixo']}; font-size:1.5rem;">●</span> **Baixo:** 0-1 casos
    - <span style="color:{COLOR_MAP_RISK['Médio']}; font-size:1.5rem;">●</span> **Médio:** 2-4 casos
    - <span style="color:{COLOR_MAP_RISK['Alto']}; font-size:1.5rem;">●</span> **Alto:** 5+ casos
    """, unsafe_allow_html=True)


# ============================================
# LAYOUT PRINCIPAL - TABS (MANTIDO)
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa Interativo", "📊 Dashboard", "📈 Análises", "📋 Dados"])

with tab1:
    st.markdown('<div class="section-title">🗺️ MAPA INTERATIVO DAS REGIONAIS DE BH</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"### 📍 Distribuição Espacial - {ano_selecionado}")
        
        # Chamada da função otimizada
        mapa_fig = criar_mapa_interativo(ano_selecionado, mostrar_nomes, filtro_risco)
        
        if mapa_fig:
            st.plotly_chart(mapa_fig, use_container_width=True)
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
            
        # ... Resto da aba 1 (Estatísticas e Gráfico de Barras) ...
        # (Omitido para foco, mas seu código original para estas seções permanece válido)
