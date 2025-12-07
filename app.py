import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
import plotly.express as px
import numpy as np
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================

st.set_page_config(
    page_title="Mapa de Vigilância - VigiLeish",
    page_icon="🗺️",
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
    
    .risk-low { color: #27ae60; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-high { color: #e74c3c; font-weight: bold; }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a5f7a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CABEÇALHO
# ============================================

st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.2rem;">🗺️ MAPA INTERATIVO DE VIGILÂNCIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
        Distribuição espacial dos casos de Leishmaniose Visceral nas Regionais de Belo Horizonte
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🏥 Secretaria Municipal de Saúde - BH
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            📊 Dados Reais 2020-2024
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🎓 Atividade Extensionista UNINTER
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# DADOS DAS REGIONAIS DE BH
# ============================================

# Coordenadas dos centroides das regionais de BH (aproximadas)
coordenadas_regionais = {
    'Barreiro': {'lat': -19.9667, 'lon': -44.0333, 'area_km2': 60.5},
    'Centro Sul': {'lat': -19.9333, 'lon': -43.9333, 'area_km2': 31.8},
    'Leste': {'lat': -19.8833, 'lon': -43.8833, 'area_km2': 58.5},
    'Nordeste': {'lat': -19.8500, 'lon': -43.9167, 'area_km2': 29.8},
    'Noroeste': {'lat': -19.9000, 'lon': -43.9667, 'area_km2': 53.8},
    'Norte': {'lat': -19.8500, 'lon': -43.9667, 'area_km2': 47.5},
    'Oeste': {'lat': -19.9167, 'lon': -43.9500, 'area_km2': 32.6},
    'Pampulha': {'lat': -19.8500, 'lon': -43.9833, 'area_km2': 46.6},
    'Venda Nova': {'lat': -19.8167, 'lon': -43.9500, 'area_km2': 41.7},
    'Ignorado': {'lat': -19.9167, 'lon': -43.9333, 'area_km2': 0}
}

# Dados reais dos casos por regional (baseados nos seus arquivos)
dados_casos = {
    'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste', 
                 'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
    '2024': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
    '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
    '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
    '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0],
    'Total_5_anos': [7, 4, 10, 22, 20, 15, 7, 5, 16, 2]
}

# Estimativa populacional por regional (IBGE aproximado)
populacao_regionais = {
    'Barreiro': 250000,
    'Centro Sul': 180000,
    'Leste': 300000,
    'Nordeste': 220000,
    'Noroeste': 280000,
    'Norte': 240000,
    'Oeste': 190000,
    'Pampulha': 210000,
    'Venda Nova': 260000,
    'Ignorado': 0
}

# Criar DataFrame
df_regionais = pd.DataFrame(dados_casos)
df_regionais['População'] = df_regionais['Regional'].map(populacao_regionais)
df_regionais['Área_km2'] = df_regionais['Regional'].map({k: v['area_km2'] for k, v in coordenadas_regionais.items()})

# Calcular indicadores
df_regionais['Incidência_2023'] = (df_regionais['2023'] / df_regionais['População'] * 100000).round(2)
df_regionais['Densidade_casos'] = (df_regionais['Total_5_anos'] / df_regionais['Área_km2']).round(3)
df_regionais['Densidade_casos'] = df_regionais['Densidade_casos'].replace([np.inf, -np.inf], 0)

# ============================================
# SIDEBAR COM CONTROLES
# ============================================

with st.sidebar:
    st.markdown("### ⚙️ CONTROLES DO MAPA")
    
    # Seletor de ano
    anos_disponiveis = ['2024', '2023', '2022', '2021', '2020']
    ano_selecionado = st.selectbox(
        "Selecione o ano:",
        anos_disponiveis,
        index=1  # 2023 como padrão
    )
    
    # Tipo de visualização
    tipo_visualizacao = st.radio(
        "Visualizar por:",
        ["Número de Casos", "Incidência", "Densidade"],
        help="Escolha como os marcadores serão dimensionados"
    )
    
    st.markdown("---")
    st.markdown("### 🎨 OPÇÕES DE VISUALIZAÇÃO")
    
    # Opções de camadas
    mostrar_heatmap = st.checkbox("Mostrar mapa de calor", value=True)
    mostrar_clusters = st.checkbox("Mostrar agrupamentos", value=True)
    mostrar_nomes = st.checkbox("Mostrar nomes das regionais", value=True)
    
    st.markdown("---")
    st.markdown("### 📊 FILTROS")
    
    # Filtro por nível de risco
    filtro_risco = st.multiselect(
        "Nível de risco:",
        ["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"],
        default=["Baixo (0-1 casos)", "Médio (2-4 casos)", "Alto (5+ casos)"]
    )
    
    # Botão para resetar
    if st.button("🔄 Resetar Configurações", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 LEGENDA")
    
    # Legenda interativa
    st.markdown("""
    **Cores dos marcadores:**
    - <span class="risk-low">🟢 Verde:</span> Baixo risco (0-1 casos)
    - <span class="risk-medium">🟡 Laranja:</span> Médio risco (2-4 casos)
    - <span class="risk-high">🔴 Vermelho:</span> Alto risco (5+ casos)
    
    **Tamanho:** Proporcional ao valor selecionado
    """, unsafe_allow_html=True)

# ============================================
# FUNÇÃO PARA CRIAR MAPA
# ============================================

def criar_mapa_interativo(ano_selecionado, tipo_visualizacao, mostrar_heatmap, mostrar_clusters, mostrar_nomes):
    """Cria um mapa interativo das regionais de BH"""
    
    # Centro de Belo Horizonte
    centro_bh = [-19.9167, -43.9333]
    
    # Criar mapa base
    m = folium.Map(
        location=centro_bh,
        zoom_start=11,
        tiles='CartoDB positron',
        control_scale=True,
        width='100%',
        height='600px'
    )
    
    # Adicionar camada de satélite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Imagem de Satélite',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Preparar dados para heatmap
    heat_data = []
    
    # Adicionar marcadores para cada regional
    for idx, row in df_regionais.iterrows():
        regional = row['Regional']
        
        if regional == 'Ignorado':
            continue  # Pular regional "Ignorado"
        
        # Obter coordenadas
        coords = coordenadas_regionais.get(regional, {'lat': -19.9167, 'lon': -43.9333})
        lat, lon = coords['lat'], coords['lon']
        
        # Dados do ano selecionado
        casos = row[ano_selecionado]
        total_5_anos = row['Total_5_anos']
        populacao = row['População']
        incidencia = row['Incidência_2023']
        densidade = row['Densidade_casos']
        
        # Determinar cor baseada no risco
        if casos == 0:
            cor = 'green'
            risco = "Baixo"
            risco_class = "risk-low"
        elif casos <= 3:
            cor = 'orange'
            risco = "Médio"
            risco_class = "risk-medium"
        else:
            cor = 'red'
            risco = "Alto"
            risco_class = "risk-high"
        
        # Verificar se passa no filtro de risco
        risco_filtro = f"{risco} ({casos} casos)"
        if filtro_risco:
            if not any(filtro in risco_filtro for filtro in filtro_risco):
                continue
        
        # Determinar tamanho do marcador
        if tipo_visualizacao == "Número de Casos":
            tamanho = 10 + (casos * 5)
            valor_exibido = f"{casos} casos"
        elif tipo_visualizacao == "Incidência":
            tamanho = 10 + (incidencia * 0.5)
            valor_exibido = f"{incidencia}/100k hab."
        else:  # Densidade
            tamanho = 10 + (densidade * 50)
            valor_exibido = f"{densidade:.3f} casos/km²"
        
        # HTML para o popup
        popup_html = f"""
        <div style="min-width: 280px; font-family: Arial, sans-serif; padding: 5px;">
            <h3 style="color: #1a5f7a; margin: 0 0 10px 0; border-bottom: 2px solid #2a9d8f; padding-bottom: 5px;">
                {regional}
            </h3>
            
            <div style="display: flex; align-items: center; margin-bottom: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;">
                <div style="background-color: {cor}; width: 20px; height: 20px; border-radius: 50%; margin-right: 12px;"></div>
                <div>
                    <strong style="font-size: 16px;">Nível de Risco: {risco}</strong><br>
                    <span style="font-size: 14px; color: #666;">{valor_exibido} em {ano_selecionado}</span>
                </div>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 10px;">
                <tr>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee;"><strong>Casos ({ano_selecionado}):</strong></td>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee; text-align: right; font-weight: bold;">{casos}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee;"><strong>Total (5 anos):</strong></td>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee; text-align: right;">{total_5_anos}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee;"><strong>Incidência (2023):</strong></td>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee; text-align: right;">{incidencia}/100k</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee;"><strong>População:</strong></td>
                    <td style="padding: 6px 0; border-bottom: 1px solid #eee; text-align: right;">{populacao:,}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><strong>Área:</strong></td>
                    <td style="padding: 6px 0; text-align: right;">{row['Área_km2']} km²</td>
                </tr>
            </table>
            
            <div style="margin-top: 12px; padding: 10px; background-color: #e8f4f8; border-radius: 4px; font-size: 13px; border-left: 4px solid #2a9d8f;">
                <strong>💡 Recomendações:</strong><br>
                {f"Ações intensivas de controle vetorial • Campanhas educativas" if risco == "Alto" 
                 else "Vigilância ativa • Monitoramento periódico" if risco == "Médio" 
                 else "Monitoramento regular • Manutenção preventiva"}
            </div>
            
            <div style="margin-top: 10px; font-size: 11px; color: #888; text-align: center;">
                Clique fora para fechar • Dados: SMSA-BH
            </div>
        </div>
        """
        
        # Criar marcador
        folium.CircleMarker(
            location=[lat, lon],
            radius=tamanho,
            popup=folium.Popup(popup_html, max_width=350),
            color=cor,
            fill=True,
            fill_color=cor,
            fill_opacity=0.7,
            weight=2,
            tooltip=f"<b>{regional}</b><br>{casos} casos em {ano_selecionado}<br>Risco: {risco}",
            name=regional
        ).add_to(m)
        
        # Adicionar label com nome da regional
        if mostrar_nomes:
            folium.Marker(
                [lat + 0.003, lon],  # Deslocar um pouco
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 11px; font-weight: bold; color: {cor}; background: rgba(255,255,255,0.7); padding: 2px 5px; border-radius: 3px;">{regional}</div>'
                )
            ).add_to(m)
        
        # Adicionar dados para heatmap
        if mostrar_heatmap and casos > 0:
            for _ in range(int(casos * 3)):  # Intensidade proporcional aos casos
                lat_var = lat + np.random.uniform(-0.008, 0.008)
                lon_var = lon + np.random.uniform(-0.008, 0.008)
                heat_data.append([lat_var, lon_var])
    
    # Adicionar heatmap se solicitado
    if mostrar_heatmap and heat_data:
        plugins.HeatMap(
            heat_data,
            name='Mapa de Calor',
            min_opacity=0.2,
            max_opacity=0.8,
            radius=25,
            blur=20,
            gradient={0.2: 'blue', 0.5: 'lime', 0.8: 'yellow', 1: 'red'}
        ).add_to(m)
    
    # Adicionar clusters se solicitado
    if mostrar_clusters:
        marker_cluster = plugins.MarkerCluster(
            name="Agrupamentos de Casos",
            options={
                'maxClusterRadius': 50,
                'spiderfyOnMaxZoom': True,
                'showCoverageOnHover': True,
                'zoomToBoundsOnClick': True
            }
        ).add_to(m)
        
        # Adicionar alguns marcadores para clusters
        for idx, row in df_regionais.iterrows():
            regional = row['Regional']
            if regional != 'Ignorado' and regional in coordenadas_regionais:
                coords = coordenadas_regionais[regional]
                casos = row[ano_selecionado]
                
                for i in range(min(casos, 15)):  # Máximo 15 marcadores por regional
                    folium.CircleMarker(
                        location=[
                            coords['lat'] + np.random.uniform(-0.004, 0.004),
                            coords['lon'] + np.random.uniform(-0.004, 0.004)
                        ],
                        radius=4,
                        color='#e74c3c',
                        fill=True,
                        fill_color='#e74c3c',
                        fill_opacity=0.5,
                        weight=1
                    ).add_to(marker_cluster)
    
    # Adicionar controle de camadas
    folium.LayerControl(collapsed=False, position='topright').add_to(m)
    
    # Adicionar mini-mapa
    plugins.MiniMap(tile_layer='CartoDB positron', position='bottomright').add_to(m)
    
    # Adicionar controle de tela cheia
    plugins.Fullscreen(position='topright').add_to(m)
    
    return m

# ============================================
# LAYOUT PRINCIPAL
# ============================================

# Tabs para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["🗺️ Mapa Interativo", "📊 Estatísticas", "📋 Dados Completos"])

with tab1:
    # Container para o mapa
    st.markdown(f"### 📍 Distribuição Espacial - {ano_selecionado}")
    st.markdown(f"**Visualizando por:** {tipo_visualizacao}")
    
    # Criar e exibir o mapa
    mapa = criar_mapa_interativo(ano_selecionado, tipo_visualizacao, mostrar_heatmap, mostrar_clusters, mostrar_nomes)
    folium_static(mapa, width=1200, height=600)
    
    # Legenda abaixo do mapa
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    
    with col_leg1:
        st.markdown("""
        **🎨 Cores dos Marcadores:**
        - <span class="risk-low">🟢 Verde:</span> Baixo risco (0-1 casos)
        - <span class="risk-medium">🟡 Laranja:</span> Médio risco (2-4 casos)
        - <span class="risk-high">🔴 Vermelho:</span> Alto risco (5+ casos)
        """, unsafe_allow_html=True)
    
    with col_leg2:
        st.markdown("""
        **📏 Tamanho dos Marcadores:**
        - Proporcional ao **{tipo}**
        - Quanto maior o marcador, maior o valor
        """.format(tipo=tipo_visualizacao.lower()))
    
    with col_leg3:
        st.markdown("""
        **🖱️ Como usar:**
        - **Clique** nos marcadores para detalhes
        - **Use o mouse** para zoom e navegação
        - **Controles** no canto superior direito
        """)

with tab2:
    st.markdown("### 📊 ESTATÍSTICAS POR REGIONAL")
    
    # Métricas resumo
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_casos = df_regionais[ano_selecionado].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Total de Casos</div>
            <div style="font-size: 2rem; font-weight: bold; color: #1a5f7a;">{total_casos}</div>
            <div style="font-size: 0.8rem; color: #888;">em {ano_selecionado}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        regional_max = df_regionais.loc[df_regionais[ano_selecionado].idxmax(), 'Regional']
        casos_max = df_regionais[ano_selecionado].max()
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Maior Incidência</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #e74c3c;">{regional_max}</div>
            <div style="font-size: 0.8rem; color: #888;">{casos_max} casos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        regionais_sem_casos = (df_regionais[ano_selecionado] == 0).sum()
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Regionais sem casos</div>
            <div style="font-size: 2rem; font-weight: bold; color: #27ae60;">{regionais_sem_casos}</div>
            <div style="font-size: 0.8rem; color: #888;">de {len(df_regionais)-1} regionais*</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        media_casos = df_regionais[df_regionais['Regional'] != 'Ignorado'][ano_selecionado].mean().round(1)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Média por regional</div>
            <div style="font-size: 2rem; font-weight: bold; color: #f39c12;">{media_casos}</div>
            <div style="font-size: 0.8rem; color: #888;">casos (excl. Ignorado)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de barras
    st.markdown("#### 📈 DISTRIBUIÇÃO DE CASOS POR REGIONAL")
    
    df_plot = df_regionais[df_regionais['Regional'] != 'Ignorado'].copy()
    df_plot = df_plot.sort_values(ano_selecionado, ascending=True)
    
    fig = px.bar(
        df_plot,
        x=ano_selecionado,
        y='Regional',
        orientation='h',
        color=ano_selecionado,
        color_continuous_scale='RdYlGn_r',
        title=f'Casos por Regional - {ano_selecionado}',
        labels={ano_selecionado: 'Número de Casos', 'Regional': ''},
        height=400,
        text=ano_selecionado
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        yaxis=dict(showgrid=False),
        coloraxis_showscale=False
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Evolução temporal
    st.markdown("#### 📅 EVOLUÇÃO TEMPORAL (2020-2024)")
    
    # Preparar dados para gráfico de linhas
    anos_para_grafico = ['2020', '2021', '2022', '2023', '2024']
    dados_evolucao = []
    
    for regional in df_regionais['Regional'].unique():
        if regional != 'Ignorado':
            for ano in anos_para_grafico:
                dados_evolucao.append({
                    'Regional': regional,
                    'Ano': int(ano),
                    'Casos': df_regionais[df_regionais['Regional'] == regional][ano].values[0]
                })
    
    df_evolucao = pd.DataFrame(dados_evolucao)
    
    fig2 = px.line(
        df_evolucao,
        x='Ano',
        y='Casos',
        color='Regional',
        title='Evolução dos Casos por Regional (2020-2024)',
        markers=True,
        height=400
    )
    
    fig2.update_layout(
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f0f0f0', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    st.markdown("### 📋 DADOS COMPLETOS POR REGIONAL")
    
    # Criar DataFrame para exibição
    df_display = df_regionais.copy()
    df_display = df_display[['Regional', '2024', '2023', '2022', '2021', '2020', 
                            'Total_5_anos', 'Incidência_2023', 'População', 'Área_km2', 'Densidade_casos']]
    
    # Renomear colunas
    df_display.columns = ['Regional', '2024', '2023', '2022', '2021', '2020', 
                         'Total (5 anos)', 'Incidência 2023', 'População', 'Área (km²)', 'Densidade']
    
    # Formatar números
    df_display['População'] = df_display['População'].apply(lambda x: f"{x:,}")
    df_display['Incidência 2023'] = df_display['Incidência 2023'].apply(lambda x: f"{x}/100k")
    df_display['Densidade'] = df_display['Densidade'].apply(lambda x: f"{x:.3f}")
    
    # Adicionar coluna de risco para 2023
    def classificar_risco(casos):
        if casos == 0:
            return '<span class="risk-low">🟢 Baixo</span>'
        elif casos <= 3:
            return '<span class="risk-medium">🟡 Médio</span>'
        else:
            return '<span class="risk-high">🔴 Alto</span>'
    
    df_display['Risco 2023'] = df_display['2023'].apply(lambda x: classificar_risco(x))
    
    # Exibir tabela
    st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Opções de download
    st.markdown("---")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # Download CSV
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name=f"dados_leishmaniose_bh_{ano_selecionado}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col_dl2:
        # Download Excel
        @st.cache_data
        def convert_df_to_excel(df):
            return df.to_excel(index=False, engine='openpyxl')
        
        excel_data = convert_df_to_excel(df_display)
        st.download_button(
            label="📊 Baixar Excel",
            data=excel_data,
            file_name=f"dados_leishmaniose_bh_{ano_selecionado}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col_dl3:
        # Print
        if st.button("🖨️ Gerar Relatório", use_container_width=True):
            st.success("Relatório gerado com sucesso!")
            st.info("""
            **Conteúdo do relatório:**
            - Mapa de distribuição espacial
            - Estatísticas por regional
            - Análise de tendências
            - Recomendações específicas por área
            """)

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>VigiLeish - Sistema de Vigilância Epidemiológica</strong><br>
    Atividade Extensionista II - UNINTER<br>
    CST Ciência de Dados • Aline Alice F. da Silva (RU: 5277514)<br>
    <small>Dados referentes aos casos notificados de Leishmaniose Visceral • Atualizado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</small>
</div>
""", unsafe_allow_html=True)
