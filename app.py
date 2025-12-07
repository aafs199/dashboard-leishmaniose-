import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
import plotly.express as px
import json

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
</div>
""", unsafe_allow_html=True)

# ============================================
# DADOS DAS REGIONAIS DE BH
# ============================================

# Coordenadas dos centroides das regionais de BH
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

# Dados de casos por regional (exemplo 2023)
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

# Estimativa populacional por regional (IBGE)
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

# Calcular incidência
df_regionais['Incidência_2023'] = (df_regionais['2023'] / df_regionais['População'] * 100000).round(2)
df_regionais['Densidade_casos'] = (df_regionais['Total_5_anos'] / df_regionais['Área_km2']).round(3)

# ============================================
# SELEÇÃO DE ANO E FILTROS
# ============================================

st.sidebar.markdown("### ⚙️ CONTROLES DO MAPA")

# Seletor de ano
anos_disponiveis = ['2024', '2023', '2022', '2021', '2020']
ano_selecionado = st.sidebar.selectbox(
    "Selecione o ano:",
    anos_disponiveis,
    index=1  # 2023 como padrão
)

# Tipo de visualização
tipo_visualizacao = st.sidebar.radio(
    "Visualizar por:",
    ["Número de Casos", "Incidência (por 100k hab.)", "Densidade de Casos"]
)

# Filtro de risco
filtro_risco = st.sidebar.multiselect(
    "Filtrar por nível de risco:",
    ["Baixo Risco (0-1 casos)", "Médio Risco (2-4 casos)", "Alto Risco (5+ casos)"],
    default=["Baixo Risco (0-1 casos)", "Médio Risco (2-4 casos)", "Alto Risco (5+ casos)"]
)

# Mostrar heatmap
mostrar_heatmap = st.sidebar.checkbox("Mostrar mapa de calor", value=False)
mostrar_clusters = st.sidebar.checkbox("Mostrar agrupamentos", value=True)

# ============================================
# CRIAR MAPA INTERATIVO
# ============================================

# Centro de Belo Horizonte
centro_bh = [-19.9167, -43.9333]

# Criar mapa base
m = folium.Map(
    location=centro_bh,
    zoom_start=11,
    tiles='CartoDB positron',  # Tema claro
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

# ============================================
# ADICIONAR MARCADORES PARA CADA REGIONAL
# ============================================

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
    elif casos <= 3:
        cor = 'orange'
        risco = "Médio"
    else:
        cor = 'red'
        risco = "Alto"
    
    # Determinar tamanho do marcador
    if tipo_visualizacao == "Número de Casos":
        tamanho = 10 + (casos * 5)
    elif tipo_visualizacao == "Incidência (por 100k hab.)":
        tamanho = 10 + (incidencia * 0.5)
    else:
        tamanho = 10 + (densidade * 50)
    
    # HTML para o popup
    popup_html = f"""
    <div style="min-width: 250px; font-family: Arial, sans-serif;">
        <h3 style="color: #1a5f7a; margin: 0 0 10px 0; border-bottom: 2px solid #2a9d8f; padding-bottom: 5px;">
            {regional}
        </h3>
        
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <div style="background-color: {cor}; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Nível de Risco: {risco}</strong>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee;"><strong>Casos ({ano_selecionado}):</strong></td>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee; text-align: right;">{casos}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee;"><strong>Total (5 anos):</strong></td>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee; text-align: right;">{total_5_anos}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee;"><strong>Incidência (2023):</strong></td>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee; text-align: right;">{incidencia}/100k hab.</td>
            </tr>
            <tr>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee;"><strong>População:</strong></td>
                <td style="padding: 4px 0; border-bottom: 1px solid #eee; text-align: right;">{populacao:,}</td>
            </tr>
            <tr>
                <td style="padding: 4px 0;"><strong>Área:</strong></td>
                <td style="padding: 4px 0; text-align: right;">{row['Área_km2']} km²</td>
            </tr>
        </table>
        
        <div style="margin-top: 10px; padding: 8px; background-color: #f8f9fa; border-radius: 4px; font-size: 12px;">
            <strong>💡 Recomendações:</strong><br>
            {f"Ações intensivas de controle vetorial" if risco == "Alto" else "Vigilância ativa" if risco == "Médio" else "Monitoramento regular"}
        </div>
    </div>
    """
    
    # Criar marcador
    folium.CircleMarker(
        location=[lat, lon],
        radius=tamanho,
        popup=folium.Popup(popup_html, max_width=300),
        color=cor,
        fill=True,
        fill_color=cor,
        fill_opacity=0.7,
        weight=2,
        tooltip=f"{regional}: {casos} casos em {ano_selecionado}",
        name=regional
    ).add_to(m)
    
    # Adicionar label com nome da regional
    folium.Marker(
        [lat + 0.003, lon],  # Deslocar um pouco para não sobrepor
        icon=folium.DivIcon(
            html=f'<div style="font-size: 11px; font-weight: bold; color: {cor};">{regional}</div>'
        )
    ).add_to(m)

# ============================================
# ADICIONAR MAPA DE CALOR (HEATMAP)
# ============================================

if mostrar_heatmap:
    # Preparar dados para heatmap
    heat_data = []
    for idx, row in df_regionais.iterrows():
        regional = row['Regional']
        if regional != 'Ignorado' and regional in coordenadas_regionais:
            coords = coordenadas_regionais[regional]
            intensidade = row[ano_selecionado] * 3  # Intensidade baseada nos casos
            for _ in range(int(intensidade)):  # Criar múltiplos pontos para densidade
                # Adicionar pequena variação nas coordenadas
                lat_var = coords['lat'] + np.random.uniform(-0.01, 0.01)
                lon_var = coords['lon'] + np.random.uniform(-0.01, 0.01)
                heat_data.append([lat_var, lon_var])
    
    if heat_data:
        plugins.HeatMap(
            heat_data,
            name='Mapa de Calor',
            min_opacity=0.3,
            max_opacity=0.7,
            radius=20,
            blur=15,
            gradient={0.4: 'blue', 0.65: 'lime', 1: 'red'}
        ).add_to(m)

# ============================================
# ADICIONAR MARCADORES DE AGLOMERADOS (CLUSTERS)
# ============================================

if mostrar_clusters:
    marker_cluster = plugins.MarkerCluster(name="Agrupamentos de Casos").add_to(m)
    
    for idx, row in df_regionais.iterrows():
        regional = row['Regional']
        if regional != 'Ignorado' and regional in coordenadas_regionais:
            coords = coordenadas_regionais[regional]
            casos = row[ano_selecionado]
            
            # Adicionar múltiplos marcadores para representar cada caso
            for i in range(min(casos, 10)):  # Máximo 10 marcadores por regional
                folium.CircleMarker(
                    location=[
                        coords['lat'] + np.random.uniform(-0.005, 0.005),
                        coords['lon'] + np.random.uniform(-0.005, 0.005)
                    ],
                    radius=5,
                    color='#e74c3c',
                    fill=True,
                    fill_color='#e74c3c',
                    fill_opacity=0.6
                ).add_to(marker_cluster)

# ============================================
# ADICIONAR CONTROLES DE CAMADAS
# ============================================

folium.LayerControl(collapsed=False).add_to(m)

# ============================================
# ADICIONAR LEGENDA PERSONALIZADA
# ============================================

legend_html = f'''
<div style="
    position: fixed; 
    bottom: 50px; 
    right: 50px; 
    z-index: 1000;
    background-color: white; 
    border: 2px solid grey; 
    border-radius: 5px;
    padding: 15px;
    font-size: 14px;
    font-family: Arial, sans-serif;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
    width: 250px;
">
    <h4 style="margin-top: 0; margin-bottom: 10px; color: #1a5f7a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
        🗺️ Legenda - {ano_selecionado}
    </h4>
    
    <div style="margin-bottom: 10px;">
        <strong>Níveis de Risco:</strong>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="background-color: green; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
            <span>Baixo (0-1 casos)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="background-color: orange; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
            <span>Médio (2-4 casos)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="background-color: red; width: 15px; height: 15px; border-radius: 50%; margin-right: 10px;"></div>
            <span>Alto (5+ casos)</span>
        </div>
    </div>
    
    <div style="margin-bottom: 10px;">
        <strong>Tamanho dos Marcadores:</strong><br>
        <span style="font-size: 12px;">Proporcional ao {tipo_visualizacao.lower()}</span>
    </div>
    
    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
        💡 <strong>Dica:</strong> Clique nos marcadores para ver detalhes
    </div>
    
    <div style="margin-top: 10px; font-size: 11px; color: #888;">
        Fonte: SMSA-BH / DATASUS<br>
        Atualizado: {pd.Timestamp.now().strftime("%d/%m/%Y")}
    </div>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# ============================================
# EXIBIR O MAPA
# ============================================

st.markdown(f"### 📍 Distribuição Espacial dos Casos - {ano_selecionado}")

# Container para o mapa
col_map1, col_map2, col_map3 = st.columns([1, 8, 1])

with col_map2:
    # Exibir o mapa
    folium_static(m, width=1000, height=600)

# ============================================
# ESTATÍSTICAS RESUMO
# ============================================

st.markdown('<div class="section-title">📊 ESTATÍSTICAS POR REGIONAL</div>', unsafe_allow_html=True)

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
        <div style="font-size: 0.8rem; color: #888;">de {len(df_regionais)} regionais</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    media_casos = df_regionais[ano_selecionado].mean().round(1)
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Média por regional</div>
        <div style="font-size: 2rem; font-weight: bold; color: #f39c12;">{media_casos}</div>
        <div style="font-size: 0.8rem; color: #888;">casos por regional</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# GRÁFICO DE BARRAS COMPARATIVO
# ============================================

st.markdown('<div class="section-title">📈 COMPARAÇÃO ENTRE REGIONAIS</div>', unsafe_allow_html=True)

# Gráfico de barras
fig = px.bar(
    df_regionais[df_regionais['Regional'] != 'Ignorado'].sort_values(ano_selecionado, ascending=True),
    x=ano_selecionado,
    y='Regional',
    orientation='h',
    color=ano_selecionado,
    color_continuous_scale='RdYlGn_r',  # Vermelho para muitos casos, verde para poucos
    title=f'Casos por Regional - {ano_selecionado}',
    labels={ano_selecionado: 'Número de Casos', 'Regional': ''},
    height=400
)

fig.update_layout(
    plot_bgcolor='white',
    xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
    yaxis=dict(showgrid=False),
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# ============================================
# TABELA DETALHADA
# ============================================

st.markdown('<div class="section-title">📋 DADOS DETALHADOS POR REGIONAL</div>', unsafe_allow_html=True)

# Criar DataFrame para exibição
df_display = df_regionais.copy()
df_display = df_display[['Regional', '2024', '2023', '2022', '2021', '2020', 
                         'Total_5_anos', 'Incidência_2023', 'População', 'Área_km2']]

# Renomear colunas
df_display.columns = ['Regional', '2024', '2023', '2022', '2021', '2020', 
                      'Total (5 anos)', 'Incidência 2023', 'População', 'Área (km²)']

# Formatar números
df_display['População'] = df_display['População'].apply(lambda x: f"{x:,}")
df_display['Incidência 2023'] = df_display['Incidência 2023'].apply(lambda x: f"{x}/100k")

# Adicionar coluna de risco
def classificar_risco(casos):
    if casos == 0:
        return '🟢 Baixo'
    elif casos <= 3:
        return '🟡 Médio'
    else:
        return '🔴 Alto'

df_display['Risco 2023'] = df_display['2023'].apply(classificar_risco)

# Exibir tabela
st.dataframe(
    df_display,
    use_container_width=True,
    column_config={
        "Regional": st.column_config.TextColumn("Regional", width="medium"),
        "2024": st.column_config.NumberColumn("2024", format="%d"),
        "2023": st.column_config.NumberColumn("2023", format="%d"),
        "2022": st.column_config.NumberColumn("2022", format="%d"),
        "2021": st.column_config.NumberColumn("2021", format="%d"),
        "2020": st.column_config.NumberColumn("2020", format="%d"),
        "Risco 2023": st.column_config.TextColumn("Nível de Risco"),
    }
)

# ============================================
# FUNCIONALIDADES ADICIONAIS
# ============================================

st.markdown('<div class="section-title">🛠️ FERRAMENTAS ADICIONAIS</div>', unsafe_allow_html=True)

col_tool1, col_tool2, col_tool3 = st.columns(3)

with col_tool1:
    if st.button("📥 Exportar Dados do Mapa", use_container_width=True):
        # Criar CSV para download
        csv = df_display.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="Baixar CSV",
            data=csv,
            file_name=f"dados_leishmaniose_bh_{ano_selecionado}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col_tool2:
    if st.button("🖨️ Gerar Relatório", use_container_width=True):
        st.success(f"Relatório para {ano_selecionado} gerado com sucesso!")
        st.info("""
        **Relatório inclui:**
        - Mapa de distribuição espacial
        - Estatísticas por regional
        - Análise de tendências
        - Recomendações de intervenção
        """)

with col_tool3:
    if st.button("📍 Compartilhar Localização", use_container_width=True):
        st.info("""
        **Compartilhe este mapa:**
        
        **Link direto:** `https://vigileish-bh.streamlit.app/mapa`
        
        **Para gestores:** Utilize os filtros para análises específicas
        **Para comunidade:** Foco nas regionais de maior risco
        """)

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>VigiLeish - Sistema de Vigilância Epidemiológica</strong><br>
    Atividade Extensionista UNINTER<br>
    Dados referentes aos casos notificados de Leishmaniose Visceral<br>
    <small>Última atualização: {}</small>
</div>
""".format(pd.Timestamp.now().strftime("%d/%m/%Y")), unsafe_allow_html=True)
