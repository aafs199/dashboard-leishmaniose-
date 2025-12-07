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
st.title("🏥 PAINEL LEISHMANIOSE VISCERAL")
st.subheader("Belo Horizonte • Monitoramento Epidemiológico • 1994-2025")
st.markdown("---")

# MENU LATERAL
with st.sidebar:
    st.header("📁 CARREGAR DADOS")
    
    st.markdown("**Faça upload dos arquivos Excel:**")
    
    # Upload dos arquivos
    arquivo1 = st.file_uploader("Dados Humanos (incidencialetalidadelv.xlsx)", type="xlsx", key="upload1")
    arquivo2 = st.file_uploader("Dados por Regional (casoshumanoslvregional.xlsx)", type="xlsx", key="upload2")
    arquivo3 = st.file_uploader("Dados Caninos (anual 2014-2023.xlsx)", type="xlsx", key="upload3")
    
    st.markdown("---")
    st.info("💡 **Dica:** Use os botões acima para carregar seus dados")

# FUNÇÃO PARA PROCESSAR DADOS
def carregar_dados(arquivo):
    if arquivo is not None:
        try:
            return pd.read_excel(arquivo)
        except Exception as e:
            st.error(f"Erro ao ler {arquivo.name}: {str(e)[:100]}")
            return None
    return None

# CARREGAR DADOS
dados_humanos = carregar_dados(arquivo1) if arquivo1 else None
dados_regionais = carregar_dados(arquivo2) if arquivo2 else None
dados_caninos = carregar_dados(arquivo3) if arquivo3 else None

# VERIFICAR SE ALGUM DADO FOI CARREGADO (CÓDIGO CORRIGIDO)
dados_carregados = False

if dados_humanos is not None and isinstance(dados_humanos, pd.DataFrame) and not dados_humanos.empty:
    dados_carregados = True
elif dados_regionais is not None and isinstance(dados_regionais, pd.DataFrame) and not dados_regionais.empty:
    dados_carregados = True  
elif dados_caninos is not None and isinstance(dados_caninos, pd.DataFrame) and not dados_caninos.empty:
    dados_carregados = True

# SEÇÃO 1: TELA INICIAL (SEM DADOS)
if not dados_carregados:
    st.markdown("## 👋 Bem-vindo ao Painel de Monitoramento!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 **Como usar:**
        1. **Na barra lateral à esquerda ←**
        2. **Clique em 'Browse files'**
        3. **Selecione seus arquivos Excel**
        4. **Os gráficos aparecerão automaticamente**
        
        ### 📁 **Arquivos necessários:**
        - `incidencialetalidadelv.xlsx`
        - `casoshumanoslvregional.xlsx`  
        - `anual 2014-2023.xlsx`
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 **Funcionalidades:**
        - 📈 Gráficos interativos
        - 📊 Indicadores em tempo real
        - 🗺️ Mapa de distribuição
        - 📥 Download dos dados
        
        ### 🔧 **Tecnologia:**
        - Desenvolvido em Python
        - Interface moderna e simples
        - Totalmente gratuito
        """)
    
    st.markdown("---")
    st.success("🚀 **Comece carregando seus dados na barra lateral!**")

# SEÇÃO 2: SE HOUVER DADOS CARREGADOS
else:
    # INDICADORES PRINCIPAIS
    st.markdown("## 📊 INDICADORES-CHAVE")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Período", "1994-2025")
    
    with col2:
        if dados_humanos is not None and not dados_humanos.empty:
            # Tentar encontrar coluna com casos
            for col in dados_humanos.columns:
                if dados_humanos[col].dtype in ['int64', 'float64']:
                    try:
                        total_casos = int(dados_humanos[col].sum())
                        st.metric("🦠 Total de Casos", f"{total_casos:,}")
                        break
                    except:
                        continue
        else:
            st.metric("🦠 Total de Casos", "Carregue dados")
    
    with col3:
        if dados_regionais is not None and not dados_regionais.empty:
            num_regionais = len(dados_regionais)
            st.metric("🗺️ Regionais", num_regionais)
        else:
            st.metric("🗺️ Regionais", "Carregue dados")
    
    with col4:
        st.metric("📈 Status", "Ativo")
    
    st.markdown("---")
    
    # GRÁFICOS
    st.markdown("## 📈 VISUALIZAÇÕES")
    
    # GRÁFICO 1: DADOS HUMANOS
    if dados_humanos is not None and not dados_humanos.empty:
        st.markdown("### 📊 Evolução Temporal")
        
        try:
            # Procurar coluna de ano (primeira coluna numérica que parece ano)
            col_ano = None
            col_casos = None
            
            for col in dados_humanos.columns:
                # Verificar se é ano
                try:
                    if dados_humanos[col].dtype in ['int64', 'float64']:
                        valores = dados_humanos[col].dropna()
                        if len(valores) > 0:
                            min_val = float(valores.min())
                            max_val = float(valores.max())
                            if min_val > 1900 and max_val < 2100:
                                col_ano = col
                except:
                    continue
            
            # Se não encontrou ano, usar primeira coluna
            if col_ano is None and len(dados_humanos.columns) > 0:
                col_ano = dados_humanos.columns[0]
            
            # Procurar coluna de casos (outra coluna numérica)
            for col in dados_humanos.columns:
                if col != col_ano:
                    try:
                        if dados_humanos[col].dtype in ['int64', 'float64']:
                            col_casos = col
                            break
                    except:
                        continue
            
            if col_ano is not None and col_casos is not None:
                # Criar gráfico
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dados_humanos[col_ano],
                    y=dados_humanos[col_casos],
                    mode='lines+markers',
                    name='Casos',
                    line=dict(color='blue', width=3)
                ))
                
                fig.update_layout(
                    title=f'Evolução dos Casos',
                    xaxis_title=col_ano,
                    yaxis_title=col_casos,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Visualização dos dados:")
                st.dataframe(dados_humanos.head())
                
        except Exception as e:
            st.error(f"Erro ao criar gráfico: {str(e)[:100]}")
            st.write("Dados carregados:")
            st.dataframe(dados_humanos.head())
    
    # GRÁFICO 2: DADOS REGIONAIS
    if dados_regionais is not None and not dados_regionais.empty:
        st.markdown("### 🗺️ Distribuição por Regional")
        
        try:
            # Encontrar coluna de regionais (primeira coluna não numérica)
            col_regional = None
            for col in dados_regionais.columns:
                if dados_regionais[col].dtype == 'object':
                    col_regional = col
                    break
            
            if col_regional is None and len(dados_regionais.columns) > 0:
                col_regional = dados_regionais.columns[0]
            
            # Encontrar colunas numéricas (anos)
            colunas_numericas = []
            for col in dados_regionais.columns:
                if col != col_regional:
                    try:
                        # Tentar converter para número
                        pd.to_numeric(dados_regionais[col])
                        colunas_numericas.append(col)
                    except:
                        continue
            
            if colunas_numericas:
                # Seletor de ano
                ano_selecionado = st.selectbox(
                    "Selecione o ano:",
                    colunas_numericas,
                    key="ano_selector"
                )
                
                # Preparar dados
                df_plot = dados_regionais[[col_regional, ano_selecionado]].copy()
                df_plot = df_plot.dropna(subset=[ano_selecionado])
                df_plot[ano_selecionado] = pd.to_numeric(df_plot[ano_selecionado], errors='coerce')
                df_plot = df_plot.dropna(subset=[ano_selecionado])
                df_plot = df_plot.sort_values(ano_selecionado, ascending=True)
                
                # Criar gráfico de barras
                if not df_plot.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=df_plot[col_regional],
                        x=df_plot[ano_selecionado],
                        orientation='h',
                        marker_color='green'
                    ))
                    
                    fig.update_layout(
                        title=f'Casos por Regional - {ano_selecionado}',
                        xaxis_title='Número de Casos',
                        yaxis_title='Regional',
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sem dados para o ano selecionado")
            else:
                st.write("Dados regionais:")
                st.dataframe(dados_regionais)
                
        except Exception as e:
            st.error(f"Erro ao processar dados regionais: {str(e)[:100]}")
            st.write("Dados regionais:")
            st.dataframe(dados_regionais)
    
    # SEÇÃO 3: TABELAS DE DADOS
    st.markdown("---")
    st.markdown("## 📋 DADOS BRUTOS")
    
    tabs = st.tabs(["👥 Dados Humanos", "🗺️ Dados Regionais", "🐕 Dados Caninos"])
    
    with tabs[0]:
        if dados_humanos is not None and not dados_humanos.empty:
            st.dataframe(dados_humanos, use_container_width=True)
        else:
            st.info("Carregue dados humanos para ver esta tabela")
    
    with tabs[1]:
        if dados_regionais is not None and not dados_regionais.empty:
            st.dataframe(dados_regionais, use_container_width=True)
        else:
            st.info("Carregue dados regionais para ver esta tabela")
    
    with tabs[2]:
        if dados_caninos is not None and not dados_caninos.empty:
            st.dataframe(dados_caninos, use_container_width=True)
        else:
            st.info("Carregue dados caninos para ver esta tabela")
    
    # RODAPÉ
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        🏥 <strong>Sistema de Monitoramento Epidemiológico</strong><br>
        Desenvolvido para a Secretaria Municipal de Saúde • 2025
    </div>
    """, unsafe_allow_html=True)

# Adicionar mensagem de debug (remova depois que funcionar)
st.sidebar.markdown("---")
st.sidebar.caption(f"Debug: dados_carregados = {dados_carregados}")
