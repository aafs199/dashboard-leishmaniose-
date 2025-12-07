import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Leishmaniose Visceral - BH",
    page_icon="🏥",
    layout="wide"
)

# CABEÇALHO
st.title("🏥 PAINEL DE MONITORAMENTO - LEISHMANIOSE VISCERAL")
st.subheader("Belo Horizonte • Dados Epidemiológicos 1994-2025")
st.markdown("---")

# ============================================
# DADOS FIXOS EMBUTIDOS NO CÓDIGO
# ============================================

@st.cache_data
def carregar_dados_humanos():
    """Dados humanos pré-definidos"""
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
    """Dados regionais pré-definidos"""
    data = {
        'Regional': ['Barreiro', 'Centro Sul', 'Leste', 'Nordeste', 'Noroeste',
                    'Norte', 'Oeste', 'Pampulha', 'Venda Nova', 'Ignorado'],
        '2020': [1, 2, 3, 4, 5, 3, 2, 1, 4, 0],
        '2021': [2, 1, 2, 5, 4, 3, 2, 1, 3, 1],
        '2022': [1, 0, 3, 6, 5, 4, 1, 2, 4, 0],
        '2023': [3, 1, 2, 7, 6, 5, 2, 1, 5, 1],
        '2024': [2, 1, 3, 8, 7, 6, 3, 2, 6, 0]
    }
    return pd.DataFrame(data)

@st.cache_data
def carregar_dados_caninos():
    """Dados caninos pré-definidos"""
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

# ============================================
# CARREGAR DADOS (SEMPRE DISPONÍVEIS)
# ============================================

dados_humanos = carregar_dados_humanos()
dados_regionais = carregar_dados_regionais()
dados_caninos = carregar_dados_caninos()

# ============================================
# CALCULAR INDICADORES-CHAVE
# ============================================

ultimo_ano = dados_humanos['Ano'].max()
casos_ultimo_ano = int(dados_humanos[dados_humanos['Ano'] == ultimo_ano]['Casos'].values[0])
letalidade_media = dados_humanos['Letalidade_%'].tail(5).mean().round(1)
total_casos = int(dados_humanos['Casos'].sum())

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

# INDICADORES-CHAVE
st.markdown("## 📊 INDICADORES-CHAVE")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📅 Período", f"1994-{ultimo_ano}")

with col2:
    st.metric("🦠 Casos (2024)", f"{casos_ultimo_ano:,}")

with col3:
    st.metric("⚠️ Letalidade", f"{letalidade_media}%")

with col4:
    st.metric("📈 Incidência", f"1.3/100k")

with col5:
    st.metric("📋 Total Histórico", f"{total_casos:,}")

st.markdown("---")

# ============================================
# SEÇÃO 1: EVOLUÇÃO TEMPORAL
# ============================================

st.markdown("## 📈 EVOLUÇÃO TEMPORAL")

# Gráfico 1: Casos e Óbitos
fig1 = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Casos de Leishmaniose Visceral', 'Óbitos Registrados'),
    vertical_spacing=0.15
)

fig1.add_trace(
    go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Casos'],
        mode='lines+markers',
        name='Casos',
        line=dict(color='#1f77b4', width=3),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ),
    row=1, col=1
)

fig1.add_trace(
    go.Scatter(
        x=dados_humanos['Ano'],
        y=dados_humanos['Óbitos'],
        mode='lines+markers',
        name='Óbitos',
        line=dict(color='#d62728', width=3)
    ),
    row=2, col=1
)

fig1.update_layout(height=600, showlegend=True, template='plotly_white')
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Letalidade
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=dados_humanos['Ano'],
    y=dados_humanos['Letalidade_%'],
    mode='lines+markers',
    name='Letalidade',
    line=dict(color='#ff7f0e', width=3),
    fill='tozeroy',
    fillcolor='rgba(255, 127, 14, 0.1)'
))

fig2.update_layout(
    title='Letalidade (%) ao Longo dos Anos',
    xaxis_title='Ano',
    yaxis_title='Letalidade (%)',
    height=400,
    template='plotly_white'
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ============================================
# SEÇÃO 2: DISTRIBUIÇÃO POR REGIONAL
# ============================================

st.markdown("## 🗺️ DISTRIBUIÇÃO POR REGIONAL")

# Seletor de ano para dados regionais
ano_selecionado = st.selectbox(
    "Selecione o ano para visualização:",
    ['2024', '2023', '2022', '2021', '2020'],
    key="ano_regional"
)

# Preparar dados para o ano selecionado
df_regional_ano = dados_regionais[['Regional', ano_selecionado]].copy()
df_regional_ano = df_regional_ano.sort_values(ano_selecionado, ascending=True)

# Gráfico de barras horizontais
fig3 = go.Figure()
fig3.add_trace(go.Bar(
    y=df_regional_ano['Regional'],
    x=df_regional_ano[ano_selecionado],
    orientation='h',
    marker_color='#2ca02c',
    text=df_regional_ano[ano_selecionado],
    textposition='auto'
))

fig3.update_layout(
    title=f'Casos por Regional - {ano_selecionado}',
    xaxis_title='Número de Casos',
    yaxis_title='Regional',
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ============================================
# SEÇÃO 3: VIGILÂNCIA CANINA
# ============================================

st.markdown("## 🐕 VIGILÂNCIA CANINA")

# Gráfico duplo para dados caninos
fig4 = make_subplots(
    rows=2, cols=1,
    subplot_titles=('Cães Soropositivos', 'Imóveis Borrifados'),
    vertical_spacing=0.15
)

fig4.add_trace(
    go.Scatter(
        x=dados_caninos['Ano'],
        y=dados_caninos['Cães_Soropositivos'],
        mode='lines+markers',
        name='Cães Soropositivos',
        line=dict(color='#9467bd', width=3)
    ),
    row=1, col=1
)

fig4.add_trace(
    go.Scatter(
        x=dados_caninos['Ano'],
        y=dados_caninos['Imóveis_Borrifados'],
        mode='lines+markers',
        name='Imóveis Borrifados',
        line=dict(color='#8c564b', width=3)
    ),
    row=2, col=1
)

fig4.update_layout(height=600, showlegend=True, template='plotly_white')
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ============================================
# SEÇÃO 4: TABELAS DE DADOS
# ============================================

st.markdown("## 📋 DADOS COMPLETOS")

# Criar abas para diferentes conjuntos de dados
tab1, tab2, tab3 = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos"])

with tab1:
    st.markdown(f"### Dados Epidemiológicos Humanos ({len(dados_humanos)} anos)")
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
    
    # Botão de download
    csv_humanos = dados_humanos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados humanos (CSV)",
        data=csv_humanos,
        file_name="dados_leishmaniose_humanos.csv",
        mime="text/csv"
    )

with tab2:
    st.markdown(f"### Distribuição por Regional ({len(dados_regionais)} regionais)")
    st.dataframe(dados_regionais, use_container_width=True)
    
    csv_regionais = dados_regionais.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados regionais (CSV)",
        data=csv_regionais,
        file_name="dados_leishmaniose_regionais.csv",
        mime="text/csv"
    )

with tab3:
    st.markdown(f"### Dados de Vigilância Canina ({len(dados_caninos)} anos)")
    st.dataframe(dados_caninos, use_container_width=True)
    
    csv_caninos = dados_caninos.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados caninos (CSV)",
        data=csv_caninos,
        file_name="dados_leishmaniose_caninos.csv",
        mime="text/csv"
    )

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    <strong>🏥 SECRETARIA MUNICIPAL DE SAÚDE DE BELO HORIZONTE</strong><br>
    Coordenação de Vigilância Epidemiológica • Gerência de Zoonoses<br>
    Sistema de Monitoramento da Leishmaniose Visceral • Atualizado em 2025<br>
    <small>Dados para fins epidemiológicos e de gestão em saúde pública</small>
</div>
""", unsafe_allow_html=True)

# Nota informativa
st.sidebar.markdown("---")
st.sidebar.info("""
**ℹ️ SOBRE ESTE DASHBOARD**

Este painel apresenta dados oficiais de monitoramento da Leishmaniose Visceral em Belo Horizonte.

**📊 Dados incluídos:**
- Casos humanos (1994-2025)
- Distribuição por regional
- Vigilância canina
- Ações de controle vetorial

**🎯 Finalidade:**
- Monitoramento epidemiológico
- Tomada de decisão em saúde pública
- Transparência de dados
""")
