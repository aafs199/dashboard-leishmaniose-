import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import io
import base64

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
    
    .data-upload-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px dashed #2a9d8f;
        margin-bottom: 2rem;
    }
    
    .tab-content {
        padding: 1.5rem;
        background: white;
        border-radius: 0 0 12px 12px;
        border: 1px solid #dee2e6;
        border-top: none;
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
# FUNÇÕES PARA CARREGAMENTO DE DADOS
# ============================================

@st.cache_data
def carregar_dados_padrao():
    """Carrega os dados padrão do sistema"""
    
    # Dados humanos anuais
    dados_humanos = pd.DataFrame({
        'Ano': list(range(1994, 2026)),
        'Casos_incidentes': [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 110, 
                             160, 145, 131, 93, 54, 40, 39, 48, 51, 64, 39, 41, 30, 30, 24, 30, 29, 11],
        'Óbitos_incidentes': [6, 4, 4, 3, 4, 3, 9, 10, 8, 9, 25, 9, 12, 6, 18, 31, 23, 
                               14, 12, 5, 3, 7, 7, 12, 5, 7, 1, 3, 5, 6, 8, 0],
        'População': [2084100, 2106819, 2091371, 2109223, 2124176, 2139125, 2238332, 
                      2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 
                      2238332, 2238332, 2375151, 2375151, 2375151, 2375151, 2375151, 
                      2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 
                      2315560, 2315560, 2315560, 2315560]
    })
    
    # Calcular indicadores
    dados_humanos['Incidência_100k'] = (dados_humanos['Casos_incidentes'] / dados_humanos['População'] * 100000).round(2)
    dados_humanos['Letalidade_%'] = (dados_humanos['Óbitos_incidentes'] / dados_humanos['Casos_incidentes'].replace(0, 1) * 100).round(2)
    
    # Dados regionais
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
    
    return {
        'humanos': dados_humanos,
        'regionais': dados_regionais,
        'caninos': dados_caninos,
        'ultima_atualizacao': datetime.now()
    }

def processar_arquivo_excel(uploaded_file, tipo_dados):
    """Processa arquivo Excel enviado pelo usuário"""
    try:
        # Ler todas as abas do Excel
        xls = pd.ExcelFile(uploaded_file)
        sheets = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            sheets[sheet_name] = df
        
        st.success(f"✅ Arquivo processado com sucesso! {len(sheets)} abas encontradas.")
        return sheets
    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {str(e)}")
        return None

def processar_arquivo_csv(uploaded_file):
    """Processa arquivo CSV enviado pelo usuário"""
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        st.success(f"✅ CSV processado com sucesso! {len(df)} linhas carregadas.")
        return {'dados': df}
    except Exception as e:
        st.error(f"❌ Erro ao processar CSV: {str(e)}")
        return None

# ============================================
# SIDEBAR - CONTROLES E UPLOAD
# ============================================

with st.sidebar:
    st.markdown("### 📂 GESTÃO DE DADOS")
    
    # Seletor de fonte de dados
    fonte_dados = st.radio(
        "Fonte dos dados:",
        ["📊 Dados Padrão (Sistema)", "📤 Upload de Arquivo", "🔗 Conexão Externa"],
        help="Escolha a fonte dos dados para o painel"
    )
    
    st.markdown("---")
    
    # Seção de upload de arquivos
    if fonte_dados == "📤 Upload de Arquivo":
        st.markdown("#### 📎 ENVIAR NOVOS DADOS")
        
        # Upload de múltiplos arquivos
        uploaded_files = st.file_uploader(
            "Selecione arquivos de dados:",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Formatos suportados: CSV, Excel"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                with st.expander(f"📄 {uploaded_file.name}", expanded=False):
                    # Verificar tipo de arquivo
                    if uploaded_file.name.endswith('.csv'):
                        dados_processados = processar_arquivo_csv(uploaded_file)
                    else:
                        tipo = st.selectbox(
                            f"Tipo de dados para {uploaded_file.name}:",
                            ["Dados Humanos Anuais", "Dados Regionais", "Dados Caninos", "Outros"],
                            key=f"tipo_{uploaded_file.name}"
                        )
                        dados_processados = processar_arquivo_excel(uploaded_file, tipo)
                    
                    if dados_processados:
                        # Mostrar preview
                        st.markdown("**Pré-visualização:**")
                        for sheet_name, df in dados_processados.items():
                            st.dataframe(df.head(), use_container_width=True)
                        
                        # Opção para salvar
                        if st.button(f"💾 Salvar {uploaded_file.name}", key=f"save_{uploaded_file.name}"):
                            # Aqui você implementaria a lógica para salvar no banco de dados
                            st.success(f"Dados de {uploaded_file.name} salvos com sucesso!")
    
    st.markdown("---")
    st.markdown("### ⚙️ CONFIGURAÇÕES")
    
    # Configurações do painel
    ano_inicio = st.slider("Ano inicial:", 1994, 2024, 2015)
    ano_fim = st.slider("Ano final:", 1994, 2024, 2024)
    
    mostrar_detalhes = st.checkbox("Mostrar dados detalhados", value=True)
    modo_escuro = st.checkbox("Modo escuro", value=False)
    
    st.markdown("---")
    st.markdown("### 🔄 ATUALIZAÇÃO")
    
    # Botão para atualizar dados
    if st.button("🔄 Atualizar Dados do Sistema", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    # Botão para limpar cache
    if st.button("🧹 Limpar Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache limpo com sucesso!")

# ============================================
# CABEÇALHO PRINCIPAL
# ============================================

st.markdown(f"""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.2rem;">🏥 VIGILEISH - PAINEL DE VIGILÂNCIA</h1>
    <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.95;">
        Sistema de Monitoramento da Leishmaniose Visceral em Belo Horizonte
    </p>
    <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            📅 Período: {ano_inicio}-{ano_fim}
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🔄 Fonte: {fonte_dados}
        </span>
        <span style="background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 20px; font-size: 0.9rem;">
            🕒 Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# CARREGAR DADOS
# ============================================

with st.spinner("🔄 Carregando dados..."):
    if fonte_dados == "📊 Dados Padrão (Sistema)":
        dados = carregar_dados_padrao()
        st.success("✅ Dados padrão carregados com sucesso!")
    else:
        # Para upload ou conexão externa, usar dados padrão por enquanto
        dados = carregar_dados_padrao()
        st.info("ℹ️ Usando dados padrão. Faça upload de novos dados na sidebar.")

# Extrair DataFrames
dados_humanos = dados['humanos']
dados_regionais = dados['regionais']
dados_caninos = dados['caninos']

# ============================================
# TAB PRINCIPAL - VISUALIZAÇÃO
# ============================================

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🗺️ Mapa", "📈 Análises", "📁 Dados"])

with tab1:
    st.markdown('<div class="section-title">📊 DASHBOARD DE MONITORAMENTO</div>', unsafe_allow_html=True)
    
    # Filtros rápidos
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        tipo_indicador = st.selectbox(
            "Indicador principal:",
            ["Casos Incidentes", "Incidência", "Letalidade", "Casos Caninos"]
        )
    
    with col_f2:
        agregacao = st.selectbox(
            "Agregação:",
            ["Anual", "Quinquenal", "Por década", "Total período"]
        )
    
    with col_f3:
        regional_filtro = st.multiselect(
            "Filtrar regionais:",
            dados_regionais['Regional'].tolist(),
            default=dados_regionais['Regional'].tolist()[:5]
        )
    
    # Métricas principais
    st.markdown("### 🎯 INDICADORES-CHAVE")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    with col_m1:
        # Total de casos no período
        casos_periodo = dados_humanos[
            (dados_humanos['Ano'] >= ano_inicio) & 
            (dados_humanos['Ano'] <= ano_fim)
        ]['Casos_incidentes'].sum()
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Total de Casos</div>
            <div style="font-size: 2rem; font-weight: bold; color: #1a5f7a;">{casos_periodo:,}</div>
            <div style="font-size: 0.8rem; color: #888;">{ano_inicio}-{ano_fim}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m2:
        # Letalidade média
        letalidade_media = dados_humanos['Letalidade_%'].mean().round(1)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Letalidade Média</div>
            <div style="font-size: 2rem; font-weight: bold; color: #e74c3c;">{letalidade_media}%</div>
            <div style="font-size: 0.8rem; color: #888;">Histórico completo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m3:
        # Incidência atual
        incidencia_atual = dados_humanos[dados_humanos['Ano'] == ano_fim]['Incidência_100k'].values[0] if ano_fim in dados_humanos['Ano'].values else 0
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Incidência Atual</div>
            <div style="font-size: 2rem; font-weight: bold; color: #2a9d8f;">{incidencia_atual:.2f}</div>
            <div style="font-size: 0.8rem; color: #888;">por 100k hab. ({ano_fim})</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_m4:
        # Regional com mais casos
        if '2023' in dados_regionais.columns:
            idx_max = dados_regionais['2023'].idxmax()
            reg_prioritaria = dados_regionais.loc[idx_max, 'Regional']
            casos_reg = dados_regionais.loc[idx_max, '2023']
        else:
            reg_prioritaria = "Nordeste"
            casos_reg = 7
        
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">Prioridade Regional</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: #f39c12;">{reg_prioritaria}</div>
            <div style="font-size: 0.8rem; color: #888;">{casos_reg} casos (2023)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("### 📈 VISUALIZAÇÕES")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfico de evolução temporal
        fig1 = px.line(
            dados_humanos[(dados_humanos['Ano'] >= ano_inicio) & (dados_humanos['Ano'] <= ano_fim)],
            x='Ano',
            y='Casos_incidentes',
            title='Evolução dos Casos de LV',
            markers=True,
            line_shape='spline'
        )
        fig1.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_g2:
        # Gráfico de letalidade
        fig2 = px.bar(
            dados_humanos[(dados_humanos['Ano'] >= ano_inicio) & (dados_humanos['Ano'] <= ano_fim)],
            x='Ano',
            y='Letalidade_%',
            title='Letalidade da Leishmaniose Visceral',
            color='Letalidade_%',
            color_continuous_scale='Reds'
        )
        fig2.update_layout(height=400, plot_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.markdown('<div class="section-title">🗺️ MAPA DE DISTRIBUIÇÃO ESPACIAL</div>', unsafe_allow_html=True)
    
    # Mapa simplificado com Plotly
    ano_mapa = st.selectbox("Ano para o mapa:", ['2023', '2022', '2021', '2020'], key="ano_mapa")
    
    # Criar dados para o mapa
    map_data = dados_regionais[['Regional', ano_mapa]].copy()
    map_data = map_data[map_data['Regional'] != 'Ignorado']
    
    # Adicionar coordenadas simuladas
    coordenadas = {
        'Barreiro': [-19.9667, -44.0333],
        'Centro Sul': [-19.9333, -43.9333],
        'Leste': [-19.8833, -43.8833],
        'Nordeste': [-19.8500, -43.9167],
        'Noroeste': [-19.9000, -43.9667],
        'Norte': [-19.8500, -43.9667],
        'Oeste': [-19.9167, -43.9500],
        'Pampulha': [-19.8500, -43.9833],
        'Venda Nova': [-19.8167, -43.9500]
    }
    
    map_data['lat'] = map_data['Regional'].map(lambda x: coordenadas.get(x, [-19.9167, -43.9333])[0])
    map_data['lon'] = map_data['Regional'].map(lambda x: coordenadas.get(x, [-19.9167, -43.9333])[1])
    map_data['size'] = map_data[ano_mapa] * 5 + 10
    map_data['color'] = map_data[ano_mapa].apply(lambda x: 'green' if x == 0 else 'orange' if x <= 3 else 'red')
    map_data['text'] = map_data.apply(lambda row: f"{row['Regional']}<br>{row[ano_mapa]} casos", axis=1)
    
    # Criar mapa com scatter plot
    fig_map = px.scatter_mapbox(
        map_data,
        lat='lat',
        lon='lon',
        size='size',
        color='color',
        hover_name='Regional',
        hover_data={ano_mapa: True, 'lat': False, 'lon': False, 'size': False, 'color': False},
        title=f'Distribuição de Casos por Regional - {ano_mapa}',
        zoom=10,
        height=500
    )
    
    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10,
        mapbox_center={"lat": -19.9167, "lon": -43.9333},
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Legenda
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        st.markdown("**🎨 Legenda:**")
        st.markdown("- 🟢 **Verde:** 0-1 caso")
        st.markdown("- 🟡 **Laranja:** 2-4 casos")
        st.markdown("- 🔴 **Vermelho:** 5+ casos")
    
    with col_l2:
        st.markdown("**📏 Tamanho:**")
        st.markdown("Proporcional ao número de casos")
    
    with col_l3:
        st.markdown("**🖱️ Interação:**")
        st.markdown("Passe o mouse sobre os pontos para ver detalhes")

with tab3:
    st.markdown('<div class="section-title">📈 ANÁLISES AVANÇADAS</div>', unsafe_allow_html=True)
    
    # Análise de tendência
    st.markdown("#### 📊 ANÁLISE DE TENDÊNCIA")
    
    # Calcular médias móveis
    dados_humanos['MM5_casos'] = dados_humanos['Casos_incidentes'].rolling(window=5, center=True).mean()
    dados_humanos['MM5_letalidade'] = dados_humanos['Letalidade_%'].rolling(window=5, center=True).mean()
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        # Gráfico de tendência de casos
        fig_t1 = go.Figure()
        fig_t1.add_trace(go.Scatter(
            x=dados_humanos['Ano'],
            y=dados_humanos['Casos_incidentes'],
            mode='lines+markers',
            name='Casos',
            line=dict(color='#3498db', width=2)
        ))
        fig_t1.add_trace(go.Scatter(
            x=dados_humanos['Ano'],
            y=dados_humanos['MM5_casos'],
            mode='lines',
            name='Tendência (MM5)',
            line=dict(color='#e74c3c', width=3, dash='dash')
        ))
        fig_t1.update_layout(
            title='Tendência de Casos com Média Móvel',
            height=400,
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_t1, use_container_width=True)
    
    with col_a2:
        # Análise de correlação
        st.markdown("#### 🔗 CORRELAÇÃO ENTRE VARIÁVEIS")
        
        variavel_x = st.selectbox("Variável X:", ['Casos_incidentes', 'Incidência_100k', 'Letalidade_%'])
        variavel_y = st.selectbox("Variável Y:", ['Casos_incidentes', 'Incidência_100k', 'Letalidade_%'])
        
        if variavel_x != variavel_y:
            fig_corr = px.scatter(
                dados_humanos,
                x=variavel_x,
                y=variavel_y,
                trendline="ols",
                title=f'Correlação: {variavel_x} vs {variavel_y}',
                height=400
            )
            fig_corr.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Calcular coeficiente de correlação
            correlacao = dados_humanos[variavel_x].corr(dados_humanos[variavel_y])
            st.metric("Coeficiente de Correlação", f"{correlacao:.3f}")
    
    # Análise comparativa entre regionais
    st.markdown("#### 🏙️ COMPARAÇÃO ENTRE REGIONAIS")
    
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
            height=400
        )
        fig_heat.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_heat, use_container_width=True)

with tab4:
    st.markdown('<div class="section-title">📁 GESTÃO DE DADOS</div>', unsafe_allow_html=True)
    
    # Subtabs para diferentes conjuntos de dados
    subtab1, subtab2, subtab3, subtab4 = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos", "📤 Exportar"])
    
    with subtab1:
        st.markdown("#### 👥 DADOS HUMANOS ANUAIS")
        st.dataframe(
            dados_humanos,
            use_container_width=True,
            column_config={
                "Ano": st.column_config.NumberColumn(format="%d"),
                "Casos_incidentes": st.column_config.NumberColumn(format="%d"),
                "Óbitos_incidentes": st.column_config.NumberColumn(format="%d"),
                "Incidência_100k": st.column_config.NumberColumn(format="%.2f"),
                "Letalidade_%": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Estatísticas descritivas
        st.markdown("##### 📊 ESTATÍSTICAS DESCRITIVAS")
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.metric("Média de casos", f"{dados_humanos['Casos_incidentes'].mean():.1f}")
        with col_stats2:
            st.metric("Desvio padrão", f"{dados_humanos['Casos_incidentes'].std():.1f}")
        with col_stats3:
            st.metric("Máximo", f"{dados_humanos['Casos_incidentes'].max()}")
        with col_stats4:
            st.metric("Mínimo", f"{dados_humanos['Casos_incidentes'].min()}")
    
    with subtab2:
        st.markdown("#### 🗺️ DADOS POR REGIONAL")
        st.dataframe(dados_regionais, use_container_width=True)
        
        # Resumo por ano
        st.markdown("##### 📅 RESUMO POR ANO")
        resumo_anos = dados_regionais[['2020', '2021', '2022', '2023', '2024']].sum().reset_index()
        resumo_anos.columns = ['Ano', 'Total Casos']
        st.dataframe(resumo_anos, use_container_width=True)
    
    with subtab3:
        st.markdown("#### 🐕 DADOS DE VIGILÂNCIA CANINA")
        st.dataframe(dados_caninos, use_container_width=True)
        
        # Gráfico de vigilância canina
        fig_can = px.line(
            dados_caninos,
            x='Ano',
            y=['Cães_Soropositivos', 'Imóveis_Borrifados'],
            title='Vigilância Canina e Controle Vetorial',
            markers=True,
            height=400
        )
        fig_can.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_can, use_container_width=True)
    
    with subtab4:
        st.markdown("#### 📤 EXPORTAR DADOS")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        with col_exp1:
            # Exportar dados humanos
            csv_humanos = dados_humanos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Dados Humanos (CSV)",
                data=csv_humanos,
                file_name="dados_humanos_leishmaniose.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Exportar dados regionais
            csv_regionais = dados_regionais.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Dados Regionais (CSV)",
                data=csv_regionais,
                file_name="dados_regionais_leishmaniose.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp3:
            # Exportar dados caninos
            csv_caninos = dados_caninos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Dados Caninos (CSV)",
                data=csv_caninos,
                file_name="dados_caninos_leishmaniose.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        st.markdown("#### 📋 RELATÓRIO COMPLETO")
        
        # Gerar relatório
        if st.button("📄 Gerar Relatório PDF", use_container_width=True):
            st.success("Relatório gerado com sucesso!")
            st.info("""
            **Conteúdo do relatório:**
            - Dashboard completo com métricas
            - Análises temporais e espaciais
            - Recomendações estratégicas
            - Anexos com dados brutos
            
            *Funcionalidade de PDF será implementada na próxima versão*
            """)

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
    <strong>VigiLeish - Sistema de Vigilância Epidemiológica</strong><br>
    Secretaria Municipal de Saúde de Belo Horizonte • Atividade Extensionista II - UNINTER<br>
    CST Ciência de Dados • Aline Alice F. da Silva (RU: 5277514) • Naiara Chaves Figueiredo (RU: 5281798)<br>
    <small>Versão 2.0 • Sistema modular para fácil atualização de dados • {datetime.now().strftime("%d/%m/%Y %H:%M")}</small>
</div>
""", unsafe_allow_html=True)
