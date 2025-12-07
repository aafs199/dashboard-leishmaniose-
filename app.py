import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PÁGINA COM DESIGN PROFISSIONAL
# ============================================

st.set_page_config(
    page_title="Sistema de Monitoramento - LV | SMSA-BH",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS PERSONALIZADO - DESIGN PROFISSIONAL
# ============================================

st.markdown("""
<style>
    /* CORES OFICIAIS SAÚDE PÚBLICA */
    :root {
        --primary: #0056a6;     /* Azul institucional */
        --secondary: #00a79d;   /* Verde saúde */
        --accent: #ff6b35;      /* Laranja alerta */
        --light: #f8f9fa;
        --dark: #343a40;
        --gray: #6c757d;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
    }
    
    /* ESTILO GERAL */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* CABEÇALHO PROFISSIONAL */
    .main-header {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        color: white;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    
    .logo-text {
        font-size: 1.8rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 1rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* CARDS MODERNOS */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid var(--primary);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 25px rgba(0, 0, 0, 0.12);
    }
    
    .metric-title {
        font-size: 0.85rem;
        color: var(--gray);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--dark);
        line-height: 1;
    }
    
    .metric-change {
        font-size: 0.85rem;
        margin-top: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        display: inline-block;
    }
    
    .positive { background: rgba(40, 167, 69, 0.1); color: var(--success); }
    .negative { background: rgba(220, 53, 69, 0.1); color: var(--danger); }
    .neutral { background: rgba(108, 117, 125, 0.1); color: var(--gray); }
    
    /* SEÇÕES */
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--dark);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary);
    }
    
    /* GRÁFICOS CONTAINER */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* BOTÕES MODERNOS */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* ABAS ELEGANTES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    /* FOOTER PROFISSIONAL */
    .footer {
        background: var(--dark);
        color: white;
        padding: 2rem;
        border-radius: 15px 15px 0 0;
        margin-top: 3rem;
        text-align: center;
    }
    
    .footer-logo {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: var(--light);
    }
    
    .footer-text {
        font-size: 0.9rem;
        opacity: 0.8;
        line-height: 1.5;
    }
    
    /* BADGES */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .badge-primary { background: rgba(0, 86, 166, 0.1); color: var(--primary); }
    .badge-success { background: rgba(40, 167, 69, 0.1); color: var(--success); }
    .badge-warning { background: rgba(255, 193, 7, 0.1); color: #856404; }
    .badge-danger { background: rgba(220, 53, 69, 0.1); color: var(--danger); }
    
    /* RESPONSIVO */
    @media (max-width: 768px) {
        .metric-value { font-size: 1.8rem; }
        .main-header { padding: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CABEÇALHO PROFISSIONAL
# ============================================

st.markdown("""
<div class="main-header">
    <div class="logo-container">
        <h1 class="logo-text">🏥 SISTEMA DE MONITORAMENTO</h1>
    </div>
    <p class="subtitle">LEISHMANIOSE VISCERAL • SECRETARIA MUNICIPAL DE SAÚDE DE BELO HORIZONTE</p>
    <div style="display: flex; gap: 1rem; margin-top: 1rem; font-size: 0.9rem;">
        <span class="badge badge-primary">Dados Oficiais</span>
        <span class="badge badge-success">Atualizado: """ + datetime.now().strftime("%d/%m/%Y") + """</span>
        <span class="badge badge-warning">Monitoramento Ativo</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# DADOS DE EXEMPLO (MESMO DO ANTERIOR)
# ============================================

@st.cache_data
def carregar_dados_humanos():
    data = {
        'Ano': list(range(1994, 2026)),
        'Casos': [34, 46, 50, 39, 25, 33, 46, 50, 76, 106, 136, 105, 128, 110, 
                 160, 145, 131, 93, 54, 40, 39, 48, 51, 64, 39, 41, 30, 30, 24, 30, 29, 11],
        'População': [2084100, 2106819, 2091371, 2109223, 2124176, 2139125, 2238332, 
                      2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 2238332, 
                      2238332, 2238332, 2375151, 2375151, 2375151, 2375151, 2375151, 
                      2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 2375152, 
                      2315560, 2315560, 2315560, 2315560],
        'Óbitos': [6, 4, 4, 3, 4, 3, 9, 10, 8, 9, 25, 9, 12, 6, 18, 31, 23, 
                   14, 12, 5, 3, 7, 7, 12, 5, 7, 1, 3, 5, 6, 8, 0]
    }
    df = pd.DataFrame(data)
    df['Incidência_100k'] = (df['Casos'] / df['População'] * 100000).round(2)
    df['Letalidade_%'] = (df['Óbitos'] / df['Casos'].replace(0, 1) * 100).round(2)
    return df

@st.cache_data
def carregar_dados_regionais():
    data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                    'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
        '2024': [2, 1, 3, 8, 7, 6, 3, 2, 6, 0],
        '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
        '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
        '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
        '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0]
    }
    return pd.DataFrame(data)

@st.cache_data
def carregar_dados_caninos():
    data = {
        'Ano': list(range(2014, 2025)),
        'Sorologias_Realizadas': [44536, 20659, 22965, 33029, 31330, 27983, 
                                  28954, 17044, 23490, 43571, 49927],
        'Cães_Soropositivos': [6198, 3807, 5529, 6539, 6591, 6165, 
                               5624, 3539, 4077, 5440, 4459],
        'Imóveis_Borrifados': [54436, 56475, 5617, 19538, 26388, 14855, 
                               73593, 78279, 64967, 51591, 30953]
    }
    df = pd.DataFrame(data)
    df['Positividade_%'] = (df['Cães_Soropositivos'] / df['Sorologias_Realizadas'] * 100).round(2)
    return df

# Carregar dados
dados_humanos = carregar_dados_humanos()
dados_regionais = carregar_dados_regionais()
dados_caninos = carregar_dados_caninos()

# ============================================
# SEÇÃO 1: INDICADORES-CHAVE (KPI CARDS)
# ============================================

st.markdown('<div class="section-header">📊 VISÃO GERAL DO MONITORAMENTO</div>', unsafe_allow_html=True)

# Calcular métricas
ultimo_ano = dados_humanos['Ano'].max()
casos_ultimo_ano = int(dados_humanos[dados_humanos['Ano'] == ultimo_ano]['Casos'].values[0])
casos_ano_anterior = int(dados_humanos[dados_humanos['Ano'] == ultimo_ano-1]['Casos'].values[0])
variacao_casos = ((casos_ultimo_ano - casos_ano_anterior) / casos_ano_anterior * 100).round(1)

letalidade_media = dados_humanos['Letalidade_%'].tail(5).mean().round(1)
total_casos = int(dados_humanos['Casos'].sum())
incidencia_atual = dados_humanos['Incidência_100k'].iloc[-1]

# Criar colunas para os cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    variacao_text = f"{'+' if variacao_casos > 0 else ''}{variacao_casos}% vs anterior"
    variacao_classe = "negative" if variacao_casos > 0 else "positive"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">CASOS EM {ultimo_ano}</div>
        <div class="metric-value">{casos_ultimo_ano:,}</div>
        <div class="metric-change {variacao_classe}">{variacao_text}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">LETALIDADE MÉDIA</div>
        <div class="metric-value">{letalidade_media}%</div>
        <div class="metric-change neutral">Últimos 5 anos</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">INCIDÊNCIA ATUAL</div>
        <div class="metric-value">{incidencia_atual}</div>
        <div class="metric-title">por 100 mil hab.</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">TOTAL HISTÓRICO</div>
        <div class="metric-value">{total_casos:,}</div>
        <div class="metric-title">desde 1994</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    reg_mais_casos = dados_regionais.loc[dados_regionais['2024'].idxmax(), 'Regional']
    casos_reg = dados_regionais['2024'].max()
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">REGIONAL PRIORITÁRIA</div>
        <div class="metric-value">{reg_mais_casos}</div>
        <div class="metric-change warning">{casos_reg} casos (2024)</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# SEÇÃO 2: ANÁLISE TEMPORAL
# ============================================

st.markdown('<div class="section-header">📈 ANÁLISE TEMPORAL DA DOENÇA</div>', unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Gráfico de Casos com área
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Casos'],
        mode='lines',
        name='Casos',
        line=dict(color='var(--primary)', width=4),
        fill='tozeroy',
        fillcolor='rgba(0, 86, 166, 0.1)',
        hovertemplate='<b>Ano %{x}</b><br>%{y} casos<extra></extra>'
    ))
    
    # Adicionar média móvel
    dados_humanos['MM5'] = dados_humanos['Casos'].rolling(window=5, center=True).mean()
    
    fig1.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['MM5'],
        mode='lines',
        name='Média Móvel (5 anos)',
        line=dict(color='var(--accent)', width=3, dash='dash'),
        hovertemplate='<b>Ano %{x}</b><br>Média: %{y:.0f} casos<extra></extra>'
    ))
    
    fig1.update_layout(
        title='Evolução dos Casos de LV (1994-2025)',
        xaxis_title='Ano',
        yaxis_title='Número de Casos',
        height=400,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)'
        )
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chart2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Gráfico de Letalidade
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Letalidade_%'],
        mode='lines+markers',
        name='Letalidade',
        line=dict(color='var(--danger)', width=3),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.1)',
        hovertemplate='<b>Ano %{x}</b><br>Letalidade: %{y:.1f}%<extra></extra>'
    ))
    
    fig2.update_layout(
        title='Letalidade da Leishmaniose Visceral (%)',
        xaxis_title='Ano',
        yaxis_title='Letalidade (%)',
        height=400,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    # Adicionar linha da média
    fig2.add_hline(
        y=letalidade_media,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Média: {letalidade_media}%",
        annotation_position="bottom right"
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SEÇÃO 3: DISTRIBUIÇÃO GEOGRÁFICA
# ============================================

st.markdown('<div class="section-header">🗺️ DISTRIBUIÇÃO POR REGIONAL ADMINISTRATIVA</div>', unsafe_allow_html=True)

# Seletor de ano com estilo
ano_selecionado = st.selectbox(
    "**Selecione o ano para análise:**",
    ['2024', '2023', '2022', '2021', '2020'],
    key="ano_regional"
)

st.markdown('<div class="chart-container">', unsafe_allow_html=True)

# Preparar dados
df_regional = dados_regionais[['Regional', ano_selecionado]].copy()
df_regional = df_regional.sort_values(ano_selecionado, ascending=True)

# Gráfico de barras horizontal profissional
fig3 = go.Figure()

# Cores gradiente baseadas nos valores
max_val = df_regional[ano_selecionado].max()
cores = [f'rgba(0, 86, 166, {0.3 + 0.7*(val/max_val)})' for val in df_regional[ano_selecionado]]

fig3.add_trace(go.Bar(
    y=df_regional['Regional'],
    x=df_regional[ano_selecionado],
    orientation='h',
    marker_color=cores,
    hovertemplate='<b>%{y}</b><br>%{x} casos<extra></extra>',
    text=df_regional[ano_selecionado],
    textposition='outside',
    textfont=dict(size=12, color='var(--dark)')
))

fig3.update_layout(
    title=f'Distribuição de Casos por Regional - {ano_selecionado}',
    xaxis_title='Número de Casos',
    yaxis_title='',
    height=500,
    template='plotly_white',
    plot_bgcolor='white',
    showlegend=False,
    margin=dict(l=0, r=0, t=50, b=0)
)

# Destacar o maior valor
fig3.add_annotation(
    x=df_regional[ano_selecionado].max() * 1.05,
    y=df_regional['Regional'].iloc[-1],
    text="Maior incidência",
    showarrow=True,
    arrowhead=1,
    ax=50,
    ay=0,
    font=dict(color='var(--accent)', size=12)
)

st.plotly_chart(fig3, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SEÇÃO 4: VIGILÂNCIA CANINA
# ============================================

st.markdown('<div class="section-header">🐕 VIGILÂNCIA CANINA & CONTROLE VETORIAL</div>', unsafe_allow_html=True)

col_can1, col_can2 = st.columns(2)

with col_can1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Gráfico de cães soropositivos
    fig4 = go.Figure()
    
    fig4.add_trace(go.Bar(
        x=dados_caninos['Ano'],
        y=dados_caninos['Cães_Soropositivos'],
        name='Cães Soropositivos',
        marker_color='var(--secondary)',
        hovertemplate='<b>Ano %{x}</b><br>%{y} cães<extra></extra>'
    ))
    
    fig4.add_trace(go.Scatter(
        x=dados_caninos['Ano'],
        y=dados_caninos['Positividade_%'],
        name='Taxa de Positividade',
        yaxis='y2',
        line=dict(color='var(--accent)', width=3),
        hovertemplate='<b>Ano %{x}</b><br>%{y:.1f}%<extra></extra>'
    ))
    
    fig4.update_layout(
        title='Cães Soropositivos e Taxa de Positividade',
        xaxis_title='Ano',
        yaxis_title='Cães Soropositivos',
        yaxis2=dict(
            title='Taxa de Positividade (%)',
            overlaying='y',
            side='right'
        ),
        height=400,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_can2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Gráfico de imóveis borrifados
    fig5 = go.Figure()
    
    fig5.add_trace(go.Scatter(
        x=dados_caninos['Ano'],
        y=dados_caninos['Imóveis_Borrifados'],
        mode='lines+markers',
        name='Imóveis Borrifados',
        line=dict(color='var(--primary)', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 86, 166, 0.1)',
        hovertemplate='<b>Ano %{x}</b><br>%{y:,} imóveis<extra></extra>'
    ))
    
    fig5.update_layout(
        title='Imóveis Borrifados para Controle Vetorial',
        xaxis_title='Ano',
        yaxis_title='Número de Imóveis',
        height=400,
        template='plotly_white',
        plot_bgcolor='white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SEÇÃO 5: DADOS DETALHADOS
# ============================================

st.markdown('<div class="section-header">📋 BASE DE DADOS COMPLETA</div>', unsafe_allow_html=True)

# Tabs elegantes
tab1, tab2, tab3 = st.tabs([
    f"👥 Dados Humanos ({len(dados_humanos)} anos)",
    f"🗺️ Dados Regionais ({len(dados_regionais)} regionais)", 
    f"🐕 Dados Caninos ({len(dados_caninos)} anos)"
])

with tab1:
    st.dataframe(
        dados_humanos,
        use_container_width=True,
        column_config={
            "Ano": st.column_config.NumberColumn(format="%d", width="small"),
            "Casos": st.column_config.NumberColumn(format="%d", width="small"),
            "Óbitos": st.column_config.NumberColumn(format="%d", width="small"),
            "Incidência_100k": st.column_config.NumberColumn(format="%.2f", width="small"),
            "Letalidade_%": st.column_config.NumberColumn(format="%.1f%%", width="small")
        },
        hide_index=True
    )
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    with col_dl2:
        csv_humanos = dados_humanos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar Dados (CSV)",
            data=csv_humanos,
            file_name="dados_humanos_lv_bh.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab2:
    st.dataframe(dados_regionais, use_container_width=True, hide_index=True)
    
    csv_regionais = dados_regionais.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Dados Regionais (CSV)",
        data=csv_regionais,
        file_name="dados_regionais_lv_bh.csv",
        mime="text/csv",
        use_container_width=True
    )

with tab3:
    st.dataframe(dados_caninos, use_container_width=True, hide_index=True)
    
    csv_caninos = dados_caninos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar Dados Caninos (CSV)",
        data=csv_caninos,
        file_name="dados_caninos_lv_bh.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============================================
# RODAPÉ PROFISSIONAL
# ============================================

st.markdown("""
<div class="footer">
    <div class="footer-logo">SECRETARIA MUNICIPAL DE SAÚDE DE BELO HORIZONTE</div>
    <div class="footer-text">
        Sistema de Monitoramento da Leishmaniose Visceral | Versão 2.0<br>
        Gerência de Vigilância Epidemiológica | Coordenação de Zoonoses<br>
        Dados oficiais para gestão em saúde pública | Atualizado em """ + datetime.now().strftime("%d/%m/%Y") + """<br>
        <small>© 2025 Prefeitura de Belo Horizonte. Todos os direitos reservados.</small>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# BARRA LATERAL (MENU)
# ============================================

with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem; background: white; border-radius: 10px; margin-bottom: 1rem;">
        <h3 style="color: var(--primary); margin-bottom: 1rem;">🔍 MENU DE NAVEGAÇÃO</h3>
        <ul style="list-style: none; padding: 0;">
            <li style="margin-bottom: 0.5rem;">📊 <a href="#" style="color: var(--dark); text-decoration: none;">Visão Geral</a></li>
            <li style="margin-bottom: 0.5rem;">📈 <a href="#" style="color: var(--dark); text-decoration: none;">Análise Temporal</a></li>
            <li style="margin-bottom: 0.5rem;">🗺️ <a href="#" style="color: var(--dark); text-decoration: none;">Distribuição Geográfica</a></li>
            <li style="margin-bottom: 0.5rem;">🐕 <a href="#" style="color: var(--dark); text-decoration: none;">Vigilância Canina</a></li>
            <li style="margin-bottom: 0.5rem;">📋 <a href="#" style="color: var(--dark); text-decoration: none;">Base de Dados</a></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1rem; background: var(--light); border-radius: 10px; margin-bottom: 1rem;">
        <h4 style="color: var(--dark); margin-bottom: 0.5rem;">ℹ️ SOBRE OS DADOS</h4>
        <p style="font-size: 0.85rem; color: var(--gray);">
        • Período: 1994-2025<br>
        • Fonte: Sistemas de informação da SMSA-BH<br>
        • Atualização: Trimestral<br>
        • Confidencialidade: Dados agregados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1rem; background: rgba(0, 86, 166, 0.05); border-radius: 10px;">
        <h4 style="color: var(--primary); margin-bottom: 0.5rem;">📞 CONTATO</h4>
        <p style="font-size: 0.85rem; color: var(--gray);">
        Gerência de Zoonoses<br>
        Secretaria Municipal de Saúde<br>
        Tel: (31) 3277-XXXX<br>
        E-mail: zoonoses@pbh.gov.br
        </p>
    </div>
    """, unsafe_allow_html=True)
