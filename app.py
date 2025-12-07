import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import sqlite3
from pathlib import Path

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
# CSS PERSONALIZADO
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
    
    .map-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
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
# DADOS DAS REGIONAIS DE BH (REAIS)
# ============================================

# Coordenadas aproximadas das regionais de BH
coordenadas_regionais = {
    'Barreiro': {'lat': -19.9667, 'lon': -44.0333, 'x': 0.1, 'y': 0.1},
    'Centro Sul': {'lat': -19.9333, 'lon': -43.9333, 'x': 0.5, 'y': 0.3},
    'Leste': {'lat': -19.8833, 'lon': -43.8833, 'x': 0.8, 'y': 0.6},
    'Nordeste': {'lat': -19.8500, 'lon': -43.9167, 'x': 0.7, 'y': 0.7},
    'Noroeste': {'lat': -19.9000, 'lon': -43.9667, 'x': 0.4, 'y': 0.4},
    'Norte': {'lat': -19.8500, 'lon': -43.9667, 'x': 0.6, 'y': 0.8},
    'Oeste': {'lat': -19.9167, 'lon': -43.9500, 'x': 0.3, 'y': 0.5},
    'Pampulha': {'lat': -19.8500, 'lon': -43.9833, 'x': 0.5, 'y': 0.9},
    'Venda Nova': {'lat': -19.8167, 'lon': -43.9500, 'x': 0.9, 'y': 0.9},
    'Ignorado': {'lat': -19.9167, 'lon': -43.9333, 'x': 0.5, 'y': 0.5}
}

# Dados reais dos seus arquivos
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

# Calcular indicadores
dados_humanos['Incidência_100k'] = (dados_humanos['Casos'] / dados_humanos['População'] * 100000).round(2)
dados_humanos['Letalidade_%'] = (dados_humanos['Óbitos'] / dados_humanos['Casos'].replace(0, 1) * 100).round(2)

# Dados regionais (seus dados reais)
dados_regionais = pd.DataFrame({
    'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
    '2024': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
    '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
    '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
    '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
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

# ============================================
# CABEÇALHO PRINCIPAL
# ============================================

st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.2rem;">🏥 VIGILEISH - PAINEL DE VIGILÂNCIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
        Sistema de Monitoramento da Leishmaniose Visceral em Belo Horizonte - MG
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            📊 Dados Reais 1994-2025
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🗺️ 10 Regionais de BH
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🎓 Atividade Extensionista UNINTER
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR COM CONTROLES
# ============================================

with st.sidebar:
    st.markdown("### ⚙️ CONTROLES DO MAPA")
    
    # Seletor de ano para o mapa
    anos_disponiveis = ['2024', '2023', '2022', '2021', '2020']
    ano_selecionado = st.selectbox(
        "Selecione o ano para o mapa:",
        anos_disponiveis,
        index=1  # 2023 como padrão
    )
    
    st.markdown("---")
    st.markdown("### 🎨 OPÇÕES DE VISUALIZAÇÃO")
    
    # Tipo de visualização
    tipo_visualizacao = st.radio(
        "Visualizar por:",
        ["Número de Casos", "Tamanho Relativo", "Cores por Risco"]
    )
    
    # Mostrar nomes
    mostrar_nomes = st.checkbox("Mostrar nomes das regionais", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 FILTROS")
    
    # Filtro por nível de risco
    filtro_risco = st.multiselect(
        "Nível de risco:",
        ["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"],
        default=["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"]
    )
    
    st.markdown("---")
    st.markdown("### 📈 LEGENDA")
    
    # Legenda interativa
    st.markdown("""
    **Cores dos marcadores:**
    - 🟢 **Verde:** Baixo risco (0-1 casos)
    - 🟡 **Laranja:** Médio risco (2-4 casos)
    - 🔴 **Vermelho:** Alto risco (5+ casos)
    
    **Tamanho:** Proporcional ao número de casos
    """)

# ============================================
# FUNÇÃO PARA CRIAR MAPA INTERATIVO
# ============================================

def criar_mapa_interativo(ano_selecionado, tipo_visualizacao, mostrar_nomes, filtro_risco):
    """Cria um mapa interativo das regionais de BH usando Plotly"""
    
    # Preparar dados para o mapa
    map_data = []
    for idx, row in dados_regionais.iterrows():
        regional = row['Regional']
        
        if regional == 'Ignorado':
            continue
        
        # Obter coordenadas
        coords = coordenadas_regionais.get(regional, {'lat': -19.9167, 'lon': -43.9333})
        lat, lon = coords['lat'], coords['lon']
        
        # Dados do ano selecionado
        casos = row[ano_selecionado]
        
        # Determinar cor baseada no risco
        if casos == 0:
            cor = '#27ae60'  # Verde
            risco = "Baixo"
        elif casos <= 3:
            cor = '#f39c12'  # Laranja
            risco = "Médio"
        else:
            cor = '#e74c3c'  # Vermelho
            risco = "Alto"
        
        # Verificar se passa no filtro de risco
        if filtro_risco:
            if not any(filtro in f"{risco} ({casos} casos)" for filtro in filtro_risco):
                continue
        
        # Determinar tamanho baseado no tipo de visualização
        if tipo_visualizacao == "Número de Casos":
            tamanho = casos * 5 + 10
        else:
            tamanho = 20 + (casos * 3)
        
        map_data.append({
            'Regional': regional,
            'Latitude': lat,
            'Longitude': lon,
            'Casos': casos,
            'Cor': cor,
            'Risco': risco,
            'Tamanho': tamanho,
            'Texto': f"<b>{regional}</b><br>Casos em {ano_selecionado}: {casos}<br>Nível de Risco: {risco}"
        })
    
    df_map = pd.DataFrame(map_data)
    
    if df_map.empty:
        st.warning("Nenhuma regional corresponde aos filtros selecionados.")
        return None
    
    # Criar mapa scatter com Plotly
    fig = px.scatter_mapbox(
        df_map,
        lat='Latitude',
        lon='Longitude',
        size='Tamanho',
        color='Risco',
        color_discrete_map={
            'Baixo': '#27ae60',
            'Médio': '#f39c12',
            'Alto': '#e74c3c'
        },
        hover_name='Regional',
        hover_data={
            'Casos': True,
            'Latitude': False,
            'Longitude': False,
            'Tamanho': False,
            'Risco': True
        },
        custom_data=['Texto'],
        title=f'Mapa de Distribuição de Casos - {ano_selecionado}',
        zoom=10,
        height=600
    )
    
    # Atualizar layout do mapa
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10,
        mapbox_center={"lat": -19.9167, "lon": -43.9333},
        margin={"r":0,"t":40,"l":0,"b":0},
        hovermode='closest'
    )
    
    # Atualizar hovertemplate
    fig.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>'
    )
    
    # Adicionar labels se solicitado
    if mostrar_nomes:
        for idx, row in df_map.iterrows():
            fig.add_trace(
                go.Scattermapbox(
                    lat=[row['Latitude'] + 0.003],
                    lon=[row['Longitude']],
                    mode='text',
                    text=[row['Regional']],
                    textfont=dict(size=10, color=row['Cor']),
                    showlegend=False,
                    hoverinfo='skip'
                )
            )
    
    return fig

# ============================================
# LAYOUT PRINCIPAL - TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa Interativo", "📊 Dashboard", "📈 Análises", "📋 Dados"])

with tab1:
    st.markdown('<div class="section-title">🗺️ MAPA INTERATIVO DAS REGIONAIS DE BH</div>', unsafe_allow_html=True)
    
    # Container para o mapa
    with st.container():
        st.markdown(f"### 📍 Distribuição Espacial - {ano_selecionado}")
        
        # Criar e exibir o mapa
        mapa_fig = criar_mapa_interativo(ano_selecionado, tipo_visualizacao, mostrar_nomes, filtro_risco)
        
        if mapa_fig:
            st.plotly_chart(mapa_fig, use_container_width=True)
            
            # Estatísticas abaixo do mapa
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                total_casos_ano = dados_regionais[ano_selecionado].sum()
                st.metric(f"Total de Casos ({ano_selecionado})", total_casos_ano)
            
            with col_stats2:
                reg_mais_casos = dados_regionais.loc[dados_regionais[ano_selecionado].idxmax(), 'Regional']
                casos_max = dados_regionais[ano_selecionado].max()
                st.metric("Regional com mais casos", f"{reg_mais_casos} ({casos_max})")
            
            with col_stats3:
                regionais_sem_casos = (dados_regionais[ano_selecionado] == 0).sum()
                st.metric("Regionais sem casos", regionais_sem_casos)
            
            # Gráfico de barras complementar
            st.markdown("#### 📊 DISTRIBUIÇÃO DETALHADA")
            
            df_ano = dados_regionais[['Regional', ano_selecionado]].copy()
            df_ano = df_ano[df_ano['Regional'] != 'Ignorado']
            df_ano = df_ano.sort_values(ano_selecionado)
            
            fig_barras = px.bar(
                df_ano,
                x=ano_selecionado,
                y='Regional',
                orientation='h',
                title=f'Casos por Regional - {ano_selecionado}',
                color=ano_selecionado,
                color_continuous_scale='RdYlGn_r',
                height=400
            )
            
            fig_barras.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_barras, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">📊 DASHBOARD DE MONITORAMENTO</div>', unsafe_allow_html=True)
    
    # Filtros para dashboard
    col_dash1, col_dash2 = st.columns(2)
    
    with col_dash1:
        ano_inicio = st.slider("Ano inicial:", 1994, 2024, 2015, key="dash_ini")
        ano_fim = st.slider("Ano final:", 1994, 2024, 2024, key="dash_fim")
    
    with col_dash2:
        indicador_principal = st.selectbox(
            "Indicador principal:",
            ["Casos Totais", "Incidência", "Letalidade", "Evolução Temporal"]
        )
    
    # Métricas principais
    st.markdown("### 🎯 INDICADORES-CHAVE")
    
    col_met1, col_met2, col_met3, col_met4 = st.columns(4)
    
    with col_met1:
        casos_periodo = dados_humanos[
            (dados_humanos['Ano'] >= ano_inicio) & 
            (dados_humanos['Ano'] <= ano_fim)
        ]['Casos'].sum()
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Total de Casos</div>
            <div style="font-size: 2rem; font-weight: bold; color: #1a5f7a;">{casos_periodo:,}</div>
            <div style="font-size: 0.8rem; color: #888;">{ano_inicio}-{ano_fim}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met2:
        letalidade_media = dados_humanos['Letalidade_%'].mean().round(1)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Letalidade Média</div>
            <div style="font-size: 2rem; font-weight: bold; color: #e74c3c;">{letalidade_media}%</div>
            <div style="font-size: 0.8rem; color: #888;">1994-2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met3:
        incidencia_atual = dados_humanos[dados_humanos['Ano'] == 2023]['Incidência_100k'].values[0]
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Incidência Atual</div>
            <div style="font-size: 2rem; font-weight: bold; color: #2a9d8f;">{incidencia_atual:.2f}</div>
            <div style="font-size: 0.8rem; color: #888;">por 100k hab. (2023)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_met4:
        reg_prioritaria = "Nordeste"
        casos_reg = 7
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Prioridade Regional</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #f39c12;">{reg_prioritaria}</div>
            <div style="font-size: 0.8rem; color: #888;">{casos_reg} casos (2023)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos do dashboard
    st.markdown("### 📈 VISUALIZAÇÕES")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico de evolução temporal
        dados_periodo = dados_humanos[
            (dados_humanos['Ano'] >= ano_inicio) & 
            (dados_humanos['Ano'] <= ano_fim)
        ]
        
        fig_evolucao = px.line(
            dados_periodo,
            x='Ano',
            y='Casos',
            title='Evolução dos Casos de LV',
            markers=True,
            line_shape='spline'
        )
        fig_evolucao.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    with col_graf2:
        # Gráfico de letalidade
        fig_letalidade = px.bar(
            dados_periodo,
            x='Ano',
            y='Letalidade_%',
            title='Letalidade da Leishmaniose Visceral',
            color='Letalidade_%',
            color_continuous_scale='Reds'
        )
        fig_letalidade.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig_letalidade, use_container_width=True)

with tab3:
    st.markdown('<div class="section-title">📈 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    # Análise comparativa entre anos
    st.markdown("#### 📅 COMPARAÇÃO ENTRE ANOS")
    
    anos_comparacao = st.multiselect(
        "Selecione os anos para comparação:",
        ['2020', '2021', '2022', '2023', '2024'],
        default=['2020', '2023']
    )
    
    if anos_comparacao:
        # Preparar dados para heatmap
        heatmap_data = []
        for regional in dados_regionais['Regional']:
            if regional != 'Ignorado':
                row = {'Regional': regional}
                for ano in anos_comparacao:
                    row[ano] = dados_regionais[dados_regionais['Regional'] == regional][ano].values[0]
                heatmap_data.append(row)
        
        df_heatmap = pd.DataFrame(heatmap_data)
        df_heatmap_melted = df_heatmap.melt(id_vars=['Regional'], var_name='Ano', value_name='Casos')
        
        fig_heat = px.density_heatmap(
            df_heatmap_melted,
            x='Ano',
            y='Regional',
            z='Casos',
            title='Heatmap de Casos por Regional e Ano',
            color_continuous_scale='YlOrRd',
            height=500
        )
        fig_heat.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_heat, use_container_width=True)
    
    # Análise de vigilância canina
    st.markdown("#### 🐕 VIGILÂNCIA CANINA")
    
    col_can1, col_can2 = st.columns(2)
    
    with col_can1:
        fig_caninos = px.line(
            dados_caninos,
            x='Ano',
            y='Cães_Soropositivos',
            title='Cães Soropositivos por Ano',
            markers=True,
            line_shape='spline'
        )
        fig_caninos.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig_caninos, use_container_width=True)
    
    with col_can2:
        fig_positividade = px.line(
            dados_caninos,
            x='Ano',
            y='Positividade_%',
            title='Taxa de Positividade Canina',
            markers=True,
            line_shape='spline'
        )
        fig_positividade.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig_positividade, use_container_width=True)

with tab4:
    st.markdown('<div class="section-title">📋 DADOS COMPLETOS</div>', unsafe_allow_html=True)
    
    subtab1, subtab2, subtab3 = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos"])
    
    with subtab1:
        st.dataframe(
            dados_humanos,
            use_container_width=True,
            column_config={
                "Ano": st.column_config.NumberColumn(format="%d"),
                "Casos": st.column_config.NumberColumn(format="%d"),
                "Óbitos": st.column_config.NumberColumn(format="%d"),
                "Incidência_100k": st.column_config.NumberColumn(format="%.2f"),
                "Letalidade_%": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Download
        csv_humanos = dados_humanos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Humanos (CSV)",
            data=csv_humanos,
            file_name="dados_humanos_leishmaniose.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with subtab2:
        st.dataframe(dados_regionais, use_container_width=True)
        
        csv_regionais = dados_regionais.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Regionais (CSV)",
            data=csv_regionais,
            file_name="dados_regionais_leishmaniose.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with subtab3:
        st.dataframe(dados_caninos, use_container_width=True)
        
        csv_caninos = dados_caninos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Dados Caninos (CSV)",
            data=csv_caninos,
            file_name="dados_caninos_leishmaniose.csv",
            mime="text/csv",
            use_container_width=True
        )

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>VigiLeish - Sistema de Vigilância Epidemiológica</strong><br>
    Secretaria Municipal de Saúde de Belo Horizonte • Atividade Extensionista II - UNINTER<br>
    CST Ciência de Dados • Aline Alice F. da Silva (RU: 5277514) • Naiara Chaves Figueiredo (RU: 5281798)<br>
    <small>Versão 2.0 • Mapa Interativo das Regionais de BH • {datetime.now().strftime('%d/%m/%Y %H:%M')}</small>
</div>
""", unsafe_allow_html=True)
